# Google OAuth認証エラー トラブルシューティングガイド

**作成日**: 2025-01-XX
**エラー**: `invalid_client` - Client authentication failed
**対象環境**: Railway n8n + Google OAuth2

---

## 🚨 エラー概要

### エラーメッセージ
```
Error: Client authentication failed (e.g., unknown client, no client authentication included, or unsupported authentication method).
{"error":"invalid_client", "error_description":"Unauthorized"}
```

### 発生条件
- n8nでGoogleサービス（Google Sheets, Google Drive, Gmail等）のOAuth認証を試みる際
- Railway環境でn8nを実行している場合

---

## 🔍 原因と対処法

### 原因1: Google Cloud Consoleでのクライアント設定が不正

**症状**: リダイレクトURIが一致しない、クライアントID/シークレットが間違っている

**確認手順**:
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを選択
3. 「APIとサービス」→「認証情報」を開く
4. OAuth 2.0 クライアント IDを確認

**対処法**:

#### Step 1: リダイレクトURIを確認・追加
```
https://[your-n8n-domain]/rest/oauth2-credential/callback
```

例（Railway環境）:
```
https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback
```

**Google Cloud Consoleでの設定**:
1. OAuth 2.0 クライアント IDをクリック
2. 「承認済みのリダイレクト URI」セクションを確認
3. 上記のURIが登録されているか確認（なければ追加）

#### Step 2: クライアントID/シークレットを確認
1. n8nのCredentials設定画面で使用している値と一致しているか確認
2. Google Cloud Consoleの値と完全一致しているか確認（コピペミス、空白文字の混入など）

---

### 原因2: n8n環境変数の設定が不正

**症状**: OAuth認証に必要な環境変数が未設定または誤設定

**確認すべき環境変数**:

#### Railway環境変数
```bash
# n8n基本設定（必須）
N8N_HOST=n8n-python-production-344b.up.railway.app
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app

# OAuth設定（Google OAuth使用時）
N8N_OAUTH_CALLBACK_URL=https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback
```

**対処法**:
1. Railway Dashboard → プロジェクト → サービス → Variables
2. 上記の環境変数が設定されているか確認
3. `N8N_HOST`と`WEBHOOK_URL`が正しいドメインを指しているか確認
4. 設定後、n8nを再起動

```bash
# Railway CLI経由で設定
railway variables set N8N_HOST=n8n-python-production-344b.up.railway.app
railway variables set N8N_PROTOCOL=https
railway variables set WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app
```

---

### 原因3: n8n Credentials設定での認証情報誤入力

**症状**: n8nのCredentials設定画面でクライアントID/シークレットが正しく入力されていない

**対処法**:

#### Step 1: Credentialsを削除して再作成
1. n8n UI → **Credentials** → **Google OAuth2 API**
2. 既存の認証情報を削除
3. 新規作成:
   - **Credential Name**: `Google OAuth2`
   - **Client ID**: Google Cloud Consoleからコピー（空白なし）
   - **Client Secret**: Google Cloud Consoleからコピー（空白なし）

#### Step 2: OAuth認証フローの再実行
1. ワークフローでGoogleノードを開く
2. **Credentials**で上記で作成した認証情報を選択
3. **Connect** または **Authenticate** ボタンをクリック
4. ブラウザでOAuth認証画面が開くことを確認
5. Googleアカウントで認証を完了

---

### 原因4: Google Cloud ConsoleでのOAuth同意画面の設定不足

**症状**: OAuth同意画面が設定されていない、またはテストユーザーが登録されていない

**対処法**:

#### Step 1: OAuth同意画面を設定
1. Google Cloud Console → **APIとサービス** → **OAuth同意画面**
2. ユーザータイプを選択（外部または内部）
3. アプリ情報を入力:
   - アプリ名: `n8n Workflow Automation`
   - ユーザーサポートメール: 自分のメールアドレス
   - デベロッパーの連絡先情報: 自分のメールアドレス
4. **保存して次へ**

#### Step 2: スコープの追加
1. **スコープ**タブ
2. **スコープを追加または削除**をクリック
3. 必要なスコープを選択（例: Google Sheets, Google Drive）
4. **保存して次へ**

#### Step 3: テストユーザーの追加（外部ユーザータイプの場合）
1. **テストユーザー**タブ
2. **+ ユーザーを追加**
3. OAuth認証に使用するGoogleアカウントのメールアドレスを追加
4. **保存**

