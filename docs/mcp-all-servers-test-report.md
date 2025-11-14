# 全MCPサーバーテストレポート

**作成日**: 2025-11-08  
**テスト環境**: Cursor (Claude Code)  
**MCP設定**: Claude Desktop設定を適用

---

## 📊 テスト結果サマリー

| MCPサーバー | ステータス | テスト結果 | 備考 |
|------------|----------|----------|------|
| **n8n-mcp** | ✅ 動作確認 | ワークフロー管理機能も動作 | wrapperスクリプト使用 |
| **notion** | ✅ 動作確認 | Notion API正常動作 | |
| **mcp-sequential-thinking** | ✅ 動作確認 | Sequential Thinking正常動作 | |
| **n8n-workflows-docs** | ✅ 動作確認 | ドキュメント取得・検索正常 | |
| **n8n-workflows** | ✅ 動作確認 | ドキュメント取得正常 | |
| **docs-mcp-server** | ✅ 動作確認 | ドキュメント検索正常 | |
| **context7-docs** | ⚠️ 未テスト | ツールが見つからない | |
| **chrome-devtools** | ⚠️ 未テスト | ツールが見つからない | |
| **playwright** | ⚠️ 未テスト | ツールが見つからない | |
| **vercel** | ⚠️ 未テスト | ツールが見つからない | |
| **github** | ⚠️ 未テスト | ツールが見つからない | |
| **obsidian** | ⚠️ 未テスト | ツールが見つからない | |
| **supabase** | ⚠️ 未テスト | ツールが見つからない | |
| **analytics-mcp** | ⚠️ 未テスト | ツールが見つからない | |

---

## ✅ 動作確認済みMCP

### 1. n8n-mcp ✅

**ステータス**: ✅ **完全動作**

**テスト結果**:
- ✅ ワークフロー管理機能が動作（`n8n_list_workflows`成功）
- ✅ ヘルスチェック成功（`n8n_health_check`成功）
- ✅ ドキュメントツール正常動作
- ✅ データベース統計取得成功

**テストコマンド**:
```javascript
// ワークフロー一覧取得
mcp__n8n-mcp__n8n_list_workflows({limit: 3})
// 結果: 3個のワークフローを取得

// ヘルスチェック
mcp__n8n-mcp__n8n_health_check()
// 結果: status: "ok", mcpVersion: "2.22.6"

// データベース統計
mcp__n8n-mcp__get_database_statistics()
// 結果: 541個のノード、2,653個のテンプレート
```

**重要な発見**:
- **wrapperスクリプトを使用することで、ワークフロー管理機能が有効化された**
- 以前は利用不可だった`n8n_list_workflows`が正常動作
- `n8n_health_check`も正常動作

---

### 2. notion ✅

**ステータス**: ✅ **動作確認**

**テスト結果**:
- ✅ Notion API正常動作
- ✅ ユーザー情報取得成功

**テストコマンド**:
```javascript
mcp_notion_API-get-self()
// 結果: ユーザー情報を取得
```

---

### 3. mcp-sequential-thinking ✅

**ステータス**: ✅ **動作確認**

**テスト結果**:
- ✅ Sequential Thinking正常動作

**テストコマンド**:
```javascript
mcp_mcp-sequential-thinking_sequentialthinking({
  thought: "テスト: Sequential Thinking MCPが動作しているか確認",
  nextThoughtNeeded: false,
  thoughtNumber: 1,
  totalThoughts: 1
})
// 結果: 正常に動作
```

---

### 4. n8n-workflows-docs ✅

**ステータス**: ✅ **動作確認**

**テスト結果**:
- ✅ ドキュメント取得成功
- ✅ ドキュメント検索成功

**テストコマンド**:
```javascript
// ドキュメント取得
mcp__n8n-workflows-docs__fetch_n8n_workflows_documentation()
// 結果: n8nワークフローコレクションのドキュメントを取得

// ドキュメント検索
mcp__n8n-workflows-docs__search_n8n_workflows_docs({query: "webhook"})
// 結果: webhook関連のドキュメントを検索
```

---

### 5. n8n-workflows ✅

**ステータス**: ✅ **動作確認**

**テスト結果**:
- ✅ ドキュメント取得成功

**テストコマンド**:
```javascript
mcp__n8n-workflows__fetch_n8n_workflows_documentation()
// 結果: n8nワークフローコレクションのドキュメントを取得
```

---

### 6. docs-mcp-server ✅

**ステータス**: ✅ **動作確認**

**テスト結果**:
- ✅ ドキュメント取得成功
- ✅ ドキュメント検索成功

**テストコマンド**:
```javascript
// ドキュメント取得
mcp__docs-mcp-server__fetch_docs_mcp_server_docs()
// 結果: docs-mcp-serverのドキュメントを取得

// ドキュメント検索
mcp__docs-mcp-server__search_docs_mcp_server_docs({query: "authentication"})
// 結果: 認証関連のドキュメントを検索
```

