# WF7 Phase4b - Cloudinary Slideshow MVP 実装計画

**作成日**: 2025-11-11
**目的**: Phase4bをFAL.aiからCloudinary Video Slideshow APIに置換（アプローチA: 1回API呼び出し）
**推定工数**: 0.5🍅

---

## 📋 実装方針

### アプローチA: 1回のAPI呼び出し

**変更点**:
- Split Out削除 → 全スライドを一括処理
- FAL.ai関連ノード削除（9ノード）
- Cloudinary Slideshow API追加（1ノード）
- ポーリングループ削除

**期待効果**:
- ノード数: 22 → 約8-10ノード（55%削減）
- API呼び出し: 7回 → 1回（86%削減）
- 処理時間: 推定50-80秒（7スライド一括処理）

---

## 🔧 修正するノード

### ✅ 流用するノード（6個）

1. **Webhook - Phase 4b Start** - 変更なし
2. **Execute Workflow Trigger** - 変更なし
3. **Code - Validate Input** - 変更なし
4. **Code - Generate Cloudinary Signature** - **変更必要** (create_slideshow用の署名)
5. **Code - Build Final Response** - **変更必要** (レスポンス形式変更)
6. **Respond to Webhook** - 変更なし

### 🆕 新規作成するノード（2個）

7. **Code - Build Slideshow Manifest** - manifest_json生成
8. **HTTP Request - Cloudinary Create Slideshow** - Slideshow API呼び出し

### ❌ 削除するノード（14個）

- Split Out - Slides
- HTTP Request - Download from Google Drive
- Code - Upload to Cloudinary with Base64
- Set - Preserve Slide Metadata
- Code - Prepare FAL Payload
- HTTP Request - Submit to FAL
- Wait - 5 Seconds
- HTTP Request - Check Status
- IF - Render Completed?
- HTTP Request - Get Result
- Code - Build Video Metadata
- Aggregate - Wait for All Videos
- Set - Retry Counter
- IF - Check Retry Limit
- Wait - Before Retry
- Code - Timeout Error

---

## 📝 新規ノードの実装詳細

### ノード7: Code - Build Slideshow Manifest

**目的**: Phase4aの出力（slides_metadata）をCloudinary manifest_json形式に変換

**入力**:
```json
{
  "script_id": "xxx",
  "slides_metadata": [
    {
      "section": "hook",
      "image_url": "https://res.cloudinary.com/.../slide_1.png",
      "duration": 3,
      "motion_prompt": "",
      "text": "..."
    }
    // ... 7 slides
  ]
}
```

**処理ロジック**:
```javascript
const input = $input.first().json;
const slides = input.slides_metadata;

if (!slides || slides.length === 0) {
  throw new Error('slides_metadata is empty');
}

// Cloudinary manifest_json構造
const manifest = {
  width: 1920,
  height: 1080,
  fps: 30,
  slides: slides.map(slide => ({
    media: slide.image_url,  // Cloudinary URL
    duration: slide.duration  // 秒単位
  }))
};

// 合計時間を計算
const totalDuration = slides.reduce((sum, s) => sum + s.duration, 0);

return {
  json: {
    script_id: input.script_id,
    manifest_json: JSON.stringify(manifest),
    slides_metadata: slides,  // デバッグ用に保持
    total_duration: totalDuration,
    slides_count: slides.length
  }
};
```

**出力**:
```json
{
  "script_id": "xxx",
  "manifest_json": "{\"width\":1920,\"height\":1080,\"fps\":30,\"slides\":[...]}",
  "slides_metadata": [...],
  "total_duration": 21,
  "slides_count": 7
}
```

---

### ノード4（修正）: Code - Generate Cloudinary Signature

**修正理由**: create_slideshow用のパラメータに変更

**修正前** (upload用):
```javascript
const stringToSign = `folder=${folder}&timestamp=${timestamp}${apiSecret}`;
```

**修正後** (create_slideshow用):
```javascript
const manifest_json = $json.manifest_json;
const stringToSign = `manifest_json=${manifest_json}&timestamp=${timestamp}${apiSecret}`;
```

**完全なコード**:
```javascript
const apiSecret = 'IKxxQL7zniUB5s9TeijsChM8hAs';  // 既存から流用
const timestamp = Math.floor(Date.now() / 1000);
const manifest_json = $json.manifest_json;

// create_slideshow用の署名生成
const stringToSign = `manifest_json=${manifest_json}&timestamp=${timestamp}${apiSecret}`;

// SHA-1ハッシュ生成（既存のsha1関数を流用）
function sha1(str) {
  // 既存の実装をそのまま使用...
  // （既存Phase4bのコードから流用）
}

const signature = sha1(stringToSign);

return {
  json: {
    ...($input.first().json),
    cloudinary_timestamp: timestamp,
    cloudinary_signature: signature
  }
};
```

---

### ノード8: HTTP Request - Cloudinary Create Slideshow

**目的**: Cloudinary Video Slideshow APIを呼び出し

**設定**:
- **Method**: POST
- **URL**: `https://api.cloudinary.com/v1_1/drzmodro8/video/create_slideshow`
- **Authentication**: None（署名で認証）
- **Body Type**: Form-urlencoded

**Body Parameters**:
```yaml
manifest_json: ={{ $json.manifest_json }}
api_key: 188947963992381
timestamp: ={{ $json.cloudinary_timestamp }}
signature: ={{ $json.cloudinary_signature }}
```

**Response Format**: JSON

**Timeout**: 180000 (180秒 - 7枚のスライドを処理)

**Retry Settings**:
- retryOnFail: true
- maxTries: 3
- waitBetweenTries: 5000

