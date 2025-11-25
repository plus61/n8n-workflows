# WF7 Phase4a ワークフロー実装ガイド - Phase4b→4c統合

**作成日時**: 2025-11-15 19:00:26 JST
**目的**: 既存のPhase4aワークフローにPhase4b（動画生成）とPhase4c（動画結合）を統合

---

## 📋 実装概要

既存の9ノードワークフローに7つの新しいノードを追加して、完全なend-to-end動画生成パイプラインを構築します。

**既存のワークフロー終了地点**:
- 最終ノード（node 9）: `Respond to Webhook - Success`
- このノードは削除せず、後で再利用します

**新規追加ノード数**: 7ノード（node 10 ～ node 16）

---

## ⚠️ 重要な前提条件

### 1. 環境変数の設定

n8n環境に以下の環境変数が必要です（Railway環境変数に追加）:

```bash
# Cloudinary設定
CLOUDINARY_CLOUD_NAME=<your_cloud_name>
CLOUDINARY_API_KEY=<your_api_key>
CLOUDINARY_API_SECRET=<your_api_secret>

# FastAPIサーバーURL（RailwayのfastapiサービスURL）
FASTAPI_SERVER_URL=<your_railway_fastapi_url>
# 例: https://fastapi-production-xxx.up.railway.app
```

### 2. スライド画像のCloudinaryアップロード

**重要**: Phase4bはCloudinary URLのみを受け付けます。現在のワークフローはGoogle Driveにアップロードしているため、以下の2つの選択肢があります：

**選択肢A（推奨）**: スライド画像をCloudinaryに変更
- node 5 (Google Drive Upload) を **Cloudinaryアップロード** に変更
- より効率的でシンプル

**選択肢B**: Google DriveとCloudinary両方にアップロード
- node 5の後に追加ノードを挿入してCloudinaryにもアップロード
- 冗長だが既存のGoogle Drive統合を維持

このガイドでは**選択肢A（Cloudinary変更）**を推奨します。

---

## 🔄 実装手順

### ステップ1: 既存node 5をCloudinaryアップロードに変更

#### 変更前（node 5 - Google Drive Upload）:
```json
{
  "parameters": {
    "operation": "upload",
    "name": "={{ $json.filename }}",
    "binaryData": true,
    "binaryPropertyName": "data",
    "options": {
      "parents": {
        "parent": ["1WF7_SLIDES_FOLDER_ID_HERE"]
      }
    }
  },
  "id": "google-drive-upload-node",
  "name": "Google Drive - Upload Slide Image",
  "type": "n8n-nodes-base.googleDrive",
  "typeVersion": 3,
  "position": [1340, 300]
}
```

#### 変更後（node 5 - Cloudinary Upload Slide Image）:

**ノードタイプ**: `Code` (n8n-nodes-base.code)
**Node ID**: `cloudinary-upload-slide-node`
**Node Name**: `Code - Upload Slide to Cloudinary`
**Position**: `[1340, 300]`

**Parameters**:
- Language: `javascript`
- Mode: `runOnceForEachItem`

**JavaScript Code**:
```javascript
// Cloudinaryにスライド画像をアップロード
const cloudinary = require('cloudinary').v2;

// Cloudinary設定
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET
});

// エラーチェック
if (!$binary.data || !$binary.data.data) {
  throw new Error('バイナリデータが存在しません');
}

const script_id = $('Notion - Get Script Data').item.json.id;
const section = $json.section;
const filename = $json.filename;

// Base64データ取得
const base64Data = $binary.data.data;

// Cloudinaryにアップロード（画像）
try {
  const result = await cloudinary.uploader.upload(`data:image/png;base64,${base64Data}`, {
    folder: 'n8n_meo_wf7_slide',
    resource_type: 'image',
    public_id: `${script_id}_${section}`,
    overwrite: true,
    invalidate: true
  });

  console.log(`✅ Cloudinary画像アップロード成功: ${section} → ${result.secure_url}`);

  return {
    json: {
      section: section,
      duration: $json.duration,
      motion_prompt: $json.motion_prompt,
      filename: filename,
      text: $json.text,
      cloudinary_image_url: result.secure_url,
      cloudinary_public_id: result.public_id,
      cloudinary_format: result.format,
      cloudinary_width: result.width,
      cloudinary_height: result.height,
      script_id: script_id
    }
  };
} catch (error) {
  console.error(`❌ Cloudinaryアップロードエラー (${section}):`, error);
  throw new Error(`Cloudinaryアップロード失敗: ${error.message}`);
}
```

