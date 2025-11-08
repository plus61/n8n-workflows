# WF7 Phase 4b: n8nワークフロー実装ガイド

**作成日**: 2025-11-08
**バージョン**: 1.0
**目的**: FAL Image-to-Video変換ワークフローのn8n実装手順書

---

## 📋 概要

Phase 4bは、Phase 4aで生成された7枚のスライド画像をFAL.aiのImage-to-Video APIで個別に動画化し、Phase 4cに渡すワークフローです。

### 処理フロー

```
Webhook受信 (slides_metadata[7])
  ↓
Split In Batches (7枚を1枚ずつ処理)
  ↓
HTTP Request - FAL Compose API呼び出し
  ↓
Wait (5秒)
  ↓
HTTP Request - Status Check (ポーリング)
  ↓
IF - Render Completed?
  ├─ Yes → Get Result URL
  └─ No → Retry Counter → Wait → Status Check へ戻る
  ↓
Code - videos_metadata構築
  ↓
Merge (7本を統合)
  ↓
Respond to Webhook
```

### 入力

Phase 4aから以下のデータを受信:

```json
{
  "script_id": "29b68d5c-2986-817f-xxxx",
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "image_url": "https://drive.google.com/uc?export=download&id=1abc...",
      "motion_prompt": "dramatic zoom in effect, professional business style, sharp focus",
      "text": "あなたのビジネス、本当に見つけられていますか？",
      "drive_file_id": "1abc...",
      "filename": "slide_1_hook.png"
    }
    // ... 6 more slides
  ]
}
```

### 出力

Phase 4cへ以下のデータを渡す:

```json
{
  "script_id": "29b68d5c-2986-817f-xxxx",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://fal.ai/files/xxx/video.mp4",
      "fal_request_id": "fal_xxx_1",
      "motion_prompt": "dramatic zoom in effect...",
      "filename": "video_1_hook.mp4",
      "render_time": 45
    }
    // ... 6 more videos
  ]
}
```

---

## 🔧 ノード構成

### 1. Webhook Trigger

**ノード名**: `Webhook - Phase 4b Start`
**ノードタイプ**: `n8n-nodes-base.webhook`

#### 設定

```json
{
  "httpMethod": "POST",
  "path": "wf7-phase4b-image-to-video",
  "responseMode": "responseNode",
  "options": {}
}
```

#### 想定リクエスト

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": "29b68d5c-2986-817f-xxxx",
    "slides_metadata": [...]
  }'
