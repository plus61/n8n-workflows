# WF7 Phase4 テストセットアップガイド

## 📋 テスト用データの準備

### 1. テスト用JSONファイルの作成

以下の2つのJSONファイルが作成されました：
- `test-script.json` - スクリプトデータ（segments情報）
- `test-assets.json` - アセットデータ（Google DriveファイルID）

### 2. Notionページへのデータ設定

#### 方法A: Rich Textプロパティに直接設定（推奨）

1. **Notionでページを開く**
   - 既存のページ: `2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9`
   - または新しいページを作成

2. **プロパティを追加/編集**
   - `Script JSON` プロパティ（Rich Text型）に以下を貼り付け：
   ```json
   {
     "segments": [
       {
         "duration": 5,
         "telop": "テスト動画1"
       },
       {
         "duration": 5,
         "telop": "テスト動画2"
       },
       {
         "duration": 5,
         "telop": "テスト動画3"
       },
       {
         "duration": 5,
         "telop": "テスト動画4"
       }
     ]
   }
   ```

   - `Assets JSON` プロパティ（Rich Text型）に以下を貼り付け：
   ```json
   {
     "assets": [
       {
         "driveFileId": "1t3BFRFgHMLYhmfp9BobiNhdK3DlUhUaC",
         "assetTag": "test_asset_1"
       },
       {
         "driveFileId": "1qyNTS3pX21H_EM6myRt9cvMBM5G1RDf7",
         "assetTag": "test_asset_2"
       },
       {
         "driveFileId": "1d4PlR2_JcXvLXVB38jyU5zdzbAE-KgQd",
         "assetTag": "test_asset_3"
       },
       {
         "driveFileId": "1M_otlP9GkT2jKqr8uZL5HgtRWuSYO5Ex",
         "assetTag": "test_asset_4"
       }
     ]
   }
   ```

   - `Article ID` プロパティ（Rich Text型）に以下を入力：
   ```
   test-phase4-001
   ```

#### 方法B: URLプロパティにJSONファイルのURLを設定

1. JSONファイルを公開できる場所にアップロード（例：GitHub Gist、Google Drive、一時的なファイルホスティング）
2. `Script JSON` プロパティ（URL型）にJSONファイルのURLを設定
3. `Assets JSON` プロパティ（URL型）にJSONファイルのURLを設定

### 3. Google DriveファイルIDの確認

テスト用のDriveファイルIDが存在しない場合は、以下を実行：

1. Google Driveにテスト用画像を4枚アップロード
2. 各ファイルの共有リンクからファイルIDを取得
3. `test-assets.json`の`driveFileId`を実際のファイルIDに置き換え

**ファイルIDの取得方法**:
- Google Driveでファイルを右クリック → 「リンクを取得」
- URL例: `https://drive.google.com/file/d/1t3BFRFgHMLYhmfp9BobiNhdK3DlUhUaC/view`
- ファイルID: `1t3BFRFgHMLYhmfp9BobiNhdK3DlUhUaC`（`/d/`と`/view`の間）

## 🚀 テスト実行

### ステップ1: NotionページIDを確認

NotionページのURLからページIDを取得：
```
https://www.notion.so/ページタイトル-2a068d5c298681a3ab0cff0bc1e4ebb9
                                 ↑この部分がページID（ハイフン付き）
```

### ステップ2: ワークフローを実行

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{"notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}'
```

### ステップ3: 実行結果を確認

```bash
# 最新の実行を確認
# n8nのUIで確認するか、MCPツールを使用
```

## 📝 期待される動作

1. **Webhook受信**: リクエストを受信
2. **Notionデータ取得**: ページからScript JSONとAssets JSONを取得
3. **Google Drive情報取得**: 各アセットのDriveファイル情報を取得
4. **FAL API送信**: 動画生成リクエストをFAL APIに送信
5. **ステータス確認**: ポーリングでステータスを確認（最大300秒待機）
6. **動画ダウンロード**: 完成した動画をダウンロード
7. **Google Driveアップロード**: 動画をDriveにアップロード
8. **Notion更新**: ページのStatusを「VideoReady」に更新

## ⚠️ 注意事項

- Google DriveファイルIDは実際に存在するファイルを指定してください
- タイムアウト設定は300秒（5分）に延長されています
- リトライ回数は20回に設定されています
- FAL APIの処理時間によっては、数分かかる場合があります

## 🔍 トラブルシューティング

### エラー: Script JSON not found
→ Notionページの`Script JSON`プロパティを確認してください

### エラー: Assets JSON not found
→ Notionページの`Assets JSON`プロパティを確認してください

### エラー: Invalid Drive File ID
→ Google DriveファイルIDが正しいか確認してください

### タイムアウトエラー
→ FAL APIの処理が長引いている可能性があります。リトライが自動的に実行されます。





