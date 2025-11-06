# Google Drive OAuth2 初回設定ガイド

## 目的
WF7 Phase2 Google Drive統合テストのためのOAuth2認証情報を初めて作成します。

## 前提条件
- n8n UIへのアクセス権限
- Google Cloud Platformプロジェクト（OAuth2クライアント作成済み）
- Railway n8nインスタンス: https://n8n-python-production-344b.up.railway.app

---

## 手順1: n8n UIアクセス

1. ブラウザで以下にアクセス：
   ```
   https://n8n-python-production-344b.up.railway.app
   ```

2. ログイン認証情報を入力してログイン

---

## 手順2: 認証情報作成

1. 左サイドバーの **「Credentials」** をクリック

2. 右上の **「Add Credential」** ボタンをクリック

3. 検索ボックスに「Google Drive」と入力

4. **「Google Drive OAuth2 API」** を選択

---

## 手順3: OAuth2設定

### 必須フィールド
- **Credential Name**: `Google Drive OAuth2 account` （既存の名前に合わせる）
- **Client ID**: Google Cloud Platformから取得
- **Client Secret**: Google Cloud Platformから取得
- **OAuth Redirect URL**: n8nが自動生成（コピーしてGoogle Cloud Platformに登録）

### 認証フロー
1. **「Connect my account」** ボタンをクリック
2. Googleアカウント選択画面が表示される
3. Google Driveアクセス権限を承認
4. 認証完了後、n8nに戻る

---

## 手順4: 認証情報ID確認

1. 作成した認証情報をクリック

2. URLから認証情報IDを確認：
   ```
   https://n8n-python-production-344b.up.railway.app/credentials/[ID]
   ```

3. **重要**: このIDをメモする（例: "39"）

---

## 手順5: ワークフロー更新（必要な場合のみ）

もし認証情報IDが"39"と異なる場合：

1. WF7 Phase4ワークフローを開く

2. 「Drive画像取得」ノードを選択

3. Credentialsドロップダウンから新しく作成した認証情報を選択

4. **「Save」** をクリック

---

## 手順6: テスト実行

### Notionテストページ準備
```json
{
  "Article ID": "gdrive-test-001",
  "Assets JSON": {
    "assets": [
      {
        "assetIndex": 0,
        "assetTag": "opening",
        "driveFileId": "1dQzmNOmUVkvDSogyiT8HHvQ2C3rlwIQs"
      },
      {
        "assetIndex": 1,
        "assetTag": "problem",
        "driveFileId": "1d4PlR2_JcXvLXVB38jyU5zdzbAE-KgQd"
      },
      {
        "assetIndex": 2,
        "assetTag": "solution",
        "driveFileId": "1M_otlP9GkT2jKqr8uZL5HgtRWuSYO5Ex"
      },
      {
        "assetIndex": 3,
        "assetTag": "cta",
        "driveFileId": "1qyNTS3pX21H_EM6myRt9cvMBM5G1RDf7"
      }
    ]
  }
}
```

### Webhook実行
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4-render \
  -H "Content-Type: application/json" \
  -d '{"notionPageId": "[NotionページID]"}'
```

---

## 成功基準

✅ 認証情報が正常に作成され、緑のチェックマーク表示
✅ Webhook実行後、エラーなく完了
✅ Railway logsに「Drive画像取得」ノードの成功ログ
✅ 4つの画像ファイルが `/tmp/asset_gdrive-test-001_*.jpg` に保存
✅ Notionページの Status が "Rendered" に更新

---

## トラブルシューティング

### エラー: "OAuth2 authentication failed"
**原因**: Google Cloud PlatformのOAuth設定が不完全
**解決策**:
1. Google Cloud PlatformでリダイレクトURIを確認
2. n8nのOAuth Redirect URLが正しく登録されているか確認

### エラー: "File not found" (404)
**原因**: driveFileIdが無効、またはアクセス権限なし
**解決策**:
1. Google Driveでファイルの共有設定を確認
2. OAuth2アカウントがファイルにアクセスできるか確認

### エラー: "Insufficient permissions"
**原因**: OAuth2スコープが不足
**解決策**:
1. Google Cloud Platformでスコープを確認
2. 必要スコープ: `https://www.googleapis.com/auth/drive.readonly`

---

## 関連ドキュメント
- [Phase2 Google Drive統合テスト計画](/Users/yuichiroooosuger/Desktop/n8n-workflows/docs/testing/phase2-google-drive-test-plan.md)
- [Google Drive OAuth2公式ドキュメント](https://developers.google.com/drive/api/guides/about-auth)