```

---

### 2. Validation Node

**ノード名**: `Code - Validate Input`
**ノードタイプ**: `n8n-nodes-base.code`

#### 設定

```json
{
  "language": "javascript",
  "jsCode": "const input = $input.first().json;\n\nif (!input.script_id) {\n  throw new Error('script_id is required');\n}\n\nif (!input.slides_metadata || input.slides_metadata.length !== 7) {\n  throw new Error('slides_metadata must contain exactly 7 items');\n}\n\n// 各スライドの必須フィールド確認\nfor (const slide of input.slides_metadata) {\n  if (!slide.image_url) throw new Error(`Missing image_url for ${slide.section}`);\n  if (!slide.duration) throw new Error(`Missing duration for ${slide.section}`);\n  if (!slide.motion_prompt) throw new Error(`Missing motion_prompt for ${slide.section}`);\n}\n\nreturn input;"
}
```

---

### 3. Split In Batches

**ノード名**: `Split In Batches - 7 Slides`
**ノードタイプ**: `n8n-nodes-base.splitInBatches`

#### 設定

```json
{
  "batchSize": 1,
  "options": {
    "reset": false
  }
}
```

#### 説明

7枚のスライドを1枚ずつ処理。FAL APIの同時実行制限（429エラー）を回避するため、逐次処理します。

---

### 4. Prepare FAL Payload

**ノード名**: `Code - Prepare FAL Payload`
**ノードタイプ**: `n8n-nodes-base.code`

#### 設定

```json
{
  "language": "javascript",
  "jsCode": "// 現在処理中のスライド\nconst slide = $input.first().json;\nconst slides = $('Code - Validate Input').item.json.slides_metadata;\nconst currentIndex = $itemIndex;\n\n// FAL Compose APIペイロード構築\nconst payload = {\n  tracks: [\n    {\n      id: \"1\",\n      type: \"video\",\n      keyframes: [\n        {\n          url: slide.image_url,\n          timestamp: 0,\n          duration: slide.duration\n        }\n      ]\n    }\n  ]\n};\n\nreturn {\n  json: {\n    fal_payload: JSON.stringify(payload),\n    slide_metadata: slide,\n    script_id: $('Code - Validate Input').item.json.script_id,\n    slide_index: currentIndex\n  }\n};"
}
```

---

### 5. Submit to FAL

**ノード名**: `HTTP Request - Submit to FAL`
**ノードタイプ**: `n8n-nodes-base.httpRequest`

#### 設定

```json
{
  "method": "POST",
  "url": "https://queue.fal.run/fal-ai/ffmpeg-api/compose",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ $json.fal_payload }}",
  "options": {
    "response": {
      "response": {
        "responseFormat": "json"
      }
    },
    "timeout": 30000
  }
}
```

#### Credentials

- **HTTP Header Auth**: FAL API Key
  - Header Name: `Authorization`
  - Header Value: `Key YOUR_FAL_API_KEY`

#### 出力例

```json
{
  "request_id": "fal_xxx_1234567890",
  "status_url": "https://queue.fal.run/fal-ai/ffmpeg-api/compose/requests/fal_xxx_1234567890/status",
  "response_url": "https://queue.fal.run/fal-ai/ffmpeg-api/compose/requests/fal_xxx_1234567890"
}
```

---

### 6. Wait for Processing

**ノード名**: `Wait - 5 Seconds`
**ノードタイプ**: `n8n-nodes-base.wait`

#### 設定

```json
{
  "resume": "time",
  "amount": 5,
  "unit": "seconds"
}
```

---

### 7. Check Render Status

**ノード名**: `HTTP Request - Check Status`
**ノードタイプ**: `n8n-nodes-base.httpRequest`

#### 設定

```json
{
  "method": "GET",
  "url": "={{ $json.status_url }}",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "options": {
    "response": {
      "response": {
        "responseFormat": "json"
      }
    },
    "timeout": 300000
  }
}
```

#### 出力例

```json
{
  "status": "COMPLETED",
  "response_url": "https://queue.fal.run/fal-ai/ffmpeg-api/compose/requests/fal_xxx_1234567890"
}
```

または

```json
{
  "status": "IN_PROGRESS"
}
```

---

### 8. Render Completed?

**ノード名**: `IF - Render Completed?`
**ノードタイプ**: `n8n-nodes-base.if`

#### 設定

```json
{
  "conditions": {
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict"
    },
    "conditions": [
      {
        "id": "render-complete-check",
        "leftValue": "={{ $json.status }}",
        "rightValue": "COMPLETED",
        "operator": {
          "type": "string",
          "operation": "equals"
        }
      }
    ],
    "combinator": "and"
  }
}
```

---

### 9. Get Result URL

**ノード名**: `HTTP Request - Get Result`
**ノードタイプ**: `n8n-nodes-base.httpRequest`

#### 設定

```json
{
  "method": "GET",
  "url": "={{ $json.response_url }}",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "options": {
    "response": {
      "response": {
        "responseFormat": "json"
      }
    }
  }
}
```

#### 出力例

```json
{
  "output": {
    "video_url": "https://fal.ai/files/xxx/video.mp4"
  }
}
```

---

### 10. Build Video Metadata

**ノード名**: `Code - Build Video Metadata`
**ノードタイプ**: `n8n-nodes-base.code`

#### 設定

```json
{
  "language": "javascript",
  "jsCode": "const resultData = $input.first().json;\nconst slideData = $('Code - Prepare FAL Payload').item.json.slide_metadata;\nconst requestId = $('HTTP Request - Submit to FAL').item.json.request_id;\nconst slideIndex = $('Code - Prepare FAL Payload').item.json.slide_index;\n\n// video_url抽出\nconst videoUrl = resultData.output?.video_url \n  || resultData.video_url \n  || resultData.result?.video_url;\n\nif (!videoUrl) {\n  throw new Error('Video URL not found in FAL API response');\n}\n\n// videos_metadataオブジェクト構築\nreturn {\n  json: {\n    section: slideData.section,\n    duration: slideData.duration,\n    video_url: videoUrl,\n    fal_request_id: requestId,\n    motion_prompt: slideData.motion_prompt,\n    filename: `video_${slideIndex + 1}_${slideData.section}.mp4`,\n    text: slideData.text,\n    slide_index: slideIndex\n  }\n};"
}
```

---

### 11. Retry Counter

**ノード名**: `Set - Retry Counter`
**ノードタイプ**: `n8n-nodes-base.set`

#### 設定

```json
{
  "mode": "manual",
  "fields": {
    "values": [
      {
        "name": "retry_count",
        "type": "number",
        "value": "={{ $json.retry_count ? $json.retry_count + 1 : 1 }}"
      },
      {
        "name": "status_url",
        "type": "string",
        "value": "={{ $json.status_url }}"
      },
      {
        "name": "request_id",
        "type": "string",
        "value": "={{ $('HTTP Request - Submit to FAL').item.json.request_id }}"
      },
      {
        "name": "slide_metadata",
        "type": "object",
        "value": "={{ $('Code - Prepare FAL Payload').item.json.slide_metadata }}"
      }
    ]
  }
}
```

---

### 12. Check Retry Limit

**ノード名**: `IF - Check Retry Limit`
**ノードタイプ**: `n8n-nodes-base.if`

#### 設定

```json
{
  "conditions": {
    "conditions": [
      {
        "id": "check-retry-limit",
        "leftValue": "={{ $json.retry_count }}",
        "rightValue": 10,
        "operator": {
          "type": "number",
          "operation": "smaller"
        }
      }
    ]
  }
}
```

#### 説明

最大10回リトライ。各動画の生成に最大50秒（5秒 × 10回）。

---

### 13. Wait Before Retry

**ノード名**: `Wait - Before Retry`
**ノードタイプ**: `n8n-nodes-base.wait`

#### 設定

```json
{
  "resume": "time",
  "amount": 5,
  "unit": "seconds"
}
```

---

### 14. Error Response (Timeout)

**ノード名**: `Code - Timeout Error`
**ノードタイプ**: `n8n-nodes-base.code`

#### 設定

```json
{
  "language": "javascript",
  "jsCode": "const slide = $json.slide_metadata;\nthrow new Error(`Rendering timeout for ${slide.section} after ${$json.retry_count} retries`);"
}
```

---

### 15. Merge Videos

**ノード名**: `Merge - All Videos`
**ノードタイプ**: `n8n-nodes-base.merge`

#### 設定

```json
{
  "mode": "append",
  "options": {}
}
```

#### 説明

Split In Batchesループが完了した後、7本の動画メタデータを配列に統合します。

---

### 16. Build Final Response

**ノード名**: `Code - Build Final Response`
**ノードタイプ**: `n8n-nodes-base.code`

#### 設定

```json
{
  "language": "javascript",
  "jsCode": "const allItems = $input.all();\nconst scriptId = $('Code - Validate Input').item.json.script_id;\n\n// videos_metadata配列を構築（sectionの順序でソート）\nconst sectionOrder = ['hook', 'intro', 'point1', 'point2', 'point3', 'summary', 'cta'];\n\nconst videosMetadata = allItems\n  .map(item => item.json)\n  .sort((a, b) => {\n    return sectionOrder.indexOf(a.section) - sectionOrder.indexOf(b.section);\n  });\n\nreturn {\n  json: {\n    success: true,\n    script_id: scriptId,\n    videos_metadata: videosMetadata,\n    videos_count: videosMetadata.length,\n    total_duration: videosMetadata.reduce((sum, v) => sum + v.duration, 0)\n  }\n};"
}
```

---

### 17. Respond to Webhook

**ノード名**: `Respond to Webhook - Success`
**ノードタイプ**: `n8n-nodes-base.respondToWebhook`

#### 設定

```json
{
  "respondWith": "json",
  "responseBody": "={{ $json }}"
}
```

---

## 🔗 ノード接続図

```
Webhook
  ↓
