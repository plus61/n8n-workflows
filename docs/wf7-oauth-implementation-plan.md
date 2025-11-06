# WF7 Google OAuth2 実装計画

**作成日**: 2025-11-05
**ステータス**: 実装準備完了
**所要時間**: 約45分

---

## 📋 現在の状況

### ✅ 完了済み
1. **Railway環境変数の確認**: すべての必須OAuth変数が正しく設定済み
   - `N8N_HOST`: n8n-python-production-344b.up.railway.app
   - `N8N_PROTOCOL`: https
   - `N8N_EDITOR_BASE_URL`: https://n8n-python-production-344b.up.railway.app
   - `WEBHOOK_URL`: https://n8n-python-production-344b.up.railway.app ✅ (https://付き)

2. **ドキュメント作成完了**:
   - Railway OAuth完全ガイド
   - クイック修正チェックリスト
   - 詳細修正ガイド

### 🔄 次のステップ

Railway環境変数は既に正しく設定されているため、以下の手順で直接OAuth2実装に進めます：

---

## 🎯 実装フェーズ1: Google Cloud Console設定（15分）

### Step 1.1: プロジェクト選択
```
1. https://console.cloud.google.com/ にアクセス
2. 既存プロジェクトを選択または新規作成
   推奨: 既存の n8n プロジェクトを使用
```

### Step 1.2: OAuth 2.0 クライアント ID 作成
```
1. 「APIとサービス」→「認証情報」
2. 「+ 認証情報を作成」→「OAuth 2.0 クライアント ID」
3. アプリケーションの種類: 「ウェブ アプリケーション」
4. 名前: n8n-railway-oauth2
5. 承認済みのリダイレクト URI に以下を追加:
   https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback
```

### Step 1.3: 必須API有効化
```
✅ Google Drive API
✅ Google Sheets API
```

**有効化コマンド（CLIの場合）**:
```bash
gcloud services enable drive.googleapis.com
gcloud services enable sheets.googleapis.com
```

### Step 1.4: クライアント情報の保存
```
以下をメモ:
- クライアントID: [長い文字列].apps.googleusercontent.com
- クライアントシークレット: [ランダムな文字列]
```

---

## 🎯 実装フェーズ2: n8n OAuth2認証情報作成（5分）

### Step 2.1: n8n UIにアクセス
```
URL: https://n8n-python-production-344b.up.railway.app
```

### Step 2.2: 新しい認証情報を作成
```
1. 左サイドバー → 「Credentials」
2. 「+ Add Credential」をクリック
3. 検索: "Google Drive OAuth2 API"
4. 選択: Google Drive OAuth2 API
```

### Step 2.3: 認証情報を入力
```
Credential Name: Google Drive OAuth2
Client ID: [Google Cloud Consoleからコピー]
Client Secret: [Google Cloud Consoleからコピー]
Scope: (デフォルトのまま)
Auth URI: https://accounts.google.com/o/oauth2/v2/auth
Access Token URI: https://oauth2.googleapis.com/token
```

### Step 2.4: アカウント接続
```
1. 「Connect my account」をクリック
2. Googleアカウント選択画面が表示される
3. 権限リクエストを承認
4. n8nに自動でリダイレクト
5. 「Connected」ステータスを確認
```

### Step 2.5: 認証情報IDをメモ
```
URLから認証情報IDをコピー:
例: /credentials/[credential-id]
```

---

## 🎯 実装フェーズ3: WF7ワークフロー更新（15分）

### Step 3.1: WF7 Phase2ワークフローを開く
```
Workflow ID: HrYFB54nhsPy5QPB
名前: WF7 Phase2: 素材取得_google版
```

### Step 3.2: 不要なノードを削除
```
削除対象:
- 「Googleアクセストークン取得」Code ノード
```

### Step 3.3: HTTP Requestノードを更新

**対象ノード（5つ）**:
1. Driveファイル作成
2. Driveコンテンツアップロード
3. Driveファイル情報取得
4. Google Sheets追記
5. （その他のGoogle API呼び出しノード）

**各ノードの設定変更**:

#### Before（手動Bearer Token）:
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

#### After（OAuth2）:
```json
{
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "googleDriveOAuth2Api"
}
```

**UIでの変更手順**:
```
1. 各HTTP Requestノードをクリック
2. Credentialsセクションを開く
3. Authentication: "Predefined Credential Type" に変更
4. Credential Type: "Google Drive OAuth2 API" を選択
5. Credential for Google Drive OAuth2 API:
   作成した「Google Drive OAuth2」を選択
6. Saveをクリック
```

### Step 3.4: ノード接続を更新
```
Before:
アセットメタ整形 → Googleアクセストークン取得 → Driveファイル作成

After:
アセットメタ整形 → Driveファイル作成
```

### Step 3.5: ワークフロー保存
```
1. 右上の「Save」をクリック
2. 変更を確認
```

---

## 🎯 実装フェーズ4: テスト実行（10分）

### Step 4.1: Notionテストページ準備
```
Notion Database: 記事管理データベース
必須プロパティ:
- Article ID: oauth-test-001
- Status: Draft
- Asset Tags: test,mountain,sunset
```

