# WF7 Phase4a テスト実行結果

**実行日**: 2025-11-09  
**ワークフローID**: `LYPbvJfkMzLlhc6t`  
**ワークフロー名**: `WF7 Phase4a - Slide Generator`  
**実行ID**: `1114`

---

## ❌ エラー発生

### エラー内容

```
NodeOperationError: Could not extract page ID from URL: undefined
```

### エラー発生ノード

**ノード**: `Notion - Get Script Data`  
**ノードID**: `2bf2db92-7784-4ce3-aa67-cc6b3c914f23`

### エラー原因

Notionノードの`pageId`パラメータが以下の式になっています：

```
={{ $json.notionPageId || $json.script_id }}
```

しかし、`Execute Workflow Trigger`ノードが`passthrough`モードのため、Webhookからのデータは`$json.body.script_id`にあります。

### 現在のデータフロー

1. **Webhook - Phase 4a Start**: `{ body: { script_id: "..." } }`
2. **Execute Workflow Trigger** (passthrough): データをそのまま渡す
3. **Notion - Get Script Data**: `$json.notionPageId || $json.script_id` → **undefined** ❌

---

## 🔧 修正方法

### Step 1: NotionノードのpageIdを修正

n8n UIで以下の手順を実行してください：

1. ワークフロー `LYPbvJfkMzLlhc6t` を開く
2. `Notion - Get Script Data`ノードを選択
3. `pageId`パラメータを以下のように変更：

**修正前**:
```
={{ $json.notionPageId || $json.script_id }}
```

**修正後**:
```
={{ $json.body.script_id || $json.body.notionPageId || $json.script_id || $json.notionPageId }}
```

これにより、以下の順序でpageIdを取得します：
1. `$json.body.script_id` (Webhook経由の場合)
2. `$json.body.notionPageId` (Webhook経由の場合)
3. `$json.script_id` (Execute Sub-workflow経由の場合)
4. `$json.notionPageId` (Execute Sub-workflow経由の場合)

---

## 🧪 修正後のテスト実行

修正後、以下のコマンドでテストを再実行してください：

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator \
  -H "Content-Type: application/json" \
  -d '{"script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}'
```

### 期待される結果

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
    // ... 6 more slides
  ]
}
```

---

## 📋 確認事項

修正後、n8n UIで以下のノードの出力を確認してください：

1. **Execute Workflow Trigger**
   - ✅ `body.script_id`が含まれているか

2. **Notion - Get Script Data**
   - ✅ Notionページのデータが取得できているか
   - ✅ `properties`が含まれているか

3. **Code - Generate Slides with Pillow**
   - ✅ 7つのアイテムが出力されているか
   - ✅ 各アイテムに`section`, `duration`, `image_base64`, `filename`が含まれているか

4. **Split Out - Individual Slides** (存在する場合)
   - ✅ 7つのアイテムに分割されているか

5. **Google Drive - Upload Slide Image**
   - ✅ 7回実行されているか
   - ✅ 各実行でGoogle DriveファイルIDが取得できているか

6. **Set - Phase 4b Input Data**
   - ✅ `slides_count`が7であるか
   - ✅ `slides_metadata`が7要素の配列であるか

---

## 📝 補足情報

### Execute Workflow Triggerノードについて

このワークフローには`Execute Workflow Trigger`ノードが含まれています。これは、親ワークフローから`Execute Sub-workflow`で呼び出された場合に使用されます。

**passthroughモード**: 入力データをそのまま出力に渡します。

**データフロー**:
- Webhook経由: `{ body: { script_id: "..." } }`
- Execute Sub-workflow経由: `{ script_id: "..." }`

そのため、`pageId`の式は両方のケースに対応する必要があります。

---

**作成者**: AI Assistant (Claude Sonnet 4.5)  
**最終更新**: 2025-11-09

