# n8n MCP クイックリファレンス

**目的**: MCPを使用したn8nへのアクセスが動作しない場合の迅速な確認手順

---

## 🚀 30秒で動作確認

### Step 1: ヘルスチェック（10秒）

```javascript
mcp_n8n-mcp_n8n_health_check()
```

**期待される結果**: `status: "ok"`

### Step 2: ワークフロー一覧取得（10秒）

```javascript
mcp_n8n-mcp_n8n_list_workflows({limit: 1})
```

**期待される結果**: ワークフローのリストが返される

### Step 3: 診断実行（10秒）

```javascript
mcp_n8n-mcp_n8n_diagnostic({verbose: true})
```

**確認項目**:
- `apiConfiguration.status.connected`: `true`
- `toolsAvailability.totalAvailable`: `38`

---

## ✅ 動作確認チェックリスト

### 必須項目（すべて✅である必要がある）

- [ ] 設定ファイルが存在する（`.mcp/config.json` または `.mcp.json`）
- [ ] 環境変数 `N8N_API_URL` が設定されている
- [ ] 環境変数 `N8N_API_KEY` が設定されている
- [ ] `n8n_health_check` が成功する
- [ ] `n8n_list_workflows` でワークフローが取得できる

---

## 🔧 よくある問題と即座の解決策

### 問題: MCPツールが利用できない

**解決策**:
1. Cursor/Claude Desktopを再起動
2. 設定ファイルのJSON形式を確認
3. 環境変数を確認: `echo $N8N_API_URL`

### 問題: API接続エラー

**解決策**:
1. URL末尾にスラッシュがないか確認
2. API Keyが正しいか確認
3. n8nインスタンスが稼働しているか確認

### 問題: ワークフローが取得できない

**解決策**:
1. ワークフローIDが正しいか確認
2. API Keyに適切な権限があるか確認
3. ヘルスチェックを実行して接続状態を確認

---

## 📋 設定ファイルテンプレート

### 最小構成（`.mcp/config.json`）

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["-y", "n8n-mcp@2.22.11"],
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your-api-key-here",
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error"
      }
    }
  }
}
```

### NVM使用時（推奨）

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "/Users/your-username/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "n8n-mcp@2.22.11"],
      "env": {
        "N8N_API_URL": "${N8N_API_URL:-https://your-n8n-instance.com}",
        "N8N_API_KEY": "${N8N_API_KEY}",
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true"
      }
    }
  }
}
```

---

## 🎯 よく使うコマンド

### ワークフロー操作

```javascript
// 一覧取得
mcp_n8n-mcp_n8n_list_workflows({limit: 10})

// 取得
mcp_n8n-mcp_n8n_get_workflow({id: "workflow-id"})

// 更新（部分）
mcp_n8n-mcp_n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [...]
})

// 削除
mcp_n8n-mcp_n8n_delete_workflow({id: "workflow-id"})
```

### 実行管理

```javascript
// 実行一覧
mcp_n8n-mcp_n8n_list_executions({limit: 10})

// 実行詳細
mcp_n8n-mcp_n8n_get_execution({id: "execution-id"})
```

### 検証

```javascript
// ワークフロー検証
mcp_n8n-mcp_n8n_validate_workflow({id: "workflow-id"})

// 自動修正
mcp_n8n-mcp_n8n_autofix_workflow({id: "workflow-id"})
```

---

## 📞 サポート

詳細なトラブルシューティングは以下を参照:
- [n8n MCP 動作状態ドキュメント](./mcp-n8n-working-state-documentation.md)
- [n8n MCP トラブルシューティング完全ガイド](./troubleshooting-n8n-mcp-comprehensive-guide.md)

