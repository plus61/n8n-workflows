# Railway + n8n + Google OAuth2 完全設定ガイド

**作成日**: 2025-11-05
**検証済み**: Railway環境での実際の成功事例に基づく
**対象**: WF7 Phase2 Google Drive/Sheets統合

---

## 🎯 概要

Railway環境でn8nのGoogle OAuth2認証を正しく設定する方法。
**重要**: サービスアカウント（JWT）ではなく、OAuth2を使用する推奨方法です。

---

## ❌ よくある問題

### 症状
- Google OAuth認証時に `400 Bad Request` エラー
- リダイレクトURIが `localhost:5678` または不安定なRailway URLを指す
- 「invalid_request」「redirect_uri_mismatch」エラー

### 根本原因
1. **WEBHOOK_URL設定不足**: `https://` プロトコルが欠けている
2. **不安定なドメイン**: Railwayのデフォルト `*.up.railway.app` が変更される
3. **環境変数の不一致**: n8nがリダイレクトURIを正しく生成できない

---

## ✅ 完全な解決策

### Phase 1: Railway環境変数の正しい設定（10分）

#### □ Step 1.1: 現在のRailway Public Domainを確認

```bash
# Railway CLIで確認
railway status

# または Railway Dashboardで確認
# Settings → Networking → Public Networking → Domain
```

**例**: `n8n-python-production-344b.up.railway.app`

**重要**: このドメインが安定しているか確認
- ✅ カスタムドメイン（最も安定）
- ✅ Railway固定ドメイン
- ❌ 一時的なup.railway.appドメイン（再デプロイで変更される可能性）

#### □ Step 1.2: Railway環境変数を設定

**必須の環境変数**:

```bash
# オプション1: Railway CLIで設定
railway variables set N8N_HOST="n8n-python-production-344b.up.railway.app"
railway variables set N8N_PROTOCOL="https"
railway variables set N8N_EDITOR_BASE_URL="https://n8n-python-production-344b.up.railway.app"
railway variables set WEBHOOK_URL="https://n8n-python-production-344b.up.railway.app"

# オプション2: Railway Dashboardで設定
# Variables タブ → Add Variable
```

**重要なポイント**:
1. **https:// を必ず含める**: `WEBHOOK_URL` と `N8N_EDITOR_BASE_URL`
2. **完全なドメイン名**: `n8n-python-production-344b.up.railway.app`（ポート番号なし）
3. **N8N_PROTOCOL=https**: 必須

#### □ Step 1.3: Railway変数テンプレートを使用（推奨）

Railwayの動的変数を活用：

```bash
WEBHOOK_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
N8N_EDITOR_BASE_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
N8N_HOST=${{RAILWAY_PUBLIC_DOMAIN}}
N8N_PROTOCOL=https
```

**メリット**:
- ドメイン変更時に自動更新
- ハードコーディング不要
- 複数環境での再利用が容易

#### □ Step 1.4: OAuth専用の環境変数（オプション）

```bash
# OAuth callback URLを明示的に設定
N8N_OAUTH_CALLBACK_URL=https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback

# タイムゾーン（推奨）
GENERIC_TIMEZONE=Asia/Tokyo
TZ=Asia/Tokyo
```

#### □ Step 1.5: 設定を確認

```bash
# 設定した環境変数を確認
railway variables | grep -E 'N8N_|WEBHOOK_URL'

# 期待される出力:
# N8N_HOST=n8n-python-production-344b.up.railway.app
# N8N_PROTOCOL=https
# N8N_EDITOR_BASE_URL=https://n8n-python-production-344b.up.railway.app
# WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app
```

#### □ Step 1.6: n8nを再デプロイ

```bash
# Railway CLIで再デプロイ
railway up

# または Railway Dashboard
# Deployments → Redeploy
```

**重要**: 環境変数の変更後は必ず再デプロイが必要

---

### Phase 2: Google Cloud Console設定（15分）

#### □ Step 2.1: Google Cloud Consoleにアクセス

https://console.cloud.google.com/

#### □ Step 2.2: プロジェクトを選択または作成

1. 既存のプロジェクトを選択、または
2. **新しいプロジェクト** を作成
   - プロジェクト名: `n8n-wf7-integration`
   - プロジェクトID: 自動生成（例: `n8n-wf7-integration-441612`）

