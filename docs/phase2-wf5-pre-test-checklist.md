# WF5テスト実行前チェックリスト

**実行日**: 2025-10-27

---

## 🚨 必須: テスト実行前に以下を確認してください

### ✅ ステップ1: トピックマスタDBの作成

**ガイド**: `/docs/phase2-topic-master-db-setup-guide.md`

```bash
# ガイドを確認
cat docs/phase2-topic-master-db-setup-guide.md
```

**作業内容**:
1. Notionでnote記事管理DBの親ページ（またはワークスペース）に移動
2. 新規ページ作成 → タイトル: `トピックマスタ`
3. `/database` → 「テーブル - インライン」を選択
4. 6つのプロパティを作成:
   - Topic Name (title)
   - Score (number)
   - Keywords (multi_select)
   - Related Articles (relation → note記事管理DB)
   - Extracted At (date)
   - Status (select: active, archived)
5. Related Articlesで **双方向リレーション** を有効化
6. Database IDを取得（URLの32文字）

**確認**:
- [ ] トピックマスタDBが作成されている
- [ ] 全6プロパティが正しく設定されている
- [ ] Related Articlesが note記事管理DB (29968d5c-2986-81ad-90d0-c24ed710503e) にリンクされている
- [ ] 双方向リレーション有効（note記事管理DBに "Topics" プロパティが追加されている）
- [ ] Database IDを取得した: `________________`

---

### ✅ ステップ2: 環境変数の設定

#### 2-1. TOPIC_MASTER_DB_ID

**取得済み**: ステップ1で取得したDatabase ID
**値**: `________________________________`

#### 2-2. GPT4_API_KEY

**取得方法**: https://platform.openai.com/api-keys

**手順**:
1. OpenAIにログイン
2. API Keys → "+ Create new secret key"
3. キー名: `n8n-wf5`
4. 作成 → キーをコピー（一度しか表示されません！）

**値**: `YOUR_OPENAI_API_KEY`（実際のAPIキーに置き換えてください）


**クレジット確認**: https://platform.openai.com/usage
- 残高: $_____ （最低$5推奨）

#### 2-3. SLACK_WEBHOOK_URL

**取得方法**: Slackアプリ設定でIncoming Webhookを作成

**手順**:
1. https://api.slack.com/apps にアクセス
2. "Create New App" → "From scratch"
3. App Name: `n8n WF5 Notification`
4. Workspace: 選択
5. "Incoming Webhooks" → "Activate Incoming Webhooks" を ON
6. "Add New Webhook to Workspace" → チャネル選択（例: #トレンド分析）
7. Webhook URLをコピー

**値**: `YOUR_SLACK_WEBHOOK_URL`（実際のWebhook URLに置き換えてください）

**テスト送信**:
```bash
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"WF5テスト通知"}' \
https://hooks.slack.com/services/YOUR_WEBHOOK_URL
```

---

### ✅ ステップ3: n8nに環境変数を設定

#### 方法A: n8n環境変数（推奨）

**n8n CLIから設定**:
```bash
# Railway環境の場合
railway run n8n env set TOPIC_MASTER_DB_ID="your_database_id"
railway run n8n env set GPT4_API_KEY="your_api_key"
railway run n8n env set SLACK_WEBHOOK_URL="your_webhook_url"

# ローカル環境の場合
# .env ファイルに以下を追加
echo 'TOPIC_MASTER_DB_ID=your_database_id' >> .env
echo 'GPT4_API_KEY=your_api_key' >> .env
echo 'SLACK_WEBHOOK_URL=your_webhook_url' >> .env
```

**n8n GUIから設定**:
1. n8nを開く
2. Settings → Environment Variables
3. 3つの変数を追加
4. 保存

#### 方法B: ワークフロー内で直接設定（テスト用のみ）

**注意**: セキュリティリスクあり。テスト後は方法Aに切り替えてください。

**設定箇所**:
1. Node 5 (GPT-4 API) → Headers → Authorization
   - `Bearer {{$env.GPT4_API_KEY}}` → `Bearer sk-proj-...`
2. Node 9 (Notion Create) → Body → parent.database_id
   - `{{$env.TOPIC_MASTER_DB_ID}}` → 実際のDatabase ID
3. Node 11 (Slack通知) → URL
   - `={{$env.SLACK_WEBHOOK_URL}}` → 実際のWebhook URL

**確認**:
- [ ] 環境変数を設定した（方法A または 方法B）
- [ ] TOPIC_MASTER_DB_ID = `________________________________`
- [ ] GPT4_API_KEY = `sk-proj-________________________________`
- [ ] SLACK_WEBHOOK_URL = `https://hooks.slack.com/services/________________________________`

---

### ✅ ステップ4: note記事管理DBのデータ確認

**Database ID**: 29968d5c-2986-81ad-90d0-c24ed710503e
**URL**: https://www.notion.so/29968d5c298681ad90d0c24ed710503e

**確認**:
1. note記事管理DBを開く
2. 過去30日以内のデータを確認
3. Status = "検知済み" または "分析済み" の記事を確認

**最小要件**:
- [ ] 過去30日以内の記事が10件以上存在する
- [ ] View CountとLike Countが設定されている（0でもOK）
- [ ] Status が "検知済み" または "分析済み" である

**データ不足の場合**:
- WF4（note記事検知）を実行してデータを蓄積
- または、手動でテストデータを10件作成

**テストデータ作成例**:
| Title | View Count | Like Count | Status | Published Date |
|-------|-----------|-----------|--------|----------------|
| テスト記事1 | 100 | 10 | 検知済み | 2025-10-20 |
| テスト記事2 | 200 | 20 | 検知済み | 2025-10-21 |
| ... | ... | ... | ... | ... |

---

## 🚀 すべての準備が完了したら

### テスト実行開始

**ガイド**: `/docs/phase2-wf5-test-execution-guide.md`

```bash
# テスト実行ガイドを確認
cat docs/phase2-wf5-test-execution-guide.md
```

**次のステップ**:
1. ✅ すべてのチェックリスト項目が完了
2. ワークフローをn8nにインポート
3. 手動実行テストを実施
4. 結果確認

---

## 📋 最終チェック

### すべて完了していますか？

- [ ] **ステップ1**: トピックマスタDBを作成した
- [ ] **ステップ2**: 環境変数（3つ）を取得した
- [ ] **ステップ3**: n8nに環境変数を設定した
- [ ] **ステップ4**: note記事管理DBにデータが10件以上ある

### すべて ✅ の場合

→ **テスト実行を開始できます！**

```bash
# テスト実行ガイドに従って実行
cat docs/phase2-wf5-test-execution-guide.md
```

### ❌ が1つでもある場合

→ **未完了の項目を完了させてください**

各ステップの詳細ガイド:
- ステップ1: `/docs/phase2-topic-master-db-setup-guide.md`
- ステップ2-4: このチェックリスト参照

---

**作成者**: Claude Code
**最終更新**: 2025-10-27
