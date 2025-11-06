# WF5: トピック抽出AI テスト実行ガイド

**作成日**: 2025-10-27
**目的**: WF5のテスト実行手順と前提条件の確認

---

## 🚨 テスト実行前の必須準備

### ステップ1: トピックマスタDBの作成確認

**確認方法**:
```bash
# ガイドを参照
cat docs/phase2-topic-master-db-setup-guide.md
```

**チェックリスト**:
- [ ] トピックマスタDBが作成されている
- [ ] 全6プロパティ（Topic Name, Score, Keywords, Related Articles, Extracted At, Status）が設定されている
- [ ] Related Articlesがnote記事管理DB (29968d5c-2986-81ad-90d0-c24ed710503e) にリンクされている
- [ ] 双方向リレーション有効（note記事管理DBに"Topics"プロパティが追加されている）
- [ ] Database IDを取得済み

**Database ID取得方法**:
1. Notionでトピックマスタを開く
2. ブラウザのアドレスバーからURLをコピー
3. `?v=` の前の32文字（ハイフン含む36文字）がDatabase ID
   - 形式: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

---

### ステップ2: 環境変数の設定確認

**n8nに設定が必要な環境変数**:

| 変数名 | 説明 | 取得方法 |
|-------|------|----------|
| `TOPIC_MASTER_DB_ID` | トピックマスタDB ID | ステップ1で取得 |
| `GPT4_API_KEY` | OpenAI API Key | https://platform.openai.com/api-keys |
| `SLACK_WEBHOOK_URL` | Slack Webhook URL | Slackアプリ設定で作成 |

**n8nでの設定方法**:

#### 方法A: n8n環境変数（推奨）
1. n8nの設定 → Settings → Environment Variables
2. 上記3つの変数を追加
3. 保存

#### 方法B: ワークフロー内で直接設定（テスト用）
1. ワークフローを開く
2. 各HTTP Requestノードで環境変数参照を直接値に置換
   - `{{$env.TOPIC_MASTER_DB_ID}}` → 実際のDatabase ID
   - `{{$env.GPT4_API_KEY}}` → 実際のAPI Key
   - `{{$env.SLACK_WEBHOOK_URL}}` → 実際のWebhook URL

**注意**: 方法Bはテスト用のみ。本番では方法Aを使用してください。

---

### ステップ3: note記事管理DBのデータ確認

**確認方法**:
1. Notionで note記事管理DB (29968d5c-2986-81ad-90d0-c24ed710503e) を開く
2. 過去30日以内のデータが存在するか確認
3. Status = "検知済み" または "分析済み" の記事が10件以上あるか確認

**最小要件**:
- [ ] 過去30日以内の記事が10件以上存在する
- [ ] View CountとLike Countが設定されている
- [ ] Status が "検知済み" または "分析済み" である

**データが不足している場合**:
- WF4（note記事検知）を実行してデータを蓄積
- または、手動でテストデータを作成

---

## 🧪 テスト実行手順

### テスト1: ワークフローのインポート

**手順**:
```bash
# ワークフローJSONを確認
cat workflows/phase2-wf5-topic-extraction-ai.json
```

**n8nでの操作**:
1. n8nを開く（URL: http://localhost:5678 または RailwayのURL）
2. 左メニュー → "Workflows" → "+ Add workflow" → "Import from File"
3. `workflows/phase2-wf5-topic-extraction-ai.json` を選択
4. インポート完了確認

**期待結果**:
- [ ] ワークフローが正常にインポートされる
- [ ] 全11ノードが表示される
- [ ] ノード接続が正しい

---

### テスト2: 環境変数の設定（ワークフロー内）

**n8nでの操作**:

#### Node 2: Notion Query
1. ノードをダブルクリック
2. Headers → Authorization を確認
   - 値: `Bearer YOUR_NOTION_API_TOKEN`
   - ✅ 既に設定済み

#### Node 5: GPT-4 API
1. ノードをダブルクリック
2. Headers → Authorization を確認
   - 値: `Bearer {{$env.GPT4_API_KEY}}`
   - ⚠️ 環境変数が設定されているか確認
   - テスト用: `Bearer sk-proj-...` に直接置換

