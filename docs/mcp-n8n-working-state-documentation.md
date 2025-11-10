# n8n MCP 動作状態ドキュメント

**作成日**: 2025-11-09  
**目的**: MCPを使用したn8nへの直接アクセスが正常に動作している状態を記録し、再現性を高める  
**ステータス**: ✅ 動作確認済み

---

## 📋 目次

1. [現在の動作状態](#現在の動作状態)
2. [設定ファイル構成](#設定ファイル構成)
3. [環境変数設定](#環境変数設定)
4. [動作確認手順](#動作確認手順)
5. [利用可能なツール一覧](#利用可能なツール一覧)
6. [再現性を高めるためのチェックリスト](#再現性を高めるためのチェックリスト)
7. [トラブルシューティング](#トラブルシューティング)

---

## ✅ 現在の動作状態

### 動作確認日時
- **確認日時**: 2025-11-09 03:41:15 UTC
- **動作状態**: ✅ 正常動作中

### 接続情報
- **n8n API URL**: `https://n8n-python-production-344b.up.railway.app`
- **API接続状態**: ✅ 接続成功
- **レスポンス時間**: 637ms（ヘルスチェック時）

### バージョン情報
- **n8n-mcp バージョン**: 2.22.6（実行中）
- **設定ファイル指定バージョン**: 2.22.11
- **最新バージョン**: 2.22.13
- **Node.js バージョン**: v24.1.0
- **プラットフォーム**: darwin (macOS)

### ツール利用状況
- **総ツール数**: 38個
- **ドキュメントツール**: 22個（有効）
- **管理ツール**: 16個（有効）
- **ワークフロー管理**: ✅ 利用可能
- **実行管理**: ✅ 利用可能

---

## 📁 設定ファイル構成

### 設定ファイルの場所と優先順位

MCP設定ファイルは以下の順序で読み込まれます：

1. **`.mcp/config.json`** (プロジェクト共通設定) ← **現在使用中**
2. **`.mcp.json`** (プロジェクトルート設定)
3. **`.cursor/mcp.json`** (Cursor専用設定)
4. **`~/Library/Application Support/Claude/claude_desktop_config.json`** (Claude Desktop設定)

### 現在の設定ファイル内容

#### `.mcp/config.json` (推奨設定)

```json
{
  "mcpServers": {
    "notion": {
      "command": "/Users/yuichiroooosuger/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer ${NOTION_API_TOKEN}\", \"Notion-Version\": \"2022-06-28\"}"
      }
    },
    "n8n-mcp": {
      "command": "/Users/yuichiroooosuger/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "n8n-mcp@2.22.11"],
      "env": {
        "N8N_API_URL": "${N8N_API_URL:-https://n8n-python-production-344b.up.railway.app}",
        "N8N_API_KEY": "${N8N_API_KEY}",
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true"
      }
    }
  }
}
```

#### `.mcp.json` (プロジェクトルート設定)

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "/Users/yuichiroooosuger/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "n8n-mcp@2.22.11"],
      "env": {
        "N8N_API_URL": "${N8N_API_URL:-https://n8n-python-production-344b.up.railway.app}",
        "N8N_API_KEY": "${N8N_API_KEY}",
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true"
      }
    }
  }
}
```

### 設定の重要なポイント

1. **バージョン指定**: `n8n-mcp@2.22.11` を明示的に指定
2. **npxパス**: NVMを使用している場合はフルパスを指定
3. **環境変数のフォールバック**: `${N8N_API_URL:-default}` 形式でデフォルト値を設定
4. **ログレベル**: `error` に設定してログを抑制
5. **URL末尾**: スラッシュを付けない

---

## 🔐 環境変数設定

### 必要な環境変数

```bash
# n8n API URL（必須）
export N8N_API_URL="https://n8n-python-production-344b.up.railway.app"

# n8n API Key（必須）
export N8N_API_KEY="your-api-key-here"
```

### 現在の環境変数状態

- **N8N_API_URL**: ✅ 設定済み (`https://n8n-python-production-344b.up.railway.app`)
- **N8N_API_KEY**: ✅ 設定済み（先頭20文字: `eyJhbGciOiJIUzI1NiIs`）

### 環境変数の確認方法

```bash
# API URLの確認
echo $N8N_API_URL

# API Keyの確認（先頭のみ表示）
echo $N8N_API_KEY | head -c 20
```

---

## 🔍 動作確認手順

### 1. 基本ヘルスチェック

```javascript
// MCPツールを使用してヘルスチェックを実行
mcp_n8n-mcp_n8n_health_check()
```

**期待される結果**:
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "apiUrl": "https://n8n-python-production-344b.up.railway.app",
    "mcpVersion": "2.22.6",
    "performance": {
      "responseTimeMs": 637
    }
  }
}
```

### 2. 詳細診断

```javascript
// 詳細診断を実行
mcp_n8n-mcp_n8n_diagnostic({verbose: true})
```

**確認項目**:
- ✅ `apiConfiguration.configured`: `true`
- ✅ `apiConfiguration.status.connected`: `true`
- ✅ `toolsAvailability.totalAvailable`: `38`
- ✅ `toolsAvailability.managementTools.enabled`: `true`

### 3. ワークフロー一覧取得

```javascript
// ワークフロー一覧を取得
mcp_n8n-mcp_n8n_list_workflows({limit: 5})
```

**期待される結果**:
- ワークフローのリストが返される
- 各ワークフローに `id`, `name`, `active`, `createdAt` などの情報が含まれる

### 4. ワークフロー取得

```javascript
// 特定のワークフローを取得
mcp_n8n-mcp_n8n_get_workflow_minimal({id: "4Oo5LL3KMKVn8gUJ"})
```

**期待される結果**:
- ワークフローの基本情報が返される

---

## 🛠️ 利用可能なツール一覧

### ワークフロー管理ツール（10個）

1. `n8n_create_workflow` - 新しいワークフローを作成
2. `n8n_get_workflow` - ワークフローIDで取得
3. `n8n_get_workflow_details` - 詳細情報を取得
4. `n8n_get_workflow_structure` - 構造のみ取得
5. `n8n_get_workflow_minimal` - 最小情報を取得
6. `n8n_update_full_workflow` - 完全更新
7. `n8n_update_partial_workflow` - 部分更新
8. `n8n_delete_workflow` - ワークフロー削除
9. `n8n_list_workflows` - ワークフロー一覧
10. `n8n_validate_workflow` - ワークフロー検証

### 実行管理ツール（4個）

1. `n8n_trigger_webhook_workflow` - Webhook経由で実行
2. `n8n_get_execution` - 実行詳細を取得
3. `n8n_list_executions` - 実行一覧
4. `n8n_delete_execution` - 実行記録削除

### システムツール（2個）

1. `n8n_health_check` - API接続確認
2. `n8n_list_available_tools` - 利用可能ツール一覧

### ドキュメントツール（22個）

- `search_nodes` - ノード検索
- `get_node_info` - ノード情報取得
- `validate_node_operation` - ノード設定検証
- `search_templates` - テンプレート検索
- `get_template` - テンプレート取得
- など

---

## ✅ 再現性を高めるためのチェックリスト

### 初期セットアップ

- [ ] Node.js v22.20.0以上がインストールされている
- [ ] NVMがインストールされ、正しいバージョンが使用されている
- [ ] 環境変数 `N8N_API_URL` が設定されている
- [ ] 環境変数 `N8N_API_KEY` が設定されている
- [ ] `.mcp/config.json` または `.mcp.json` が存在する
- [ ] 設定ファイルのJSON形式が正しい
- [ ] n8n-mcpのバージョンが明示的に指定されている

### 動作確認

- [ ] `n8n_health_check` が成功する
- [ ] `n8n_diagnostic` で接続状態が `connected: true` になる
- [ ] `n8n_list_workflows` でワークフロー一覧が取得できる
- [ ] `n8n_get_workflow` でワークフローが取得できる
- [ ] `n8n_update_partial_workflow` でワークフローが更新できる
- [ ] `n8n_delete_workflow` でワークフローが削除できる

### 設定ファイルの確認

- [ ] 設定ファイルのパスが正しい
- [ ] `command` が正しいnpxパスを指している
- [ ] `args` にバージョン指定がある（`n8n-mcp@2.22.11`）
- [ ] `env.N8N_API_URL` が設定されている
- [ ] `env.N8N_API_KEY` が設定されている
- [ ] `env.MCP_MODE` が `stdio` に設定されている
- [ ] `env.LOG_LEVEL` が `error` に設定されている

### 環境変数の確認

```bash
# 確認コマンド
echo "N8N_API_URL: $N8N_API_URL"
echo "N8N_API_KEY: ${N8N_API_KEY:0:20}..."
node --version
which npx
```

---

## 🔧 トラブルシューティング

### MCPが動作しない場合

#### 1. 設定ファイルの確認

```bash
# 設定ファイルの存在確認
ls -la .mcp/config.json
ls -la .mcp.json

# JSON形式の確認
cat .mcp/config.json | jq .
```

#### 2. 環境変数の確認

```bash
# 環境変数が設定されているか確認
env | grep N8N
```

#### 3. npxの確認

```bash
# npxが正しく動作するか確認
npx -y n8n-mcp@2.22.11 --version

# NVMを使用している場合、フルパスを確認
/Users/yuichiroooosuger/.nvm/versions/node/v22.20.0/bin/npx --version
```

#### 4. Cursor/Claude Desktopの再起動

設定ファイルを変更した場合は、必ずCursorまたはClaude Desktopを再起動してください。

### API接続エラーの場合

#### 1. URLの確認

- URL末尾にスラッシュがないか確認
- HTTPSが正しく設定されているか確認
- Railwayのデプロイ状態を確認

#### 2. API Keyの確認

- API Keyが正しく設定されているか確認
- API Keyが有効期限内か確認
- n8nインスタンスでAPI Keyが有効化されているか確認

#### 3. ネットワーク接続の確認

```bash
# n8n APIへの接続確認
curl -I https://n8n-python-production-344b.up.railway.app/healthz
```

### ツールが利用できない場合

#### 1. バージョンの確認

```javascript
// 診断を実行してバージョンを確認
mcp_n8n-mcp_n8n_diagnostic({verbose: true})
```

#### 2. キャッシュのクリア

```bash
# npmキャッシュのクリア
npm cache clean --force

# npxキャッシュのクリア（必要に応じて）
rm -rf ~/.npm/_npx
```

#### 3. バージョンの更新

```bash
# 最新バージョンに更新
npm install -g n8n-mcp@latest

# または特定バージョンに更新
npm install -g n8n-mcp@2.22.13
```

---

## 📝 ベストプラクティス

### 1. バージョン固定

設定ファイルでバージョンを明示的に指定することで、予期しない動作を防ぎます：

```json
"args": ["-y", "n8n-mcp@2.22.11"]
```

### 2. 環境変数のフォールバック

設定ファイルでデフォルト値を設定することで、環境変数が未設定でも動作します：

```json
"N8N_API_URL": "${N8N_API_URL:-https://n8n-python-production-344b.up.railway.app}"
```

### 3. ログレベルの設定

不要なログを抑制するために、`LOG_LEVEL` を `error` に設定：

```json
"LOG_LEVEL": "error"
```

### 4. 定期的な動作確認

定期的にヘルスチェックを実行して、接続状態を確認：

```javascript
mcp_n8n-mcp_n8n_health_check()
```

### 5. 設定ファイルのバックアップ

重要な設定ファイルはバックアップを取っておく：

```bash
cp .mcp/config.json .mcp/config.json.backup
```

---

## 🔄 更新履歴

- **2025-11-09**: 初版作成、動作状態を記録

---

## 📚 関連ドキュメント

- [n8n MCP トラブルシューティング完全ガイド](./troubleshooting-n8n-mcp-comprehensive-guide.md)
- [n8n API直接アクセスガイド](./n8n-api-direct-access-guide.md)
- [MCP統合ガイド](./mcp-integration-guide.md)

---

## 💡 注意事項

1. **API Keyの管理**: API Keyは機密情報です。設定ファイルに直接記載する場合は、Gitにコミットしないよう注意してください。

2. **バージョン管理**: n8n-mcpのバージョンは定期的に更新されるため、最新バージョンへの更新を検討してください。

3. **接続状態の確認**: 長時間使用していない場合や、エラーが発生した場合は、まずヘルスチェックを実行してください。

4. **設定ファイルの優先順位**: 複数の設定ファイルが存在する場合、優先順位に注意してください。

---

**最終更新**: 2025-11-09  
**確認者**: AI Assistant  
**動作状態**: ✅ 正常動作中

