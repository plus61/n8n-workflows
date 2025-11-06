# WF7 Phase2 OAuth版 クイックリファレンス

**対象**: WF7 Phase2 (OAuth版) 検証用
**Webhook URL**: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google`

---

## 🚀 即座に実行可能なテストコマンド

### テストケース1: 既存ページを使用（推奨）

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-meo-001",
    "notionPageId": "29e68d5c-2986-81c7-a260-cf9084f8d864",
    "assetTags": "opening,problem,solution,cta"
  }'
```

**ページ情報**:
- Page ID: `29e68d5c-2986-81c7-a260-cf9084f8d864`
- Article ID: `test-meo-001`
- Database: `29b68d5c-2986-817f-b4e6-f84cf75ea9ed`
- ステータス: `AssetsReady` (既存データあり)

---

### テストケース2: Phase4統合テストページ

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "integration-test-001",
    "notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9",
    "assetTags": "opening,problem,solution,cta"
  }'
```

**ページ情報**:
- Page ID: `2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9`
- Article ID: `integration-test-001`
- タイトル: "Phase1→Phase4統合テスト記事"

---

## 📋 入力データ形式

### 必須パラメータ

| パラメータ | 型 | 説明 | 例 |
|-----------|---|------|---|
| `articleId` | string | 記事識別子 | `test-meo-001` |
| `notionPageId` | string | NotionページID (UUID形式) | `29e68d5c-2986-81c7-a260-cf9084f8d864` |
| `assetTags` | string | カンマ区切りのアセットタグ | `opening,problem,solution,cta` |

### JSON形式

```json
{
  "articleId": "<記事ID>",
  "notionPageId": "<NotionページID>",
  "assetTags": "<カンマ区切りタグ>"
}
```

---

## 🔍 ページIDの取得方法

### Notion URLから取得

1. Notionでページを開く
2. URLを確認:
   ```
   https://www.notion.so/[TITLE]-[PAGE_ID]
   ```
3. 最後の部分（ハイフン区切りのUUID）をコピー

**例**:
```
https://www.notion.so/WF7-Phase2-OAuth-test-2a068d5c298681a3ab0cff0bc1e4ebb9
                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^
                                                      ↑ これをコピー
```

**コピーする値**: `2a068d5c298681a3ab0cff0bc1e4ebb9`

**注意**: URLではハイフンが省略される場合があるため、32文字の16進数文字列を取得し、以下の形式に変換:
```
2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9
```

---

## ✅ 新規テストページ作成手順

### Step 1: Notionでページ作成

1. データベースを開く: `29b68d5c-2986-817f-b4e6-f84cf75ea9ed`
2. 「新規」をクリック
3. プロパティを設定:
   - **Title**: "WF7 Phase2 OAuthテスト"
   - **Article ID**: `phase2-oauth-test-001`
   - **Status**: `Draft`
4. ページを保存

### Step 2: ページIDを取得

1. ページURLを確認
2. ページIDをコピー（上記の方法を参照）

### Step 3: Webhook実行

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "phase2-oauth-test-001",
    "notionPageId": "<Step 2で取得したページID>",
    "assetTags": "opening,problem,solution,cta"
  }'
```

---

## 🎯 推奨アセットタグ

### 標準4セグメント動画用

```
opening,problem,solution,cta
```

### 英語タグ（検索性能が高い）

```
business,office,meeting,team,success,growth,technology,future,innovation
```

### 日本語タグ（検索性能が低い可能性）

```
ビジネス,オフィス,会議,チーム,成功,成長,テクノロジー,未来,イノベーション
```

**注意**: 日本語タグはPexels/Unsplash検索でマッチ率が低い可能性があります。

---

## 🔍 実行結果の確認方法

### 1. Railway Logsで確認

```bash
railway logs --tail 50
```

**確認ポイント**:
- ✅ `200 OK` レスポンス
- ✅ Google Drive API呼び出し成功
- ✅ Notion更新成功

### 2. Notionページで確認

1. テストページを開く
2. 以下のプロパティを確認:
   - **Status**: `AssetsReady` に更新されているか
   - **Assets**: JSONが記録されているか
   - **Error Message**: エラーがないか

### 3. 期待されるAssets JSON構造

```json
{
  "images": [
    {
      "tag": "opening",
      "url": "https://drive.google.com/...",
      "source": "google_drive",
      "width": 1080,
      "height": 1920
    },
    {
      "tag": "problem",
      "url": "https://drive.google.com/...",
      "source": "google_drive",
      "width": 1080,
      "height": 1920
    }
  ],
  "totalAssets": 4
}
```

---

## ⚠️ トラブルシューティング

### エラー: `GOOGLE_APPLICATION_CREDENTIALS_JSON is not set`
**原因**: 環境変数未設定  
**解決策**: Railway環境変数に `GOOGLE_APPLICATION_CREDENTIALS_JSON` を設定

### エラー: `Failed to obtain Google access token`
**原因**: JSON形式エラーまたはサービスアカウント無効  
**解決策**: `wf7-google-auth-fix-guide.md` を参照

### エラー: `invalid_grant`
**原因**: サービスアカウントが無効  
**解決策**: Google Cloud Consoleでサービスアカウントを再作成

### エラー: `unauthorized_client`
**原因**: APIが無効化されている  
**解決策**: Google Cloud ConsoleでAPIを有効化

### エラー: `insufficient_permissions`
**原因**: ロールが不足  
**解決策**: サービスアカウントに適切なロールを付与

---

## 📚 関連ドキュメント

- `wf7-phase2-test-data-collection-report.md` - 詳細なテストデータ収集レポート
- `wf7-phase2-test-input-samples.json` - テスト入力サンプルJSON
- `wf7-google-auth-fix-guide.md` - Google認証エラー修正ガイド
- `phase2-google-drive-test-plan.md` - Phase2 Google Drive統合テスト計画

---

**最終更新**: 2025-11-05