Code - Validate Input
  ↓
Split In Batches ────────────────────┐
  ↓                                   │
Code - Prepare FAL Payload           │
  ↓                                   │
HTTP Request - Submit to FAL         │
  ↓                                   │
Wait - 5 Seconds                     │
  ↓                                   │
HTTP Request - Check Status          │
  ↓                                   │
IF - Render Completed?               │
  ├─ Yes → Get Result               │
  │         ↓                        │
  │    Code - Build Video Metadata   │
  │         ↓                        │
  │    [戻る] ──────────────────────┘
  │
  └─ No → Set - Retry Counter
           ↓
      IF - Check Retry Limit
        ├─ Yes → Wait - Before Retry → Check Status へ戻る
        └─ No → Code - Timeout Error

Merge - All Videos
  ↓
Code - Build Final Response
  ↓
Respond to Webhook
```

---

## 🧪 テスト手順

### 1. 単体テスト（FAL API直接呼び出し）

```bash
# FAL Compose API動作確認
curl -X POST https://queue.fal.run/fal-ai/ffmpeg-api/compose \
  -H "Authorization: Key YOUR_FAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tracks": [
      {
        "id": "1",
        "type": "video",
        "keyframes": [
          {
            "url": "https://drive.google.com/uc?export=download&id=YOUR_IMAGE_ID",
            "timestamp": 0,
            "duration": 3
          }
        ]
      }
    ]
  }'
```

期待結果:
```json
{
  "request_id": "fal_xxx_1234567890",
  "status_url": "https://queue.fal.run/fal-ai/ffmpeg-api/compose/requests/fal_xxx_1234567890/status"
}
```

### 2. Status Check確認

```bash
# 5秒待機後
curl -X GET "https://queue.fal.run/fal-ai/ffmpeg-api/compose/requests/fal_xxx_1234567890/status" \
  -H "Authorization: Key YOUR_FAL_API_KEY"
