# WF7 Phase4a→4b→4c 統合設計書

**作成日時**: 2025-11-15 18:54:12 JST
**目的**: Phase4a（スライド生成）、Phase4b（単一動画生成）、Phase4c（動画結合）を統合し、完全なend-to-endワークフローを実現する

---

## 現状分析

### 現在のPhase4aワークフロー（wf7_phase4a.json）

**フロー**:
1. `Webhook - Phase 4a Start` → page_id受信
2. `Notion - Get Script Data` → script_id取得
3. `Code - Generate Slides with Pillow` → 7枚のスライド生成（Python/Pillow）
4. `Code - Convert to Binary` → 7アイテムに分割
5. `Google Drive - Upload Slide Image` → 7並列アップロード
6. `Code - Merge Slide Metadata` → メタデータ結合
7. `Aggregate - Combine All Slides` → 1アイテムに集約
8. `Set - Phase 4b Input Data` → Phase4b用データ準備
9. `Respond to Webhook - Success` → **ここで終了**

**問題点**:
- Phase4b（動画生成）が呼び出されていない
- Phase4c（動画結合）が呼び出されていない
- 最終的な動画が生成されない

### 確認済みエンドポイント

#### Phase4b: `/generate-single-video` (POST)

**リクエスト**:
```json
{
  "section": "hook",           // hook, intro, point1-3, summary, cta
  "duration": 3,               // 1-20秒
  "image_url": "https://res.cloudinary.com/...",  // Cloudinary URLのみ
  "motion_prompt": "dramatic zoom in...",
  "text": "フックテキスト",
  "script_id": "2aa68d5c-..."
}
```

**レスポンス**:
```json
{
  "success": true,
  "section": "hook",
  "duration": 3,
  "videoData": "base64...",    // ⚠️ base64エンコードされた動画データ
  "video_size_bytes": 150000,
  "script_id": "2aa68d5c-...",
  "motion_prompt": "dramatic zoom in...",
  "text": "フックテキスト",
  "filename": "video_hook.mp4",
  "mimeType": "video/mp4"
}
```

**重要**: Cloudinary URLのみ受け付け、videoDataはbase64形式で返される

#### Phase4c: `/concat-videos` (POST)

**リクエスト**:
```json
{
  "script_id": "2aa68d5c-...",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://res.cloudinary.com/...",  // ⚠️ URL形式を期待
      "cloudinary_public_id": "n8n_meo_wf7_slide/...",
      "motion_prompt": "...",
      "filename": "video_hook.mp4",
      "text": "...",
      "script_id": "..."
    }
    // ... 7本分
  ]
}
```

**レスポンス**:
```json
{
  "success": true,
  "script_id": "unknown",
  "final_video_url": "https://v3b.fal.media/files/...",
  "thumbnail_url": "https://v3b.fal.media/files/...",
  "total_duration": 80,
  "video_count": 7,
  "status": "COMPLETED"
}
```

**重要**: video_url（URL形式）を期待、base64データは受け付けない

---

## データフロー課題

### 問題: Phase4b出力とPhase4c入力の不一致

- **Phase4b出力**: `videoData`（base64）
- **Phase4c期待**: `video_url`（URL）

### 解決策: Cloudinaryへの動画アップロード

Phase4bの出力（base64動画データ）をCloudinaryにアップロードし、URLを取得する必要がある。

**メリット**:
1. Phase4aで既にCloudinaryを使用している（画像アップロード実績あり）
2. Cloudinaryは動画もサポート
3. URLベースの統一的なデータフローを維持

**実装方法**:
- n8n HTTP Requestノード or Codeノードでcloudinary APIを呼び出し
- base64 → バイナリ変換 → Cloudinaryアップロード → URL取得

---

## 統合ワークフロー設計

### 新規ノード構成（追加部分）

**現在の「Set - Phase 4b Input Data」ノードの後に追加**:

