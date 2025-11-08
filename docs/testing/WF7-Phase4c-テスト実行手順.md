# WF7 Phase4c テスト実行手順

**作成日**: 2025-11-08  
**対象ワークフロー**: `WF7 Phase4 - V3 Fixed_final` (ID: `r9Sp5n0mkUCcH8cw`)  
**目的**: Phase4c（FFmpeg動画結合）の動作確認

---

## 📋 テスト概要

Phase4bで生成された7本の動画をFFmpegで結合し、Google Driveにアップロード、Notion DBを更新するPhase4c処理をテストします。

### テスト対象ノード

1. `Code - Phase4c FFmpeg Concat`: 7本の動画をダウンロードしてFFmpegで結合
2. `Code - Read Video Binary`: 結合した動画をバイナリデータとして読み込み
3. `Google Drive - Upload Final Video`: Google Driveにアップロード
4. `Notion - Update Script Record`: Notion DBの`Status`と`Video URL`を更新
5. `Code - Cleanup Temp Files`: 一時ファイルを削除
6. `Respond to Webhook`: Webhook応答を返す

---

## 🎯 前提条件

### 必要な設定

- [ ] n8n UIにアクセス可能: `https://n8n-python-production-344b.up.railway.app/`
- [ ] ワークフローID `r9Sp5n0mkUCcH8cw` が存在し、アクティブ
- [ ] Google Drive OAuth2認証が設定済み
- [ ] Notion API認証が設定済み
- [ ] FFmpegがn8nサーバーにインストールされている
- [ ] `curl`コマンドがn8nサーバーで利用可能

### テストデータの準備

Phase4b完了後のデータ形式で、以下のフィールドが必要です：

- `script_id`: NotionページID（文字列）
- `articleId`: 記事ID（文字列、オプション）
- `videos_metadata`: 7本の動画メタデータ配列
  - `section`: セクション名（hook, intro, point1, point2, point3, summary, cta）
  - `duration`: 動画の長さ（秒）
  - `video_url`: 動画のURL

---

## 🚀 テスト実行手順

### 方法1: n8n UIでノードを手動実行（推奨）

#### Step 1: ワークフローを開く

1. ブラウザで `https://n8n-python-production-344b.up.railway.app/` にアクセス
2. 左サイドバー → **"Workflows"** をクリック
3. **"WF7 Phase4 - V3 Fixed_final"** をクリック
4. ワークフローIDが `r9Sp5n0mkUCcH8cw` であることを確認

#### Step 2: Code - Phase4c FFmpeg Concatノードを開く

1. ワークフローエディタで **"Code - Phase4c FFmpeg Concat"** ノードを探す
2. ノードをクリックして選択
3. 右側の設定パネルが表示されることを確認

#### Step 3: Pin Dataを設定

1. 設定パネルで **"Pin Data"** タブを選択
2. 以下のテストデータをコピー&ペースト：

```json
[
  {
    "json": {
      "script_id": "test-script-phase4c-001",
      "articleId": "test-article-001",
      "videos_metadata": [
        {
          "section": "hook",
          "duration": 3,
          "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
        },
        {
          "section": "intro",
          "duration": 10,
          "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
        },
        {
          "section": "point1",
          "duration": 13,
          "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
        },
        {
          "section": "point2",
          "duration": 13,
          "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
        },
        {
          "section": "point3",
          "duration": 14,
          "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
        },
        {
          "section": "summary",
          "duration": 20,
          "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
        },
        {
          "section": "cta",
          "duration": 7,
          "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
        }
      ]
    }
  }
]
```

3. **"Save"** をクリックしてPin Dataを保存

#### Step 4: ノードを実行

1. 設定パネルの下部にある **"Execute Node"** ボタンをクリック
2. 実行結果を確認
3. エラーが発生していないことを確認

#### Step 5: 各ノードの実行結果を確認

1. **Code - Phase4c FFmpeg Concat**:
   - ✅ `success: true` が返されている
   - ✅ `output_video_path` が設定されている
   - ✅ `output_video_size` が0より大きい
   - ✅ `total_duration` が80秒（3+10+13+13+14+20+7）

2. **Code - Read Video Binary**:
   - ✅ `binary.data` が設定されている
   - ✅ Base64エンコードされた動画データが含まれている

3. **Google Drive - Upload Final Video**:
   - ✅ `webViewLink` が設定されている
   - ✅ Google Driveに動画がアップロードされている

4. **Notion - Update Script Record**:
   - ✅ HTTP 200 OKが返されている
   - ✅ Notion DBの`Status`が`Rendered`に更新されている
   - ✅ Notion DBの`Video URL`が更新されている

5. **Code - Cleanup Temp Files**:
   - ✅ `cleanup_success: true` が返されている

6. **Respond to Webhook**:
   - ✅ レスポンスが返されている
   - ✅ `success: true` が含まれている
   - ✅ `final_video_url` が設定されている

---

### 方法2: ワークフロー全体を実行（E2Eテスト）