### Step 4.2: Webhook実行
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "oauth-test-001",
    "notionPageId": "[ページIDをここに]",
    "assetTags": "test,mountain,sunset"
  }'
```

### Step 4.3: 期待される結果
```json
{
  "status": "success",
  "articleId": "oauth-test-001",
  "assets": [
    {
      "url": "https://drive.google.com/file/d/[FILE_ID1]/view",
      "type": "image",
      "filename": "oauth-test-001_asset1.jpg"
    },
    {
      "url": "https://drive.google.com/file/d/[FILE_ID2]/view",
      "type": "image",
      "filename": "oauth-test-001_asset2.jpg"
    },
    {
      "url": "https://drive.google.com/file/d/[FILE_ID3]/view",
      "type": "image",
      "filename": "oauth-test-001_asset3.jpg"
    }
  ],
  "notionStatus": "AssetsReady"
}
```

### Step 4.4: 検証項目
- [ ] Webhookが200 OKを返す
- [ ] Google Driveに3つの画像ファイルが作成される
- [ ] Google Sheetsに記録が追加される（オプション）
- [ ] Notion Statusが「AssetsReady」に更新される
- [ ] エラーログがない

---

## 🚨 トラブルシューティング

### エラー1: redirect_uri_mismatch
```
原因: Google Cloud ConsoleのリダイレクトURIが不正
確認:
1. https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback
2. 末尾のスラッシュなし
3. httpではなくhttps

解決策:
Google Cloud Console → 認証情報 → OAuth 2.0 クライアント ID
→ URIを修正 → 保存
```

### エラー2: invalid_client
```
原因: クライアントIDまたはシークレットが不正
確認:
1. n8n認証情報のClient IDとSecretを再確認
2. Google Cloud Consoleの値と一致するか

解決策:
n8n Credentials → 編集 → 正しい値を入力 → 再接続
```

### エラー3: access_denied
```
原因: OAuth同意画面で拒否、またはスコープ不足
確認:
1. Google Drive APIとSheets APIが有効か
2. OAuth同意画面のステータス（Testing/Production）

解決策:
- Testing状態の場合: テストユーザーを追加
- Production公開を検討
```

### エラー4: Token has been expired or revoked
```
原因: OAuth同意画面が「Testing」状態で7日間経過
確認:
Google Cloud Console → OAuth同意画面 → ステータス確認

解決策:
オプションA: Production に公開
オプションB: 7日ごとに再認証
オプションC: テストユーザーを維持
```

---

## 📊 成功基準

### 最小限の成功基準
- [ ] n8n OAuth2認証情報が「Connected」状態
- [ ] Webhookテストが成功（200 OK）
- [ ] Google Driveにファイルが作成される

### 完全な成功基準
- [ ] すべてのGoogle API呼び出しが成功
- [ ] エラーログがゼロ
- [ ] Notionページが正しく更新される
- [ ] パフォーマンス: <10秒で完了

### 長期的成功基準
- [ ] 7日後もトークンが有効（Production公開の場合）
- [ ] 複数ユーザーでの動作確認
- [ ] エラー率 <0.1%

---

## 📝 実装後の確認事項

### セキュリティ
- [ ] OAuth Client Secretは環境変数に保存されていない（n8nが管理）
- [ ] サービスアカウントJSONキーファイルを削除（使用しない場合）
- [ ] .gitignoreに認証情報ファイルが含まれているか確認

### ドキュメント
- [ ] 実装手順を記録
- [ ] OAuth認証情報IDをプロジェクトドキュメントに記録
- [ ] トラブルシューティング結果を記録

### モニタリング
- [ ] Railway logsでエラー監視を設定
- [ ] OAuth token更新の自動化を確認（n8nが自動処理）
- [ ] Google API使用量を監視

---

## 🎯 次のステップ

### 即座に実行（今日）
1. ✅ Railway環境変数確認 - 完了
2. ⏳ Google Cloud Console OAuth設定 - 実行待ち
3. ⏳ n8n OAuth2認証情報作成 - 実行待ち
4. ⏳ WF7ワークフロー更新 - 実行待ち
5. ⏳ テスト実行 - 実行待ち

### 今週中に実行
- [ ] 本番データでの動作確認
- [ ] エラーハンドリングの強化
- [ ] OAuth同意画面をProductionに公開（推奨）

### 来週以降
- [ ] パフォーマンスモニタリング
- [ ] 他のワークフローへのOAuth適用検討
- [ ] Google Sheets Native Nodeへの移行検討

---

## 📚 参照ドキュメント

- [Railway OAuth完全ガイド](./railway-google-oauth-complete-guide.md)
- [WF7 Google認証修正ガイド](./wf7-google-auth-fix-guide.md)
- [WF7 クイック修正チェックリスト](./wf7-google-auth-quick-fix.md)

---

**最終更新**: 2025-11-05 11:30 JST
**ステータス**: Railway環境変数確認完了、実装準備完了
**次のアクション**: Google Cloud Console OAuth設定を開始
