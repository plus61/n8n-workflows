# WF7 Phase4a統合指示書（Claude Code用）

**作成日**: 2025-11-08  
**対象ワークフロー**: WF7phase4_v3 (`qSN7EHj5yl0nPXij`)  
**統合対象**: Phase4aワークフロー (`LYPbvJfkMzLlhc6t`)  
**目的**: Phase4aサブワークフローを親フローに統合し、スライド画像生成処理を追加

---

## 📋 実装タスク: S1 - Phase4aサブフロー統合

### 現状確認

**親フロー**: `qSN7EHj5yl0nPXij` (WF7phase4_v3)  
**現在のフロー構造**:
```
Webhook → Webhookデータ抽出 → Notion API呼び出し → URL抽出 → URL型チェック → 
データ統合 → Split Out → Driveファイル情報取得 → メタデータ整形 → ペイロード構築 → 
Submit to FAL → ...
```

**統合後のフロー構造**:
```
Webhook → Webhookデータ抽出 → Notion API呼び出し → URL抽出 → URL型チェック → 
データ統合 → HTTP Request (Phase4a呼び出し) → Set Phase4a Payload → 
(既存のSplit Out以降をPhase4a出力に置き換え)
```

---

## 🔧 実装手順

### Step 1: 親フローの取得

```javascript
// n8n MCPを使用して親フローを取得
const parentWorkflow = await mcp_n8n_get_workflow({
  id: "qSN7EHj5yl0nPXij"
});
```

### Step 2: Phase4a呼び出しノードの追加

**ノード仕様**:
- **ノード名**: `HTTP Request - Call Phase4a`
- **ノードタイプ**: `n8n-nodes-base.httpRequest`
- **typeVersion**: `4.2`
- **位置**: 「データ統合」ノードの後、X座標: `-2480` → `-2256`に配置

**設定内容**:
```json
{
  "parameters": {
    "method": "POST",
    "url": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator",
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
    "jsonBody": "={{ {\n  script_id: $('データ統合').item.json.notionPageId\n} }}",
    "options": {
      "response": {
        "response": {
          "responseFormat": "json"
        }
      },
      "timeout": 300000
    }
  },
  "onError": "continueRegularOutput",
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 5000
}
```

**ノードID生成**: UUID v4形式（例: `phase4a-call-xxxx-xxxx-xxxx`）

### Step 3: Phase4a出力データ整形ノードの追加

**ノード仕様**:
- **ノード名**: `Set - Phase4a Payload`
- **ノードタイプ**: `n8n-nodes-base.set`
- **typeVersion**: `3.4`
- **位置**: Phase4a呼び出しノードの後、X座標: `-2032`に配置

**設定内容**:
```json
{
  "parameters": {
    "assignments": {
      "assignments": [
        {
          "id": "script-id",
          "name": "script_id",
          "value": "={{ $('データ統合').item.json.notionPageId }}",
          "type": "string"
        },
        {
          "id": "article-id",
          "name": "articleId",
          "value": "={{ $('データ統合').item.json.articleId }}",
          "type": "string"
        },
        {
          "id": "slides-metadata",
          "name": "slides_metadata",
          "value": "={{ $json.slides_metadata || [] }}",
          "type": "array"
        },
        {
          "id": "slides-count",
          "name": "slides_count",
          "value": "={{ $json.slides_generated || ($json.slides_metadata || []).length }}",
          "type": "number"
        },
        {
          "id": "phase4a-success",
          "name": "phase4a_success",
          "value": "={{ $json.success === true }}",
          "type": "boolean"
        }
      ]
    },
    "options": {}
  }
}
```

### Step 4: エラーハンドリングノードの追加

**ノード仕様**:
- **ノード名**: `IF - Phase4a Success Check`
- **ノードタイプ**: `n8n-nodes-base.if`
- **typeVersion**: `2.2`
- **位置**: `Set - Phase4a Payload`の後、X座標: `-1808`に配置

**設定内容**:
```json
{
  "parameters": {
    "conditions": {
      "options": {
        "caseSensitive": true,
        "leftValue": "",
        "typeValidation": "strict",
        "version": 2
      },
      "conditions": [
        {
          "id": "check-phase4a-success",
          "leftValue": "={{ $json.phase4a_success }}",
          "rightValue": true,
          "operator": {
            "type": "boolean",
            "operation": "equals"
          }
        },
        {
          "id": "check-slides-count",
          "leftValue": "={{ $json.slides_count }}",
          "rightValue": 7,
          "operator": {
            "type": "number",
            "operation": "equals"
          }
        }
      ],
      "combinator": "and"
    },
    "options": {}
  },
  "onError": "continueErrorOutput"
}
```

**エラー時の処理**:
- **False分岐**: `Notion - Update Status Error` → `Respond to Webhook - Error`
- **True分岐**: 既存の処理フロー（Phase4bへ）