```

### 3. n8n統合テスト

#### Step 1: 1枚のスライドでテスト

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": "test-001",
    "slides_metadata": [
      {
        "section": "hook",
        "duration": 3,
        "image_url": "https://drive.google.com/uc?export=download&id=YOUR_IMAGE_ID",
        "motion_prompt": "dramatic zoom in effect",
        "text": "テスト"
      }
    ]
  }'
```

#### Step 2: 7枚すべてでE2Eテスト

Phase 4aの実際の出力を使用。

---

## ⚠️ エラーハンドリング

### 1. FAL API 429 (Rate Limit)

**エラー**: `Too Many Requests`

**対処**: Split In Batchesで逐次処理済み（1枚ずつ）

追加対策が必要な場合:
```json
{
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 10000
}
```

### 2. Google Drive画像アクセスエラー

**エラー**: `Failed to fetch image from URL`

**原因**: Google Driveの共有設定が「制限付き」

**対処**:
1. Phase 4aで生成時に共有設定を「リンクを知っている全員」に変更
2. または、FAL APIに渡す前にダウンロード可能URLに変換

### 3. レンダリングタイムアウト

**エラー**: 10回リトライ後もCOMPLETED にならない

**原因分析**:
- 画像サイズが大きすぎる（>5MB）
- FAL APIの混雑
- image_urlが無効

**対処**:
- Phase 4aで画像サイズを最適化（<500KB推奨）
- リトライ回数を15回に増加
- エラーログをNotionに記録

### 4. video_url抽出失敗

**エラー**: `Video URL not found in FAL API response`

**対処**: レスポンス構造を詳細ログ

```javascript
console.log('FAL Response:', JSON.stringify(resultData, null, 2));
```

---

## 📊 パフォーマンス指標

### 目標値

- **1本あたりの処理時間**: <60秒
  - Submit: 1秒
  - Wait + Status Check: 40-50秒（FAL側の処理）
  - Get Result: 1秒
- **7本合計**: <420秒（7分）
- **メモリ使用**: <50MB（画像データはURL参照）
- **成功率**: 95%+

### 実測値の取得

n8n UIの「Execution Time」パネルで各ノードの時間を確認。

### 最適化案

**並列処理**: Split In BatchesをbatchSize=3に変更（3本ずつ並列）

リスク:
- FAL API 429エラーの可能性
- n8n同時実行制限

推奨: 初期実装は逐次処理、安定後に並列化検討

---

## 🔐 セキュリティ

### 1. FAL API Key管理

**必須**: n8n環境変数に保存

```bash
# Railway環境変数設定
railway variables set FAL_API_KEY="your_fal_api_key"
```

n8nノードで参照:
```
={{ $vars.FAL_API_KEY }}
```

### 2. Google Drive画像の一時公開

**リスク**: 画像URLが一時的に公開状態

**対策**:
- Phase 4b完了後に共有設定をリセット（Phase 4cで実施）
- または、FAL APIが認証付きURLに対応している場合は認証使用

---

## 📝 次のステップ

Phase 4b完了後、以下を実施:

1. ✅ **Todo完了**: Phase 4b実装ガイド作成
2. ⏳ **次のタスク**: Phase 4b n8nワークフローJSON作成
3. ⏳ **並行タスク**: Phase 4b単体テスト実施
4. ⏳ **統合タスク**: Phase 4a → 4b → 4c E2Eテスト

---

## 📌 Phase 4全体との統合

### Phase 4a → 4b データ契約

Phase 4aの出力がそのままPhase 4bの入力になるよう設計:

```json
{
  "script_id": "xxx",
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "image_url": "https://drive.google.com/uc?...",
      "motion_prompt": "...",
      "drive_file_id": "...",
      "filename": "slide_1_hook.png"
    }
  ]
}
```

### Phase 4b → 4c データ契約

Phase 4bの出力がPhase 4cの入力要件を満たす:

```json
{
  "script_id": "xxx",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://fal.ai/files/xxx/video.mp4",
      "fal_request_id": "...",
      "filename": "video_1_hook.mp4"
    }
  ]
}
```

---

**作成者**: Claude Code (Sonnet 4.5)
**更新日**: 2025-11-08
**関連ドキュメント**:
- WF7-Phase4abc-docking-plan.md
- WF7-Phase4a-n8nワークフロー実装ガイド.md
- WF7-Phase4c-n8nワークフロー実装ガイド.md
- docs/knowledge/wf7-phase4-troubleshooting-guide.md
