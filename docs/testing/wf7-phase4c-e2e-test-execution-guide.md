# WF7 Phase4c E2Eテスト実行ガイド

**作成日**: 2025-11-08  
**ワークフローID**: `chPw11OY5sex6d9I`  
**ワークフロー名**: WF7 Phase4c - Perfect Implementation  
**目的**: Phase4cワークフローのE2Eテストを実施し、7本の動画を結合してGoogle Driveにアップロード、Notion DBを更新する処理を検証

---

## 📋 テスト前提条件

### 1. 認証情報の確認

以下の認証情報がn8nに設定されていることを確認：

- ✅ **FAL API Key** (Header Auth)
  - Credential ID: `voV5kURaCkiUjLTZ`
  - Header Name: `Authorization`
  - Value: `Key YOUR_FAL_API_KEY`

- ✅ **Google Drive OAuth2**
  - Credential ID: `plniYONxQ1iPNoAi`
  - アップロード先フォルダへのアクセス権限あり

- ✅ **Notion API**
  - Credential ID: `y89xQdP2gCTcdyup`
  - 対象データベースへのアクセス権限あり

### 2. ワークフローの状態確認

- ワークフローURL: `https://n8n-python-production-344b.up.railway.app/workflow/chPw11OY5sex6d9I`
- 現在の状態: `active: false` (手動実行のみ可能)

---

## 🧪 E2Eテスト実行手順

### Step 1: テストデータの準備

Phase4bの出力を模擬した7本の動画URLデータを準備します。

**テストデータファイル**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/test-phase4c-mock-data.json`

**Pin Data用JSON形式**:
```json
[
  {
    "section": "hook",
    "duration": 3,
    "video_url": "https://fal.media/files/lion/test-video-hook-3s.mp4",
    "order": 1,
    "script_id": "test-script-001"
  },
  {
    "section": "intro",
    "duration": 10,
    "video_url": "https://fal.media/files/lion/test-video-intro-10s.mp4",
    "order": 2,
    "script_id": "test-script-001"
  },
  {
    "section": "point1",
    "duration": 13,
    "video_url": "https://fal.media/files/lion/test-video-point1-13s.mp4",
    "order": 3,
    "script_id": "test-script-001"
  },
  {
    "section": "point2",
    "duration": 13,
    "video_url": "https://fal.media/files/lion/test-video-point2-13s.mp4",
    "order": 4,
    "script_id": "test-script-001"
  },
  {
    "section": "point3",
    "duration": 13,
    "video_url": "https://fal.media/files/lion/test-video-point3-13s.mp4",
    "order": 5,
    "script_id": "test-script-001"
  },
  {
    "section": "summary",
    "duration": 20,
    "video_url": "https://fal.media/files/lion/test-video-summary-20s.mp4",
    "order": 6,
    "script_id": "test-script-001"
  },
  {
    "section": "cta",
    "duration": 7,
    "video_url": "https://fal.media/files/lion/test-video-cta-7s.mp4",
    "order": 7,
    "script_id": "test-script-001"
  }
]
```

**注意**: 上記URLはモックデータです。実際のテストには、Phase4bで生成された有効なFAL動画URLが必要です。

### Step 2: n8n UIでのテスト実行

1. **ワークフローを開く**
   - URL: `https://n8n-python-production-344b.up.railway.app/workflow/chPw11OY5sex6d9I`
   - n8n UIにログイン

2. **Pin Dataの設定**
   - `When clicking 'Test workflow'` (Manual Trigger) ノードを選択
   - 右サイドバー → **"Pin Data"** タブを開く
   - 上記のテストデータJSONを貼り付け
   - **"Save"** をクリック

3. **ワークフローの実行**
   - 右上の **"Test workflow"** ボタンをクリック
   - または、Manual Triggerノードの **"Execute Node"** をクリック

### Step 3: 各ノードの実行結果確認

#### 3.1 Aggregate Videos ノード

