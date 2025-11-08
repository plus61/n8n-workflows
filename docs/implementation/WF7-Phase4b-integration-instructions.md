# WF7 Phase4b統合指示書（S2実装）

**作成日**: 2025-11-08  
**対象ワークフロー**: WF7phase4_v3 (`qSN7EHj5yl0nPXij`)  
**統合対象**: Phase4bワークフロー (`wHaKi98mTlUvFIOR`)  
**目的**: Phase4bサブワークフローを親フローに統合し、FAL Image-to-Video処理を追加

---

## 📋 実装タスク: S2 - Phase4bサブフロー統合

### 現状確認

**親フロー**: `qSN7EHj5yl0nPXij` (WF7phase4_v3)  
**現在のフロー構造**:
```
Webhook → ... → データ統合 → HTTP Request - Call Phase4a → Set - Phase4a Payload → 
IF - Phase4a Success Check
  ├─ [true] → Split Out → Driveファイル情報取得 → メタデータ整形 → ペイロード構築 → 
  │            Submit to FAL → Fetch Status → Wait for Processing → Check Render Status → 
  │            Render Completed? → Get Image Result URL → Download Image → DriveへUL → ...
  └─ [false] → エラー時Notion更新 → エラー時Webhook応答
```

**統合後のフロー構造**:
```
Webhook → ... → データ統合 → HTTP Request - Call Phase4a → Set - Phase4a Payload → 
IF - Phase4a Success Check
  ├─ [true] → HTTP Request - Call Phase4b → Set - Phase4b Payload → 
  │            IF - Phase4b Success Check
  │              ├─ [true] → Phase4c処理（次のステップ）
  │              └─ [false] → エラー時Notion更新 → エラー時Webhook応答
  └─ [false] → エラー時Notion更新 → エラー時Webhook応答
```

---

## 🔧 実装手順

### Step 1: Phase4b呼び出しノードの追加

**ノード仕様**:
- **ノード名**: `HTTP Request - Call Phase4b`
- **ノードタイプ**: `n8n-nodes-base.httpRequest`
- **typeVersion**: `4.2`
- **位置**: `IF - Phase4a Success Check`のTrue分岐後、X座標: `-1808` → `-1584`に配置

**設定内容**:
```json
{
  "method": "POST",
  "url": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ {\n  \"script_id\": $('Set - Phase4a Payload').item.json.script_id,\n  \"slides_metadata\": $('Set - Phase4a Payload').item.json.slides_metadata\n} }}",
  "options": {
    "timeout": 600000
  }
}
```

**接続**:
- 入力: `IF - Phase4a Success Check` (True分岐)
- 出力: `Set - Phase4b Payload`

---

### Step 2: Phase4b出力データ整形ノードの追加

**ノード仕様**:
- **ノード名**: `Set - Phase4b Payload`
- **ノードタイプ**: `n8n-nodes-base.set`
- **typeVersion**: `3.4`
- **位置**: X座標: `-1584`, Y座標: `-128`

**設定内容**:
```json
{
  "assignments": {
    "assignments": [
      {
        "id": "assign1",
        "name": "script_id",
        "value": "={{ $json.script_id }}",
        "type": "string"
      },
      {
        "id": "assign2",
        "name": "articleId",
        "value": "={{ $('Set - Phase4a Payload').item.json.articleId }}",
        "type": "string"
      },
      {
        "id": "assign3",
        "name": "videos_metadata",
        "value": "={{ $json.videos_metadata }}",
        "type": "object"
      },
      {
        "id": "assign4",
        "name": "videos_count",
        "value": "={{ $json.videos_count }}",
        "type": "number"
      },
      {
        "id": "assign5",
        "name": "total_duration",
        "value": "={{ $json.total_duration }}",
        "type": "number"
      },
      {
        "id": "assign6",
        "name": "phase4b_success",
        "value": "={{ $json.success }}",
        "type": "boolean"
      }
    ]
  }
}
```

**接続**:
- 入力: `HTTP Request - Call Phase4b`
- 出力: `IF - Phase4b Success Check`

---

### Step 3: Phase4b成功判定ノードの追加

**ノード仕様**:
- **ノード名**: `IF - Phase4b Success Check`
- **ノードタイプ**: `n8n-nodes-base.if`
- **typeVersion**: `2.2`
- **位置**: X座標: `-1360`, Y座標: `-128`

**設定内容**:
```json
{
  "conditions": {
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict",
      "version": 2
    },
    "conditions": [
      {
        "id": "cond1",
        "leftValue": "={{ $json.phase4b_success }}",
        "rightValue": true,
        "operator": {
          "type": "boolean",
          "operation": "equals"
        }
      },
      {
        "id": "cond2",
        "leftValue": "={{ $json.videos_count }}",
        "rightValue": 7,
        "operator": {
          "type": "number",
          "operation": "equals"
        }
      }
    ],
    "combinator": "and"
  }
}
```

**接続**:
- 入力: `Set - Phase4b Payload`
- True分岐: Phase4c処理（次のステップで実装）
- False分岐: `エラー時Notion更新（Phase4b）` → `エラー時Webhook応答（Phase4b）`

---

### Step 4: エラーハンドリングノードの追加

**ノード1: エラー時Notion更新（Phase4b）**
- **ノード名**: `エラー時Notion更新（Phase4b）`
- **ノードタイプ**: `n8n-nodes-base.httpRequest`
- **typeVersion**: `4.2`
- **位置**: X座標: `-1360`, Y座標: `-368`

