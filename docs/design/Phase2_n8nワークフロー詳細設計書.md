# Phase2: コンテンツ生成 - n8nワークフロー詳細設計書

**フェーズ**: Phase2 - コンテンツ生成（Week 3-6）
**目標**: note×SNS×LINE連携で22,000PV構築
**総工数**: 80U = 240🍅
**状態**: ⏳ 待機中（Phase1完了後に着手）
**作成日**: 2025-10-27
**バージョン**: 1.0

---

## 📋 目次

1. [Phase2概要](#phase2概要)
2. [WF5: トピック抽出AI](#wf5-トピック抽出ai)
3. [WF6: note記事自動生成](#wf6-note記事自動生成)
4. [WF7: SNS動画化](#wf7-sns動画化)
5. [WF8: SNS投稿自動化](#wf8-sns投稿自動化)
6. [WF9: LINE再配信](#wf9-line再配信)
7. [データフロー統合](#データフロー統合)
8. [技術要件](#技術要件)

---

## Phase2概要

### ビジネス目標

**定量目標**:
- note記事40本公開（週10本×4週）
- SNS投稿40本配信（週10本×4週）
- 累計PV 22,000達成

**定性目標**:
- AI自動生成による記事品質の一定化
- SNS×note×LINEのオムニチャネル配信
- トピックデータの蓄積とフィードバックループ構築

### 全体アーキテクチャ

```
[WF4: note投稿検知] (Phase1)
   ↓ 記事データ蓄積
[WF5: トピック抽出AI] ← 人気トピック特定
   ↓ トピックリスト
[WF6: note記事自動生成] ← GPT-4で記事作成
   ↓ 新規記事公開
[Notion: note記事管理DB更新]
   ↓
┌──────────────┬──────────────┬──────────────┐
│              │              │              │
[WF7: SNS動画化] [WF8: SNS投稿] [WF9: LINE再配信]
   ↓              ↓              ↓
[動画生成]    [X/Instagram]  [LINE配信]
```

### ワークフロー一覧

| WF | 名称 | 工数 | 優先度 | 依存 | 主要技術 |
|----|------|------|--------|------|----------|
| **WF5** | トピック抽出AI | 18🍅 | P0 | WF4 | GPT-4, Notion |
| **WF6** | note記事自動生成 | 30🍅 | P0 | WF5 | GPT-4, note API |
| **WF7** | SNS動画化 | 30🍅 | P1 | WF6 | Runway/Synthesia |
| **WF8** | SNS投稿自動化 | 24🍅 | P0 | WF6, WF7 | X API, Instagram API |
| **WF9** | LINE再配信 | 18🍅 | P1 | WF6 | LINE Messaging API |

---

## WF5: トピック抽出AI

### 基本情報

- **工数**: 18🍅（6ユニット）
- **目的**: Notion「note記事管理DB」から人気記事を分析し、トレンドトピックを抽出
- **トリガー**: Schedule（週2回：水曜・土曜 09:00）
- **実行頻度**: 週2回

### 設計意図

**なぜこのワークフローが必要か**:
- 手動でトピック選定すると属人的になる
- データ駆動でトピック決定することで、PV最大化
- 過去記事の人気度を定量評価し、次のコンテンツ戦略に反映

### ワークフロー構成

```
[1] Schedule Trigger（水・土 09:00）
     ↓
[2] Notion: note記事管理DB取得（過去30日）
     ↓ viewCount, likeCount, 公開日
[3] Function: スコアリング
     ↓ PV×0.6 + いいね×0.4 = 人気度スコア
[4] Function: トップ10記事抽出
     ↓ スコア上位10件
[5] GPT-4: トピック抽出
     ↓ 共通キーワード、トレンド分析
[6] Notion: トピックマスタ更新
     ↓ トピック名、スコア、関連記事リスト
[7] Slack: トピック通知
     ↓ 「今週のトレンドトピック: {トピック}」
```

### GPT-4プロンプト設計

```
あなたはコンテンツストラテジストです。
以下の人気note記事データから、トレンドトピックを抽出してください。

【データ】
{top10記事のタイトル、カテゴリ、本文プレビュー}

【分析観点】
1. 共通キーワードの抽出
2. ユーザーニーズの推定
3. 次に書くべきトピック提案（5つ）

【出力形式】
## トレンドキーワード
## ユーザーニーズ分析
## 次のトピック提案（優先度順）
```

### データ構造

**Notion: トピックマスタ**

| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| Topic Name | Title | トピック名 |
| Score | Number | 人気度スコア |
| Keywords | Multi-select | 関連キーワード |
| Related Articles | Relation | 関連記事リスト |
| Extracted At | Date | 抽出日時 |
| Status | Select | active/archived |

---

## WF6: note記事自動生成

### 基本情報

- **工数**: 30🍅（10ユニット）
- **目的**: トピックマスタに基づき、GPT-4でnote記事を自動生成・公開
- **トリガー**: Schedule（毎日 10:00）
- **実行頻度**: 毎日1本 → 週7本（目標10本達成のため手動追加実行も可）

### 設計意図

**なぜこのワークフローが必要か**:
- 手動記事作成は時間がかかる（1本2-3時間）
- AI自動化で週10本のペースを維持
- 一定品質を保ちながら量産体制を構築

### ワークフロー構成

```
[1] Schedule Trigger（毎日 10:00）
     ↓
[2] Notion: トピックマスタ取得
     ↓ Status='active' のトピック
[3] Function: トピック選択
     ↓ スコア最高のトピックを選択
[4] GPT-4: 記事タイトル生成
     ↓ 3候補生成
[5] Function: タイトル選択
     ↓ 最もCTR高そうなタイトル
[6] GPT-4: 記事本文生成（3,000-5,000文字）
     ↓ 構成: 導入→本論→結論
[7] Function: note Markdown変換
     ↓ HTML → note Markdown形式
[8] HTTP Request: note API投稿
     ↓ タイトル、本文、カテゴリ、タグ
[9] Notion: note記事管理DB登録
     ↓ 自動生成フラグ付き
[10] Slack: 投稿完了通知
     ↓ 「新規記事公開: {タイトル}」
```

### GPT-4プロンプト設計

#### タイトル生成

```
あなたはnoteで人気の記事タイトルを書く専門家です。

【トピック】
{トピック名}

【関連キーワード】
{キーワードリスト}

【タスク】
以下の3つのタイトルを生成してください:
1. 疑問形（例: 「〜は本当に効果的？」）
2. How-to形式（例: 「〜を成功させる5つの方法」）
3. ストーリー形式（例: 「〜で失敗した私が学んだこと」）

【制約】
- 30文字以内
- 数字を含める
- 検索されやすいキーワードを含む
```

#### 本文生成

```
あなたは英語学童・バイリンガル教育の専門ライターです。

【タイトル】
{選択されたタイトル}

【ターゲット読者】
- 3-10歳の子供を持つ保護者
- 英語教育に関心がある
- 教室選びを検討中

【構成】
1. 導入（500文字）: 読者の悩みに共感
2. 本論（2,500文字）: 具体的な解決策・事例
3. 結論（500文字）: アクション呼びかけ

【トーン】
- 親しみやすい
- 専門的すぎない
- 具体例を多用

【出力形式】
note Markdown形式で出力してください。
```

### note API統合

```yaml
Node Type: HTTP Request
Method: POST
URL: https://note.com/api/v2/notes
Authentication: OAuth2 (note APIトークン)
Headers:
  - Content-Type: application/json
Body:
  {
    "note": {
      "name": "{{$json.title}}",
      "body": "{{$json.markdownBody}}",
      "status": "published",
      "price": 0,
      "eyecatch": "{{$json.eyecatchUrl}}"
    }
  }
```

---

## WF7: SNS動画化

### 基本情報

- **工数**: 30🍅（10ユニット）
- **目的**: note記事から動画コンテンツを自動生成し、SNS用に最適化
- **トリガー**: Webhook（WF6からの通知）
- **実行頻度**: WF6実行後（毎日1本）

### 設計意図

**なぜこのワークフローが必要か**:
- テキストだけでなく動画でもリーチ拡大
- Instagram Reels、TikTok、YouTube Shortsで拡散
- 動画生成の自動化でリソース削減

### ワークフロー構成

```
[1] Webhook Trigger（WF6からの通知）
     ↓ articleId, title, bodyPreview
[2] Notion: 記事本文取得
     ↓ 完全な本文データ
[3] GPT-4: 動画スクリプト生成
     ↓ 30-60秒の動画台本
[4] HTTP Request: Runway/Synthesia API
     ↓ スクリプト → 動画生成
[5] Function: 動画ダウンロード・保存
     ↓ MP4ファイル取得
[6] Google Drive: 動画保存
     ↓ ファイルID取得
[7] Notion: 動画管理DB登録
     ↓ 動画URL、関連記事リンク
[8] Slack: 動画生成完了通知
```

### 動画生成API選定

| API | 特徴 | 料金 | 用途 |
|-----|------|------|------|
| **Runway Gen-2** | 高品質、リアル映像 | $12/100クレジット | メイン |
| **Synthesia** | アバター解説動画 | $30/月（10動画） | 補助 |
| **D-ID** | トーキングヘッド | $5.9/月 | 補助 |

**推奨**: Runway Gen-2をメインに使用

---

## WF8: SNS投稿自動化

### 基本情報

- **工数**: 24🍅（8ユニット）
- **目的**: note記事・動画をX、Instagramに自動投稿し、拡散を最大化
- **トリガー**: Schedule（毎日 20:00）
- **実行頻度**: 毎日1回

### 設計意図

**なぜこのワークフローが必要か**:
- 最適な投稿時間（20:00-21:00）に自動投稿
- 複数プラットフォームへの同時配信
- ハッシュタグ最適化で検索流入増加

### ワークフロー構成

```
[1] Schedule Trigger（毎日 20:00）
     ↓
[2] Notion: 今日公開の記事取得
     ↓ publishedDate = 今日
[3] Google Drive: 動画取得（存在する場合）
     ↓ 動画URL
[4] GPT-4: SNS投稿文生成
     ↓ X用（140文字）、Instagram用（2,200文字）
[5] Function: ハッシュタグ最適化
     ↓ トレンドハッシュタグ追加
[6] HTTP Request: X API投稿
     ↓ テキスト + 画像/動画
[7] HTTP Request: Instagram API投稿
     ↓ キャプション + メディア
[8] Notion: 投稿ログ保存
     ↓ プラットフォーム、投稿ID、URL
[9] Slack: 投稿完了通知
```

### X/Instagram API設定

**X API v2**:

```yaml
Method: POST
URL: https://api.twitter.com/2/tweets
Authentication: OAuth 2.0
Body:
  {
    "text": "{{$json.tweetText}}",
    "media": {
      "media_ids": ["{{$json.mediaId}}"]
    }
  }
```

**Instagram Graph API**:

```yaml
Method: POST
URL: https://graph.facebook.com/v18.0/{ig-user-id}/media
Authentication: Access Token
Body:
  {
    "image_url": "{{$json.imageUrl}}",
    "caption": "{{$json.caption}}",
    "access_token": "{{ACCESS_TOKEN}}"
  }
```

---

## WF9: LINE再配信

### 基本情報

- **工数**: 18🍅（6ユニット）
- **目的**: 人気記事をLINE友だちに再配信し、CVR向上
- **トリガー**: Schedule（週1回：金曜 19:00）
- **実行頻度**: 週1回

### 設計意図

**なぜこのワークフローが必要か**:
- 既存LINE友だちへのリエンゲージメント
- 人気記事の再活用でPV底上げ
- ステップ配信だけでなく、定期的なコンテンツ配信

### ワークフロー構成

```
[1] Schedule Trigger（金曜 19:00）
     ↓
[2] Notion: 人気記事トップ3取得
     ↓ viewCount降順で3件
[3] Google Sheets: LINE友だちリスト取得
     ↓ userId一覧
[4] Function: メッセージ構築
     ↓ 記事紹介文 + URL
[5] Loop: 友だちごと処理
     ├→ [6] HTTP Request: LINE Messaging API
     └→ [7] Function: 配信ログ記録
[8] Google Sheets: 再配信ログ保存
     ↓ articleId, deliveredCount
[9] Slack: 配信完了通知
```

---

## データフロー統合

### Phase2データフロー全体図

```
[WF4: note投稿検知] (Phase1)
   ↓ 記事データ蓄積
   ↓
[Notion: note記事管理DB]
   ↓
[WF5: トピック抽出AI]
   ↓ 人気トピック
[Notion: トピックマスタ]
   ↓
[WF6: note記事自動生成]
   ↓ 新規記事公開
[note API] + [Notion: note記事管理DB]
   ↓
┌──────────────────┬──────────────────┬──────────────────┐
│                  │                  │                  │
[WF7: SNS動画化]  [WF8: SNS投稿]    [WF9: LINE再配信]
   ↓                  ↓                  ↓
[Google Drive]    [X/Instagram]      [LINE配信]
   ↓                  ↓                  ↓
[Notion: 動画DB]  [Notion: 投稿ログ] [Google Sheets: 配信ログ]
```

### データベース追加設計

#### Notion: トピックマスタ

| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| Topic Name | Title | トピック名 |
| Score | Number | 人気度スコア |
| Keywords | Multi-select | 関連キーワード |
| Related Articles | Relation | 関連記事（note記事管理DBへ） |
| Extracted At | Date | 抽出日時 |
| Status | Select | active/archived |

#### Notion: 動画管理DB

| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| Title | Title | 動画タイトル |
| Video URL | URL | Google Drive URL |
| Related Article | Relation | 元記事（note記事管理DBへ） |
| Platform | Multi-select | YouTube/Instagram/TikTok |
| Duration | Number | 動画長（秒） |
| Generated At | Date | 生成日時 |
| Status | Select | pending/generated/published |

#### Notion: SNS投稿ログ

| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| Platform | Select | X/Instagram |
| Post ID | Text | プラットフォーム投稿ID |
| Post URL | URL | 投稿URL |
| Related Article | Relation | note記事へのリンク |
| Post Text | Rich Text | 投稿文 |
| Published At | Date | 投稿日時 |
| Engagement | Number | いいね・RT数 |

---

## 技術要件

### API統合

| API | 用途 | 認証方式 | レート制限 |
|-----|------|----------|-----------|
| **GPT-4 API** | 記事生成、トピック抽出 | API Key | 10,000 req/日 |
| **note API** | 記事投稿 | OAuth2 | 100 req/日 |
| **X API v2** | ツイート投稿 | OAuth 2.0 | 1,500 req/日 |
| **Instagram Graph API** | 投稿 | Access Token | 200 req/時 |
| **Runway API** | 動画生成 | API Key | クレジット制 |
| **Google Drive API** | 動画保存 | OAuth2 | 1,000 req/日 |

### コスト見積もり

**月次コスト**:
- GPT-4 API: $50（記事生成10本/日×30日）
- Runway: $36（動画10本/日×30日）
- note API: 無料
- X API: 無料（Free Tier）
- Instagram API: 無料

**合計**: 約$86/月（約¥13,000）

### エラーハンドリング

- **GPT-4 API障害**: リトライ3回 → フォールバック（テンプレート記事生成）
- **note API障害**: リトライ3回 → 下書き保存 → 手動公開
- **SNS API障害**: リトライ3回 → ログ保存 → 翌日再投稿

---

## Phase2完了判定基準

- [ ] WF5, WF6, WF7, WF8, WF9すべて稼働
- [ ] note記事40本公開達成
- [ ] SNS投稿40本達成
- [ ] 累計PV 22,000達成
- [ ] 動画生成成功率 >80%
- [ ] SNS投稿成功率 >95%
- [ ] LINE再配信開封率 >40%

---

## 関連ドキュメント

- [[MEO集客自動化_n8nワークフロー全体構成]]
- [[Phase1_n8nワークフロー詳細設計書]]
- [[Phase3_n8nワークフロー詳細設計書]]
- [[Phase4_n8nワークフロー詳細設計書]]

---

## 更新履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|----------|--------|
| 1.0 | 2025-10-27 | 初版作成 - Phase2全ワークフロー設計 | Claude + User |

---

**次のステップ**: Phase1完了後にWF5から順次実装
