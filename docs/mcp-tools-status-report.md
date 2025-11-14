# MCPツール利用可能状況レポート

**作成日**: 2025-11-09  
**調査元**: README.md、設定ファイル、実際の動作確認  
**環境**: Cursor (Claude Code)

---

## 📊 サマリー

| カテゴリ | 設定済み | 動作確認済み | 未設定/未テスト |
|---------|---------|------------|---------------|
| **n8n関連** | 2 | 2 | 0 |
| **ドキュメント** | 3 | 3 | 0 |
| **データベース** | 1 | 1 | 1 |
| **その他** | 1 | 1 | 7 |
| **合計** | **7** | **7** | **8** |

---

## ✅ 現在利用可能なMCPツール

### 1. n8n-mcp ✅ **完全動作中**

**設定ファイル**: `.mcp/config.json`  
**バージョン**: 2.22.6（実行中）、2.22.11（設定）、2.22.13（最新）  
**ステータス**: ✅ 正常動作

#### 利用可能なツール（合計38個）

**ワークフロー管理（10個）**:
- `n8n_create_workflow` - ワークフロー作成
- `n8n_get_workflow` - ワークフロー取得
- `n8n_get_workflow_details` - 詳細情報取得
- `n8n_get_workflow_structure` - 構造取得
- `n8n_get_workflow_minimal` - 最小情報取得
- `n8n_update_workflow` - ワークフロー更新
- `n8n_delete_workflow` - ワークフロー削除
- `n8n_list_workflows` - ワークフロー一覧
- `n8n_validate_workflow` - ワークフロー検証
- `n8n_autofix_workflow` - 自動修正

**実行管理（4個）**:
- `n8n_trigger_webhook_workflow` - Webhook経由実行
- `n8n_get_execution` - 実行詳細取得
- `n8n_list_executions` - 実行一覧
- `n8n_delete_execution` - 実行削除

**システム（2個）**:
- `n8n_health_check` - ヘルスチェック ✅ 動作確認済み
- `n8n_list_available_tools` - 利用可能ツール一覧

**ドキュメントツール（22個）**:
- `search_nodes` - ノード検索
- `get_node_info` - ノード情報取得
- `get_node_essentials` - ノード基本情報
- `list_nodes` - ノード一覧
- `search_templates` - テンプレート検索
- `get_template` - テンプレート取得
- `list_templates` - テンプレート一覧
- その他15個のドキュメント関連ツール

#### データベース統計
- **総ノード数**: 541個
- **総テンプレート数**: 2,653個
- **AIツール**: 271個
- **トリガー**: 108個
- **ドキュメントカバレッジ**: 87%（470ノード）

#### 接続情報
- **n8n API URL**: `https://n8n-python-production-344b.up.railway.app`
- **API接続状態**: ✅ 接続成功
- **レスポンス時間**: 571ms（ヘルスチェック時）

#### 注意事項
- ⚠️ バージョン更新推奨: 現在2.22.6 → 最新2.22.13
- 更新コマンド: `npm install -g n8n-mcp@2.22.13`

---

### 2. notion ✅ **動作確認済み**

**設定ファイル**: `.mcp/config.json`  
**ステータス**: ✅ 正常動作

#### 利用可能なツール
- `mcp_notion_API-get-user` - ユーザー取得
- `mcp_notion_API-get-users` - ユーザー一覧
- `mcp_notion_API-get-self` - 自分の情報取得 ✅ 動作確認済み
- `mcp_notion_API-post-database-query` - データベースクエリ
- `mcp_notion_API-post-search` - 検索
- `mcp_notion_API-get-block-children` - ブロック子要素取得
- `mcp_notion_API-patch-block-children` - ブロック子要素追加
- `mcp_notion_API-retrieve-a-block` - ブロック取得
- `mcp_notion_API-update-a-block` - ブロック更新
- `mcp_notion_API-delete-a-block` - ブロック削除
- `mcp_notion_API-retrieve-a-page` - ページ取得
- `mcp_notion_API-patch-page` - ページ更新
- `mcp_notion_API-post-page` - ページ作成
- `mcp_notion_API-create-a-database` - データベース作成
- `mcp_notion_API-update-a-database` - データベース更新
- `mcp_notion_API-retrieve-a-database` - データベース取得
- `mcp_notion_API-retrieve-a-page-property` - ページプロパティ取得
- `mcp_notion_API-retrieve-a-comment` - コメント取得
- `mcp_notion_API-create-a-comment` - コメント作成

---

### 3. n8n-workflows-docs ✅ **動作確認済み**

**設定方法**: gitmcp.io経由（README.mdに記載）  
**ステータス**: ✅ 正常動作

#### 利用可能なツール
- `mcp_n8n-workflows-docs_fetch_n8n_workflows_documentation` - ドキュメント取得 ✅
- `mcp_n8n-workflows-docs_search_n8n_workflows_docs` - ドキュメント検索 ✅
- `mcp_n8n-workflows-docs_search_n8n_workflows_code` - コード検索
- `mcp_n8n-workflows-docs_fetch_generic_url_content` - URLコンテンツ取得

**特徴**:
- 世界最大のn8nワークフローコレクション（2,053ワークフロー）へのアクセス
- 365ユニークインテグレーションの活用
- カテゴリー別・トリガー別・複雑度別の高度な検索