**設定内容**:
```json
{
  "method": "PATCH",
  "url": "=https://api.notion.com/v1/pages/{{ $('Set - Phase4a Payload').item.json.script_id }}",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "notionApi",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Notion-Version",
        "value": "2022-06-28"
      },
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={\n  \"properties\": {\n    \"status\": {\n      \"status\": {\n        \"name\": \"Phase4bエラー\"\n      }\n    },\n    \"errorMessage\": {\n      \"rich_text\": [\n        {\n          \"text\": {\n            \"content\": \"Phase4b呼び出しに失敗しました\"\n          }\n        }\n      ]\n    }\n  }\n}"
}
```

**ノード2: エラー時Webhook応答（Phase4b）**
- **ノード名**: `エラー時Webhook応答（Phase4b）`
- **ノードタイプ**: `n8n-nodes-base.respondToWebhook`
- **typeVersion**: `1.1`
- **位置**: X座標: `-1136`, Y座標: `-368`

**設定内容**:
```json
{
  "respondWith": "json",
  "responseBody": "={{ { success: false, error: \"Phase4b processing failed\" } }}"
}
```

---

### Step 5: 既存FAL処理ブロックの削除（後で実施）

以下のノードを削除予定（Phase4c実装後に削除）:
- `Split Out` (ID: `6c179b70-9314-467c-902a-757abd79755b`)
- `Driveファイル情報取得` (ID: `28076977-8c2b-4803-b803-6a6b7c8e8022`)
- `メタデータ整形` (ID: `51fcc73d-c7b6-4673-91f7-607013751063`)
- `ペイロード構築` (ID: `b6a12553-9438-4380-872b-15e1a0f75b4d`)
- `Submit to FAL` (ID: `5a5e9fb3-26a8-4ff0-89d4-2ab5e062a214`)
- `Fetch Status` (ID: `0e6f652f-ad64-4c90-b0ab-b830d6dda199`)
- `Wait for Processing` (ID: `0a70c028-e4f8-4fd1-abc1-f0b978900d22`)
- `Check Render Status` (ID: `b740c66e-9941-4dad-9251-4cfa387309ba`)
- `Render Completed?` (ID: `c8427945-8c7a-4871-9f3e-88d0492abf79`)
- `Get Image Result URL` (ID: `a5f5c585-ce10-4fcf-a45d-9f0fd9726f32`)
- `Download Image` (ID: `16ffaaee-bff3-4432-90c4-bb6f9647af77`)
- `Retry Counter` (ID: `4ac4470f-ae4b-4bfb-ab77-1681d1a04e2b`)
- `Check Retry Limit` (ID: `d76166cc-2f31-4d83-8ffe-a48c7cf8b6cc`)
- `Wait Before Retry` (ID: `cf1caad2-c849-4d56-88ed-41b9f6acc9b7`)
- `Timeout Error Response` (ID: `04d1ee60-ea4c-447c-8f9d-6fc3c26b24c3`)

**注意**: これらのノードはPhase4c実装後に削除します。現時点では接続を変更するだけです。

---

## 🔗 接続変更

### 変更前
```
IF - Phase4a Success Check (True) → Split Out → ...
```

### 変更後
```
IF - Phase4a Success Check (True) → HTTP Request - Call Phase4b → 
Set - Phase4b Payload → IF - Phase4b Success Check
  ├─ [true] → Phase4c処理（次のステップ）
  └─ [false] → エラー時Notion更新（Phase4b） → エラー時Webhook応答（Phase4b）
```

---

## 📝 データフロー

### Phase4a → Phase4b
```json
{
  "script_id": "29b68d5c-2986-817f-xxxx",
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "image_url": "https://drive.google.com/uc?export=download&id=...",
      "motion_prompt": "dramatic zoom in effect...",
      "drive_file_id": "...",
      "filename": "slide_1_hook.png"
    }
    // ... 6 more slides
  ]
}
```

### Phase4b → Phase4c（次のステップ）
```json
{
  "script_id": "29b68d5c-2986-817f-xxxx",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://fal.ai/files/xxx/video.mp4",
      "fal_request_id": "fal_xxx_1",
      "motion_prompt": "...",
      "filename": "video_1_hook.mp4"
    }
    // ... 6 more videos
  ],
  "videos_count": 7,
  "total_duration": 80
}
```

---

## ✅ 実装チェックリスト

- [ ] Step 1: `HTTP Request - Call Phase4b`ノード追加
- [ ] Step 2: `Set - Phase4b Payload`ノード追加
- [ ] Step 3: `IF - Phase4b Success Check`ノード追加
- [ ] Step 4: エラーハンドリングノード追加
- [ ] Step 5: 接続変更（`IF - Phase4a Success Check`のTrue分岐を変更）
- [ ] ワークフロー検証
- [ ] テスト実行

---

## 🧪 テスト手順

1. ワークフローを保存・アクティブ化
2. Webhookをトリガー:
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{
    "notionPageId": "YOUR_NOTION_PAGE_ID"
  }'
```

3. 期待される動作:
   - Phase4a: 7枚のスライド画像生成
   - Phase4b: 7本の動画生成（`videos_metadata`出力）
   - Phase4c: 次のステップで実装予定

---

## 📚 関連ドキュメント

- `docs/implementation/WF7-Phase4-FAL実装計画書.md` - 全体計画
- `docs/implementation/WF7-Phase4b-n8nワークフロー実装ガイド.md` - Phase4b詳細
- `docs/implementation/WF7-Phase4abc-docking-plan.md` - 統合計画

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08