#### Step 1: Webhookエンドポイントを確認

1. ワークフローエディタで **"Webhook"** ノードを確認
2. Webhook URLをコピー:
   ```
   https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script
   ```

#### Step 2: Phase4b完了後のデータでWebhookをトリガー

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{
    "notionPageId": "test-script-phase4c-001"
  }'
```

**注意**: 実際のテストでは、Phase4aとPhase4bが正常に完了した後のデータを使用してください。

#### Step 3: 実行結果を確認

1. n8n UIで実行履歴を確認
2. 各ノードが正常に実行されていることを確認
3. エラーノードがないことを確認

---

## ✅ 期待される結果

### 成功時の出力

**Code - Phase4c FFmpeg Concat**:
```json
{
  "success": true,
  "script_id": "test-script-phase4c-001",
  "output_video_path": "/tmp/wf7_phase4c_xxx/final_video_test-script-phase4c-001_1234567890.mp4",
  "output_video_size": 15728640,
  "total_duration": 80,
  "videos_count": 7,
  "temp_dir": "/tmp/wf7_phase4c_xxx",
  "articleId": "test-article-001"
}
```

**Google Drive - Upload Final Video**:
```json
{
  "id": "1xyz...abc",
  "name": "WF7_Final_test-script-phase4c-001_20251108_153045.mp4",
  "mimeType": "video/mp4",
  "webViewLink": "https://drive.google.com/file/d/1xyz...abc/view",
  "webContentLink": "https://drive.google.com/uc?id=1xyz...abc&export=download"
}
```

**Respond to Webhook**:
```json
{
  "success": true,
  "script_id": "test-script-phase4c-001",
  "final_video_url": "https://drive.google.com/file/d/1xyz...abc/view",
  "video_size_mb": 15.0,
  "total_duration": 80,
  "notion_updated": true
}
```

---

## ⚠️ トラブルシューティング

### 問題1: FFmpeg結合失敗

**症状**: `Code - Phase4c FFmpeg Concat`でエラーが発生

**原因**:
- FFmpegがインストールされていない
- 動画URLが無効
- 動画ファイルの形式が異なる

**解決方法**:
- n8nサーバーでFFmpegがインストールされているか確認
- 動画URLが有効か確認
- 動画ファイルの形式を確認（MP4形式であることを確認）

### 問題2: Google Driveアップロード失敗

**症状**: `Google Drive - Upload Final Video`でエラーが発生

**原因**:
- Google Drive認証情報が無効
- バイナリデータが正しく設定されていない

**解決方法**:
- Google Drive OAuth2認証情報を確認
- `binaryData: true` と `binaryPropertyName: "data"` が設定されているか確認

### 問題3: Notion DB更新失敗

**症状**: `Notion - Update Script Record`でエラーが発生

**原因**:
- Notion API認証情報が無効
- `script_id`が存在しない
- プロパティ名が間違っている

**解決方法**:
- Notion API認証情報を確認
- `script_id`が有効なNotionページIDか確認
- プロパティ名が正確か確認（`Status`, `Video URL`）

### 問題4: 一時ファイルのクリーンアップ失敗

**症状**: `Code - Cleanup Temp Files`でエラーが発生

**原因**:
- 一時ディレクトリが既に削除されている
- 権限の問題

**解決方法**:
- エラーは無視しても問題ない（処理は完了している）
- 必要に応じて手動でクリーンアップ

---

## 📝 テストチェックリスト

- [ ] `Code - Phase4c FFmpeg Concat`が正常に実行される
- [ ] 7本の動画がダウンロードされる
- [ ] FFmpegで動画が結合される
- [ ] `Code - Read Video Binary`が正常に実行される
- [ ] バイナリデータが正しく読み込まれる
- [ ] `Google Drive - Upload Final Video`が正常に実行される
- [ ] Google Driveに動画がアップロードされる
- [ ] `Notion - Update Script Record`が正常に実行される
- [ ] Notion DBの`Status`が`Rendered`に更新される
- [ ] Notion DBの`Video URL`が更新される
- [ ] `Code - Cleanup Temp Files`が正常に実行される
- [ ] 一時ファイルが削除される
- [ ] `Respond to Webhook`が正常に実行される
- [ ] Webhook応答が返される

---

## 🔗 関連ドキュメント

- `docs/implementation/WF7-Phase4bノード参照修正手順.md`: Phase4b修正手順
- `docs/testing/WF7-Phase4b-テストデータ作成ガイド.md`: Phase4b完了データの作成方法（**重要**）
- `docs/implementation/WF7-Phase4c-ClaudeCode実装指示書.md`: Phase4c実装指示書
- `docs/implementation/WF7-Phase4c-実装手順.md`: Phase4c実装手順書
- `workflows/wf7_phase4b_fixed_r9Sp5n0mkUCcH8cw.json`: 現在のワークフローJSON
- `test-phase4c-payload.json`: テストデータサンプル

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08  
**次のステップ**: テスト実行後、結果をドキュメントに反映