### Step 5: 既存ノードの接続変更

**変更前の接続**:
```javascript
"データ統合": {
  "main": [[{node: "Split Out", type: "main", index: 0}]]
}
```

**変更後の接続**:
```javascript
"データ統合": {
  "main": [[{node: "HTTP Request - Call Phase4a", type: "main", index: 0}]]
},
"HTTP Request - Call Phase4a": {
  "main": [[{node: "Set - Phase4a Payload", type: "main", index: 0}]]
},
"Set - Phase4a Payload": {
  "main": [[{node: "IF - Phase4a Success Check", type: "main", index: 0}]]
},
"IF - Phase4a Success Check": {
  "main": [
    [{node: "Split Out (Modified)", type: "main", index: 0}],  // True分岐
    [{node: "Notion - Update Status Error", type: "main", index: 0}]  // False分岐
  ]
}
```

### Step 6: Split Outノードの修正

既存の「Split Out」ノードを、Phase4aの`slides_metadata`配列を分割するように変更:

**変更前**:
```json
{
  "parameters": {
    "fieldToSplitOut": "assetsData"
  }
}
```

**変更後**:
```json
{
  "parameters": {
    "fieldToSplitOut": "slides_metadata"
  }
}
```

**ノード名変更**: `Split Out` → `Split Out - Phase4a Slides`

### Step 7: メタデータ整形ノードの修正

既存の「メタデータ整形」ノードを、Phase4aの出力形式に合わせて修正:

**変更前の設定**:
- `driveFileId`: `$('Split Out').item.json.driveFileId`
- `imageUrl`: `$json.webContentLink || ...`

**変更後の設定**:
```json
{
  "parameters": {
    "assignments": {
      "assignments": [
        {
          "id": "article-id",
          "name": "articleId",
          "value": "={{ $('Set - Phase4a Payload').item.json.articleId }}",
          "type": "string"
        },
        {
          "id": "section",
          "name": "section",
          "value": "={{ $json.section }}",
          "type": "string"
        },
        {
          "id": "duration",
          "name": "duration",
          "value": "={{ $json.duration }}",
          "type": "number"
        },
        {
          "id": "motion-prompt",
          "name": "motion_prompt",
          "value": "={{ $json.motion_prompt }}",
          "type": "string"
        },
        {
          "id": "image-url",
          "name": "imageUrl",
          "value": "={{ $json.image_url }}",
          "type": "string"
        },
        {
          "id": "drive-file-id",
          "name": "driveFileId",
          "value": "={{ $json.image_url ? $json.image_url.match(/id=([^&]+)/)?.[1] : '' }}",
          "type": "string"
        }
      ]
    }
  }
}
```

**ノード名変更**: `メタデータ整形` → `Set - Slide Metadata`

### Step 8: エラー処理ノードの追加

**Notion - Update Status Error**:
```json
{
  "parameters": {
    "method": "PATCH",
    "url": "=https://api.notion.com/v1/pages/{{ $('データ統合').item.json.notionPageId }}",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "notionApi",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Notion-Version",
          "value": "2022-06-28"
        }
      ]
    },
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ {\n  properties: {\n    Status: { select: { name: 'Failed' } },\n    'Error Message': { rich_text: [{ text: { content: 'Phase4a failed: ' + ($json.error || 'Unknown error') } }] }\n  }\n} }}"
  },
  "credentials": {
    "notionApi": {
      "id": "y89xQdP2gCTcdyup",
      "name": "Notion account"
    }
  }
}
```

**Respond to Webhook - Error**:
```json
{
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ {\n  success: false,\n  error: 'Phase4a slide generation failed',\n  script_id: $('データ統合').item.json.notionPageId,\n  details: $json\n} }}"
  }
}
```

---

## 📝 n8n MCP実装コマンド

### 1. ワークフロー取得

```javascript
const workflow = await mcp_n8n_get_workflow({
  id: "qSN7EHj5yl0nPXij"
});
```

### 2. ノード追加（n8n_update_partial_workflow使用）

```javascript
// Phase4a呼び出しノード追加
await mcp_n8n_update_partial_workflow({
  id: "qSN7EHj5yl0nPXij",
  operations: [
    {
      type: "addNode",
      node: {
        id: "phase4a-call-xxxx-xxxx-xxxx",  // UUID生成
        name: "HTTP Request - Call Phase4a",
        type: "n8n-nodes-base.httpRequest",
        typeVersion: 4.2,
        position: [-2256, -128],
        parameters: {
          // 上記の設定内容
        }
      }
    },
    {
      type: "addNode",
      node: {
        id: "set-phase4a-payload-xxxx",
        name: "Set - Phase4a Payload",
        type: "n8n-nodes-base.set",
        typeVersion: 3.4,
        position: [-2032, -128],
        parameters: {
          // 上記の設定内容
        }
      }
    },
    {
      type: "addNode",
      node: {
        id: "if-phase4a-success-xxxx",
        name: "IF - Phase4a Success Check",
        type: "n8n-nodes-base.if",
        typeVersion: 2.2,
        position: [-1808, -128],
        parameters: {
          // 上記の設定内容
        }
      }
    }
  ]
});
```

