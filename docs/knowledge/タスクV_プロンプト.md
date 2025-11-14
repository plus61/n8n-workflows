# タスクV: AIレポート自動生成 - 実装プロンプト

**生成日**: 2025-10-26  
**元要件**: タスクV_AIレポート自動生成_要件定義書.md  
**使用ガイド**: docs/prompt-design-guide.md

---

## 🎯 実装プロンプト

```markdown
@mcp-sequential-thinking
@n8n-workflows-docs
@n8n-mcp

MEO集客自動化プロジェクトのAIレポート自動生成ワークフローを作成したいです。段階的に設計して実装してください。

【背景・現状】
- MEO集客自動化プロジェクトのPhase4（Week 11-12）
- Phase3まででデータ収集基盤は完成（タスクU: KPI統合ダッシュボード）
- 現在: 週5時間の手動分析作業が発生
- 問題点:
  1. データ分析に週5時間（年260時間）を消費
  2. 改善提案が経験則に依存し、客観性に欠ける
  3. PDCAサイクルが週1回と遅い
  4. 施策決定に時間がかかり、タイミングを逃す
- 手動作業: KPIデータを見て、Excel/Notionにレポート作成、Slackで共有、改善施策を検討

【目標・要件】
目的: AI自走改善ループの稼働（データ収集→AI分析→改善提案→自動実行）

## 処理フロー

### フロー全体
```
1. データ収集（タスクUから）
   ↓
2. GPT-4でAI分析・レポート生成
   ↓
3. レポート配信（Notion + LINE + メール）
   ↓