**注意**: 外部ユーザータイプの場合、公開前に最大100人のテストユーザーを追加できます。

---

### 原因5: Railway環境でのドメイン/プロトコル不一致

**症状**: `N8N_HOST`と実際のRailwayドメインが一致していない

**確認手順**:
1. Railway Dashboard → サービス → **Settings** → **Networking**
2. **Domain**を確認（例: `n8n-python-production-344b.up.railway.app`）
3. `N8N_HOST`環境変数と一致しているか確認

**対処法**:
```bash
# 実際のRailwayドメインに合わせて環境変数を設定
railway variables set N8N_HOST=[実際のRailwayドメイン]
railway variables set WEBHOOK_URL=https://[実際のRailwayドメイン]
railway variables set N8N_PROTOCOL=https
```

---

## ✅ チェックリスト

OAuth認証エラーを解決するための確認項目:

### Google Cloud Console
- [ ] OAuth 2.0 クライアント IDが作成されている
- [ ] リダイレクトURIが正しく設定されている（`https://[domain]/rest/oauth2-credential/callback`）
- [ ] クライアントIDとシークレットをコピー済み（空白なし）
- [ ] OAuth同意画面が設定されている
- [ ] テストユーザーが登録されている（外部ユーザータイプの場合）
- [ ] 必要なAPIが有効化されている（Google Sheets API, Google Drive API等）

### Railway環境変数
- [ ] `N8N_HOST`が正しいドメインを指している
- [ ] `N8N_PROTOCOL=https`が設定されている
- [ ] `WEBHOOK_URL`が正しいURLを指している
- [ ] 環境変数設定後、n8nが再起動されている

### n8n Credentials
- [ ] Google OAuth2認証情報が作成されている
- [ ] クライアントIDが正しく入力されている（空白なし）
- [ ] クライアントシークレットが正しく入力されている（空白なし）
- [ ] OAuth認証フローを再実行した

### ワークフローノード
- [ ] Googleノードで正しいCredentialsが選択されている
- [ ] OAuth認証が完了している（Connect/Authenticate状態）

---

## 🔄 解決手順のまとめ

### 完全な再設定手順

1. **Google Cloud Consoleでの設定**
   ```bash
   1. プロジェクト作成/選択
   2. OAuth 2.0 クライアント ID作成
   3. リダイレクトURI追加: https://[your-domain]/rest/oauth2-credential/callback
   4. OAuth同意画面設定
   5. テストユーザー追加（外部タイプの場合）
   6. 必要なAPI有効化
   ```

2. **Railway環境変数の設定**
   ```bash
   railway variables set N8N_HOST=[your-railway-domain]
   railway variables set N8N_PROTOCOL=https
   railway variables set WEBHOOK_URL=https://[your-railway-domain]
   ```

3. **n8n Credentialsの再作成**
   ```bash
   1. 既存のGoogle OAuth2認証情報を削除
   2. 新規作成（Client ID/Secretを正しく入力）
   3. OAuth認証フローを実行
   ```

4. **動作確認**
   ```bash
   1. ワークフローでGoogleノードを開く
   2. OAuth認証が成功するか確認
   3. 実際にAPI呼び出しが成功するかテスト
   ```

---

## 🚨 Railway環境での既知の問題

### 問題: Railway環境でのGoogle OAuth認証問題

**状況**: Railway環境では、Google OAuth認証が正常に動作しない場合がある

**回避策**: 
- Google Drive/Sheetsの代わりにNotion APIやRailway Volumeを使用
- 詳細は [`docs/architecture/wf7-phase3-storage-solution.md`](./architecture/wf7-phase3-storage-solution.md) を参照

**影響範囲**:
- Google Sheets Node
- Google Drive Node
- Gmail Node（OAuth認証のみ、API Key認証は動作）

---

## 📚 参考資料

- [n8n Google OAuth2認証ガイド](https://docs.n8n.io/integrations/builtin/credentials/google/)
- [Google Cloud Console - OAuth 2.0設定](https://console.cloud.google.com/apis/credentials)
- [Railway環境変数設定](https://docs.railway.app/develop/variables)

---

**作成日**: 2025-01-XX
**最終更新**: 2025-01-XX
**ステータス**: 検証済み
