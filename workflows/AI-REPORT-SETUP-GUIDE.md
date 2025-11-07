# AIレポート自動生成ワークフロー - セットアップガイド

**作成日**: 2025-10-26  
**バージョン**: 1.0  
**対象**: タスクV（AIレポート自動生成）

---

## 📋 目次

- [概要](#概要)
- [前提条件](#前提条件)
- [セットアップ手順](#セットアップ手順)
  - [1. Notion Database作成](#1-notion-database作成)
  - [2. 環境変数設定](#2-環境変数設定)
  - [3. ワークフローインポート](#3-ワークフローインポート)
  - [4. 認証情報設定](#4-認証情報設定)
  - [5. テスト実行](#5-テスト実行)
- [週次・月次ワークフロー作成](#週次月次ワークフロー作成)
- [運用手順](#運用手順)
- [トラブルシューティング](#トラブルシューティング)

---

## 🎯 概要

### このワークフローについて

MEO集客自動化プロジェクトPhase4のコア機能：
- **目的**: データ収集→AI分析→改善提案→自動実行のループ
- **頻度**: 日次・週次・月次
- **技術**: n8n + GPT-4 + Notion + LINE

### 成果物

1. **ワークフローJSON**
   - ✅ `ai-report-daily.json` （完成）
   - 📝 週次・月次は日次をベースに作成（本ガイド参照）

2. **ドキュメント**
   - このセットアップガイド
   - 元の要件定義書（`タスクV_AIレポート自動生成_要件定義書.md`）
   - プロンプト（`タスクV_プロンプト.md`）

---

## 🔧 前提条件

### 必須タスク

- ✅ **タスクU完了**: KPI統合ダッシュボードが稼働
- ✅ **APIエンドポイント**: タスクUのAPI URLが利用可能
- ✅ **n8nインスタンス**: Railway上で稼働中

### 必要なサービス

| サービス | 用途 | 準備すること |
|---------|------|-------------|
| **n8n** | ワークフロー実行 | Railwayで稼働確認 |
| **OpenAI API** | GPT-4分析 | API キー取得 |
| **Notion** | レポート保存 | Integration作成、API キー |
| **LINE Notify** | 通知配信 | トークン取得 |
| **タスクU API** | KPIデータ取得 | API URL、認証トークン |
| **タスクW/X Webhook** | 自動実行連携 | Webhook URL |

---

## 📝 セットアップ手順

### 1. Notion Database作成

#### 1-1. 新規Databaseを作成

1. Notionで新しいページを作成
2. 「Database - Full page」を選択
3. データベース名: **「AIレポート履歴」**

#### 1-2. プロパティを設定

以下のプロパティを追加：

| プロパティ名 | タイプ | 説明 | 設定 |
|-------------|--------|------|------|
| **Title** | Title | レポート名 | デフォルト（例: "日次レポート 2025-11-15"） |
| **Period** | Select | 頻度 | daily / weekly / monthly |
| **Generated_At** | Date | 生成日時 | 日時を含む |
| **PV_Achievement** | Number | PV達成率 | % |
| **CVR_Current** | Number | 現在のCVR | % |
| **Proposals_Count** | Number | 改善提案数 | 個 |
| **Auto_Executed** | Number | 自動実行数 | 個 |
| **Manual_Required** | Number | 手動確認数 | 個 |
| **Status** | Select | ステータス | generated / reviewed / implemented |

#### 1-3. Database IDを取得

```
Notion Database URL: 
https://www.notion.so/workspace/abc123def456?v=xyz789

Database ID = abc123def456 （?より前の部分）
```

#### 1-4. Integration接続

1. Notion Settings → Connections
2. 「Connect to」→ n8n Integrationを選択
3. 「AIレポート履歴」データベースに接続

---

### 2. 環境変数設定

#### 2-1. n8nで環境変数を設定

Railway n8nの管理画面で以下を設定：

```bash
# タスクU API
TASK_U_API_URL=https://your-task-u-api.com/api
TASK_U_API_TOKEN=your_task_u_bearer_token

# Notion
NOTION_REPORT_DB_ID=abc123def456ghi789

# タスクW/X Webhook
TASK_W_WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app/webhook/task-w
TASK_X_WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app/webhook/task-x
```

#### 2-2. 環境変数の確認

n8nのワークフロー内で `{{$env.TASK_U_API_URL}}` が正しく展開されることを確認。

---

### 3. ワークフローインポート

#### 3-1. 日次ワークフローをインポート

1. n8n管理画面を開く
2. 左上メニュー（☰）→ **「Import from File」**
3. `ai-report-daily.json` を選択
4. インポート完了

#### 3-2. ワークフロー名を確認

- 名前: **「AIレポート自動生成（日次）」**
- タグ: **「AI Report」**
- トリガー: Schedule Trigger (毎日9:00)

---

### 4. 認証情報設定

ワークフローをインポート後、以下の認証情報を設定：

#### 4-1. Task U API Token

ノード: **「KPIデータ取得」**

1. ノードをクリック
2. Credentials → **「HTTP Header Auth」**を選択
3. 新規作成:
   - Name: `Task U API Token`
   - Header Name: `Authorization`
   - Header Value: `Bearer YOUR_TASK_U_TOKEN`
4. 保存

#### 4-2. OpenAI API

ノード: **「GPT-4 AI分析」**

1. ノードをクリック
2. Credentials → **「OpenAI API」**を選択
3. 新規作成:
   - Name: `OpenAI API`
   - API Key: `sk-proj-...` （OpenAI APIキー）
4. 保存

#### 4-3. Notion API

ノード: **「Notionレポート保存」**

1. ノードをクリック
2. Credentials → **「Notion API」**を選択
3. 新規作成:
   - Name: `Notion API`
   - API Key: `secret_...` （Notion Integrationのシークレット）
   - または OAuth2で接続
4. 保存

#### 4-4. LINE Notify

ノード: **「LINE通知」** と **「LINE緊急アラート」**

1. ノードをクリック
2. Credentials → **「LINE Notify OAuth2」**を選択
3. 新規作成:
   - Name: `LINE Notify`
   - Access Token: `YOUR_LINE_NOTIFY_TOKEN`
4. 保存
5. 同じ認証情報を「LINE緊急アラート」ノードにも設定

---

### 5. テスト実行

#### 5-1. 手動実行でテスト

1. ワークフロー画面右上の **「Execute Workflow」** をクリック
2. 実行を待つ（約30秒-1分）
3. 各ノードの出力を確認

#### 5-2. 確認ポイント

| ノード | 確認内容 | 正常な状態 |
|-------|---------|-----------|
| KPIデータ取得 | HTTPレスポンス200 | KPIデータが取得できている |
| データ整形 | jsonオブジェクト | 達成率等が計算されている |
| GPT-4 AI分析 | choices[0].message.content | Markdownレポートが生成 |
| レポート構造化 | proposals配列 | 5つの提案が抽出されている |
| Notionレポート保存 | idとurl | Notionページが作成された |
| LINE通知 | status: sent | LINEメッセージが送信された |

#### 5-3. エラー対応

エラーが発生した場合、[トラブルシューティング](#トラブルシューティング)セクションを参照。

---

## 🔄 週次・月次ワークフロー作成

日次ワークフローをベースに、週次・月次を作成します。

### 週次ワークフロー作成

#### ステップ1: 日次をコピー

1. 「AIレポート自動生成（日次）」を開く
2. 右上メニュー（...）→ **「Duplicate」**
3. 名前を **「AIレポート自動生成（週次）」** に変更

#### ステップ2: 変更点を適用

**Node 1: Schedule Trigger**
```
変更前: cron: "0 9 * * *"（毎日9:00）
変更後: cron: "0 9 * * 1"（毎週月曜9:00）
```

**Node 2: KPIデータ取得**
```
変更前: url: "={{$env.TASK_U_API_URL}}/kpi/daily"
変更後: url: "={{$env.TASK_U_API_URL}}/kpi/weekly"
```

**Node 4: GPT-4 AI分析**

プロンプトに以下を追加:
```
【週次分析の追加観点】
- 週間トレンドの詳細分析
- 曜日別のパフォーマンス比較
- 先週との比較
- 今週の重要イベント影響
```

max_tokens: 2500 → 3000 （分析深度を上げる）

#### ステップ3: 保存とテスト

1. 保存
2. 手動実行でテスト
3. Notionレポートが「週次」として保存されることを確認

### 月次ワークフロー作成

#### ステップ1: 日次をコピー

1. 「AIレポート自動生成（日次）」を開く
2. 右上メニュー（...）→ **「Duplicate」**
3. 名前を **「AIレポート自動生成（月次）」** に変更

#### ステップ2: 変更点を適用

**Node 1: Schedule Trigger**
```
変更前: cron: "0 9 * * *"（毎日9:00）
変更後: cron: "0 9 1 * *"（毎月1日9:00）
```

**Node 2: KPIデータ取得**
```
変更前: url: "={{$env.TASK_U_API_URL}}/kpi/daily"
変更後: url: "={{$env.TASK_U_API_URL}}/kpi/monthly"
```

**Node 4: GPT-4 AI分析**

プロンプトに以下を追加:
```
【月次分析の追加観点】
- 月間総括と達成度評価
- 週別トレンドの分析
- 先月との詳細比較
- 次月の戦略提案
- 季節性の考慮
```

max_tokens: 2500 → 4000 （さらに深い分析）

#### ステップ3: PDF配信追加（オプション）

月次レポートにPDF配信を追加する場合：

1. **「PDF生成」ノード追加** (Puppeteer または PDF.co)
   - Notionページ→PDF変換
   
2. **「メール送信」ノード追加**
   - Gmail または SMTPノード
   - PDFを添付
   - 宛先: チームメンバー

#### ステップ4: 保存とテスト

1. 保存
2. 手動実行でテスト
3. Notionレポートが「月次」として保存されることを確認

---

## 🚀 運用手順

### 日常運用

#### 1. レポート確認

**毎日9:30**（日次レポート完了後）:
1. LINEでサマリー通知を確認
2. Notionで詳細レポートを確認
3. 「手動確認が必要な施策」を確認

**毎週月曜10:00**（週次レポート完了後）:
1. 週間総括を確認
2. 改善提案の実行状況をレビュー

**毎月1日10:00**（月次レポート完了後）:
1. 月間総括を確認
2. PDFレポートをダウンロード
3. チームミーティングで共有

#### 2. 手動確認が必要な施策の対応

Notionレポートの「手動確認が必要な施策」セクション:
1. 各提案を読む
2. 実行可否を判断
3. Statusを「reviewed」に変更
4. 実行する場合は該当タスク（W/X）を手動でトリガー

#### 3. レポート品質の評価

週に1回、以下を確認:
- GPT-4の提案は的確か？
- 自動実行された施策の効果は？
- 改善提案の採用率は70%以上か？

### トラブル時の対応

#### エラーアラートが来た場合

1. LINEメッセージのリンクからNotionレポートを開く
2. エラー内容を確認
3. [トラブルシューティング](#トラブルシューティング)で対処

#### レポートが生成されない場合

1. n8nワークフロー画面で実行ログを確認
2. 失敗したノードを特定
3. エラーメッセージを確認
4. [トラブルシューティング](#トラブルシューティング)で対処

---

## 🔍 トラブルシューティング

### 1. KPIデータ取得失敗

**症状**: 「KPIデータ取得」ノードがエラー

**原因と対処**:

| 原因 | 対処方法 |
|-----|---------|
| タスクU APIがダウン | タスクUの稼働状況を確認、Railwayログを確認 |
| 認証トークンが無効 | 環境変数 `TASK_U_API_TOKEN` を再設定 |
| API URLが間違っている | 環境変数 `TASK_U_API_URL` を確認 |
| ネットワークエラー | Railwayのネットワーク状態を確認、しばらく待ってリトライ |

**フォールバック**:
- 3回リトライ後、「データ整形」ノードで前日データを使用
- フォールバックレポートが生成される

### 2. GPT-4 API失敗

**症状**: 「GPT-4 AI分析」ノードがエラー

**原因と対処**:

| 原因 | 対処方法 |
|-----|---------|
| APIキーが無効 | OpenAI APIキーを再設定 |
| レート制限超過 | しばらく待ってからリトライ（1分後） |
| 予算超過 | OpenAIダッシュボードで使用量確認、予算アラート設定 |
| タイムアウト | max_tokensを2000に減らす |

**フォールバック**:
- 3回リトライ後、「レポート構造化」ノードで簡易テンプレートレポート生成
- 「GPT-4 APIが一時的に利用できません」というメッセージ

### 3. Notion保存失敗

**症状**: 「Notionレポート保存」ノードがエラー

**原因と対処**:

| 原因 | 対処方法 |
|-----|---------|
| Notion APIキーが無効 | Notion Integrationを再作成、APIキーを再設定 |
| Database IDが間違っている | 環境変数 `NOTION_REPORT_DB_ID` を確認 |
| Integrationが接続されていない | NotionでDatabaseにIntegrationを接続 |
| レート制限 | しばらく待ってからリトライ |

**フォールバック**:
- 3回リトライ後、Google Sheetsに保存（要設定）
- LINE通知で「Notion保存失敗、Sheetsに保存」と通知

### 4. LINE通知失敗

**症状**: 「LINE通知」ノードがエラー

**原因と対処**:

| 原因 | 対処方法 |
|-----|---------|
| LINE Notifyトークンが無効 | トークンを再取得、再設定 |
| メッセージが長すぎる | メッセージを1000文字以内に短縮 |
| レート制限 | 通知頻度を下げる |

**フォールバック**:
- 3回リトライ後、メール通知に切り替え（要設定）
- エラーログをn8nに記録

### 5. タスクW/X連携失敗

**症状**: 「タスクW/X連携」ノードがエラー

**原因と対処**:

| 原因 | 対処方法 |
|-----|---------|
| Webhook URLが間違っている | 環境変数 `TASK_W_WEBHOOK_URL` を確認 |
| タスクW/Xがダウン | タスクW/Xの稼働状況を確認 |
| JSONフォーマットエラー | 送信データの形式を確認 |

**対処**:
- エラーログを確認
- 手動でタスクW/Xをトリガー

---

## 📚 補足資料

### ワークフロー構造図

```
1. Schedule Trigger (cron)
   ↓
2. KPIデータ取得 (HTTP Request)
   ↓
3. データ整形 (Function) ────┐
   ↓                        │（並列）
4. GPT-4 AI分析 (OpenAI)    │
   ↓                        │
5. レポート構造化 (Function) │
   ↓                        │
6. Notionレポート保存        │
   ↓                        │
7. LINE通知                  │
   ↓                        │
8. 自動実行判定 (IF)         │
   ↓ (true)                 │
9. タスクW/X連携             │
                            │
10. アラート判定 (IF) ←──────┘
    ↓ (true)
11. LINE緊急アラート
```

### 環境変数一覧

```bash
# 必須
TASK_U_API_URL=https://your-task-u-api.com/api
TASK_U_API_TOKEN=your_task_u_bearer_token
NOTION_REPORT_DB_ID=abc123def456ghi789
TASK_W_WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app/webhook/task-w
TASK_X_WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app/webhook/task-x

# オプション（将来的に追加）
GOOGLE_SHEETS_BACKUP_ID=xxx
EMAIL_RECIPIENT=team@example.com
```

### Notionプロパティ詳細

```json
{
  "Title": {
    "type": "title",
    "title": [
      {
        "text": {
          "content": "日次レポート 2025-11-15"
        }
      }
    ]
  },
  "Period": {
    "type": "select",
    "select": {
      "name": "daily"  // daily | weekly | monthly
    }
  },
  "Generated_At": {
    "type": "date",
    "date": {
      "start": "2025-11-15T09:30:00+09:00"
    }
  },
  "PV_Achievement": {
    "type": "number",
    "number": 83.0
  },
  "CVR_Current": {
    "type": "number",
    "number": 25.5
  },
  "Proposals_Count": {
    "type": "number",
    "number": 5
  },
  "Auto_Executed": {
    "type": "number",
    "number": 3
  },
  "Manual_Required": {
    "type": "number",
    "number": 2
  },
  "Status": {
    "type": "select",
    "select": {
      "name": "generated"  // generated | reviewed | implemented
    }
  }
}
```

### GPT-4プロンプトテンプレート

完全なプロンプトは `ai-report-daily.json` の「GPT-4 AI分析」ノードを参照。

**構造**:
```
役割定義 → KPIデータ → 分析観点 → 出力形式
```

**出力形式**:
```markdown
## 📊 KPI達成度サマリー
## 📈 トレンド分析
## ⚠️ 問題点・ボトルネック
## 💡 改善提案（優先度順）
### 提案1: ...
## 🤖 自動実行予定
## 📌 手動確認が必要な施策
```

---

## ✅ チェックリスト

### セットアップ完了チェック

- [ ] Notion Database作成完了
- [ ] 10個のプロパティ設定完了
- [ ] Integration接続完了
- [ ] 環境変数6個設定完了
- [ ] ワークフローインポート完了
- [ ] 認証情報4つ設定完了
- [ ] 手動実行でテスト成功
- [ ] Notionレポート作成確認
- [ ] LINE通知受信確認
- [ ] 週次ワークフロー作成完了（オプション）
- [ ] 月次ワークフロー作成完了（オプション）

### 運用開始前チェック

- [ ] タスクUが稼働中
- [ ] APIエンドポイントが応答
- [ ] OpenAI API予算設定
- [ ] LINE Notify動作確認
- [ ] タスクW/X Webhookが準備済み
- [ ] チームに通知方法を共有
- [ ] トラブルシューティングガイドを確認

---

## 🎓 次のステップ

### Phase4完了判定

以下を全て満たすこと:
1. ✅ 日次・週次・月次レポートが自動生成される
2. ✅ GPT-4が客観的な改善提案を5つ以上生成する
3. ✅ 自動実行可能な提案が自動でタスクW/Xに連携される
4. ✅ **7日間連続で正常稼働する**
5. ✅ 人間の介入なしでPDCAサイクルが回る

### さらなる改善

- 📊 ダッシュボードのビジュアル化（Grafana等）
- 🤖 A/Bテスト自動実施
- 📧 ステークホルダー向けメール配信
- 🔔 Slackボットとの統合
- 📈 KPI予測モデルの追加

---

**完了！** このガイドに従って、AIレポート自動生成ワークフローを完全にセットアップできます。

質問がある場合は、元の要件定義書（`タスクV_AIレポート自動生成_要件定義書.md`）を参照してください。

