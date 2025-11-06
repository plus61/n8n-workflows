# MEO Operations Hub 再設計計画書

**目的**  
LINE登録／ステップ配信／記事自動作成／SNS動画生成に跨る MEO オートメーションで、Notion ページと n8n ワークフローの情報が分散している状態を解消し、1 つの統合ハブから運用状況を把握・更新できるようにする。

---

## 1. ゴール
- Notion 上に「MEO Operations Hub」データベースを新設し、既存の `動画管理DB` / `note記事管理DB` / LINE 配信データを統合して参照できる。
- 各 n8n ワークフロー（WF7 Phase1〜5、LINE 養育フロー等）が Hub DB のレコードを起点／終点に処理するようノード設定とコードを整理する。
- Webhook 実行結果やエラーが Hub DB に集約され、運用担当がビューを切り替えるだけで状況把握できる。

---

## 2. Notion 情報設計

### 2.1 新規データベース: MEO Operations Hub
- **主キー**: `Title`（例: キャンペーン名 + 記事ID）
- **主要プロパティ**
  | プロパティ名 | 型 | 役割 |
  |--------------|----|------|
  | `Article ID` | Text | n8n から渡される記事識別子 |
  | `Workflow Status` | Select | Draft / ScriptReady / AssetsReady / NarrationReady / Rendered / Distributed / Failed |
  | `Channel` | Multi-select | LINE / note / YouTube / TikTok 等 |
  | `Related Video` | Relation → 動画管理DB | 動画メタを参照 |
  | `Related Article` | Relation → note記事管理DB | 長文記事メタ |
  | `Related LINE Campaign` | Relation → LINE配信DB | ステップ配信設定 |
  | `Current Phase` | Formula | 各 Relation のステータスから算出 |
  | `Latest Execution ID` | Text | n8n 実行ID |
  | `Script JSON` / `Assets JSON` / `Render URL` / `Thumbnail URL` | URL / Rich text | 各工程の成果物 |
  | `Error Log` | Rich text | 最新エラー内容／スタックトレース |
  | `Schedule Date` | Date | 配信予定日 |

- **推奨ビュー**
  1. **Kanban – Overview**
     - 列: `Workflow Status`
     - フィルター: `Channel` が空ではない
     - 表示プロパティ: `Article ID`, `Channel`, `Current Phase`, `Latest Execution ID`
  2. **Table – Channel Matrix**
     - ソート: `Channel` 昇順 → `Current Phase` 昇順
     - フィルター: `Workflow Status` ≠ `Archive`
     - 列カスタム: `Channel`, `Workflow Status`, `Schedule Date`, `Related Video`, `Related Article`, `Related LINE Campaign`
  3. **Calendar – Release Schedule**
     - 基準日: `Schedule Date`
     - 表示名: `Title`
     - 表示プロパティ: `Workflow Status`, `Channel`
  4. **Timeline – Production Pipeline**
     - 期間軸: `Created At` → `Schedule Date`
     - グループ: `Channel`
     - 期間表示: 月
  5. **Gallery – Campaign Snapshot**
     - カード: `Title`, `Workflow Status`, `Channel`, `Thumbnail URL`
     - フィルター: `Workflow Status` が `Rendered` または `Distributed`
  6. **Board – Error Inbox**
     - 列: `Workflow Status`
     - フィルター: `Workflow Status` = `Failed`
     - 表示プロパティ: `Article ID`, `Error Log`, `Latest Execution ID`
  7. **List – Data Ops**
     - ソート: `Last Edited Time` 降順
     - 表示プロパティ: `Article ID`, `Channel`, `Workflow Status`, `Current Phase`, `Latest Execution ID`, `Related` 各 DB
     - 用途: バルク編集・運用チェック

### 2.2 既存 DB 調整
- `動画管理DB` / `note記事管理DB` に以下を追加
  - `Hub Entry` (Relation → Hub DB)
  - `Lifecycle Stage` (Select)
  - `Last Sync At` (Date)
- テンプレートを Hub 用に更新し、新規ページ作成時に自動で Hub Entry と紐づくよう設定する。

### 2.3 LINE 配信 DB
- 必要なら新規作成し、プロパティを統一:
  - `Campaign ID`, `Segment`, `Template`, `Step Order`, `Scheduled At`, `Hub Entry` relation。