#### Node 9: Notion Create
1. ノードをダブルクリック
2. Body → parent.database_id を確認
   - 値: `{{$env.TOPIC_MASTER_DB_ID}}`
   - ⚠️ 環境変数が設定されているか確認
   - テスト用: 実際のDatabase IDに直接置換

#### Node 11: Slack通知
1. ノードをダブルクリック
2. URL を確認
   - 値: `={{$env.SLACK_WEBHOOK_URL}}`
   - ⚠️ 環境変数が設定されているか確認
   - テスト用: 実際のWebhook URLに直接置換

---

### テスト3: 手動実行テスト

**n8nでの操作**:
1. ワークフローを開く
2. 右上の "Execute Workflow" ボタンをクリック
3. 実行開始

**実行中の確認ポイント**:
- [ ] Node 1 (Schedule Trigger): スキップされる（手動実行のため）
- [ ] Node 2 (Notion Query): 緑色のチェックマーク ✅
  - Output: 100件以内の記事データ
- [ ] Node 3 (Function - スコアリング): ✅
  - Output: スコア付き記事配列
- [ ] Node 4 (Function - トップ10): ✅
  - Output: トップ10記事の配列
- [ ] Node 5 (GPT-4 API): ✅ （10-20秒かかる）
  - Output: GPT-4のJSON レスポンス
- [ ] Node 6 (Function - Parse): ✅
  - Output: パース済みトピックデータ
- [ ] Node 7 (Function - Preprocessing): ✅
  - Output: 関連記事付きトピック配列（5件）
- [ ] Node 8 (Loop): ✅
  - 5回ループ
- [ ] Node 9 (Notion Create): ✅ （各ループで1回）
  - Output: Notion作成レスポンス
- [ ] Node 10 (Wait): ✅
  - 400ms待機
- [ ] Node 11 (Slack通知): ✅
  - Slackに通知送信

**実行完了確認**:
- [ ] 全ノードが緑色のチェックマーク ✅
- [ ] エラーノードがない
- [ ] 実行時間が30-40秒以内

---

### テスト4: トピックマスタDBの確認

**Notionでの確認**:
1. トピックマスタDBを開く
2. 新しく追加された5件のトピックを確認

**確認項目**:
- [ ] 5件のトピックページが作成されている
- [ ] 各トピックのプロパティが正しく設定されている
  - [ ] Topic Name: トピック名が入力されている
  - [ ] Score: 数値（0-1000程度）が設定されている
  - [ ] Keywords: キーワードが5-10個設定されている
  - [ ] Related Articles: 関連記事（1-10件）がリンクされている
  - [ ] Extracted At: 今日の日時が設定されている
  - [ ] Status: "active" が選択されている

**Related Articlesの確認**:
1. トピックページを開く
2. Related Articlesのリンクをクリック
3. note記事管理DBの記事が表示されることを確認

**双方向リレーションの確認**:
1. note記事管理DBを開く
2. Related Articlesに含まれていた記事を開く
3. "Topics" プロパティに今回のトピックが表示されることを確認

---

### テスト5: Slack通知の確認

**Slackでの確認**:
1. 設定したSlackチャネル（例: #トレンド分析）を開く
2. WF5からの通知が届いているか確認

**通知内容の確認**:
- [ ] ヘッダー: "🔥 トレンドトピック Top 5"
- [ ] セクション1: 5つのトピック
  - 各トピック: 番号、タイトル、スコア、関連記事数、理由
- [ ] セクション2: トレンドキーワード一覧

**通知例**:
```
📊 *今週のトレンドトピック分析完了*

🔥 トレンドトピック Top 5

1. *MEO対策の基礎と実践*
スコア: 156.4 | 関連記事: 3件
理由: GoogleマップとMEOに関する関心が高まっている

2. *英語教育の最新トレンド*
スコア: 142.8 | 関連記事: 5件
理由: バイリンガル教育への保護者の関心が増加

...

*トレンドキーワード*: MEO, Googleマップ, 集客, 英語教育, バイリンガル
```

---

## ⚠️ よくあるエラーと対処法

### エラー1: Node 2 (Notion Query) でエラー

**エラーメッセージ**: `401 Unauthorized` または `validation_error`