---

### 4. n8n-workflows ✅ **動作確認済み**

**設定方法**: gitmcp.io経由  
**ステータス**: ✅ 正常動作

#### 利用可能なツール
- `mcp_n8n-workflows_fetch_n8n_workflows_documentation` - ドキュメント取得 ✅
- `mcp_n8n-workflows_search_n8n_workflows_docs` - ドキュメント検索
- `mcp_n8n-workflows_search_n8n_workflows_code` - コード検索
- `mcp_n8n-workflows_fetch_generic_url_content` - URLコンテンツ取得

---

### 5. docs-mcp-server ✅ **動作確認済み**

**ステータス**: ✅ 正常動作

#### 利用可能なツール
- `mcp_docs-mcp-server_fetch_docs_mcp_server_docs` - ドキュメント取得 ✅
- `mcp_docs-mcp-server_search_docs_mcp_server_docs` - ドキュメント検索 ✅
- `mcp_docs-mcp-server_search_docs_mcp_server_code` - コード検索
- `mcp_docs-mcp-server_fetch_generic_url_content` - URLコンテンツ取得

---

### 6. mcp-sequential-thinking ✅ **動作確認済み**

**ステータス**: ✅ 正常動作

#### 利用可能なツール
- `mcp_mcp-sequential-thinking_sequentialthinking` - 段階的思考プロセス ✅

**用途**:
- 複雑な問題の段階的分析
- 設計と実装の計画
- エラーハンドリング設計

---

## ⚠️ READMEに記載されているが未設定/未テストのMCP

### 1. context7-docs ⚠️
- **状態**: ツールが見つからない
- **README記載**: docs/mcp/README.mdに記載あり

### 2. chrome-devtools ⚠️
- **状態**: ツールが見つからない
- **README記載**: docs/mcp/README.mdに記載あり

### 3. playwright ⚠️
- **状態**: ツールが見つからない
- **README記載**: docs/mcp/README.mdに記載あり
- **用途**: E2Eテスト、スクレイピング

### 4. vercel ⚠️
- **状態**: ツールが見つからない
- **README記載**: docs/mcp/README.mdに記載あり

### 5. github ⚠️
- **状態**: ツールが見つからない
- **README記載**: docs/mcp/README.mdに記載あり
- **用途**: リポジトリ操作、PR作成

### 6. obsidian ⚠️
- **状態**: ツールが見つからない
- **README記載**: docs/mcp/README.mdに記載あり

### 7. supabase ⚠️
- **状態**: ツールが見つからない
- **README記載**: docs/mcp/README.mdに記載あり
- **用途**: データベース管理

### 8. analytics-mcp ⚠️
- **状態**: ツールが見つからない
- **README記載**: docs/mcp/README.mdに記載あり
- **用途**: Google Analytics

---

## 📋 設定ファイルの状況

### 現在の設定ファイル

#### `.mcp/config.json`（推奨設定）
```json
{
  "mcpServers": {
    "notion": {
      "command": "/Users/yuichiroooosuger/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{...}"
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

#### `.mcp.json`（プロジェクトルート）
- n8n-mcpのみ設定

### gitmcp.io経由の設定（README.mdに記載）

#### Claude Desktop設定
```json
{
  "mcpServers": {
    "n8n-workflows": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://gitmcp.io/plus61/n8n-workflows"]
    }
  }
}
```

#### Cursor設定
```json
{
  "mcpServers": {
    "n8n-workflows": {
      "command": "/Users/[ユーザー名]/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "mcp-remote", "https://gitmcp.io/plus61/n8n-workflows"]
    }
  }
}
```

---

## 🎯 推奨事項

### 1. n8n-mcpのバージョン更新
```bash
npm install -g n8n-mcp@2.22.13
```

### 2. 未設定MCPの追加検討
READMEに記載されている以下のMCPの追加を検討：
- **github** - リポジトリ操作、PR作成
- **playwright** - E2Eテスト、スクレイピング
- **supabase** - データベース管理

### 3. 設定ファイルの統一
- `.mcp/config.json`を推奨設定として使用
- gitmcp.io経由のMCPも`.mcp/config.json`に追加を検討

---

## 📚 関連ドキュメント

- [README.md](../README.md) - プロジェクト全体の概要
- [docs/mcp/README.md](mcp/README.md) - MCP使用ガイド集
- [MCP_SETUP.md](../MCP_SETUP.md) - MCPセットアップガイド
- [docs/mcp-n8n-quick-reference.md](mcp-n8n-quick-reference.md) - n8n MCPクイックリファレンス
- [docs/mcp-all-servers-test-report.md](mcp-all-servers-test-report.md) - 全MCPサーバーテストレポート

---

## ✅ 動作確認チェックリスト

### n8n-mcp
- [x] ヘルスチェック成功
- [x] ワークフロー一覧取得成功
- [x] データベース統計取得成功
- [x] 38個のツールが利用可能

### notion
- [x] API接続成功
- [x] ユーザー情報取得成功

### ドキュメント系MCP
- [x] n8n-workflows-docs動作確認
- [x] n8n-workflows動作確認
- [x] docs-mcp-server動作確認

### sequential-thinking
- [x] Sequential Thinking動作確認

---

**最終更新**: 2025-11-09