4. 改善提案の自動実行（タスクW/Xへ連携）
```

### トリガー
- 日次: 毎日9:00（Schedule）
- 週次: 月曜9:00（Schedule）
- 月次: 1日9:00（Schedule）

### 入力データ
ソース: タスクU（KPI統合ダッシュボード）のAPIエンドポイント
形式: JSON

サンプルデータ構造:
```json
{
  "date": "2025-11-15",
  "period": "daily",
  "kpis": {
    "pv": {
      "current": 18500,
      "target": 22300,
      "yesterday": 18200,
      "last_week": 17000,
      "last_month": 15000
    },
    "cvr": {
      "current": 25.5,
      "target": 30.0,
      "yesterday": 26.0,
      "last_week": 24.0,
      "last_month": 22.0
    },
    "line": {
      "friends": 1200,
      "open_rate": 45.0,
      "click_rate": 12.5
    },
    "note": {
      "articles": 42,
      "top_articles": [
        {
          "title": "英語学童の選び方",
          "pv": 850,
          "cv": 15
        }
      ]
    },
    "sns": {
      "posts": 45,
      "engagement_rate": 3.2
    },
    "demo": {
      "reservations": 35,
      "conversions": 10,
      "conversion_rate": 28.5
    }
  }
}
```

### 処理内容
1. **データ収集** (Node 1-3)
   - HTTP Request: タスクUのAPIからKPIデータ取得（Bearer認証）
   - Function: データ整形・達成率計算
   - エラー時: 3回リトライ → 前日データで代替 + アラート

2. **AI分析** (Node 4-5)
   - GPT-4 API呼び出し（gpt-4-turbo, temperature: 0.3）
   - プロンプト:
     ```
     あなたはMEO集客自動化プロジェクトのデータアナリストです。
     以下のKPIデータを分析し、改善提案を行ってください。
     
     【KPIデータ】
     - PV: {{current_pv}} / 目標22,300 ({{achievement_rate}}%)
     - CVR: {{current_cvr}}% / 目標30%
     - LINE友だち: {{line_friends}}人
     - note記事: {{note_articles}}本
     - SNS投稿: {{sns_posts}}本
     - デモ予約: {{demo_reservations}}件
     - 成約率: {{conversion_rate}}%
     
     【分析観点】
     1. 目標達成度の評価
     2. 前週比・前月比のトレンド分析
     3. 問題点・ボトルネックの特定
     4. 改善提案（優先度順、Top 5）
     
     【出力形式】
     以下の構造化されたMarkdown形式で出力してください：
     ## 📊 KPI達成度サマリー
     ## 📈 トレンド分析
     ## ⚠️ 問題点・ボトルネック
     ## 💡 改善提案（優先度順）
     ### 提案1: [タイトル]
     - 期待効果: ...
     - 実行難易度: ...
     - 推奨実施時期: ...
     ## 🤖 自動実行予定
     ## 📌 手動確認が必要な施策
     ```
   - Function: レポートをパース、改善提案を抽出・分類（自動実行可能/手動確認必要）
   - エラー時: 3回リトライ → 簡易レポート（テンプレート）生成 + アラート

3. **レポート保存** (Node 6)
   - Notion API: 専用データベースに新規ページ作成
   - プロパティ:
     - Title: "日次レポート {{date}}"
     - Period: Select（daily/weekly/monthly）
     - Generated_At: Date
     - PV_Achievement: Number（達成率）
     - CVR_Current: Number
     - Proposals_Count: Number
     - Auto_Executed: Number
     - Manual_Required: Number
     - Content: Rich Text（Markdown）
     - Status: Select（generated/reviewed/implemented）
   - エラー時: 3回リトライ → Google Sheetsに保存 + アラート

4. **通知配信** (Node 7)
   - LINE Messaging API: サマリー通知（160文字以内）
     ```
     📊 日次レポート完了
     
     【達成度】
     PV: {{pv_achievement}}% | CVR: {{cvr_achievement}}%
     
     【Top提案】
     🔥 {{proposal_1}} → {{status_1}}
     ⚡ {{proposal_2}} → {{status_2}}
     
     詳細: {{notion_url}}
     ```
   - エラー時: 3回リトライ → メール通知 + エラーログ

5. **自動実行連携** (Node 8-9)
   - IF Node: 改善提案に自動実行可能フラグがあるか判定
   - HTTP Request: タスクW（人気記事再配信）/タスクX（トピック再学習）のWebhook呼び出し
   - Body: 自動実行可能な提案のJSON
   - 手動確認必要な提案: Notion上でステータス「要確認」に設定

6. **アラート機能** (Node 10)
   - IF Node: 異常値検知
     - PV急減: 前日比-20%以上
     - CVR急減: 前日比-15%以上
   - LINE即時通知:
     ```
     🚨 緊急アラート
     
     {{alert_type}}: {{value}}
     前日比: {{change}}%
     
     レポート: {{notion_url}}
     ```

### 出力
- Notion: レポートページ作成（Markdown形式、グラフ埋め込み）
- LINE: サマリー通知（日次・週次・月次）
- メール: 詳細レポートPDF添付（週次・月次のみ）
- タスクW/X: 自動実行指示JSON

【制約条件】
- 使用サービス:
  - n8n（Railway上で稼働、v1.0以上）
  - GPT-4 API（gpt-4-turbo、月次予算アラート設定）
  - Notion API（v2022-06-28以降、レート制限遵守）
  - LINE Messaging API
  - タスクU API（KPIデータ取得用）
  - タスクW/X Webhook（アクション連携用）

- パフォーマンス要件:
  - レポート生成時間: 日次3分以内、週次5分以内、月次10分以内
  - GPT-4レスポンス: 30秒以内
  - Notion保存: 10秒以内
  - LINE通知遅延: 30秒以内

- セキュリティ要件:
  - APIキー: n8n環境変数で管理（平文禁止）
  - データアクセス: Notion Integration最小権限
  - 通信: 全API通信HTTPS必須

- エラーハンドリング:
  - 全APIコール: 3回リトライ（指数バックオフ）
  - フォールバック戦略あり（上記処理内容参照）
  - エラーログ: n8nに30日間保存
  - 即時アラート: LINE + メール

【依頼内容】
1. Sequential Thinkingで設計を段階的に考える
   - Zie619から類似のワークフロー例を探す（特にGPT-4統合、スケジュール分析、レポート生成）
   - 最適なノード構成を検討（6つのノードグループ）
   - エラーハンドリング戦略を立てる（リトライ、フォールバック、アラート）
   - GPT-4トークン最適化（コスト削減）
   - 週次・月次への拡張方法を検討

2. n8n-workflows-docsで参考例を探す
   - Schedule Trigger（複数頻度）のパターン
   - GPT-4 API連携のベストプラクティス
   - Notion API（Rich Text、Database作成）の実装例
   - HTTP Request認証（Bearer Token）の設定方法
   - エラーハンドリング（リトライ、フォールバック）の実装
   - Function Node（データ整形、パース）のコード例

3. n8n-mcpで実装
   【メインワークフロー: AIレポート自動生成（日次）】
   
   Node 1: Schedule Trigger
   - cron: "0 9 * * *"（毎日9:00）
   - timezone: "Asia/Tokyo"
   
   Node 2: HTTP Request - KPIデータ取得
   - method: GET
   - url: "{{$env.TASK_U_API_URL}}/kpi/daily"
   - authentication: Bearer Token
   - token: "{{$env.TASK_U_API_TOKEN}}"
   - continueOnFail: true
   - retry: 3（指数バックオフ）
   
   Node 3: Function - データ整形
   - 達成率計算
   - 前日比・前週比計算
   - GPT-4プロンプト用にフォーマット
   
   Node 4: GPT-4 - AI分析
   - model: "gpt-4-turbo"
   - temperature: 0.3
   - max_tokens: 2500
   - prompt: "{{上記のプロンプトテンプレート}}"
   - continueOnFail: true
   - retry: 3
   
   Node 5: Function - レポート構造化
   - GPT-4出力をパース
   - 改善提案を抽出（正規表現またはJSON解析）
   - 自動実行可能/手動確認必要に分類
   
   Node 6: Notion - レポート保存
   - operation: "Create Page"
   - database_id: "{{$env.NOTION_REPORT_DB_ID}}"
   - properties設定（上記参照）
   - continueOnFail: true
   - retry: 3
   
   Node 7: LINE Notify - サマリー通知
   - message: "{{上記のテンプレート}}"
   - continueOnFail: true
   - retry: 3
   
   Node 8: IF - 自動実行判定
   - condition: "{{$json.proposals.auto_executable.length > 0}}"
   - true: → Node 9
   - false: → End
   
   Node 9: HTTP Request - タスクW/X連携
   - method: POST
   - url: "{{$env.TASK_W_WEBHOOK_URL}}"
   - body: "{{$json.proposals.auto_executable}}"
   
   Node 10: IF - アラート判定（並列）
   - PV急減 or CVR急減 → LINE即時通知
   
   【週次・月次ワークフローの作成も依頼】
   - 日次ワークフローをベースに作成
   - 変更点:
     - Schedule Trigger（週次: 月曜9:00、月次: 1日9:00）
     - データ集計期間（API URLのパラメータ変更）
     - GPT-4プロンプト（分析深度を上げる）
     - メールPDF配信追加（Puppeteer/PDF.co使用）

4. バリデーションと最適化
   - ワークフロー全体の接続確認
   - エラーハンドリングのテスト（各APIの失敗ケース）
   - パフォーマンステスト（3分以内に完了するか）
   - GPT-4トークン数確認（コスト見積もり）
   - 改善提案の抽出ロジック検証
   - 週次・月次ワークフローの動作確認

5. ドキュメント生成
   - ワークフロー構造図
   - 各ノードの設定値一覧
   - 環境変数リスト（TASK_U_API_URL等）
   - エラー時の対応手順
   - 運用マニュアル（簡易版）

【参考情報】
- 前提タスク: タスクU（KPI統合ダッシュボード）が完成していること
- 連携タスク: タスクW（人気記事再配信）、タスクX（トピック再学習）
- Notion Database: 新規作成が必要（レポート履歴管理用）
- 実装期間: 6ユニット（18🍅 = 約9時間）
- Phase4目標: AI自走改善ループ稼働（7日間連続で人間の介入なし）

【成功の基準】
1. 機能的成功:
   - 日次・週次・月次レポートが自動生成される
   - GPT-4が客観的な改善提案を5つ以上生成する
   - 自動実行可能な提案が自動でタスクW/Xに連携される
   - レポート生成成功率: 99%以上
   - 処理時間: 日次3分以内、週次5分以内、月次10分以内

2. ビジネス的成功:
   - 分析工数: 週5時間 → 0時間
   - PDCA速度: 週1回 → 日次
   - 1週間連続で正常稼働
   - 自動実行された施策が3つ以上ある
   - KPIが改善傾向（CVR +0.5%以上）

3. 運用的成功:
   - エラー発生時に適切にフォールバック
   - アラートが正しく動作
   - レポートが読みやすく、アクション可能な内容
```