**期待される出力**:
```json
{
  "video_url": [
    "https://fal.media/files/lion/test-video-hook-3s.mp4",
    "https://fal.media/files/lion/test-video-intro-10s.mp4",
    "https://fal.media/files/lion/test-video-point1-13s.mp4",
    "https://fal.media/files/lion/test-video-point2-13s.mp4",
    "https://fal.media/files/lion/test-video-point3-13s.mp4",
    "https://fal.media/files/lion/test-video-summary-20s.mp4",
    "https://fal.media/files/lion/test-video-cta-7s.mp4"
  ],
  "script_id": "test-script-001"
}
```

**確認ポイント**:
- ✅ 7本の動画URLが配列として集約されている
- ✅ script_idが含まれている

#### 3.2 ペイロード構築 ノード

**期待される出力**:
```json
{
  "inputs": [
    {"type": "video", "url": "https://fal.media/files/lion/test-video-hook-3s.mp4"},
    {"type": "video", "url": "https://fal.media/files/lion/test-video-intro-10s.mp4"},
    {"type": "video", "url": "https://fal.media/files/lion/test-video-point1-13s.mp4"},
    {"type": "video", "url": "https://fal.media/files/lion/test-video-point2-13s.mp4"},
    {"type": "video", "url": "https://fal.media/files/lion/test-video-point3-13s.mp4"},
    {"type": "video", "url": "https://fal.media/files/lion/test-video-summary-20s.mp4"},
    {"type": "video", "url": "https://fal.media/files/lion/test-video-cta-7s.mp4"}
  ],
  "output_format": "mp4",
  "concat_method": "concat",
  "video_codec": "h264",
  "audio_codec": "aac"
}
```

**確認ポイント**:
- ✅ FAL FFmpeg API /compose形式のペイロードが構築されている
- ✅ 7本の動画が正しい順序で含まれている

#### 3.3 Submit to FAL ノード

**期待される出力**:
```json
{
  "request_id": "fal-ai-ffmpeg-api-xxxxxxxxxxxx",
  "status_url": "https://queue.fal.run/fal-ai/ffmpeg-api/compose/requests/fal-ai-ffmpeg-api-xxxxxxxxxxxx/status"
}
```

**確認ポイント**:
- ✅ FAL APIへのリクエストが成功している
- ✅ request_idが返されている

**エラー時の対処**:
- `401 Unauthorized`: FAL APIキーを確認
- `422 Unprocessable Entity`: 動画URLが有効か確認

#### 3.4 Wait for Processing ノード

**動作**: 10秒間待機

**確認ポイント**:
- ✅ 10秒待機後に次のノードに進む

#### 3.5 Fetch Status ノード

**期待される出力** (最終的に):
```json
{
  "status": "COMPLETED",
  "output": {
    "video": {
      "url": "https://fal.media/files/lion/rendered-final-video.mp4",
      "content_type": "video/mp4",
      "file_size": 12345678
    }
  }
}
```

**確認ポイント**:
- ✅ ステータスが `COMPLETED` になるまでポーリング
- ✅ 完成動画のURLが取得できる

**エラー時の対処**:
- `status: "PROCESSING"`: さらに待機が必要（最大20回リトライ）
- `status: "FAILED"`: Error Handlerに進む

#### 3.6 Render Completed? ノード

**期待される動作**:
- `status === "COMPLETED"` → True分岐 → Download Video
- `status !== "COMPLETED"` → False分岐 → Error Handler

**確認ポイント**:
- ✅ 条件分岐が正しく動作している

#### 3.7 Download Video ノード

**期待される出力**:
- Binary data: 動画ファイルのバイナリデータ

**確認ポイント**:
- ✅ 動画ファイルがダウンロードされている
- ✅ Binary property名が `data` になっている

#### 3.8 Upload to Google Drive ノード

**期待される出力**:
```json
{
  "id": "xxxxxxxxxxxxxxxxxxxxx",
  "name": "WF7_Final_test-script-001_20251108_123456.mp4",
  "webViewLink": "https://drive.google.com/file/d/xxxxxxxxxxxxxxxxxxxxx/view",
  "webContentLink": "https://drive.google.com/uc?id=xxxxxxxxxxxxxxxxxxxxx&export=download"
}
```