#### 10. `Loop - Iterate Over 7 Slides`
- **タイプ**: Splitout Batches または Code
- **目的**: 7枚のスライドメタデータを1つずつ処理
- **入力**: `slides_metadata` 配列（7アイテム）
- **出力**: 各スライドのメタデータ（7並列実行）

#### 11. `HTTP Request - Generate Single Video` (Phase4b)
- **タイプ**: HTTP Request
- **URL**: `https://{{FASTAPI_SERVER_URL}}/generate-single-video`
- **メソッド**: POST
- **ボディ**:
  ```json
  {
    "section": "={{ $json.section }}",
    "duration": "={{ $json.duration }}",
    "image_url": "={{ $json.cloudinary_image_url }}",
    "motion_prompt": "={{ $json.motion_prompt }}",
    "text": "={{ $json.text }}",
    "script_id": "={{ $json.script_id }}"
  }
  ```
- **並列実行**: 7アイテム並列

#### 12. `Aggregate - Collect 7 Videos`
- **タイプ**: Aggregate
- **目的**: 7本の動画レスポンスを1つに集約

#### 13. `Code - Upload Videos to Cloudinary`
- **タイプ**: Code (Python or JavaScript)
- **目的**: 7本の動画（base64）をCloudinaryにアップロード
- **処理**:
  1. 各動画のbase64データをバイナリに変換
  2. Cloudinary Video Upload APIを呼び出し
  3. 返されたURLとpublic_idを保存
- **出力**: 7本分のCloudinary URL

#### 14. `Code - Prepare Phase4c Payload`
- **タイプ**: Code
- **目的**: Phase4c用のペイロードを作成
- **処理**:
  ```javascript
  const videos_metadata = items.map((item, index) => ({
    section: item.json.section,
    duration: item.json.duration,
    video_url: item.json.cloudinary_video_url,  // Cloudinary URL
    cloudinary_public_id: item.json.cloudinary_public_id,
    motion_prompt: item.json.motion_prompt,
    filename: item.json.filename,
    text: item.json.text,
    script_id: item.json.script_id
  }));

  return [{
    json: {
      script_id: items[0].json.script_id,
      videos_metadata: videos_metadata
    }
  }];
  ```

#### 15. `HTTP Request - Concatenate Videos` (Phase4c)
- **タイプ**: HTTP Request
- **URL**: `https://{{FASTAPI_SERVER_URL}}/concat-videos`
- **メソッド**: POST
- **ボディ**:
  ```json
  {
    "script_id": "={{ $json.script_id }}",
    "videos_metadata": "={{ $json.videos_metadata }}"
  }
  ```

#### 16. `Respond to Webhook - Final Success`
- **タイプ**: Respond to Webhook
- **データ**:
  ```json
  {
    "success": true,
    "script_id": "={{ $json.script_id }}",
    "final_video_url": "={{ $json.final_video_url }}",
    "thumbnail_url": "={{ $json.thumbnail_url }}",
    "total_duration": "={{ $json.total_duration }}",
    "video_count": 7,
    "individual_videos": "={{ $json.individual_video_urls }}"
  }
  ```

---

## データフロー図

```
[1] Webhook Trigger (page_id)
    ↓
[2] Notion Get Script (script_id取得)
    ↓
[3] Generate 7 Slides (Pillow/Python) → 7アイテム
    ↓
[4] Convert to Binary → 7アイテム
    ↓
[5] Upload to Google Drive (7並列) → 7 Google Drive URLs
    ↓
[6] Merge Slide Metadata → 7アイテム
    ↓
[7] Aggregate → 1アイテム (slides_metadata配列)
    ↓
[8] Set Phase4b Input Data
    ↓
[9] ⚠️ 現在のワークフローはここで終了
    ↓
    ━━━━━━━━ 以下を追加 ━━━━━━━━
    ↓
[10] Loop Over 7 Slides → 7並列アイテム
    ↓
[11] HTTP: /generate-single-video (7並列) → 7 videoData (base64)
    ↓
[12] Aggregate 7 Videos → 1アイテム
    ↓
[13] Code: Upload to Cloudinary (7並列) → 7 Cloudinary URLs
    ↓
[14] Code: Prepare Phase4c Payload
     {
       script_id: "...",
       videos_metadata: [7本のURL付きメタデータ]
     }
    ↓
[15] HTTP: /concat-videos → final_video_url
    ↓
[16] Respond: 最終結果
     {
       final_video_url, thumbnail_url,
       total_duration, individual_videos
     }
```