### 2.4 既存データ移行
1. Notion から現行ページをエクスポート／抽出し、Hub DB に一括登録。
2. 既存ページの主要プロパティ（Article ID, Status 等）を Hub DB と整合させる。
3. 旧個別ページはアーカイブし、Hub の Relation から辿れるよう案内を追加。

---

## 3. n8n ワークフロー調整方針

### 3.1 共通コンテキスト取得
- 各ワークフローの冒頭で `Fetch Hub Context` Code ノードを挿入し、`articleId` をキーに Hub DB のレコードを取得。
- 取得結果を `context` オブジェクトとして後続ノードで使用（Notion API Node → `Resource: Page, Operation: Update` 等で再利用）。

### 3.2 Phase1〜5 の変更
- Phase1: Hub DB から `Script JSON` を書き込み、`Workflow Status` を `ScriptReady` に更新。
- Phase2: Hub DB から `Asset Tags` / `Assets JSON` / `Google Drive ID` 等を読み書きし、結果を `AssetsReady` へ遷移。
- Phase3: ナレーション生成後、`Voice URL`／`Narration Status` を Hub に保存。
- Phase4: FFmpeg レンダリング完了で `Render URL`, `Thumbnail URL`, `Latest Execution ID` を更新し、ステータスを `Rendered` に。
- Phase5: メタ登録後に `Distributed` へ遷移し、配信ログを `Related LINE Campaign` / `Related Article` に書き戻す。

### 3.3 LINE 配信フロー
- LINE ステップ配信ワークフローが Hub DB の `Channel = LINE` かつ `Workflow Status = Distributed` のレコードを監視し、自動投入。
- Segment 分岐や配信テンプレートを `Related LINE Campaign` から取得。

### 3.4 共通ノード更新
- Notion ノードの参照先を Hub DB に統一。
- 環境変数／コード内ハードコードされていた `notionPageId` を廃止し、Hub参照に一本化。
- 例外時は `Error Log` と `Workflow Status = Failed` を Hub に書き戻すトリートメントを追加。

---

## 4. 実装ステップ

1. **Notion 準備**
   - Hub DB 作成 → プロパティ／ビュー設定 → 既存テンプレート更新。
   - 必要に応じて新 DB (`LINE Campaigns` 等) を作成。
2. **データ移行**
   - 既存ページを Hub に登録し、Relation で紐づけ。
   - 旧ページの整理とリダイレクト案内作成。
3. **n8n 改修**
   - Phase1〜5 / LINE 関連ワークフローで `Fetch Hub Context` ノードを追加。
   - Notion Update ノードの対象・フィールドを Hub に切り替え。
   - エラーハンドリングとステータス更新処理を Hub 基準に統一。
4. **テスト**
   - サンプル記事で Phase1→Phase5→LINE を通し、Hub に意図したデータが蓄積・可視化されることを検証。
   - 失敗ケース（API エラー等）で `Error Log` と `Workflow Status` が正しく更新されるか確認。
5. **ドキュメント整備**
   - `docs/n8n-notion-integration.md` を新規作成し、Hub DB 構造／n8n ノード設定／運用ルールを記載。
   - 既存の `wf7-*.md` などに Hub 構成への移行手順・変更点を追記。

---

## 5. 留意点
- Hub DB の編集権限を持つメンバーと調整し、既存テンプレート変更に伴う影響を周知する。
- n8n の Notion Credential に Hub DB へのアクセス権限があるか事前に確認（必要なら権限を追加）。
- 大量データ移行が必要な場合は n8n もしくは外部スクリプトでバッチ処理を実施。
- Hub 統合後は Notion ページ作成フローを見直し、Hub テンプレートから開始する運用に切り替える。

---

## 6. 期待されるメリット
- MEO 関連の進捗を Hub DB のビューだけで把握・更新でき、散在した Notion ページを横断する手間が減る。
- n8n が Hub DB を唯一のデータソースとして参照するため、pageId ハードコードやプロパティ名の不一致によるエラーが軽減される。
- エラー／配信ログ／生成物が Hub に集約され、運用改善やレポート作成が容易になる。
