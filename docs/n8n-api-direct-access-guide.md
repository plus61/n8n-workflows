# n8n API直接アクセスガイド - MCP代替案

**作成日**: 2025-11-08  
**目的**: n8n-mcpのワークフロー管理機能が使えない場合の代替手段

---

## 🎯 概要

n8n-mcpのワークフロー管理機能が利用できない場合、以下の方法でn8n APIを直接呼び出すことができます：

1. **HTTP Requestノード**（n8nワークフロー内）
2. **Codeノード**（JavaScript/Python）
3. **curlコマンド**（ターミナル）
4. **カスタムMCPサーバー**（上級者向け）

---

## 📋 n8n API エンドポイント

### 基本URL
```
https://n8n-python-production-344b.up.railway.app/api/v1
```

### 認証
すべてのリクエストに以下のヘッダーが必要：
```
X-N8N-API-KEY: your-api-key-here
```

---

## 🔧 方法1: HTTP Requestノードを使用

### ワークフロー一覧取得

**設定**:
```json
{
  "method": "GET",
  "url": "https://n8n-python-production-344b.up.railway.app/api/v1/workflows",
  "sendHeaders": true,
  "headerParameters": {
    "X-N8N-API-KEY": "={{$env.N8N_API_KEY}}"
  },
  "options": {
    "response": {
      "response": {
        "responseFormat": "json"
      }
    }
  }
}
```

### ワークフロー取得

**設定**:
```json
{
  "method": "GET",
  "url": "https://n8n-python-production-344b.up.railway.app/api/v1/workflows/={{$json.workflowId}}",
  "sendHeaders": true,
  "headerParameters": {
    "X-N8N-API-KEY": "={{$env.N8N_API_KEY}}"
  }
}
```

### ワークフロー作成

**設定**:
```json
{
  "method": "POST",
  "url": "https://n8n-python-production-344b.up.railway.app/api/v1/workflows",
  "sendHeaders": true,
  "headerParameters": {
    "X-N8N-API-KEY": "={{$env.N8N_API_KEY}}",
    "Content-Type": "application/json"
  },
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  "bodyParametersJson": "={{ JSON.stringify($json.workflow) }}"
}
```

**入力データ例**:
```json
{
  "workflow": {
    "name": "My New Workflow",
    "nodes": [
      {
        "id": "webhook-1",
        "name": "Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [250, 300],
        "parameters": {
          "httpMethod": "POST",
          "path": "my-endpoint"
        }
      }
    ],
    "connections": {}
  }
}
```

### ワークフロー更新（完全置換）

**設定**:
```json
{
  "method": "PUT",
  "url": "https://n8n-python-production-344b.up.railway.app/api/v1/workflows/={{$json.workflowId}}",
  "sendHeaders": true,
  "headerParameters": {
    "X-N8N-API-KEY": "={{$env.N8N_API_KEY}}",
    "Content-Type": "application/json"
  },
  "sendBody": true,
  "contentType": "json",
  "specifyBody": "json",
  "bodyParametersJson": "={{ JSON.stringify($json.workflow) }}"
}
```

### ワークフロー削除

**設定**:
```json
{
  "method": "DELETE",
  "url": "https://n8n-python-production-344b.up.railway.app/api/v1/workflows/={{$json.workflowId}}",
  "sendHeaders": true,
  "headerParameters": {
    "X-N8N-API-KEY": "={{$env.N8N_API_KEY}}"
  }
}
```

### ワークフロー実行履歴取得

**設定**:
```json
{
  "method": "GET",
  "url": "https://n8n-python-production-344b.up.railway.app/api/v1/executions",
  "sendQuery": true,
  "queryParameters": {
    "workflowId": "={{$json.workflowId}}",
    "limit": "10"
  },
  "sendHeaders": true,
  "headerParameters": {
    "X-N8N-API-KEY": "={{$env.N8N_API_KEY}}"
  }
}
```

---

## 💻 方法2: Codeノード（JavaScript）を使用

### ワークフロー一覧取得

```javascript
const apiUrl = 'https://n8n-python-production-344b.up.railway.app/api/v1';
const apiKey = $env.N8N_API_KEY;

const response = await fetch(`${apiUrl}/workflows`, {
  method: 'GET',
  headers: {
    'X-N8N-API-KEY': apiKey
  }
});

const workflows = await response.json();

return workflows.data.map(workflow => ({
  json: {
    id: workflow.id,
    name: workflow.name,
    active: workflow.active,
    createdAt: workflow.createdAt,
    updatedAt: workflow.updatedAt
  }
}));
```

