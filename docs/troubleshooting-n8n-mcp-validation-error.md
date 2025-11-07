# n8n MCP APIバリデーションエラー - Claude Code（Cursor）での対処法

**作成日**: 2025-11-07  
**カテゴリ**: n8n, n8n-mcp, Claude Code, Cursor, トラブルシューティング  
**ステータス**: 検証済み

---

## 🎯 問題の概要

Claude Code（Cursor）から`n8n_update_partial_workflow`を呼び出す際、以下のバリデーションエラーが発生：

```json
{
  "success": false,
  "error": "Invalid request: request/body must NOT have additional properties",
  "code": "VALIDATION_ERROR"
}
```

---

## 🔍 根本原因

### 1. n8n Public APIの制限

**公式の問題**: [Issue #18574](https://github.com/n8n-io/n8n/issues/18574)

n8n Public APIには以下の制限があります：

```yaml
制限事項:
  - パーシャルアップデート（PATCH）非サポート
  - プロパティ削除は不可能（null/undefinedがバリデーションエラー）
  - ワークフロー更新は完全置換（PUT）のみ

必須手順:
  1. GET /workflows/:id で全体取得
  2. JSONを手動編集
  3. PUT /workflows/:id で完全置換
```

### 2. MCPツールのバージョン問題

- **現在のバージョン**: v2.22.6（診断結果）
- **グローバルインストール**: v2.22.8
- **最新バージョン**: v2.22.11
- **問題**: 古いバージョンでリクエスト形式がn8n APIの期待と不一致

### 3. Claude Code（Cursor）での実行環境

- Cursorは`npx -y n8n-mcp`を使用してMCPサーバーを起動
- 実行時にダウンロードされるバージョンが古い可能性
- MCP設定ファイル（`.cursor/mcp.json`）でバージョン指定が必要

---

## ✅ 解決策

### 方法1: `n8n_update_full_workflow`を使用（推奨・確実）

**部分更新の代わりに完全更新を使用**

```javascript
// ✅ 推奨パターン
// 1. 現在のワークフロー取得
const workflow = await mcp__n8n-mcp__n8n_get_workflow({ 
  id: "SDO8X6oR5W5y2s6A" 
});

// 2. 必要な修正を適用
const webhookNode = workflow.nodes.find(
  n => n.id === "c86282e3-6130-4bfb-8607-9e5d7dacd398"
);
if (webhookNode) {
  webhookNode.onError = "continueRegularOutput";
}

const notionNode = workflow.nodes.find(
  n => n.id === "6024339e-fac2-4ab2-b2e3-ea403ed01e60"
);
if (notionNode) {
  notionNode.onError = "continueRegularOutput";
}

// 3. 全体を更新
await mcp__n8n-mcp__n8n_update_full_workflow({
  id: "SDO8X6oR5W5y2s6A",
  name: workflow.name,
  nodes: workflow.nodes,
  connections: workflow.connections
});
```

**メリット**:
- 確実に動作する
- n8n APIの仕様に完全準拠
- バリデーションエラーが発生しない

**デメリット**:
- 全体取得→修正→全体更新のステップが必要
- 部分更新より処理が重い

---

### 方法2: MCPツールを最新バージョンに更新

#### 2.1 CursorのMCP設定を更新

`.cursor/mcp.json`を作成/更新：

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["-y", "n8n-mcp@2.22.11"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "https://n8n-python-production-344b.up.railway.app",
        "N8N_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**重要**: バージョンを明示的に指定（`n8n-mcp@2.22.11`）

#### 2.2 Cursorを再起動

設定変更後、Cursorを完全に再起動：
1. Cursorを終了
2. 再度起動
3. MCP接続を確認

#### 2.3 グローバルインストールを更新（オプション）

```bash
npm install -g n8n-mcp@2.22.11
```

ただし、Cursorは`npx -y`を使用するため、グローバルインストールは影響しない可能性があります。

---

### 方法3: バージョン固定のnpxキャッシュクリア

```bash
# npxキャッシュをクリア
rm -rf ~/.npm/_npx

# 最新バージョンを強制ダウンロード
npx -y n8n-mcp@latest --version
```

---

## 🔧 トラブルシューティング手順

### Step 1: 現在のMCPバージョンを確認

```javascript
// Claude Codeで実行
mcp__n8n-mcp__n8n_diagnostic({verbose: true})
```

**確認項目**:
- `versionInfo.current`: 現在のバージョン
- `versionInfo.latest`: 最新バージョン
- `versionInfo.upToDate`: 更新が必要か

### Step 2: MCP設定ファイルの確認

```bash
# CursorのMCP設定ファイルを確認
cat ~/.cursor/mcp.json
# または
cat .cursor/mcp.json
```

**確認項目**:
- `args`にバージョン指定があるか
- 環境変数が正しく設定されているか

### Step 3: エラーの詳細を確認

```javascript
// エラーが発生した操作を再実行
mcp__n8n-mcp__n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [...],
  validateOnly: true  // 検証のみ実行
})
```

---

## 📝 ベストプラクティス

### 1. ワークフロー更新時の推奨パターン

```javascript
// ✅ 推奨: 完全更新を使用
async function updateWorkflow(workflowId, updates) {
  // 1. 現在のワークフロー取得
  const workflow = await mcp__n8n-mcp__n8n_get_workflow({ id: workflowId });
  
  // 2. 修正を適用
  updates.forEach(update => {
    const node = workflow.nodes.find(n => n.id === update.nodeId);
    if (node) {
      Object.assign(node, update.changes);
    }
  });
  
  // 3. 完全更新
  return await mcp__n8n-mcp__n8n_update_full_workflow({
    id: workflowId,
    name: workflow.name,
    nodes: workflow.nodes,
    connections: workflow.connections
  });
}
```

### 2. エラーハンドリング

```javascript
try {
  await mcp__n8n-mcp__n8n_update_partial_workflow({...});
} catch (error) {
  if (error.code === "VALIDATION_ERROR") {
    // バリデーションエラーの場合、完全更新にフォールバック
    console.log("部分更新失敗、完全更新に切り替え");
    await updateWorkflowWithFullUpdate(...);
  } else {
    throw error;
  }
}
```

### 3. MCP設定のバージョン管理

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["-y", "n8n-mcp@2.22.11"],  // ← バージョン固定
      "env": {...}
    }
  }
}
```

---

## 🚨 既知の制限事項

1. **n8n APIの制限**
   - パーシャルアップデート非サポート
   - プロパティ削除不可
   - 完全置換のみ

2. **MCPツールの制限**
   - 古いバージョンでリクエスト形式が不一致
   - バージョン2.22.11以降で改善される可能性

3. **Cursorの制限**
   - MCP設定変更後、再起動が必要
   - `npx -y`がキャッシュを使用する可能性

---

## 📚 関連ドキュメント

- [n8n MCP統合ガイド](./mcp-integration-guide.md)
- [WF7 Phase4 トラブルシューティングガイド](./knowledge/wf7-phase4-troubleshooting-guide.md)
- [continueOnFail削除失敗の原因と対処法](../n8n-mcp_continueOnFail削除失敗の原因と対処法.md)

---

## ✅ チェックリスト

- [ ] MCP設定ファイル（`.cursor/mcp.json`）にバージョン指定があるか確認
- [ ] `n8n_update_full_workflow`を使用する方法を試したか
- [ ] Cursorを再起動したか
- [ ] `n8n_diagnostic`でバージョンを確認したか
- [ ] エラーメッセージの詳細を確認したか

---

**最終更新**: 2025-11-07  
**次回確認**: MCPツール v2.22.11以降で問題が解決されているか確認