---

### ステップ2: node 6（Merge Metadata）を更新

既存のnode 6 (`Code - Merge Slide Metadata`) は、Google Drive URLではなくCloudinary URLを使うように更新します。

**変更後のJavaScript Code**:
```javascript
// Cloudinaryアップロードのレスポンスとスライドメタデータをマージ
// 既にCloudinaryアップロードノードで必要なデータがあるので、そのまま返す
const slideData = $json;

// エラーチェック
if (!slideData || !slideData.cloudinary_image_url) {
  throw new Error('Cloudinaryアップロードに失敗しました: URLが取得できませんでした');
}

return {
  json: slideData
};
```

---

### ステップ3: node 9（旧Respond to Webhook）を削除して接続を変更

既存のnode 9 (`Respond to Webhook - Success`) を削除し、代わりに新しいノードフローを追加します。

**node 8からの接続先を変更**:
- 変更前: `node 8 → node 9 (Respond to Webhook)`
- 変更後: `node 8 → node 10 (Loop Over Slides)`

---

### ステップ4: node 10 - Loop Over 7 Slides

**ノードタイプ**: `Code` (n8n-nodes-base.code)
**Node ID**: `loop-slides-node`
**Node Name**: `Code - Loop Over 7 Slides`
**Position**: `[2220, 300]`

**Parameters**:
- Language: `javascript`
- Mode: `runOnceForAllItems`

**JavaScript Code**:
```javascript
// slides_metadata配列を展開して、7つのアイテムに分割
const script_id = $json.script_id;
const slides_metadata = $json.slides_metadata;

// エラーチェック
if (!slides_metadata || !Array.isArray(slides_metadata)) {
  throw new Error('slides_metadataが配列ではありません');
}

if (slides_metadata.length !== 7) {
  throw new Error(`スライド数が不正です。期待: 7枚、実際: ${slides_metadata.length}枚`);
}

// 各スライドをアイテムとして返す
return slides_metadata.map(slide => ({
  json: {
    section: slide.section,
    duration: slide.duration,
    cloudinary_image_url: slide.cloudinary_image_url,
    cloudinary_public_id: slide.cloudinary_public_id,
    motion_prompt: slide.motion_prompt,
    text: slide.text,
    filename: slide.filename,
    script_id: script_id
  }
}));
```

---

### ステップ5: node 11 - HTTP Request to Phase4b (Generate Single Video)

**ノードタイプ**: `HTTP Request` (n8n-nodes-base.httpRequest)
**Node ID**: `http-phase4b-node`
**Node Name**: `HTTP Request - Generate Single Video (Phase4b)`
**Position**: `[2440, 300]`

**Parameters**:
- **Authentication**: None
- **Request Method**: `POST`
- **URL**: `={{ $env.FASTAPI_SERVER_URL }}/generate-single-video`
- **Send Body**: Yes
- **Specify Body**: `JSON`
- **JSON Body**:
```json
={
  "section": $json.section,
  "duration": $json.duration,
  "image_url": $json.cloudinary_image_url,
  "motion_prompt": $json.motion_prompt,
  "text": $json.text,
  "script_id": $json.script_id
}
```
- **Options**:
  - **Timeout**: `60000` (60秒)
  - **Response**: `Include Response Headers and Status`

**エラーハンドリング**:
- Continue On Fail: `true`（推奨）

---

### ステップ6: node 12 - Aggregate 7 Videos

**ノードタイプ**: `Aggregate` (n8n-nodes-base.aggregate)
**Node ID**: `aggregate-videos-node`
**Node Name**: `Aggregate - Collect 7 Videos`
**Position**: `[2660, 300]`

**Parameters**:
- **Aggregate**: `Aggregate All Item Data`
- **Options**: デフォルト

---

### ステップ7: node 13 - Upload Videos to Cloudinary

**ノードタイプ**: `Code` (n8n-nodes-base.code)
**Node ID**: `cloudinary-upload-videos-node`
**Node Name**: `Code - Upload Videos to Cloudinary`
**Position**: `[2880, 300]`

**Parameters**:
- Language: `javascript`
- Mode: `runOnceForAllItems`

