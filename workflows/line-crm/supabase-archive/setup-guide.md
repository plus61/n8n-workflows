# LINE Lead Pipeline - Supabase ワークフロー セットアップガイド

**ステータス**: 🗄️ **アーカイブ** - このガイドは参考用です  
**現在の推奨**: [Notion版](../README.md)を使用してください

---

## 📋 概要

LINE友だち追加イベントをWebhookで受信し、Supabase PostgreSQLに自動保存するワークフローです。

---

## 🚀 セットアップ手順

### **Step 1: Supabaseテーブル作成**

1. **Supabase Dashboardにログイン**
   ```
   https://supabase.com/dashboard
   ```

2. **プロジェクトを選択**
   - プロジェクト: `gmeo_00`

3. **SQL Editorを開く**
   - 左サイドバー: SQL Editor

4. **スキーマを実行**
   - [`schema.sql`](./schema.sql) の内容をコピー&ペースト
   - **Run** をクリック

5. **テーブル確認**
   - Table Editor → `line_leads` テーブルが作成されていることを確認

---

### **Step 2: ワークフローのインポート**

1. **n8n UIにアクセス**
   ```
   https://n8n-python-production-344b.up.railway.app
   ```

2. **Workflows ページに移動**

3. **右上の「⋯」メニュー → Import from File**

4. **[`workflow.json`](./workflow.json)を選択**

5. **Import をクリック**

---

### **Step 3: PostgreSQL認証情報の設定**

#### **3-1: 認証情報の作成**

1. **左サイドバー: Credentials → + Add Credential**

2. **「Postgres」を検索して選択**

3. **接続情報を入力**
   ```
   Credential name: Supabase PostgreSQL (gmeo_00)
   
   Host:     db.ivlfrmzysbzrrqicsady.supabase.co
   Database: postgres
   Port:     5432
   User:     postgres
   Password: [your-supabase-password]
   
   SSL:      require (プルダウンで選択)
   ```

4. **🧪 Test Connection をクリック**
   - ✅ "Connection test successful" が表示されることを確認

5. **💾 Save をクリック**

#### **3-2: ワークフローに認証情報を設定**

1. **インポートしたワークフローを開く**

2. **「Supabase Insert」ノードをクリック**

3. **Credentials セクション**
   - **Select Credential**: `Supabase PostgreSQL (gmeo_00)` を選択

4. **💾 Save をクリック**

---

### **Step 4: Webhook URLの確認**

1. **「LINE Webhook Trigger」ノードをクリック**

2. **Webhook URL を確認**
   ```
   Test URL:       https://n8n-python-production-344b.up.railway.app/webhook-test/line-lead
   Production URL: https://n8n-python-production-344b.up.railway.app/webhook/line-lead
   ```

3. **この URLをLINE Webhook設定に登録**

---

## 🧪 テスト手順

### **Test 1: LINE検証リクエスト（空配列）**

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook-test/line-lead \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Uc797a7262ff3e3c5aa9b58f52e1e510e",
    "events": []
  }'
```

**期待される結果**: ワークフローが停止し、データベースに挿入されない

---

### **Test 2: 正常なfollowイベント**

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook-test/line-lead \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Uc797a7262ff3e3c5aa9b58f52e1e510e",
    "events": [
      {
        "type": "follow",
        "timestamp": 1761387464181,
        "source": {
          "type": "user",
          "userId": "TEST_USER_12345"
        },
        "replyToken": "test_reply_token"
      }
    ]
  }'
```

**期待される結果**: データベースにレコードが挿入される

---

### **Test 3: Supabaseでデータ確認**

1. **Supabase → Table Editor → line_leads**

2. **最新のレコードを確認**
   ```sql
   SELECT * FROM line_leads 
   ORDER BY created_at DESC 
   LIMIT 5;
   ```

3. **期待されるデータ**
   ```
   id: 1
   lead_id: 123-1761387464181
   user_id: TEST_USER_12345
   display_name: (空文字)
   picture_url: (空文字)
   timestamp_jst: 2025-10-25T19:17:44.000Z
   processed_at: 2025-10-25T19:17:45.000Z
   source: webhook
   status: pending
   ```

---

## 📊 ワークフロー構成

### **ノード構成**

1. **LINE Webhook Trigger**
   - LINE Platformからのイベント受信
   - Path: `line-lead`
   - HTTP Method: POST

2. **Data Validation & Transform**
   - LINE検証リクエストの検出とスキップ
   - followイベントのみ処理
   - lead_id生成（n8n実行ID + タイムスタンプ）
   - データ構造の変換

3. **Supabase Insert**
   - PostgreSQL INSERT操作
   - テーブル: `line_leads`
   - スキーマ: `public`

4. **Success Log**
   - 成功ログの記録
   - 挿入されたレコードIDの出力

5. **Error Handler**
   - エラーハンドリング
   - エラーログの記録

### **データフロー**

```
LINE Webhook
    ↓
Data Validation & Transform
    ↓
Supabase Insert
    ↓
Success Log
```

---

## 🔧 カスタマイズ

### **ステータス値の変更**

`Data Validation & Transform`ノードの`status`値を変更：

```javascript
status: 'pending'  // デフォルト
// または
status: 'new'
status: 'active'
```

### **ソース値の変更**

`Data Validation & Transform`ノードの`source`値を変更：

```javascript
source: 'webhook'  // デフォルト
// または
source: 'LP_LINE'
source: 'manual'
```

---

## 🚨 トラブルシューティング

### **問題1: n8nからSupabaseに接続できない**

**症状**: "Connection refused" エラー

**解決策**:
1. ホスト名が正しいか確認: `db.ivlfrmzysbzrrqicsady.supabase.co`
2. SSL設定が `require` になっているか確認
3. パスワードに特殊文字がある場合はエスケープ

---

### **問題2: データが挿入されない**

**症状**: ワークフローは成功するがSupabaseにデータがない

**解決策**:
1. RLSポリシー確認
   ```sql
   SELECT * FROM pg_policies WHERE tablename = 'line_leads';
   ```
2. n8n実行ログ確認
3. Supabase Postgres Logs確認

---

### **問題3: LINE検証リクエストで500エラー**

**症状**: LINE Webhook検証時にエラー

**解決策**:
1. Data Validationノードのコード確認
2. `shouldStop` フラグが正しく設定されているか確認
3. 実行ログで `[VALIDATION] LINE verification request detected` が表示されるか確認

---

## ✅ セットアップ完了チェックリスト

### **Supabase**
- [ ] テーブル `line_leads` 作成完了
- [ ] インデックス作成完了
- [ ] RLS設定完了
- [ ] 接続情報を安全に保管

### **n8n**
- [ ] ワークフローインポート完了
- [ ] PostgreSQL認証情報作成完了
- [ ] 認証情報接続テスト成功
- [ ] Supabase Insertノードに認証情報設定完了
- [ ] Webhook URL確認完了

### **動作テスト**
- [ ] 検証リクエストテスト成功（データ挿入されない）
- [ ] 正常なfollowイベントテスト成功（データ挿入される）
- [ ] Supabaseでデータ確認完了

---

## 🔗 関連ドキュメント

- [スキーマ定義](./schema.sql)
- [ワークフロー定義](./workflow.json)
- [移行ノート](./migration-notes.md)
- [Notion版README](../README.md)

---

**⚠️ このセットアップガイドはアーカイブです。現在の推奨は [Notion版](../README.md) です。**