### ワークフロー取得

```javascript
const apiUrl = 'https://n8n-python-production-344b.up.railway.app/api/v1';
const apiKey = $env.N8N_API_KEY;
const workflowId = $input.first().json.workflowId;

const response = await fetch(`${apiUrl}/workflows/${workflowId}`, {
  method: 'GET',
  headers: {
    'X-N8N-API-KEY': apiKey
  }
});

const workflow = await response.json();

return [{ json: workflow }];
```

### ワークフロー作成

```javascript
const apiUrl = 'https://n8n-python-production-344b.up.railway.app/api/v1';
const apiKey = $env.N8N_API_KEY;
const workflowData = $input.first().json;

const response = await fetch(`${apiUrl}/workflows`, {
  method: 'POST',
  headers: {
    'X-N8N-API-KEY': apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(workflowData)
});

const result = await response.json();

return [{ json: result }];
```

### ワークフロー更新（完全置換）

```javascript
const apiUrl = 'https://n8n-python-production-344b.up.railway.app/api/v1';
const apiKey = $env.N8N_API_KEY;
const workflowId = $input.first().json.workflowId;
const workflowData = $input.first().json.workflow;

const response = await fetch(`${apiUrl}/workflows/${workflowId}`, {
  method: 'PUT',
  headers: {
    'X-N8N-API-KEY': apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(workflowData)
});

const result = await response.json();

return [{ json: result }];
```

### ワークフロー更新（部分更新の代替）

```javascript
// 1. 現在のワークフローを取得
const apiUrl = 'https://n8n-python-production-344b.up.railway.app/api/v1';
const apiKey = $env.N8N_API_KEY;
const workflowId = $input.first().json.workflowId;

const getResponse = await fetch(`${apiUrl}/workflows/${workflowId}`, {
  method: 'GET',
  headers: {
    'X-N8N-API-KEY': apiKey
  }
});

const currentWorkflow = await getResponse.json();

// 2. 必要な修正を適用
const updates = $input.first().json.updates;
const updatedNodes = currentWorkflow.nodes.map(node => {
  const update = updates.find(u => u.nodeId === node.id);
  if (update) {
    return { ...node, ...update.changes };
  }
  return node;
});

// 3. 完全更新
const putResponse = await fetch(`${apiUrl}/workflows/${workflowId}`, {
  method: 'PUT',
  headers: {
    'X-N8N-API-KEY': apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    ...currentWorkflow,
    nodes: updatedNodes
  })
});

const result = await putResponse.json();

return [{ json: result }];
```

---

## 🐚 方法3: curlコマンドを使用

### ワークフロー一覧取得

```bash
curl -X GET \
  "https://n8n-python-production-344b.up.railway.app/api/v1/workflows" \
  -H "X-N8N-API-KEY: your-api-key-here"
```

### ワークフロー取得

```bash
curl -X GET \
  "https://n8n-python-production-344b.up.railway.app/api/v1/workflows/WORKFLOW_ID" \
  -H "X-N8N-API-KEY: your-api-key-here"
```

### ワークフロー作成

```bash
curl -X POST \
  "https://n8n-python-production-344b.up.railway.app/api/v1/workflows" \
  -H "X-N8N-API-KEY: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My New Workflow",
    "nodes": [
      {
        "id": "webhook-1",
        "name": "Webhook",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [250, 300],
        "parameters": {
          "httpMethod": "POST",
          "path": "my-endpoint"
        }
      }
    ],
    "connections": {}
  }'
```

### ワークフロー更新

```bash
curl -X PUT \
  "https://n8n-python-production-344b.up.railway.app/api/v1/workflows/WORKFLOW_ID" \
  -H "X-N8N-API-KEY: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

### ワークフロー削除

```bash
curl -X DELETE \
  "https://n8n-python-production-344b.up.railway.app/api/v1/workflows/WORKFLOW_ID" \
  -H "X-N8N-API-KEY: your-api-key-here"