---

## 📝 補足説明

### このプロンプトについて

**設計方針**:
- プロンプト設計指針書の「ワークフロー作成用（詳細版）」テンプレートを使用
- 要件定義書の785行の内容を、実装に必要な情報に絞って整理
- Sequential Thinkingで段階的に設計→実装できるよう構造化

**選択したMCP**:
- `@mcp-sequential-thinking`: 複雑なワークフロー設計を段階的に思考
- `@n8n-workflows-docs`: Zie619から類似例（GPT統合、レポート生成）を検索
- `@n8n-mcp`: 実際のワークフロー実装

**プロンプトの特徴**:
1. ✅ 具体的なノード構成（Node 1-10）を明示
2. ✅ 実際のコード例（JSON、プロンプト、cron式）を含む
3. ✅ エラーハンドリング戦略を詳細化
4. ✅ パフォーマンス目標を数値で指定
5. ✅ 成功の基準を測定可能に定義

### 使用方法

1. **このプロンプトをコピー**（```markdown の中身全て）
2. **Cursor/Claudeに貼り付け**
3. **実行を待つ**（Sequential Thinkingで段階的に設計されます）
4. **結果を確認**して、必要に応じて調整

### 想定される実行フロー

```
1. Sequential Thinking開始（5-10 thoughts）
   - Zie619から類似ワークフロー検索
   - ノード構成の最適化検討
   - エラーハンドリング戦略

2. n8n-workflows-docs検索
   - GPT-4統合の例
   - Schedule Triggerの設定方法
   - Notion API Rich Textの扱い方

3. n8n-mcpで実装
   - メインワークフロー作成（日次）
   - ノード接続・設定
   - テスト実行

4. 週次・月次ワークフロー作成

5. バリデーション・最適化

6. ドキュメント生成
```

### 期待される成果物

- ✅ n8nワークフローJSON（3つ: 日次、週次、月次）
- ✅ Notion Database設計（レポート履歴管理用）
- ✅ 環境変数リスト
- ✅ 運用マニュアル
- ✅ テスト結果レポート

---

**生成完了**: このプロンプトは「タスクV_AIレポート自動生成_要件定義書.md」の内容を、「prompt-design-guide.md」のガイドラインに従って変換したものです。

