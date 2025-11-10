# WF7 Unified Operations Dashboard — Requirements

## 1. 背景と目的
- 現行の自動集客フロー（note自動投稿→動画化、LP→LINE追加→ステップ配信）の可視化と運用調整を一枚のダッシュボードで行えるようにする。
- n8n・Notion・Google Drive 等の既存ストレージや自動化を維持しつつ、運用担当者の視認性とガバナンスを向上。
- Claude Code で迅速に実装できるよう、複雑性を増やさず既存技術の実用例が多い構成に限定する。

## 2. 制約・設計原則
1. **広く利用されている技術のみ**：Next.js(React)、Tailwind CSS、Supabase/PostgreSQL、Chart.js、LINE Messaging API、GA4 Reporting API、Notion API、Google Drive API、n8n REST API など採用実績が豊富なSaaS/APIに限定。
2. **低複雑性**：マイクロサービス化やリアルタイム双方向通信は避け、スケジュール or on-demand 取得＋キャッシュのシンプル構成。
3. **既存ワークフロー維持**：n8n が唯一のオーケストレーター。フロントはモニタリング＆設定更新用の薄いレイヤー。
4. **インフラ最小化**：Vercel または Cloudflare Pages で静的ホスティング＋Supabase Backend で API/DB をまとめる。
5. **監査性確保**：全ての手動変更は履歴テーブルに保存。ロールバックは n8n 側のフローを再実行する方針。

## 3. 想定ユーザー
| ロール | 主目的 | 主要機能 |
| --- | --- | --- |
| マーケ担当 | KPI監視、ステップ配信の文章調整 | Analytics、LINE/ステップ管理、note/動画品質メモ |
| クリエイティブ担当 | プロンプト品質調整、成果チェック | note記事・動画管理、フィードバック記録 |
| オペレーション担当 | n8n実行状態監視、エラー再実行 | 実行ログ、再実行トリガー、連携設定 |

## 4. システムコンテキスト（テキスト図）
```
Users → Frontend (Next.js) → Backend API (Supabase Edge Functions)
                                   ↓
     ┌─────────────┬─────────────┬──────────────┐
     │n8n REST API │Notion API    │Google APIs (Drive/GA4)│
     └─────────────┴─────────────┴──────────────┘
                                   ↓
                           Supabase Postgres (Cache/Config)
```

## 5. モジュール別機能要件

### 5.1 オペレーションコックピット
- ダッシュボード上部に「今日の指標」「エラー発生数」「n8n最新実行時刻」をカード表示。
- n8n ワークフロー一覧をREST APIで取得し、`status`, `lastSuccess`, `lastError`, `rerunWebhookURL` を表示。
- 失敗行には「再実行」ボタン（n8n Execute Workflow Trigger へPOST）。

### 5.2 LP Analytics
- GA4 Reporting API から `sessions`, `conversions`, `trafficMedium` を取得し、日次ラインチャート + チャネル別テーブル。
- 指標は Supabase に日次キャッシュ（cron or n8n バッチ）。直近7日を即時取得、それ以外は日別CSVをダウンロード可能。

### 5.3 LINE 友だち追加・タグ管理
- Messaging API `GET /friendship/summary` 等で友だち数、増減、ブロック数を取得。
- 友だちリストはフロントには全件表示せず、タグごとの集計数のみテーブル化。
- タグ操作は n8n 経由：フロント→Supabase→n8n Webhook でメッセージを発行し、n8n が Messaging API に反映。

### 5.4 LINE ステップ配信エディタ
- ステップシナリオは `steps` テーブル（step_order, delay_days, message_template, status, updated_by, version）。
- フロントで文章・遅延日数を編集→ドラフト保存（ステータス `pending`）。
- 承認者がプレビュー（実際のテンプレートをLLMに送らず、静的レンダリング）し「反映」→n8n にWebhookし、最新シナリオで配信ノードを更新。
- 変更履歴をタイムライン表示、差分を比較できるよう markdown diff を生成。

### 5.5 note 記事オートメーション管理
- n8n が Notion/Drive に格納したドラフトメタデータをSupabaseに同期。
- ダッシュボードで「生成プロンプト」「使用モデル」「出力URL」「PV/スキ/コメント」を表形式で表示。
- プロンプト調整用の短いテキストエリアとタグ付け（例えば「教育系」「ストーリー型」）。保存はSupabase→n8n Webhook→Notion 更新。