**エラーハンドリング**:
- onError: continueRegularOutput

**期待されるレスポンス**:
```json
{
  "asset_id": "xxx",
  "public_id": "video/slideshow_xxx",
  "version": 1731331200,
  "format": "mp4",
  "resource_type": "video",
  "created_at": "2025-11-11T12:00:00Z",
  "bytes": 1234567,
  "width": 1920,
  "height": 1080,
  "duration": 21.0,
  "url": "http://res.cloudinary.com/.../slideshow_xxx.mp4",
  "secure_url": "https://res.cloudinary.com/.../slideshow_xxx.mp4"
}
```

---

### ノード5（修正）: Code - Build Final Response

**修正理由**: レスポンス形式をCloudinary Slideshow用に変更

**修正後のコード**:
```javascript
const input = $input.first().json;

// エラーハンドリング
if (input.error || !input.secure_url) {
  return [{
    json: {
      success: false,
      error: input.error || 'Video generation failed',
      script_id: $('Code - Build Slideshow Manifest').item.json.script_id || 'unknown'
    }
  }];
}

// 正常時のレスポンス
const manifestData = $('Code - Build Slideshow Manifest').item.json;

return [{
  json: {
    success: true,
    script_id: manifestData.script_id,
    video_url: input.secure_url,
    video_duration: input.duration || manifestData.total_duration,
    video_format: input.format || 'mp4',
    width: input.width || 1920,
    height: input.height || 1080,
    cloudinary_asset_id: input.asset_id,
    cloudinary_public_id: input.public_id,
    slides_count: manifestData.slides_count,
    created_at: input.created_at || new Date().toISOString()
  }
}];
```

**出力例**:
```json
{
  "success": true,
  "script_id": "2a368d5c-2986-8185-a10e-ce6a9fedcdd4",
  "video_url": "https://res.cloudinary.com/drzmodro8/video/upload/v1731331200/video/slideshow_xxx.mp4",
  "video_duration": 21.0,
  "video_format": "mp4",
  "width": 1920,
  "height": 1080,
  "cloudinary_asset_id": "xxx",
  "cloudinary_public_id": "video/slideshow_xxx",
  "slides_count": 7,
  "created_at": "2025-11-11T12:00:00Z"
}
```

---

## 🔄 新しいワークフロー構造（8ノード）

```
1. Webhook - Phase 4b Start
   ↓
2. Execute Workflow Trigger
   ↓
3. Code - Validate Input
   ↓
4. Code - Build Slideshow Manifest (新規)
   ↓
5. Code - Generate Cloudinary Signature (修正)
   ↓
6. HTTP Request - Cloudinary Create Slideshow (新規)
   ↓
7. Code - Build Final Response (修正)
   ↓
8. Respond to Webhook
```

**エラー出力接続**:
- Code - Validate Input (error) → Code - Build Final Response

---

## 🧪 テスト計画

### テストデータ

Phase4aの実際の出力を使用:
```json
{
  "script_id": "2a368d5c-2986-8185-a10e-ce6a9fedcdd4",
  "slides_metadata": [
    {
      "section": "hook",
      "image_url": "https://res.cloudinary.com/drzmodro8/image/upload/v1731255123/n8n_meo_wf7_slide/slide_1.png",
      "duration": 3,
      "motion_prompt": "",
      "text": "..."
    }
    // ... 7 slides total
  ]
}
```

### テスト手順

1. **Phase4a実行** - 7枚のスライド生成
2. **Phase4aの出力を取得** - Notion DBまたはExecutionから
3. **Phase4b Webhook呼び出し** - Phase4aの出力をそのまま送信
4. **結果確認**:
   - ✅ HTTP 200 OK
   - ✅ video_url が返却される
   - ✅ 動画が再生可能（mp4）
   - ✅ 処理時間 <180秒
   - ✅ Executionエラーなし

### テストコマンド例

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": "2a368d5c-2986-8185-a10e-ce6a9fedcdd4",
    "slides_metadata": [
      {
        "section": "hook",
        "image_url": "https://res.cloudinary.com/drzmodro8/image/upload/v1731255123/n8n_meo_wf7_slide/slide_1.png",
        "duration": 3,
        "motion_prompt": "",
        "text": "Test slide"
      }
    ]
  }' \
  -w "\n\nHTTP Status: %{http_code}\nTime Total: %{time_total}s\n"
```

---

## ✅ Go/No-Go判断基準

### ✅ Go条件（Phase 2へ進む）

- API動作成功（HTTP 200 OK）
- video_urlが返却される
- 動画が再生可能（mp4形式）
- 処理時間 <180秒
- n8n Executionエラーなし

### ❌ No-Go条件（代替案検討）

- Cloudinary API認証エラー（署名生成失敗）
- manifest_json形式エラー（API仕様不一致）
- 処理時間 >300秒（実用不可）
- 動画生成失敗（エラーレスポンス）

### 代替案

1. **Runpod GPU + FFmpeg** - 自前レンダリング
2. **Cloudinary Layers API** - 別アプローチ
3. **外部サービス** - Runway ML、Luma等

---

## 📊 期待される改善効果

| 指標 | 旧（FAL.ai） | 新（Cloudinary） | 改善率 |
|-----|-------------|-----------------|-------|
| ノード数 | 22 | 8 | 64%削減 |
| API呼び出し | 7回 | 1回 | 86%削減 |
| 処理時間 | ~140秒 | ~60-80秒 | 43-57%削減 |
| コード行数 | ~500行 | ~150行 | 70%削減 |
| エラーポイント | 14箇所 | 4箇所 | 71%削減 |

---

**次のステップ**: n8n UIでワークフロー修正を実行