#### □ Step 2.3: OAuth同意画面を設定

1. **APIとサービス** → **OAuth同意画面**
2. ユーザータイプを選択:
   - **外部**: 個人用、テストユーザー100人まで
   - **内部**: Google Workspace組織内のみ

**推奨**: **外部** を選択（個人使用の場合）

3. アプリ情報を入力:
   ```
   アプリ名: n8n Workflow Automation
   ユーザーサポートメール: [あなたのメールアドレス]
   アプリのロゴ: （オプション）
   アプリのドメイン:
     - ホームページ: https://n8n-python-production-344b.up.railway.app
   デベロッパーの連絡先情報: [あなたのメールアドレス]
   ```

4. **スコープ**:
   - **+ スコープを追加または削除** をクリック
   - 以下を選択:
     - `https://www.googleapis.com/auth/drive.file` (Google Drive)
     - `https://www.googleapis.com/auth/spreadsheets` (Google Sheets)
     - `https://www.googleapis.com/auth/gmail.send` (Gmail - オプション)

5. **テストユーザー**（外部ユーザータイプの場合）:
   - **+ ユーザーを追加**
   - OAuth認証に使用するGoogleアカウントのメールアドレスを追加

6. **保存して次へ** → 完了

#### □ Step 2.4: OAuth 2.0 クライアントIDを作成

1. **APIとサービス** → **認証情報**
2. **+ 認証情報を作成** → **OAuth 2.0 クライアント ID**
3. アプリケーションの種類: **ウェブ アプリケーション**
4. 名前: `n8n-railway-oauth-client`
5. **承認済みのリダイレクト URI** を追加:
   ```
   https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback
   ```

**重要**:
- `https://` を必ず含める
- `/rest/oauth2-credential/callback` で終わる
- Railway環境変数で設定したドメインと完全一致

6. **作成** をクリック
7. **クライアントID** と **クライアントシークレット** をコピー
   - クライアントID: `xxxxxxxxxxxx.apps.googleusercontent.com`
   - クライアントシークレット: `GOCSPX-xxxxxxxxxxxxxxxxxxxxx`

#### □ Step 2.5: 必要なAPIを有効化

1. **APIとサービス** → **ライブラリ**
2. 以下のAPIを検索して **有効にする**:
   - [ ] **Google Drive API**
   - [ ] **Google Sheets API**
   - [ ] **Gmail API** (オプション)

---

### Phase 3: n8n OAuth2認証情報作成（5分）

#### □ Step 3.1: n8n UIにアクセス

https://n8n-python-production-344b.up.railway.app

#### □ Step 3.2: Credentialsページを開く

左サイドバー → **Credentials** → **Add Credential**

#### □ Step 3.3: Google Drive OAuth2 APIを選択

検索ボックスに「Google Drive」と入力
→ **Google Drive OAuth2 API** を選択

#### □ Step 3.4: 認証情報を入力

| フィールド | 値 |
|-----------|---|
| Credential Name | `Google Drive OAuth2` |
| Client ID | [Step 2.4でコピーしたID] |
| Client Secret | [Step 2.4でコピーしたシークレット] |

#### □ Step 3.5: OAuth Redirect URIを確認

n8nが表示する **OAuth Redirect URL** を確認：

**期待値**:
```
https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback
```

**問題のある例**:
- ❌ `http://localhost:5678/rest/oauth2-credential/callback`
- ❌ `https://web-production-xxxx.up.railway.app/...` (不安定なドメイン)

**問題がある場合**:
→ **Phase 1に戻る**: Railway環境変数を再確認

#### □ Step 3.6: OAuth認証を実行

1. **Connect my account** ボタンをクリック
2. Googleアカウント選択画面が表示される
3. OAuth同意画面のテストユーザーとして追加したアカウントを選択
4. アクセス権限を確認:
   - Google Driveファイルの表示、編集、作成、削除
   - Google Sheetsスプレッドシートの表示、編集、作成、削除
5. **許可** をクリック
6. n8nに自動でリダイレクト
7. **緑のチェックマーク** が表示されれば成功

#### □ Step 3.7: 認証情報IDをメモ