**原因**:
- Notion API Tokenが無効
- Database IDが間違っている

**対処法**:
1. Notion API Tokenを確認（YOUR_NOTION_API_TOKEN）
2. Database IDを確認（29968d5c-2986-81ad-90d0-c24ed710503e）
3. Tokenに書き込み権限があるか確認

---

### エラー2: Node 5 (GPT-4 API) でエラー

**エラーメッセージ**: `401 Unauthorized` または `insufficient_quota`

**原因**:
- GPT-4 API Keyが無効
- OpenAIアカウントのクレジット不足

**対処法**:
1. OpenAI API Keyを確認
2. https://platform.openai.com/usage でクレジット残高確認
3. 必要に応じてクレジット追加

---

### エラー3: Node 6 (Parse) でエラー

**エラーメッセージ**: `GPT-4レスポンスのJSON parse失敗`

**原因**:
- GPT-4がJSON以外のテキストを出力した

**対処法**:
1. Node 5のOutputを確認
2. GPT-4のレスポンスを確認（JSONフォーマットか？）
3. プロンプトを調整（"必ずJSON形式のみで出力"を強調）

---

### エラー4: Node 9 (Notion Create) でエラー

**エラーメッセージ**: `object_not_found` または `validation_error`

**原因**:
- TOPIC_MASTER_DB_IDが設定されていない
- Database IDが間違っている
- Relationプロパティの設定が間違っている

**対処法**:
1. トピックマスタDBが作成されているか確認
2. Database IDが正しいか確認
3. Related Articlesプロパティがnote記事管理DBを指しているか確認

---

### エラー5: Node 11 (Slack通知) でエラー

**エラーメッセージ**: `invalid_payload` または `404 Not Found`

**原因**:
- Slack Webhook URLが無効

**対処法**:
1. Slack Webhook URLを確認
2. Slackアプリ設定で新しいWebhook URLを作成
3. SLACK_WEBHOOK_URL環境変数を更新

---

## 📊 テスト結果の記録

### テスト実行日時
- 実行日時: _____年___月___日 __:__ JST

### テスト結果サマリー

| テスト項目 | 結果 | 備考 |
|-----------|------|------|
| ワークフローインポート | ✅ / ❌ |  |
| 環境変数設定 | ✅ / ❌ |  |
| 手動実行テスト | ✅ / ❌ | 実行時間: ___秒 |
| トピックマスタDB確認 | ✅ / ❌ | 作成件数: ___件 |
| Slack通知確認 | ✅ / ❌ |  |

### 発見した問題点
1.
2.
3.

### 改善提案
1.
2.
3.

---

## 🚀 次のステップ

### テスト成功の場合
1. ✅ ワークフローを有効化（Active=true）
2. 次の水曜または土曜 09:00の自動実行を待つ
3. Execution Historyで実行結果確認
4. WF6（note記事自動生成）の実装準備

### テスト失敗の場合
1. エラーログを確認
2. 上記「よくあるエラーと対処法」を参照
3. 必要に応じてワークフローを修正
4. 再度テスト実行

---

## 📝 テスト実行チェックリスト

### 事前準備
- [ ] トピックマスタDBを作成した
- [ ] Database IDを取得した
- [ ] 環境変数（TOPIC_MASTER_DB_ID, GPT4_API_KEY, SLACK_WEBHOOK_URL）を設定した
- [ ] note記事管理DBに過去30日のデータが10件以上ある

### テスト実行
- [ ] ワークフローをn8nにインポートした
- [ ] 手動実行テストを実施した
- [ ] 全ノードが成功（緑色のチェックマーク）した
- [ ] 実行時間が30-40秒以内だった

### 結果確認
- [ ] トピックマスタDBに5件のトピックが作成された
- [ ] 各トピックのプロパティが正しく設定されている
- [ ] Related Articlesが正しくリンクされている
- [ ] 双方向リレーションが動作している
- [ ] Slack通知が正しく届いた

### 本番稼働準備
- [ ] ワークフローを有効化した
- [ ] Schedule Triggerが水曜・土曜 09:00に設定されている
- [ ] 次回の自動実行日時を記録した

---

**作成者**: Claude Code
**最終更新**: 2025-10-27
