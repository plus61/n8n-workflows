# WF7 Phase4c E2Eテスト - 実際のデータ取得ガイド

**作成日**: 2025-11-08  
**目的**: Phase4a/bを実行して実際の動画URLデータを取得し、Phase4cのE2Eテストに使用する

---

## 📋 現状確認

### Phase4a/bの実行状況

- ✅ **Phase4a**: 実行可能（Webhook: `wf7-phase4a-slide-generator`）
- ✅ **Phase4b**: 実行可能（Webhook: `wf7-phase4b-image-to-video`）
- ⚠️ **問題**: Phase4aで7枚のスライドが生成されているが、1枚のみ処理される問題がある

### 確認されたテスト用script_id

- `2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9` - Phase1→Phase4統合テスト記事

---

## 🔧 実際のデータ取得方法

### 方法1: Phase4a/bを順次実行（推奨）

#### Step 1: Phase4aを実行

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator \
  -H "Content-Type: application/json" \
  -d '{"script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}'
```

**期待される出力**:
```json
{
  "success": true,
  "script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9",
  "slides_generated": 7,
  "google_drive_urls": [
    "https://drive.google.com/uc?export=download&id=...",
    // ... 7本のURL
  ],
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "motion_prompt": "...",
      "image_url": "https://drive.google.com/uc?export=download&id=..."
    },
    // ... 7枚のスライド
  ]
}
```

**注意**: 現在は1枚のみ生成される問題があります。7枚生成される場合は、その出力を保存してください。

#### Step 2: Phase4bを実行

Phase4aの出力を使ってPhase4bを実行:

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9",
    "slides_metadata": [
      {
        "section": "hook",
        "duration": 3,
        "motion_prompt": "dramatic zoom in effect",
        "image_url": "https://drive.google.com/uc?export=download&id=..."
      },
      // ... 7枚のスライドメタデータ
    ]
  }'
```

**期待される出力**:
```json
{
  "success": true,
  "script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://fal.media/files/lion/...",
      "fal_request_id": "...",
      "motion_prompt": "...",
      "filename": "video_1_hook.mp4",
      "text": "...",
      "slide_index": 0,
      "script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"
    },
    // ... 7本の動画メタデータ
  ],
  "videos_count": 7,
  "total_duration": 79
}
```

#### Step 3: Phase4cのPin Dataを準備

Phase4bの出力から、Phase4cのPin Data用JSONを作成:

```json
[
  {
    "section": "hook",
    "duration": 3,
    "video_url": "https://fal.media/files/lion/...",
    "order": 1,
    "script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"
  },
  {
    "section": "intro",
    "duration": 10,
    "video_url": "https://fal.media/files/lion/...",
    "order": 2,
    "script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"
  },
  // ... 7本の動画データ
]
```

---

### 方法2: 実行履歴から取得

Phase4bの過去の実行履歴から実際の動画URLを取得:

1. n8n UIでPhase4bワークフローを開く
2. 実行履歴から成功した実行を選択
3. `Code - Build Final Response`ノードの出力を確認
4. `videos_metadata`配列から`video_url`を抽出

---

### 方法3: 統合ワークフローを使用

Phase4ab統合ワークフロー（ID: `rg4bT7i7YyvXtl0l`）を使用:

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4ab-integrated \
  -H "Content-Type: application/json" \
  -d '{"script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}'
```

**注意**: このワークフローにもPhase4aの1枚のみ処理される問題がある可能性があります。

---

## 🐛 既知の問題

### Phase4aの問題: 1枚のみ処理される

**症状**: `Code - Generate Slides with Pillow`で7枚生成されているが、`Code - Convert to Binary`で1枚のみ処理される

**原因**: 
- `Split Out`ノードが正しく動作していない可能性
- `Code - Convert to Binary`の実行モードが`runOnceForEachItem`になっていない可能性

**対処法**:
1. Phase4aワークフローを確認
2. `Split Out - Individual Slides`ノードが正しく設定されているか確認
3. `Code - Convert to Binary`ノードの実行モードを確認

---

## 📝 実際のデータ取得手順（簡易版）

### 1. Phase4aを実行してスライドURLを取得

```bash
# Phase4a実行
RESPONSE=$(curl -s -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator \
  -H "Content-Type: application/json" \
  -d '{"script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}')

# レスポンスを保存
echo "$RESPONSE" > phase4a-response.json

# スライドメタデータを確認
echo "$RESPONSE" | jq '.slides_metadata'
```

### 2. Phase4bを実行して動画URLを取得

```bash
# Phase4aの出力を使ってPhase4bを実行
RESPONSE=$(curl -s -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video \
  -H "Content-Type: application/json" \
  -d @phase4a-response.json)

# レスポンスを保存
echo "$RESPONSE" > phase4b-response.json

# 動画メタデータを確認
echo "$RESPONSE" | jq '.videos_metadata'
```

### 3. Phase4c用Pin Dataを作成

```bash
# Phase4bの出力からPhase4c用Pin Dataを作成
jq '.videos_metadata | map({section, duration, video_url, order: (.slide_index + 1), script_id})' phase4b-response.json > phase4c-pindata.json
```

---

## ✅ 次のステップ

1. Phase4a/bを実行して実際のデータを取得
2. 取得したデータでPhase4cのE2Eテストを実行
3. 問題があれば、Phase4aの修正を検討

---

**関連ドキュメント**:
- `/docs/testing/wf7-phase4c-e2e-test-execution-guide.md`: E2Eテスト実行ガイド
- `/docs/testing/wf7-phase4ab-integrated-e2e-test-report.md`: Phase4ab統合テストレポート

