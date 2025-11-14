# MCP設定ディレクトリ

このディレクトリには、MCP（Model Context Protocol）サーバーの設定ファイルが格納されています。

## 📁 ファイル構成

- **`config.json`** - 現在のMCP設定（実際に使用中）
- **`config.json.template`** - 設定ファイルのテンプレート（新規セットアップ用）

## 🚀 クイックセットアップ

### 1. 設定ファイルの確認

```bash
# 現在の設定を確認
cat .mcp/config.json
```

### 2. 環境変数の設定

```bash
# n8n API URLを設定
export N8N_API_URL="https://n8n-python-production-344b.up.railway.app"

# n8n API Keyを設定
export N8N_API_KEY="your-api-key-here"
```

### 3. 動作確認

```javascript
// MCPツールを使用してヘルスチェック
mcp_n8n-mcp_n8n_health_check()
```

## 📚 詳細ドキュメント

- **[n8n MCP クイックリファレンス](../docs/mcp-n8n-quick-reference.md)** - 30秒で動作確認
- **[n8n MCP 動作状態ドキュメント](../docs/mcp-n8n-working-state-documentation.md)** - 詳細な設定とトラブルシューティング
- **[n8n MCP ドキュメントインデックス](../docs/mcp-n8n-index.md)** - すべてのドキュメントへのナビゲーション

## ⚙️ 設定ファイルの場所

MCP設定ファイルは以下の優先順位で読み込まれます：

1. **`.mcp/config.json`** ← **推奨**（プロジェクト共通）
2. **`.mcp.json`**（プロジェクトルート）
3. **`.cursor/mcp.json`**（Cursor専用）
4. **`~/Library/Application Support/Claude/claude_desktop_config.json`**（Claude Desktop）

## 🔧 トラブルシューティング

MCPが動作しない場合は、以下を確認してください：

1. [クイックリファレンス](../docs/mcp-n8n-quick-reference.md) の「よくある問題と即座の解決策」
2. [動作状態ドキュメント](../docs/mcp-n8n-working-state-documentation.md) の「トラブルシューティング」
3. [トラブルシューティング完全ガイド](../docs/troubleshooting-n8n-mcp-comprehensive-guide.md)

## 📝 設定ファイルテンプレート

新規セットアップ時は `config.json.template` をコピーして使用：

```bash
cp .mcp/config.json.template .mcp/config.json
# その後、環境変数を設定して使用
```

---

**最終更新**: 2025-11-09