作成した認証情報をクリックしてURLを確認:
```
https://n8n-python-production-344b.up.railway.app/credentials/[ID]
                                                              ^^^^
```

例: ID = `39`

このIDを後で使用します。

---

### Phase 4: ワークフロー更新（10分）

#### □ Step 4.1: WF7 Phase2ワークフローを開く

n8n UI → **Workflows** → **WF7 Phase2: 素材取得_google版**

#### □ Step 4.2: カスタムJWT認証ノードを削除

**削除するノード**:
- [ ] **Googleアクセストークン取得** (Custom Code node)

#### □ Step 4.3: HTTP Requestノードを更新

以下のノードを更新：

**1. Driveファイル作成**

**変更前**:
```json
{
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "=Bearer {{$node[\"Googleアクセストークン取得\"].json.accessToken}}"
      }
    ]
  }
}
```

**変更後**:
```json
{
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "googleDriveOAuth2Api"
}
```

**手順**:
1. ノードをクリック
2. **Authentication** ドロップダウン → **Predefined Credential Type** を選択
3. **Credential Type** → **Google Drive OAuth2 API** を選択
4. **Credential for Google Drive OAuth2 API** → **Google Drive OAuth2** を選択（Step 3.4で作成）
5. **Send Headers** → 削除（不要）

**2. Driveコンテンツアップロード**

同様に変更:
- **Authentication** → **Predefined Credential Type**
- **Credential Type** → **Google Drive OAuth2 API**
- **Credential** → **Google Drive OAuth2**
- Authorization ヘッダー削除

**3. Driveファイル情報取得**

同様に変更。

**4. Google Sheets追記**

**変更後**:
```json
{
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "googleSheetsOAuth2Api"
}
```

**手順**:
1. **Credential Type** → **Google Sheets OAuth2 API** を選択
2. **Credential for Google Sheets OAuth2 API** → **Google Sheets OAuth2** を選択

**注意**: Google Sheets OAuth2認証情報も別途作成が必要
（Google Drive OAuth2と同じ手順でCredentials画面から作成）

#### □ Step 4.4: 接続を更新

**削除したノードの影響を修正**:

1. **アセットメタ整形** の出力 → **Driveファイル作成** に直接接続
2. **Googleアクセストークン取得** への接続を削除

#### □ Step 4.5: ワークフローを保存

右上の **Save** をクリック

---

### Phase 5: テスト実行（5分）

#### □ Step 5.1: テストペイロードを準備

```json
{
  "articleId": "oauth-test-001",
  "notionPageId": "test-page-id",
  "assetTags": "mountain,sunset,ocean"
}
```

#### □ Step 5.2: Webhook実行

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "oauth-test-001",
    "notionPageId": "14e96d7e-3ed1-8127-b0a0-f920eab4ec50",
    "assetTags": "mountain,sunset,ocean"
  }'
```

#### □ Step 5.3: 結果確認

**成功の場合**:
```json
{
  "status": "success",
  "articleId": "oauth-test-001",
  "assets": [
    {
      "assetTag": "mountain",
      "assetIndex": 0,
      "source": "pexels",
      "driveFileId": "1xxxxxxxxxxxxxxxxxxxx",
      "driveWebViewLink": "https://drive.google.com/file/d/1xxxx/view"
    },
    ...
  ]
}
```

**失敗の場合**: エラーメッセージを確認

#### □ Step 5.4: Google Driveを確認

1. https://drive.google.com/ にアクセス
2. OAuth認証したアカウントでログイン
3. 以下のファイルが作成されているか確認:
   - `asset_oauth-test-001_0.jpg` (mountain)
   - `asset_oauth-test-001_1.jpg` (sunset)
   - `asset_oauth-test-001_2.jpg` (ocean)

#### □ Step 5.5: Railway logsを確認

```bash
railway logs --tail 100
```

エラーがないか確認。

---

## 🎉 成功基準

### 完了チェックリスト

- [ ] Railway環境変数が正しく設定されている
- [ ] n8nのリダイレクトURIが `https://[stable-domain]/rest/oauth2-credential/callback`
- [ ] Google Cloud ConsoleでOAuth同意画面が設定済み
- [ ] OAuth 2.0 クライアントIDが作成済み
- [ ] リダイレクトURIがGoogle Cloud Consoleに登録済み
- [ ] n8nでGoogle OAuth2認証情報が作成され、緑のチェックマーク表示
- [ ] ワークフローノードがOAuth2認証を使用
- [ ] テスト実行が成功
- [ ] Google Driveにファイルがアップロードされている

