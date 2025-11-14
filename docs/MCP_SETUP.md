# MCPセットアップガイド

**目的**: MCPを使用してn8nに直接アクセスするためのセットアップガイド

---

## 🎯 このガイドの目的

このガイドでは、MCP（Model Context Protocol）を使用してCursor/Claude Desktopから直接n8nのワークフローを操作するための設定方法を説明します。

## ⚡ クイックスタート（3ステップ）

### Step 1: 環境変数の設定

```bash
# n8n API URLを設定
export N8N_API_URL="https://n8n-python-production-344b.up.railway.app"

# n8n API Keyを設定
export N8N_API_KEY="your-api-key-here"
```

### Step 2: 設定ファイルの確認

プロジェクトには既に設定ファイルが用意されています：

- **`.mcp/config.json`** - プロジェクト共通設定（推奨）
- **`.mcp.json`** - プロジェクトルート設定

設定ファイルが存在しない場合は、テンプレートをコピー：

```bash
cp .mcp/config.json.template .mcp/config.json
```

### Step 3: 動作確認

Cursor/Claude Desktopを再起動後、以下で動作確認：

```javascript
mcp_n8n-mcp_n8n_health_check()
```

**期待される結果**: `status: "ok"`

---

## 📚 詳細ドキュメント

### クイックリファレンス

- **[n8n MCP クイックリファレンス](docs/mcp-n8n-quick-reference.md)**
  - 30秒で動作確認
  - よく使うコマンド
  - よくある問題と即座の解決策

### 詳細ガイド

- **[n8n MCP 動作状態ドキュメント](docs/mcp-n8n-working-state-documentation.md)**
  - 現在の動作状態の記録
  - 設定ファイル構成
  - 環境変数設定
  - 再現性を高めるためのチェックリスト

- **[n8n MCP 動作確認ログ](docs/mcp-n8n-verification-log.md)**
  - 動作確認の記録テンプレート
  - 問題発生時の記録方法

### トラブルシューティング

- **[n8n MCP トラブルシューティング完全ガイド](docs/troubleshooting-n8n-mcp-comprehensive-guide.md)**
  - よくある問題と解決策
  - 診断手順

### 設定ディレクトリ

- **[.mcp/README.md](.mcp/README.md)** - MCP設定ディレクトリの説明
- **[.cursor/MCP_SETUP.md](.cursor/MCP_SETUP.md)** - CursorでのMCP設定ガイド

### インデックス

- **[n8n MCP ドキュメントインデックス](docs/mcp-n8n-index.md)** - すべてのドキュメントへのナビゲーション

---

## 🔍 動作確認チェックリスト

- [ ] 環境変数 `N8N_API_URL` が設定されている
- [ ] 環境変数 `N8N_API_KEY` が設定されている
- [ ] 設定ファイル（`.mcp/config.json` または `.mcp.json`）が存在する
- [ ] Cursor/Claude Desktopを再起動した
- [ ] `n8n_health_check` が成功する
- [ ] `n8n_list_workflows` でワークフローが取得できる

---

## 🛠️ 利用可能な機能

MCPを使用すると、以下の操作が可能です：

### ワークフロー管理

- ✅ ワークフローの作成
- ✅ ワークフローの取得・更新・削除
- ✅ ワークフローの検証
- ✅ ワークフローの自動修正

### 実行管理

- ✅ 実行履歴の確認
- ✅ Webhook経由での実行
- ✅ 実行詳細の取得

### ノード・テンプレート検索

- ✅ ノード情報の検索
- ✅ テンプレートの検索・取得
- ✅ ノード設定の検証

---

## 🆘 問題が発生した場合

1. **[クイックリファレンス](docs/mcp-n8n-quick-reference.md)** の「よくある問題と即座の解決策」を確認
2. **[動作状態ドキュメント](docs/mcp-n8n-working-state-documentation.md)** の「トラブルシューティング」を確認
3. **[トラブルシューティング完全ガイド](docs/troubleshooting-n8n-mcp-comprehensive-guide.md)** で詳細を確認

---

## 📝 設定ファイルの場所

MCP設定ファイルは以下の優先順位で読み込まれます：

1. **`.mcp/config.json`** ← **推奨**（プロジェクト共通）
2. **`.mcp.json`**（プロジェクトルート）
3. **`.cursor/mcp.json`**（Cursor専用）
4. **`~/Library/Application Support/Claude/claude_desktop_config.json`**（Claude Desktop）

---

**最終更新**: 2025-11-09