```

---

## 🔄 方法4: カスタムMCPサーバー（上級者向け）

n8n APIをラップするカスタムMCPサーバーを作成することも可能です。

### 実装例（TypeScript）

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "n8n-api-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "n8n_list_workflows",
      description: "List all workflows",
      inputSchema: {
        type: "object",
        properties: {
          limit: { type: "number" },
          active: { type: "boolean" },
        },
      },
    },
    {
      name: "n8n_get_workflow",
      description: "Get a workflow by ID",
      inputSchema: {
        type: "object",
        properties: {
          id: { type: "string" },
        },
        required: ["id"],
      },
    },
    // ... 他のツール
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  const apiUrl = process.env.N8N_API_URL;
  const apiKey = process.env.N8N_API_KEY;

  switch (name) {
    case "n8n_list_workflows": {
      const response = await fetch(`${apiUrl}/api/v1/workflows`, {
        headers: { "X-N8N-API-KEY": apiKey },
      });
      const data = await response.json();
      return { content: [{ type: "text", text: JSON.stringify(data) }] };
    }
    // ... 他のケース
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## 📊 比較表

| 方法 | メリット | デメリット | 推奨度 |
|------|---------|----------|--------|
| **HTTP Requestノード** | ✅ n8nワークフロー内で完結<br>✅ 視覚的に分かりやすい<br>✅ エラーハンドリングが簡単 | ⚠️ ワークフローが必要<br>⚠️ 設定が複雑 | ⭐⭐⭐⭐⭐ |
| **Codeノード** | ✅ 柔軟性が高い<br>✅ 複雑なロジックに対応<br>✅ エラーハンドリングが簡単 | ⚠️ コードを書く必要がある<br>⚠️ デバッグが難しい | ⭐⭐⭐⭐ |
| **curlコマンド** | ✅ シンプル<br>✅ スクリプト化可能 | ⚠️ ターミナルが必要<br>⚠️ エラーハンドリングが難しい | ⭐⭐⭐ |
| **カスタムMCP** | ✅ MCPとして統合可能<br>✅ 再利用可能 | ⚠️ 開発時間がかかる<br>⚠️ メンテナンスが必要 | ⭐⭐ |

---

## 🎯 推奨アプローチ

### ケース1: n8nワークフロー内で使用

**推奨**: HTTP RequestノードまたはCodeノード

```javascript
// Codeノードでn8n APIを呼び出す
const apiUrl = $env.N8N_API_URL;
const apiKey = $env.N8N_API_KEY;

// ワークフロー一覧取得
const workflows = await fetch(`${apiUrl}/api/v1/workflows`, {
  headers: { 'X-N8N-API-KEY': apiKey }
}).then(r => r.json());

return workflows.data.map(w => ({ json: w }));
```

### ケース2: 外部スクリプトから使用

**推奨**: curlコマンドまたはHTTP Requestライブラリ

```bash
#!/bin/bash
API_URL="https://n8n-python-production-344b.up.railway.app/api/v1"
API_KEY="your-api-key-here"

# ワークフロー一覧取得
curl -X GET "${API_URL}/workflows" \
  -H "X-N8N-API-KEY: ${API_KEY}"
```

### ケース3: Claude Codeから使用

**推奨**: Codeノードを使用したn8nワークフローを作成し、それをWebhook経由で呼び出す

---

## ⚠️ 注意事項

### 1. APIキーの管理

- ✅ 環境変数（`$env.N8N_API_KEY`）を使用
- ❌ ハードコードしない
- ✅ n8n Credentials機能を活用

### 2. エラーハンドリング

```javascript
try {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const data = await response.json();
  return [{ json: data }];
} catch (error) {
  return [{
    json: {
      error: error.message,
      success: false
    }
  }];
}
```

### 3. レート制限

n8n APIにはレート制限がある可能性があります。大量のリクエストを送信する場合は、適切な間隔を空けてください。

### 4. ワークフローアクティブ化

**重要**: n8n API経由ではワークフローをアクティブ化できません。アクティブ化はn8n UIで手動で行う必要があります。

---

## 📚 参考リンク

- [n8n Public REST API Documentation](https://docs.n8n.io/api/)
- [n8n API Reference](https://docs.n8n.io/api/api-reference/)
- [HTTP Request Node Documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)

---

## ✅ まとめ

n8n-mcpのワークフロー管理機能が使えない場合、以下の方法で代替できます：

1. **HTTP Requestノード**: n8nワークフロー内で使用（推奨）
2. **Codeノード**: より柔軟な処理が必要な場合
3. **curlコマンド**: スクリプトやターミナルから使用
4. **カスタムMCPサーバー**: 長期的な解決策が必要な場合

最も実用的なのは、**HTTP RequestノードまたはCodeノード**を使用する方法です。

---

**最終更新**: 2025-11-08