---

## 🚨 トラブルシューティング

### 問題1: `400 Bad Request` - redirect_uri_mismatch

**原因**: リダイレクトURIの不一致

**解決策**:
1. n8nのCredentials画面でOAuth Redirect URLを確認
2. Google Cloud Consoleの承認済みリダイレクトURIと完全一致するか確認
3. 不一致の場合:
   - Phase 1に戻ってRailway環境変数を修正
   - n8nを再デプロイ
   - OAuth認証情報を再作成

### 問題2: リダイレクトURIが `localhost:5678` のまま

**原因**: Railway環境変数が反映されていない

**解決策**:
```bash
# 環境変数を再確認
railway variables | grep N8N_

# N8N_HOST と WEBHOOK_URL が正しいか確認
# 修正後、必ず再デプロイ
railway up
```

### 問題3: `access_denied` エラー

**原因**: OAuth同意画面のテストユーザーに追加されていない

**解決策**:
1. Google Cloud Console → OAuth同意画面 → テストユーザー
2. 認証に使用するGoogleアカウントを追加
3. OAuth認証をやり直し

### 問題4: トークンが7日で期限切れ

**原因**: OAuth同意画面のPublishing statusが「Testing」

**解決策**:
- **短期的**: 7日ごとに再認証
- **長期的**: OAuth同意画面を「Production」に公開
  - Google審査が必要
  - または「Internal」に変更（Google Workspace組織の場合）

### 問題5: `insufficient_permissions` エラー

**原因**: OAuth同意画面でスコープが不足

**解決策**:
1. Google Cloud Console → OAuth同意画面 → スコープ
2. 以下のスコープが追加されているか確認:
   - `https://www.googleapis.com/auth/drive.file`
   - `https://www.googleapis.com/auth/spreadsheets`
3. スコープ追加後、OAuth認証をやり直し

---

## 📋 環境変数まとめ

### 必須環境変数（Railway）

```bash
# ドメイン設定
N8N_HOST=n8n-python-production-344b.up.railway.app
N8N_PROTOCOL=https
N8N_EDITOR_BASE_URL=https://n8n-python-production-344b.up.railway.app
WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app

# または動的変数を使用（推奨）
N8N_HOST=${{RAILWAY_PUBLIC_DOMAIN}}
N8N_PROTOCOL=https
N8N_EDITOR_BASE_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
WEBHOOK_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
```

### オプション環境変数

```bash
# OAuth callback URL（明示的設定）
N8N_OAUTH_CALLBACK_URL=https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback

# タイムゾーン
GENERIC_TIMEZONE=Asia/Tokyo
TZ=Asia/Tokyo

# n8n基本設定
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=[secure-password]
```

---

## 📚 関連ドキュメント

- [WF7 Google認証エラー 修正ガイド](./wf7-google-auth-fix-guide.md)
- [WF7 Google認証エラー - クイック修正](./wf7-google-auth-quick-fix.md)
- [Google OAuth Troubleshooting](./troubleshooting-google-oauth.md)
- [n8n Google OAuth2 公式ドキュメント](https://docs.n8n.io/integrations/builtin/credentials/google/oauth-generic/)

---

## 🌟 ベストプラクティス

### セキュリティ

1. **環境変数の保護**
   - 本番環境ではBasic認証を有効化
   - OAuth clientシークレットをGitに含めない

2. **OAuth同意画面**
   - 必要最小限のスコープのみ要求
   - テストユーザーを定期的に見直し

3. **トークン管理**
   - n8nが自動でトークンを更新
   - 手動でのトークン管理は不要

### パフォーマンス

1. **認証情報の再利用**
   - 複数のワークフローで同じOAuth2認証情報を使用
   - 認証情報ごとにトークンが管理される

2. **エラーハンドリング**
   - OAuth2認証失敗時のリトライロジック
   - トークン更新失敗時の通知設定

---

**最終更新**: 2025-11-05
**検証環境**: Railway + n8n v1.117.3
**ステータス**: 実戦検証済み ✅