**確認ポイント**:
- ✅ Google Driveに動画がアップロードされている
- ✅ ファイル名が正しい形式になっている
- ✅ webViewLinkが取得できる

**エラー時の対処**:
- `403 Forbidden`: Google Drive OAuth2認証を再実行
- `404 Not Found`: フォルダIDを確認

#### 3.9 Update Notion DB ノード

**期待される動作**:
- Notion Page ID `test-script-001` のプロパティを更新
- Status: `VideoReady` または `completed`
- Video URL: Google DriveのwebViewLink

**確認ポイント**:
- ✅ Notion DBが更新されている
- ✅ ステータスが正しく変更されている
- ✅ 動画URLが記録されている

**エラー時の対処**:
- `400 Bad Request`: pageId (script_id) が有効か確認
- `401 Unauthorized`: Notion APIトークンを確認

#### 3.10 Respond to Webhook ノード

**期待される出力**:
```json
{
  "success": true,
  "message": "Phase4c completed",
  "final_video_url": "https://drive.google.com/file/d/xxxxxxxxxxxxxxxxxxxxx/view"
}
```

**確認ポイント**:
- ✅ 成功レスポンスが返されている
- ✅ final_video_urlが含まれている

---

## 📊 テスト結果記録

### テスト実行記録テンプレート

```yaml
テスト実行日時: 2025-11-08 HH:MM:SS
テスト種別: E2Eテスト
ワークフローID: chPw11OY5sex6d9I

実行結果:
  ✅ Aggregate Videos: PASS / FAIL
  ✅ ペイロード構築: PASS / FAIL
  ✅ Submit to FAL: PASS / FAIL
  ✅ Wait for Processing: PASS / FAIL
  ✅ Fetch Status: PASS / FAIL
  ✅ Render Completed?: PASS / FAIL
  ✅ Download Video: PASS / FAIL
  ✅ Upload to Google Drive: PASS / FAIL
  ✅ Update Notion DB: PASS / FAIL
  ✅ Respond to Webhook: PASS / FAIL

実行時間:
  - FAL Submit: X秒
  - レンダリング待機: Y秒
  - ステータスポーリング: Z秒
  - ダウンロード: W秒
  - Google Driveアップロード: V秒
  - Notion更新: U秒
  合計実行時間: T秒

最終動画:
  URL: https://drive.google.com/...
  再生時間: XX秒
  ファイルサイズ: XX MB
  品質: ✅ 良好 / ⚠️ 要改善 / ❌ 不良

エラー:
  - [エラー詳細を記録]

備考:
  - [その他の気づき]
```

---

## 🐛 トラブルシューティング

### 問題1: Google Driveノードのエラー

**エラー**: `Invalid value for 'operation'`

**原因**: Google Driveノードのoperationパラメータが無効

**対処**: 
1. Google Driveノードを開く
2. Operationを `upload` に設定
3. Binary Dataを `true` に設定
4. Binary Property Nameを `data` に設定

### 問題2: FAL APIタイムアウト

**エラー**: `Timeout after 200 seconds`

**原因**: FALのレンダリングが長時間実行中

**対処**:
- Fetch Statusノードのリトライ回数を確認
- 動画の長さ/ファイルサイズを確認
- FAL APIのステータスを直接確認

### 問題3: Notion DB更新失敗

**エラー**: `400 Bad Request` (Update Notion DB)

**原因**: `script_id` (pageId) が無効

**対処**:
- Phase4aで生成されたNotion PageのIDを確認
- Notion DBのプロパティ名が正確か確認

---

## 🔗 関連ドキュメント

- `/docs/testing/wf7-phase4c-test-setup-guide.md`: テストセットアップガイド
- `/docs/implementation/WF7-Phase4c-ClaudeCode実装指示書.md`: 実装指示書
- `/test-phase4c-mock-data.json`: テストデータ

---

**次のステップ**: 上記の手順に従ってE2Eテストを実行し、結果を記録してください。

