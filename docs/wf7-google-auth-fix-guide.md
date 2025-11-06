# WF7 Google認証エラー 修正ガイド

**作成日**: 2025-11-05
**対象**: WF7 Phase2: 素材取得_google版 (ID: HrYFB54nhsPy5QPB)
**エラー**: Google Drive/Sheets API認証失敗

---

## 🚨 問題の概要

### 現在の状況
WF7 Phase2ワークフローが**カスタムJWT認証**を使用してGoogle APIにアクセスしていますが、以下の問題があります：

1. **複雑性**: Code nodeで手動でJWTトークンを生成する200行以上のコード
2. **エラー発生率**: 暗号化処理、トークン生成でのエラーが発生しやすい
3. **環境変数依存**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`, `GOOGLE_SCOPES` が必要
4. **デバッグ困難**: エラーメッセージが不明瞭で原因特定が困難
5. **メンテナンス負荷**: Google認証仕様変更時の対応が複雑

### 影響を受けるノード
- **Googleアクセストークン取得** (Custom JWT生成)
- **Driveファイル作成** (Manual Bearer Token)
- **Driveコンテンツアップロード** (Manual Bearer Token)
- **Driveファイル情報取得** (Manual Bearer Token)
- **Google Sheets追記** (Manual Bearer Token)

---

## 💡 推奨される解決策

### オプション1: n8n組み込みGoogle OAuth2認証（推奨）

**メリット**:
- ✅ n8nが自動でトークン管理
- ✅ エラー処理が自動化
- ✅ トークン更新が自動
- ✅ UIから簡単に設定可能
- ✅ メンテナンスフリー

**デメリット**:
- ⚠️ Railway環境では動作しない可能性（既知の問題）
- ⚠️ OAuth2フロー初回設定が必要

**実装ステップ**:

#### Step 1: Google Cloud Console設定
```bash
1. Google Cloud Console (https://console.cloud.google.com/) にアクセス
2. プロジェクトを選択または新規作成
3. 「APIとサービス」→「認証情報」
4. 「OAuth 2.0 クライアント ID」を作成
5. リダイレクトURIを追加:
   https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback
6. Client ID と Client Secret をコピー
```

#### Step 2: n8n OAuth2認証情報作成
```bash
1. n8n UI (https://n8n-python-production-344b.up.railway.app) にログイン
2. Credentials → Add Credential
3. 「Google Drive OAuth2 API」を選択
4. 以下を入力:
   - Credential Name: Google Drive OAuth2
   - Client ID: [Google Cloud Consoleからコピー]
   - Client Secret: [Google Cloud Consoleからコピー]
5. 「Connect my account」をクリック
6. Googleアカウントで認証を完了
7. 認証情報IDをメモ（URLから確認）
```

#### Step 3: HTTP Requestノードを更新
現在のHTTP Requestノードの認証設定を変更：

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

#### Step 4: 不要なノードを削除
- **Googleアクセストークン取得** ノードを削除
- 接続を直接 **アセットメタ整形** → **Driveファイル作成** に変更

---

### オプション2: サービスアカウント認証（現在の方法を改善）

**メリット**:
- ✅ UIでのOAuth不要
- ✅ 自動化に適している
- ✅ Railway環境での既知の問題を回避

**デメリット**:
- ❌ 環境変数の設定が必須
- ❌ サービスアカウントキーの管理が必要
- ❌ デバッグが複雑

**必要な環境変数**:
```bash
# Railway環境変数に設定
GOOGLE_APPLICATION_CREDENTIALS_JSON='{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}'

GOOGLE_SCOPES='https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/spreadsheets'
```

**実装ステップ**:

#### Step 1: サービスアカウント作成
```bash
1. Google Cloud Console → IAMと管理 → サービスアカウント
2. 「サービスアカウントを作成」
3. 名前: n8n-wf7-service-account
4. ロールを付与:
   - Google Drive: ドライブ ファイル編集者
   - Google Sheets: Google スプレッドシート編集者
5. 「キーを作成」→ JSON形式でダウンロード
```

#### Step 2: Railway環境変数設定
```bash
railway variables set GOOGLE_APPLICATION_CREDENTIALS_JSON='[JSONキーの内容]'
railway variables set GOOGLE_SCOPES='https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/spreadsheets'
```

#### Step 3: Code nodeのエラーハンドリング改善
現在の「Googleアクセストークン取得」ノードに以下を追加：

```javascript
try {
  // 既存のJWT生成コード
  // ...
} catch (error) {
  // 詳細なエラーログ
  console.error('JWT generation failed:', {
    error: error.message,
    stack: error.stack,
    credentialsPresent: !!$env.GOOGLE_APPLICATION_CREDENTIALS_JSON,
    scopesPresent: !!$env.GOOGLE_SCOPES
  });

  throw new Error(`Google authentication failed: ${error.message}`);
}
```

---

### オプション3: Google Drive Native Node使用（最も簡単）

**メリット**:
- ✅ n8nが全てを自動処理
- ✅ UIから簡単設定
- ✅ エラー処理が自動
- ✅ コードゼロ

**デメリット**:
- ⚠️ Railway環境での既知の問題
- ⚠️ カスタマイズ性が低い

**実装ステップ**:

#### Step 1: OAuth2認証情報作成（オプション1と同じ）

#### Step 2: HTTP Requestノードを置き換え
以下のノードを置き換え：

| 現在のノード | 置き換え先 |
|------------|----------|
| Driveファイル作成 | Google Drive: Upload a File |
| Driveコンテンツアップロード | （不要） |
| Driveファイル情報取得 | Google Drive: Get a File |
| Google Sheets追記 | Google Sheets: Append |

---

## 🔍 現在のエラーの診断方法

### Step 1: 環境変数を確認
```bash
# Railway Dashboard または CLI
railway variables

# 以下が設定されているか確認
- GOOGLE_APPLICATION_CREDENTIALS_JSON
- GOOGLE_SCOPES
```

### Step 2: サービスアカウントキーの検証
```bash
# JSONキーが正しいか確認
echo $GOOGLE_APPLICATION_CREDENTIALS_JSON | jq .

# 必須フィールドの確認
- type: "service_account"
- project_id: 存在する
- private_key: "-----BEGIN PRIVATE KEY-----" で始まる
- client_email: ...@...iam.gserviceaccount.com
- token_uri: "https://oauth2.googleapis.com/token"
```

### Step 3: ワークフロー実行ログを確認
```bash
# Railway logs
railway logs

# エラーパターンを検索
- "GOOGLE_APPLICATION_CREDENTIALS_JSON is not set"
- "Failed to obtain Google access token"
- "invalid_grant"
- "unauthorized_client"
```

---

## ✅ 推奨アクション

### 短期的対応（今すぐ実行可能）
1. **環境変数の確認と設定**
   - `GOOGLE_APPLICATION_CREDENTIALS_JSON` が正しく設定されているか
   - JSON形式が正しいか（エスケープ文字に注意）
   - サービスアカウントが有効か

2. **エラーログの収集**
   - Railway logsで具体的なエラーメッセージを確認
   - 「Googleアクセストークン取得」ノードの出力を確認

3. **テスト実行**
   ```bash
   curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
     -H "Content-Type: application/json" \
     -d '{
       "articleId": "test-001",
       "notionPageId": "test-page-id",
       "assetTags": "test,image,sample"
     }'
   ```

### 中期的対応（1-2日）
1. **オプション1を試す**: n8n OAuth2認証
   - Google Cloud Consoleでの設定
   - n8nでの認証情報作成
   - ワークフローノード更新

2. **動作確認**
   - テストデータでの実行
   - エラーログの確認
   - 成功時の動作確認

### 長期的対応（1週間）
1. **アーキテクチャ改善**
   - Google Drive Native Nodeへの移行
   - エラーハンドリングの強化
   - リトライロジックの追加

2. **代替ストレージの検討**
   - Notion APIでの画像管理
   - Railway Volumeでのローカルストレージ
   - S3/Cloudflare R2などの外部ストレージ

---

## 🚨 既知の問題と回避策

### 問題1: Railway環境でのOAuth2認証失敗
**症状**: `invalid_client`, `unauthorized` エラー

**原因**:
- リダイレクトURIの不一致
- 環境変数 `N8N_HOST`, `WEBHOOK_URL` の設定不足

**回避策**:
```bash
# Railway環境変数を設定
railway variables set N8N_HOST=n8n-python-production-344b.up.railway.app
railway variables set N8N_PROTOCOL=https
railway variables set WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app
railway variables set N8N_OAUTH_CALLBACK_URL=https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback
```

### 問題2: サービスアカウントのprivate_keyフォーマットエラー
**症状**: `Invalid JWT signature` エラー

**原因**:
- 改行文字 `\n` が正しくエスケープされていない
- JSONパースエラー

**回避策**:
```javascript
// Code nodeで改行を正規化
const credentials = JSON.parse(credentialsJson);
credentials.private_key = credentials.private_key.replace(/\\n/g, '\n');
```

### 問題3: トークン有効期限切れ
**症状**: 1時間後に `invalid_token` エラー

**原因**:
- JWTトークンの有効期限が1時間
- トークン更新ロジックなし

**回避策**:
```javascript
// トークンキャッシュとリトライロジックを追加
const tokenCache = {
  token: null,
  expiresAt: null
};

if (!tokenCache.token || Date.now() >= tokenCache.expiresAt) {
  // 新しいトークンを取得
  const tokenResponse = await this.helpers.httpRequest({...});
  tokenCache.token = tokenResponse.access_token;
  tokenCache.expiresAt = Date.now() + (tokenResponse.expires_in * 1000) - 300000; // 5分前に更新
}
```

---

## 📚 関連ドキュメント

- [Google Drive OAuth2 Setup Guide](./setup/google-drive-oauth2-setup-guide.md)
- [Google OAuth Troubleshooting](./troubleshooting-google-oauth.md)
- [WF7 Hybrid VEO3 Design](./wf7-hybrid-veo3-design.md)

---

## 🎯 次のステップ

### 即座に実行
1. ✅ Railway環境変数を確認
2. ✅ サービスアカウントキーの検証
3. ✅ テスト実行でエラーログ収集

### 今週中に実行
1. ⏳ オプション1（OAuth2）またはオプション3（Native Node）を試す
2. ⏳ エラーハンドリングの改善
3. ⏳ ドキュメント更新

### 来週以降
1. 📅 代替ストレージソリューションの評価
2. 📅 アーキテクチャ全体の見直し
3. 📅 自動テストの追加

---

**最終更新**: 2025-11-05
**ステータス**: 診断完了・修正待ち