---

## ⚠️ 未テストMCP

以下のMCPは設定されていますが、利用可能なツールが見つかりませんでした：

1. **context7-docs** - Context7ドキュメント
2. **chrome-devtools** - Chrome DevTools
3. **playwright** - Playwright自動化
4. **vercel** - Vercel
5. **github** - GitHub
6. **obsidian** - Obsidian
7. **supabase** - Supabase
8. **analytics-mcp** - Google Analytics

**原因の可能性**:
- CursorがこれらのMCPサーバーを認識していない
- MCPサーバーが起動していない
- ツール名の命名規則が異なる
- Cursorの再起動が必要

---

## 🎯 重要な発見

### n8n-mcpのワークフロー管理機能が有効化された

**以前の状態**:
- ❌ `n8n_list_workflows`が利用不可
- ❌ `n8n_health_check`が利用不可
- ❌ ワークフロー管理ツールが利用不可

**現在の状態**:
- ✅ `n8n_list_workflows`が正常動作
- ✅ `n8n_health_check`が正常動作
- ✅ ワークフロー管理ツールが利用可能

**原因**:
- **wrapperスクリプト（`/Users/yuichiroooosuger/.local/bin/n8n-mcp-wrapper.sh`）を使用することで、ワークフロー管理機能が有効化された**

---

## 📋 テスト詳細

### n8n-mcp テスト結果

#### ワークフロー一覧取得
```json
{
  "success": true,
  "data": {
    "workflows": [
      {
        "id": "0SI8qdISZ087GEj0",
        "name": "WF7-TEST: FFmpeg Async Polling Test",
        "active": false,
        "isArchived": true,
        "createdAt": "2025-11-06T05:24:05.130Z",
        "updatedAt": "2025-11-07T04:24:49.597Z",
        "tags": [],
        "nodeCount": 12
      },
      {
        "id": "18nxCY4ak7Et6UXr",
        "name": "LINE Lead Pipeline - Notion",
        "active": true,
        "isArchived": false,
        "createdAt": "2025-11-03T05:14:27.752Z",
        "updatedAt": "2025-11-03T05:14:54.147Z",
        "tags": [],
        "nodeCount": 13
      },
      {
        "id": "1AQaG5RsHhTSdFRP",
        "name": "Flux Dev Image Generation Fal.ai",
        "active": false,
        "isArchived": false,
        "createdAt": "2025-11-07T22:48:07.529Z",
        "updatedAt": "2025-11-07T22:48:07.529Z",
        "tags": [],
        "nodeCount": 12
      }
    ],
    "returned": 3,
    "nextCursor": "eyJsaW1pdCI6Mywib2Zmc2V0IjozfQ==",
    "hasMore": true
  }
}
```

#### ヘルスチェック
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "apiUrl": "https://n8n-python-production-344b.up.railway.app",
    "mcpVersion": "2.22.6",
    "versionCheck": {
      "current": "2.22.6",
      "latest": "2.22.11",
      "upToDate": false
    },
    "performance": {
      "responseTimeMs": 386
    }
  }
}
```

---

## ✅ 結論

### 動作確認済み（6個）

1. ✅ **n8n-mcp** - 完全動作（ワークフロー管理機能も動作）
2. ✅ **notion** - 正常動作
3. ✅ **mcp-sequential-thinking** - 正常動作
4. ✅ **n8n-workflows-docs** - 正常動作
5. ✅ **n8n-workflows** - 正常動作
6. ✅ **docs-mcp-server** - 正常動作

### 未テスト（8個）

1. ⚠️ **context7-docs** - ツールが見つからない
2. ⚠️ **chrome-devtools** - ツールが見つからない
3. ⚠️ **playwright** - ツールが見つからない
4. ⚠️ **vercel** - ツールが見つからない
5. ⚠️ **github** - ツールが見つからない
6. ⚠️ **obsidian** - ツールが見つからない
7. ⚠️ **supabase** - ツールが見つからない
8. ⚠️ **analytics-mcp** - ツールが見つからない

### 重要な成果

**n8n-mcpのワークフロー管理機能が有効化された**

- wrapperスクリプトを使用することで、以前利用不可だったワークフロー管理機能が動作するようになった
- `n8n_list_workflows`、`n8n_health_check`などが正常動作
- これにより、n8n APIを直接呼び出す必要がなくなった

---

## 🔍 次のステップ

### 未テストMCPの確認

1. **Cursorを再起動**
   - 設定変更を反映させるため

2. **MCPサーバーの起動確認**
   - 各MCPサーバーが正しく起動しているか確認

3. **ツール名の確認**
   - 利用可能なツールリストを確認し、正しいツール名を使用

---

**最終更新**: 2025-11-08