**JavaScript Code**:
```javascript
// Phase4bから返されたvideoData（base64）をCloudinaryにアップロード
const cloudinary = require('cloudinary').v2;

// Cloudinary設定
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET
});

// Aggregateノードからデータ取得
const videosData = items[0].json.data;

if (!videosData || !Array.isArray(videosData)) {
  throw new Error('動画データが取得できませんでした');
}

if (videosData.length !== 7) {
  throw new Error(`動画数が不正です。期待: 7本、実際: ${videosData.length}本`);
}

// 各動画をCloudinaryにアップロード
const uploadPromises = videosData.map(async (video, index) => {
  const section = video.section;
  const script_id = video.script_id;
  const videoData = video.videoData;

  if (!videoData) {
    throw new Error(`動画データが存在しません: ${section}`);
  }

  try {
    // Cloudinaryにアップロード（動画）
    const result = await cloudinary.uploader.upload(`data:video/mp4;base64,${videoData}`, {
      folder: 'n8n_meo_wf7_videos',
      resource_type: 'video',
      public_id: `${script_id}_${section}`,
      overwrite: true,
      invalidate: true
    });

    console.log(`✅ Cloudinary動画アップロード成功 (${index+1}/7): ${section} → ${result.secure_url}`);

    return {
      section: section,
      duration: video.duration,
      video_url: result.secure_url,
      cloudinary_public_id: result.public_id,
      cloudinary_format: result.format,
      cloudinary_duration: result.duration,
      cloudinary_width: result.width,
      cloudinary_height: result.height,
      motion_prompt: video.motion_prompt,
      filename: video.filename,
      text: video.text,
      script_id: script_id,
      video_size_bytes: video.video_size_bytes
    };
  } catch (error) {
    console.error(`❌ Cloudinary動画アップロードエラー (${section}):`, error);
    throw new Error(`Cloudinary動画アップロード失敗 (${section}): ${error.message}`);
  }
});

// 全てのアップロードを並列実行
const uploadedVideos = await Promise.all(uploadPromises);

console.log(`✅ 全動画のCloudinaryアップロード完了: ${uploadedVideos.length}本`);

// 7本の動画メタデータを返す
return uploadedVideos.map(video => ({
  json: video
}));
```

---

### ステップ8: node 14 - Prepare Phase4c Payload

**ノードタイプ**: `Code` (n8n-nodes-base.code)
**Node ID**: `prepare-phase4c-node`
**Node Name**: `Code - Prepare Phase4c Payload`
**Position**: `[3100, 300]`

**Parameters**:
- Language: `javascript`
- Mode: `runOnceForAllItems`

**JavaScript Code**:
```javascript
// Phase4c用のペイロードを作成
// itemsには7本の動画メタデータが含まれている

const videos_metadata = items.map(item => ({
  section: item.json.section,
  duration: item.json.duration,
  video_url: item.json.video_url,
  cloudinary_public_id: item.json.cloudinary_public_id,
  motion_prompt: item.json.motion_prompt,
  filename: item.json.filename,
  text: item.json.text,
  script_id: item.json.script_id,
  video_size_bytes: item.json.video_size_bytes,
  cloudinary_format: item.json.cloudinary_format,
  cloudinary_duration: item.json.cloudinary_duration,
  cloudinary_width: item.json.cloudinary_width,
  cloudinary_height: item.json.cloudinary_height
}));

// エラーチェック
if (videos_metadata.length !== 7) {
  throw new Error(`動画数が不正です。期待: 7本、実際: ${videos_metadata.length}本`);
}

const script_id = items[0].json.script_id;

console.log(`✅ Phase4cペイロード準備完了: script_id=${script_id}, 動画数=${videos_metadata.length}`);

return [{
  json: {
    script_id: script_id,
    videos_metadata: videos_metadata,
    video_count: videos_metadata.length,
    individual_video_urls: videos_metadata.map(v => v.video_url)
  }
}];
```

---

### ステップ9: node 15 - HTTP Request to Phase4c (Concatenate Videos)

**ノードタイプ**: `HTTP Request` (n8n-nodes-base.httpRequest)
**Node ID**: `http-phase4c-node`
**Node Name**: `HTTP Request - Concatenate Videos (Phase4c)`
**Position**: `[3320, 300]`

**Parameters**:
- **Authentication**: None
- **Request Method**: `POST`
- **URL**: `={{ $env.FASTAPI_SERVER_URL }}/concat-videos`
- **Send Body**: Yes
- **Specify Body**: `JSON`
- **JSON Body**:
```json
={
  "script_id": $json.script_id,
  "videos_metadata": $json.videos_metadata
}
```
- **Options**:
  - **Timeout**: `120000` (120秒)
  - **Response**: `Include Response Headers and Status`

---

### ステップ10: node 16 - Respond to Webhook - Final Success

