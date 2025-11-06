# WF7 Google認証エラー - クイック修正チェックリスト

**作成日**: 2025-11-05
**所要時間**: 15-30分
**対象**: WF7 Phase2: 素材取得_google版

---

## 🎯 目的

WF7のGoogle認証エラーを診断し、即座に修正可能な問題を解決する。

---

## ✅ チェックリスト

### Phase 1: 環境変数の確認（5分）

#### □ Step 1.1: Railway環境変数を表示
```bash
railway variables
```

#### □ Step 1.2: 必須環境変数の存在確認
以下が設定されているか確認：

- [ ] `GOOGLE_APPLICATION_CREDENTIALS_JSON`
- [ ] `GOOGLE_SCOPES`（オプション、デフォルト値使用可）
- [ ] `GOOGLE_DRIVE_FOLDER_ID`（オプション、'root'がデフォルト）
- [ ] `GSHEET_ID`（オプション、Google Sheets使用時のみ）

**問題**: 上記が**未設定**の場合
→ **[Phase 2へ]**: サービスアカウント設定が必要

**問題なし**: 全て設定済み
→ **[Phase 3へ]**: JSON形式の検証

---

### Phase 2: サービスアカウント作成と設定（15分）

#### □ Step 2.1: Google Cloud Consoleでサービスアカウント作成

1. https://console.cloud.google.com/ にアクセス
2. プロジェクトを選択（または新規作成）
3. **IAMと管理** → **サービスアカウント**
4. **+ サービスアカウントを作成** をクリック

**サービスアカウント名**: `n8n-wf7-service`

#### □ Step 2.2: ロールの付与

以下のロールを選択：

- [ ] **Google Drive**: `Drive File Editor` (roles/drive.file)
- [ ] **Google Sheets**: `Sheets Editor` (roles/sheets.editor)

#### □ Step 2.3: JSONキーのダウンロード

1. 作成したサービスアカウントをクリック
2. **キー** タブ → **鍵を追加** → **新しい鍵を作成**
3. **JSON** を選択してダウンロード
4. ファイル名: `n8n-wf7-service-account-key.json`

#### □ Step 2.4: Google Drive APIの有効化

1. **APIとサービス** → **ライブラリ**
2. 「Google Drive API」を検索
3. **有効にする** をクリック

#### □ Step 2.5: Google Sheets APIの有効化

1. **APIとサービス** → **ライブラリ**
2. 「Google Sheets API」を検索
3. **有効にする** をクリック

#### □ Step 2.6: Railway環境変数を設定

```bash
# JSONキーの内容をコピー
cat n8n-wf7-service-account-key.json

# Railway環境変数に設定（1行に圧縮）
railway variables set GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type":"service_account","project_id":"your-project",...}'

# スコープを設定（オプション）
railway variables set GOOGLE_SCOPES='https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/spreadsheets'
```

**重要**: JSON文字列は1行に圧縮し、シングルクォートで囲む

#### □ Step 2.7: n8nを再起動

```bash
railway up
```

または Railway Dashboard → Redeploy

---

### Phase 3: JSON形式の検証（5分）

#### □ Step 3.1: 環境変数の取得と検証

```bash
# 環境変数を取得
railway variables get GOOGLE_APPLICATION_CREDENTIALS_JSON > temp-creds.json

# JSON形式が正しいか検証
cat temp-creds.json | jq .

# 必須フィールドの確認
cat temp-creds.json | jq '{
  type,
  project_id,
  private_key_id,
  client_email,
  token_uri
}'
```

#### □ Step 3.2: 必須フィールドの確認

- [ ] `type`: "service_account"
- [ ] `project_id`: 存在する（例: "my-project-12345"）
- [ ] `private_key_id`: 存在する
- [ ] `private_key`: "-----BEGIN PRIVATE KEY-----" で始まる
- [ ] `client_email`: "...@...iam.gserviceaccount.com" 形式
- [ ] `token_uri`: "https://oauth2.googleapis.com/token"

**問題**: フィールドが欠けている、または形式が不正
→ **[Phase 2に戻る]**: サービスアカウントを再作成

**問題なし**: 全てのフィールドが正常
→ **[Phase 4へ]**: テスト実行

---

### Phase 4: テスト実行（5分）

#### □ Step 4.1: Notionテストページ準備

Notionで以下のプロパティを持つテストページを作成：

| プロパティ | 値 |
|-----------|---|
| Article ID | `google-auth-test-001` |
| Status | `Draft` |

ページIDをコピー（URLの最後の部分）:
```
https://www.notion.so/google-auth-test-001-[PAGE_ID]
                                            ^^^^^^^^^ これをコピー
```

