# 既存MCPでn8nワークフロー管理の代替可能性調査

**作成日**: 2025-11-08  
**目的**: 現在利用可能なMCPでn8n APIを呼び出せるか調査

---

## 🔍 現在利用可能なMCP

### 確認済みMCP

1. **n8n-mcp**
   - ステータス: ✅ 接続済み
   - ワークフロー管理機能: ❌ 利用不可
   - ドキュメントツール: ✅ 利用可能

2. **notion**
   - ステータス: ✅ 接続済み
   - 用途: Notion API専用
   - HTTP Request機能: ❌ なし

---

## 📋 調査結果

### Notion MCPでの代替可能性

**結論**: ❌ **代替不可**

**理由**:
- Notion MCPはNotion API専用のツール
- HTTP Requestや汎用API呼び出し機能は提供されていない
- n8n APIを呼び出す機能はない

**利用可能なNotion MCPツール**:
- `mcp_notion_API-get-user` - Notionユーザー取得
- `mcp_notion_API-get-users` - Notionユーザー一覧
- `mcp_notion_API-post-database-query` - Notionデータベースクエリ
- `mcp_notion_API-post-search` - Notion検索
- `mcp_notion_API-retrieve-a-page` - Notionページ取得
- `mcp_notion_API-patch-page` - Notionページ更新
- `mcp_notion_API-post-page` - Notionページ作成
- など（すべてNotion API専用）

---

## 🔄 代替案

### 案1: 追加のMCPサーバーを導入

#### HTTP Request用MCPサーバー

一般的なHTTP Requestを実行できるMCPサーバーは存在しない可能性が高い。MCPサーバーは通常、特定のサービス（Notion、GitHub、Vercelなど）専用に設計されている。

#### カスタムMCPサーバーの作成

n8n APIをラップするカスタムMCPサーバーを作成することは可能だが、開発時間がかかる。

---

### 案2: n8n-mcpの設定を確認

**推奨**: n8n-mcpのワークフロー管理機能が使えない原因を特定し、修正する

**確認事項**:
1. `.cursor/mcp.json`で`N8N_API_URL`と`N8N_API_KEY`が正しく設定されているか
2. 環境変数が正しく読み込まれているか
3. MCPサーバーが管理モードで起動しているか

**確認コマンド**:
```bash
# 設定ファイル確認
cat .cursor/mcp.json | grep -A 10 "n8n-mcp"

# 環境変数確認
echo $N8N_API_URL
echo $N8N_API_KEY
```

---

### 案3: n8nワークフロー内でn8n APIを呼び出す

**推奨**: ✅ **最も実用的**

n8nワークフロー内でHTTP RequestノードまたはCodeノードを使用してn8n APIを直接呼び出す。

**メリット**:
- 追加のMCPサーバー不要
- n8nワークフロー内で完結
- エラーハンドリングが容易

**実装例**:
```json
{
  "method": "GET",
  "url": "https://n8n-python-production-344b.up.railway.app/api/v1/workflows",
  "sendHeaders": true,
  "headerParameters": {
    "X-N8N-API-KEY": "={{$env.N8N_API_KEY}}"
  }
}
```

詳細は `docs/n8n-api-direct-access-guide.md` を参照。

---

## 📊 比較表

| 方法 | 実現可能性 | 工数 | 推奨度 |
|------|----------|------|--------|
| **Notion MCPで代替** | ❌ 不可能 | - | - |
| **他のMCPで代替** | ⚠️ 困難（適切なMCPが存在しない） | 高 | ⭐ |
| **n8n-mcp設定修正** | ✅ 可能 | 低 | ⭐⭐⭐⭐⭐ |
| **n8nワークフロー内でAPI呼び出し** | ✅ 可能 | 低 | ⭐⭐⭐⭐⭐ |
| **カスタムMCP作成** | ✅ 可能 | 高 | ⭐⭐ |

---

## ✅ 結論

### 既存MCPでの代替可能性

**Notion MCP**: ❌ **代替不可**
- Notion API専用のため、n8n APIを呼び出す機能はない

**n8n-mcp**: ⚠️ **設定確認が必要**
- ワークフロー管理機能が使えない原因を特定し、修正する必要がある

### 推奨アプローチ

1. **最優先**: n8n-mcpの設定を確認し、ワークフロー管理機能を有効化
   - `.cursor/mcp.json`で`N8N_API_URL`と`N8N_API_KEY`を確認
   - 環境変数が正しく設定されているか確認
   - Cursorを再起動

2. **代替案**: n8nワークフロー内でn8n APIを直接呼び出す
   - HTTP RequestノードまたはCodeノードを使用
   - 詳細は `docs/n8n-api-direct-access-guide.md` を参照

3. **長期的**: カスタムMCPサーバーを作成
   - 開発時間がかかるが、再利用可能

---

## 🔍 次のステップ

1. **n8n-mcp設定の確認**
   ```bash
   cat .cursor/mcp.json | grep -A 10 "n8n-mcp"
   ```

2. **環境変数の確認**
   ```bash
   echo $N8N_API_URL
   echo $N8N_API_KEY
   ```

3. **設定修正後、Cursorを再起動**

4. **再テスト**
   - n8n-mcpのワークフロー管理機能が使えるか確認

---

**最終更新**: 2025-11-08