### 5.6 動画生成管理
- 生成ジョブ一覧（動画ID、使用プロンプト、解像度、ステータス、公開URL、再生数）をテーブルとサムネサムネイルで表示。
- 品質評価ラベル（OK/要再生成）とメモを付与。`needs_regen` が true の行は n8n 側で再実行キューに載せる。

### 5.7 KPI 早見 + アラート
- LP/LINE/note/動画の主要KPIを1枚のカード群に統合し、閾値を下回ると視覚的警告＋Slack Webhook 通知。
- 閾値は設定画面で変更可能、変更時は監査ログ残す。

### 5.8 監査ログ・アクセス制御
- ログテーブル `audit_logs` にユーザーID、操作対象、差分、実行結果、関連n8n run ID を記録。
- Auth は Supabase Auth（Google / email）を想定。ロール：viewer / editor / approver / admin。

## 6. データモデル（サンプル）
- `steps`：LINE ステップ配信設定。
- `prompts`：note・動画の生成プロンプトと評価軸。
- `kpi_daily`：LP, LINE, note, video の日次指標。
- `job_runs`：n8n 実行結果から同期した履歴。
- `assets`：生成された記事・動画のメタ情報。
- `audit_logs`：操作履歴。

## 7. 連携要件
1. **n8n REST API**
   - `/rest/workflows/{id}/run` を Execute Workflow Trigger 経由でキック。
   - `/rest/executions?workflowId` で最新ステータス取得。
2. **Notion API**
   - データベースビューの同期を n8n バッチでJSON化→Supabase にアップサート。
3. **Google APIs**
   - GA4 Reporting API, Drive File Metadata API（生成動画やnoteのURL解決）。
4. **LINE Messaging API**
   - 友だち数、タグ、メッセージ送信予約。直接呼ばず、n8n でアクセストークンを管理し、フロントはWebhookで指示。

## 8. 非機能要件
- **可用性**：致命的障害時でも既存n8n自動化は継続。フロント停止は運用画⾯のみ影響する設計。
- **性能**：各ビューの初回描画 < 2 秒（キャッシュ済データ）。生データ呼び出しは、ロード中インジケータと再試行導線。
- **拡張性**：追加チャネル（例：YouTubeアナリティクス）を同じパターンで差し替え可能にする共通KPIインターフェース。
- **セキュリティ**：機密トークンはSupabase Vault/環境変数管理。署名付きリクエストでn8n Webhookを保護。
- **監査**：`audit_logs` を週次でエクスポートし、Notionへ自動貼り付け。

## 9. Claude Code への実装指針
1. **スタック提案**：Next.js 14 App Router + Tailwind CSS + shadcn/ui + Chart.js、状態管理は Zustand。API 呼び出しは `@supabase/supabase-js` と REST fetch。
2. **API 層**：Supabase Edge Functions で統合 API を提供し、n8n/GA4 などの外部API呼び出しを1箇所に集約。Claudeには OpenAPI 仕様を提示し、型に沿った実装を促す。
3. **コード生成テンプレ**：LLM には「各機能は `/modules/<feature>` ディレクトリ内に UI + hooks + service を分割」「UI は server components を優先」など明確な指示を渡す。
4. **テスト戦略**：Playwright で主要フロー（ステップ編集、プロンプト更新、アラート設定）だけを自動テスト。複雑なモックを避け、MSW でAPIレスポンスを差し替える程度に留める。
5. **LLM プロンプト最適化**：プロンプト編集画面にはテンプレートセクションを設け、Claudeに渡す指示書（例：tone, target, CTA）をJSONで保持。Claude Codeには JSON Schema を渡し、スキーマ準拠の出力を要求する。

## 10. 導入ステップ（推奨）
1. Supabase プロジェクト作成＆ベーススキーマ適用。
2. n8n で GA4/LINE/Notion/Drive 同期ワークフローを整備し、Supabase RPC へ書き込むよう変更。
3. Next.js プロジェクト雛形を作成し、Auth とダッシュボードレイアウトを優先構築。
4. 各モジュール（Analytics→LINE→ステップ→note→動画）の順に画面とAPIを追加。
5. 監査ログ・アラート・テストを最後に実装し、完成後に運用手順書をNotionへ登録。

---
この要件定義を Claude Code へ渡せば、低リスクで実用例の多いスタックを前提に実装計画を生成できます。必要に応じて OpenAPI 仕様や DB スキーマDDLを追記してください。