#### □ Step 4.2: Webhook実行

```bash
# Webhook URLに POST リクエスト
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "google-auth-test-001",
    "notionPageId": "[コピーしたページID]",
    "assetTags": "mountain,sunset,ocean"
  }'
```

#### □ Step 4.3: 結果確認

**成功の場合**:
```json
{
  "status": "success",
  "articleId": "google-auth-test-001",
  "assets": [...]
}
```

**失敗の場合**:
```json
{
  "error": "...",
  "message": "..."
}
```

#### □ Step 4.4: Railway logsでエラー確認

```bash
railway logs --tail 50
```

エラーパターンを検索：

| エラーメッセージ | 原因 | 解決策 |
|----------------|------|-------|
| `GOOGLE_APPLICATION_CREDENTIALS_JSON is not set` | 環境変数未設定 | Phase 2に戻る |
| `Failed to obtain Google access token` | JSON形式エラー | Phase 3に戻る |
| `invalid_grant` | サービスアカウントが無効 | Phase 2.1から再作成 |
| `unauthorized_client` | APIが無効化されている | Phase 2.4-2.5を確認 |
| `insufficient_permissions` | ロールが不足 | Phase 2.2を確認 |

---

## 🎉 成功確認

### □ 最終チェック

1. **Webhook実行が成功**: ステータスコード 200
2. **Google Driveにファイル作成**: 3つの画像ファイルがアップロード
3. **Google Sheetsに記録**: Assets シートに行が追加（オプション）
4. **Notionページ更新**: Status が "AssetsReady" に更新

---

## 🚨 トラブルシューティング

### 問題1: `GOOGLE_APPLICATION_CREDENTIALS_JSON is not set`

**原因**: 環境変数が設定されていない

**解決策**:
```bash
# 環境変数を確認
railway variables | grep GOOGLE

# 設定されていない場合は Phase 2 を実行
```

---

### 問題2: `Failed to parse GOOGLE_APPLICATION_CREDENTIALS_JSON`

**原因**: JSON形式が不正（改行、エスケープ文字の問題）

**解決策**:
```bash
# JSON を1行に圧縮
cat n8n-wf7-service-account-key.json | jq -c . > oneline.json

# 環境変数を再設定
railway variables set GOOGLE_APPLICATION_CREDENTIALS_JSON="$(cat oneline.json)"
```

---

### 問題3: `invalid_grant` または `unauthorized_client`

**原因**: サービスアカウントが無効、またはAPIが無効化

**解決策**:
1. Google Cloud Console → IAMと管理 → サービスアカウント
2. サービスアカウントが **有効** になっているか確認
3. **APIとサービス** → **有効なAPI** で以下を確認:
   - Google Drive API
   - Google Sheets API

---

### 問題4: `insufficient_permissions`

**原因**: サービスアカウントに必要なロールが付与されていない

**解決策**:
1. Google Cloud Console → IAMと管理 → サービスアカウント
2. サービスアカウントをクリック → **権限** タブ
3. 以下のロールが付与されているか確認:
   - `roles/drive.file` (Drive File Editor)
   - `roles/sheets.editor` (Sheets Editor)
4. 付与されていない場合は **ロールを付与** から追加

---

## 📋 完了後の確認項目

### □ ドキュメント更新

- [ ] 環境変数をプロジェクトドキュメントに記録
- [ ] サービスアカウント情報を安全に保管
- [ ] テスト結果を記録

### □ セキュリティチェック

- [ ] JSONキーファイルを削除（ローカル）
- [ ] Git履歴にJSONキーが含まれていないか確認
- [ ] `.gitignore` に `*-key.json` を追加

```bash
# .gitignore に追加
echo "*-key.json" >> .gitignore
echo "temp-creds.json" >> .gitignore
git add .gitignore
git commit -m "Add service account key files to gitignore"
```

---

## 🔄 次のステップ

### 修正完了後

1. ✅ 本番データでテスト実行
2. ✅ エラーモニタリングの設定
3. ✅ 定期的なトークン更新の確認

### 長期的改善

1. 📅 OAuth2認証への移行検討（より安全）
2. 📅 代替ストレージソリューションの評価
3. 📅 エラーハンドリングの強化

---

**完了時刻**: _________________
**実行者**: _________________
**結果**: ✅ 成功 / ❌ 失敗（理由: ________________）

---

**関連ドキュメント**:
- [WF7 Google認証エラー 修正ガイド](./wf7-google-auth-fix-guide.md)
- [Google OAuth Troubleshooting](./troubleshooting-google-oauth.md)