---

## 実装上の注意点

### 1. Cloudinary設定

**必要な環境変数**:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

**アップロードAPI**:
```javascript
// n8n Code node example
const cloudinary = require('cloudinary').v2;

cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET
});

// Upload video (base64)
const result = await cloudinary.uploader.upload(`data:video/mp4;base64,${videoData}`, {
  folder: 'n8n_meo_wf7_videos',
  resource_type: 'video',
  public_id: `${script_id}_${section}`
});

// result.secure_url → Cloudinary URL
// result.public_id → Cloudinary public ID
```

### 2. エラーハンドリング

**各段階でのエラー処理**:
- Phase4b呼び出し失敗 → リトライ or スキップ
- Cloudinaryアップロード失敗 → リトライ or フォールバック
- Phase4c呼び出し失敗 → エラーレスポンス返却

**推奨**: 各HTTP Requestノードに「Continue On Fail」オプションを設定

### 3. パフォーマンス

**並列実行**:
- Phase4b: 7並列実行（各3-20秒の動画生成）→ 最大20秒
- Cloudinaryアップロード: 7並列実行 → 約5-10秒

**想定実行時間**:
- スライド生成: 5-10秒
- Phase4b (7並列): 15-25秒
- Cloudinaryアップロード (7並列): 5-10秒
- Phase4c: 10-15秒
- **合計**: 約35-60秒

### 4. データサイズ

- 各動画（base64）: 約100-500KB
- 7本合計: 約0.7-3.5MB
- 最終動画: 約1-5MB

**n8nのメモリ制限に注意**: 大きなbase64データを扱うため、適切なチャンク処理が必要

---

## テスト計画

### 1. Phase4b単体テスト

**ペイロード**:
```json
{
  "section": "hook",
  "duration": 3,
  "image_url": "https://res.cloudinary.com/drzmodro8/image/upload/...",
  "motion_prompt": "dramatic zoom in",
  "text": "テストテキスト",
  "script_id": "test-script-id"
}
```

**期待結果**: `videoData` (base64) が返される

### 2. Cloudinaryアップロードテスト

base64動画データをCloudinaryにアップロードし、URLが取得できることを確認

### 3. Phase4c単体テスト

**ペイロード**: `/tmp/wf7-phase4c-test-payload.json`（既存）

**期待結果**: `final_video_url` が返される

### 4. End-to-End統合テスト

**入力**:
```json
{
  "page_id": "2aa68d5c-2986-815c-aba4-da72d9830bf3"
}
```

**期待結果**:
```json
{
  "success": true,
  "script_id": "2aa68d5c-...",
  "final_video_url": "https://...",
  "thumbnail_url": "https://...",
  "total_duration": 80,
  "video_count": 7
}
```

---

## 次のステップ

1. ✅ Phase4bエンドポイント仕様確認（完了）
2. ✅ Phase4cエンドポイント仕様確認（完了）
3. ✅ 統合設計完了（本ドキュメント）
4. ⏳ n8nワークフローJSON作成
5. ⏳ n8nにインポート＆テスト
6. ⏳ End-to-End動作確認

---

## 関連ファイル

- **現在のワークフロー**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7_phase4a.json`
- **Phase4b実装**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/render_server.py:490-540`
- **Phase4c実装**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/phase4c_ffmpeg_concat.py`
- **テストペイロード**: `/tmp/wf7-phase4c-test-payload.json`