### 3. 接続変更

```javascript
await mcp_n8n_update_partial_workflow({
  id: "qSN7EHj5yl0nPXij",
  operations: [
    {
      type: "addConnection",
      sourceNode: "データ統合",
      targetNode: "HTTP Request - Call Phase4a",
      sourceOutput: "main",
      targetInput: "main"
    },
    {
      type: "addConnection",
      sourceNode: "HTTP Request - Call Phase4a",
      targetNode: "Set - Phase4a Payload",
      sourceOutput: "main",
      targetInput: "main"
    },
    {
      type: "addConnection",
      sourceNode: "Set - Phase4a Payload",
      targetNode: "IF - Phase4a Success Check",
      sourceOutput: "main",
      targetInput: "main"
    },
    {
      type: "addConnection",
      sourceNode: "IF - Phase4a Success Check",
      targetNode: "Split Out - Phase4a Slides",
      sourceOutput: "main",
      targetInput: "main",
      branch: 0  // True分岐
    },
    {
      type: "removeConnection",
      sourceNode: "データ統合",
      targetNode: "Split Out"
    }
  ]
});
```

### 4. 既存ノード更新

```javascript
await mcp_n8n_update_partial_workflow({
  id: "qSN7EHj5yl0nPXij",
  operations: [
    {
      type: "updateNode",
      nodeId: "6c179b70-9314-467c-902a-757abd79755b",  // Split OutノードID
      updates: {
        name: "Split Out - Phase4a Slides",
        parameters: {
          fieldToSplitOut: "slides_metadata"
        }
      }
    },
    {
      type: "updateNode",
      nodeId: "51fcc73d-c7b6-4673-91f7-607013751063",  // メタデータ整形ノードID
      updates: {
        name: "Set - Slide Metadata",
        parameters: {
          // 上記の変更後の設定
        }
      }
    }
  ]
});
```

---

## ✅ 検証項目

実装完了後、以下を確認:

1. **ノード追加確認**
   - [ ] `HTTP Request - Call Phase4a`ノードが追加されている
   - [ ] `Set - Phase4a Payload`ノードが追加されている
   - [ ] `IF - Phase4a Success Check`ノードが追加されている

2. **接続確認**
   - [ ] 「データ統合」→「HTTP Request - Call Phase4a」の接続がある
   - [ ] 「HTTP Request - Call Phase4a」→「Set - Phase4a Payload」の接続がある
   - [ ] 「Set - Phase4a Payload」→「IF - Phase4a Success Check」の接続がある
   - [ ] 「IF - Phase4a Success Check」のTrue分岐が「Split Out - Phase4a Slides」に接続されている

3. **設定確認**
   - [ ] Phase4a呼び出しURLが正しい
   - [ ] `script_id`が`notionPageId`から正しく渡されている
   - [ ] `slides_metadata`が正しく取得できている

4. **テスト実行**
   - [ ] Webhookでテスト実行
   - [ ] Phase4aが正常に呼び出される
   - [ ] `slides_metadata`が7件返ってくる
   - [ ] エラー時にNotionステータスが`Failed`に更新される

---

## 🚨 注意事項

1. **既存のSplit Outノード**: `assetsData`から`slides_metadata`への変更により、既存のアセット処理フローが変更されます。Phase4b統合時にさらに調整が必要です。

2. **エラーハンドリング**: Phase4aが失敗した場合、既存のFAL処理フローには進まず、エラーレスポンスを返すようにします。

3. **データ構造**: Phase4aの出力形式（`slides_metadata`配列）が既存の`assetsData`配列と異なるため、後続ノードの調整が必要です。

4. **位置調整**: ノードのX座標は既存ノードと重ならないように調整してください。

---

## 📊 期待される結果

実装完了後、以下のデータフローが実現されます:

```
Webhook受信
  ↓
Notion API呼び出し（スクリプト取得）
  ↓
データ統合
  ↓
HTTP Request - Call Phase4a（7枚スライド生成）
  ↓
Set - Phase4a Payload（データ整形）
  ↓
IF - Phase4a Success Check
  ├─ True → Split Out - Phase4a Slides → 後続処理
  └─ False → Notion更新（エラー） → Webhook応答（エラー）
```

---

**実装担当**: Claude Code  
**検証担当**: Claude (Assistant)  
**完了予定**: 実装後即座にテスト実行