**ノードタイプ**: `Respond to Webhook` (n8n-nodes-base.respondToWebhook)
**Node ID**: `respond-webhook-final-node`
**Node Name**: `Respond to Webhook - Final Success`
**Position**: `[3540, 300]`

**Parameters**:
- **Respond With**: `JSON`
- **Response Body**:
```javascript
={{
  {
    success: true,
    script_id: $json.script_id,
    final_video_url: $json.final_video_url,
    thumbnail_url: $json.thumbnail_url,
    total_duration: $json.total_duration,
    video_count: $json.video_count,
    status: $json.status,
    individual_videos: $('Code - Prepare Phase4c Payload').item.json.individual_video_urls
  }
}}
```

---

## 🔗 ノード接続（Connections）

```
[1] Webhook Trigger
  ↓
[2] Notion Get Script
  ↓
[3] Code - Generate Slides (Pillow)
  ↓
[4] Code - Convert to Binary
  ↓
[5] Code - Upload Slide to Cloudinary ← 変更
  ↓
[6] Code - Merge Slide Metadata ← 更新
  ↓
[7] Aggregate - Combine All Slides
  ↓
[8] Set - Phase 4b Input Data
  ↓
[10] Code - Loop Over 7 Slides ← 新規
  ↓
[11] HTTP Request - Generate Single Video (Phase4b) ← 新規
  ↓
[12] Aggregate - Collect 7 Videos ← 新規
  ↓
[13] Code - Upload Videos to Cloudinary ← 新規
  ↓
[14] Code - Prepare Phase4c Payload ← 新規
  ↓
[15] HTTP Request - Concatenate Videos (Phase4c) ← 新規
  ↓
[16] Respond to Webhook - Final Success ← 新規
```

---

## ✅ 実装チェックリスト

### 事前準備
- [ ] Railway環境変数に `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` を設定
- [ ] Railway環境変数に `FASTAPI_SERVER_URL` を設定（FastAPIサービスのURL）
- [ ] 現在のワークフローをバックアップ済み（`2025-11-15_18-58_wf7_phase4a_backup.json`）

### ノード変更
- [ ] node 5: Google DriveからCloudinaryアップロードに変更
- [ ] node 6: Merge Metadataコードを更新
- [ ] node 9: 旧Respond to Webhookを削除（または接続を外す）

### ノード追加
- [ ] node 10: Loop Over 7 Slidesを追加
- [ ] node 11: HTTP Request (Phase4b)を追加
- [ ] node 12: Aggregate 7 Videosを追加
- [ ] node 13: Upload Videos to Cloudinaryを追加
- [ ] node 14: Prepare Phase4c Payloadを追加
- [ ] node 15: HTTP Request (Phase4c)を追加
- [ ] node 16: Respond to Webhook Finalを追加

### 接続確認
- [ ] 全てのノード接続が正しく設定されている
- [ ] エラーハンドリング設定が適切

### テスト
- [ ] Webhookエンドポイントが有効
- [ ] テストペイロードで実行: `{"script_id": "2aa68d5c-2986-815c-aba4-da72d9830bf3"}`
- [ ] 7枚のスライドが生成される
- [ ] 7本の動画がCloudinaryにアップロードされる
- [ ] 最終動画が生成される
- [ ] Webhookレスポンスに`final_video_url`が含まれる

---

## 🐛 トラブルシューティング

### Cloudinaryアップロードエラー
- 環境変数が正しく設定されているか確認
- Cloudinaryのアカウント制限を確認（無料プランは容量制限あり）

### Phase4b 404エラー
- `FASTAPI_SERVER_URL`が正しいか確認
- FastAPIサービスが起動しているか確認（Railway logs確認）

### Phase4b 422エラー
- リクエストボディに必要なフィールドが全て含まれているか確認
- `image_url`がCloudinary URLかどうか確認

### Phase4c 500エラー
- 動画数が正確に7本か確認
- 各動画の`video_url`が有効か確認

---

## 📊 期待される実行時間

- スライド生成: 5-10秒
- Phase4b (7並列): 15-25秒
- Cloudinaryアップロード (7並列): 5-10秒
- Phase4c: 10-15秒
- **合計**: 約35-60秒

---

## 📚 関連ドキュメント

- 統合設計書: `now/2025-11-15_18-54_phase4a-4b-4c-integration-design.md`
- Phase4bエンドポイント: `workflows/wf7-video-renderer/render_server.py:490-540`
- Phase4cエンドポイント: `workflows/wf7-video-renderer/render_server.py:412+`
- バックアップ: `now/2025-11-15_18-58_wf7_phase4a_backup.json`
