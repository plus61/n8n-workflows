# WF7 Phase4c テスト実行ガイド（簡易版）

**作成日**: 2025-11-09  
**対象ワークフロー**: `WF7 Phase4 - V3 Fixed_final` (ID: `r9Sp5n0mkUCcH8cw`)  
**目的**: Phase4cの動作確認を迅速に実施

---

## 🚀 クイックスタート

### Step 1: ワークフローを開く

1. ブラウザで `https://n8n-python-production-344b.up.railway.app/` にアクセス
2. ワークフロー **"WF7 Phase4 - V3 Fixed_final"** (ID: `r9Sp5n0mkUCcH8cw`) を開く

### Step 2: Pin Dataを設定

**対象ノード**: `IF - Phase4b Success Check` の**True分岐**（`Code - Phase4c FFmpeg Concat`の前）

1. `IF - Phase4b Success Check` ノードをクリック
2. 右側の設定パネルで **"Pin Data"** タブを選択
3. 以下のテストデータをコピー&ペースト：

```json
[
  {
    "json": {
      "script_id": "test-script-phase4c-001",
      "articleId": "test-article-001",
      "success": true,
      "phase4b_success": true,
      "videos_count": 7,
      "total_duration": 80,
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

4. **"Save"** をクリック

### Step 3: テスト実行

#### 方法A: ノード単位で実行（推奨）

1. `Code - Phase4c FFmpeg Concat` ノードをクリック
2. 設定パネル下部の **"Execute Node"** をクリック
3. 実行結果を確認

#### 方法B: ワークフロー全体を実行

1. 右上の **"Test workflow"** ボタンをクリック
2. 実行履歴で各ノードの結果を確認

---

## ✅ 確認ポイント

### Code - Phase4c FFmpeg Concat

**期待される出力**:
```json
{
  "success": true,
  "script_id": "test-script-phase4c-001",
  "output_video_path": "/tmp/wf7_phase4c_xxx/final_video_xxx.mp4",
  "output_video_size": 15728640,
  "total_duration": 80,
  "videos_count": 7,
  "temp_dir": "/tmp/wf7_phase4c_xxx"
}
```

**確認項目**:
- ✅ `success: true`
- ✅ `output_video_path` が設定されている
- ✅ `output_video_size` が0より大きい
- ✅ `total_duration` が80秒

### Code - Read Video Binary

**確認項目**:
- ✅ `binary.data` が設定されている（Base64エンコードされた動画データ）

### Google Drive - Upload Final Video

**確認項目**:
- ✅ `webViewLink` が設定されている
- ✅ Google Driveに動画がアップロードされている

### Notion - Update Script Record

**確認項目**:
- ✅ HTTP 200 OKが返されている
- ✅ Notion DBの`Status`が`Rendered`に更新されている

### Code - Cleanup Temp Files

**確認項目**:
- ✅ `cleanup_success: true` が返されている

---

## ⚠️ よくあるエラーと対処法

### エラー1: 動画ダウンロード失敗

**エラーメッセージ**: `RuntimeError: 動画ダウンロード失敗`

**対処法**:
1. 動画URLが有効か確認（ブラウザで直接アクセス）
2. `curl`コマンドがn8nサーバーで利用可能か確認
3. タイムアウト時間を延長（現在120秒）

### エラー2: FFmpeg結合失敗

**エラーメッセージ**: `RuntimeError: FFmpeg結合失敗`

**対処法**:
1. FFmpegがn8nサーバーにインストールされているか確認
2. 動画ファイルの形式を確認（MP4形式であることを確認）
3. 動画ファイルが破損していないか確認

### エラー3: Google Driveアップロード失敗

**エラーメッセージ**: `403 Forbidden` または `Invalid value for 'operation'`

**対処法**:
1. Google Drive OAuth2認証を再実行
2. `binaryData: true` と `binaryPropertyName: "data"` が設定されているか確認

### エラー4: Notion DB更新失敗

**エラーメッセージ**: `400 Bad Request` または `404 Not Found`

**対処法**:
1. `script_id`が有効なNotionページIDか確認
2. Notion API認証情報を確認
3. プロパティ名が正確か確認（`Status`, `Video URL`）

---

## 📊 テスト結果記録

テスト実行後、以下の情報を記録してください：

```yaml
テスト実行日時: 2025-11-09 HH:MM:SS
ワークフローID: r9Sp5n0mkUCcH8cw

実行結果:
  ✅ Code - Phase4c FFmpeg Concat: PASS / FAIL
  ✅ Code - Read Video Binary: PASS / FAIL
  ✅ Google Drive - Upload Final Video: PASS / FAIL
  ✅ Notion - Update Script Record: PASS / FAIL
  ✅ Code - Cleanup Temp Files: PASS / FAIL
  ✅ Respond to Webhook: PASS / FAIL

実行時間:
  - 動画ダウンロード: X秒
  - FFmpeg結合: Y秒
  - Google Driveアップロード: Z秒
  - Notion更新: W秒
  合計実行時間: T秒

最終動画:
  URL: https://drive.google.com/...
  ファイルサイズ: XX MB
  再生時間: XX秒

エラー:
  - [エラー詳細を記録]

備考:
  - [その他の気づき]
```

---

## 🔗 関連ドキュメント

- `docs/testing/WF7-Phase4c-テスト実行手順.md`: 詳細なテスト手順
- `docs/testing/wf7-phase4c-e2e-test-execution-guide.md`: E2Eテストガイド
- `test-phase4b-pindata-for-phase4c.json`: テストデータファイル

---

**次のステップ**: テスト実行後、結果を記録し、エラーがあれば対処してください。

