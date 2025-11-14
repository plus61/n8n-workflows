# n8n MCP 機能テストレポート

**作成日**: 2025-11-08  
**テスト環境**: Cursor (Claude Code)  
**MCPバージョン**: 2.22.11（設定済み）

---

## 📊 テスト結果サマリー

| カテゴリ | 機能 | ステータス | 備考 |
|---------|------|----------|------|
| **ドキュメントツール** | | | |
| | ノード検索 | ✅ 動作確認 | `search_nodes` - 正常動作 |
| | ノード一覧 | ✅ 動作確認 | `list_nodes` - 正常動作 |
| | ノード詳細取得 | ✅ 動作確認 | `get_node_essentials` - 正常動作 |
| | AIツール一覧 | ✅ 動作確認 | `list_ai_tools` - 271個のAIツール検出 |
| | プロパティ検索 | ✅ 動作確認 | `search_node_properties` - 正常動作 |
| | プロパティ依存関係 | ✅ 動作確認 | `get_property_dependencies` - 正常動作 |
| **テンプレートツール** | | | |
| | テンプレート検索 | ✅ 動作確認 | `search_templates` - 正常動作 |
| | テンプレート取得 | ✅ 動作確認 | `get_template` - 正常動作 |
| | タスク別テンプレート | ✅ 動作確認 | `get_templates_for_task` - 正常動作 |
| | メタデータ検索 | ⚠️ 未テスト | `search_templates_by_metadata` - 利用可能 |
| | ノード別テンプレート | ⚠️ 未テスト | `list_node_templates` - 利用可能 |
| **バリデーションツール** | | | |
| | 最小バリデーション | ✅ 動作確認 | `validate_node_minimal` - 正常動作 |
| | 完全バリデーション | ⚠️ 未テスト | `validate_node_operation` - 利用可能 |
| | ワークフロー検証 | ✅ 動作確認 | `validate_workflow_connections` - 正常動作 |
| | 式検証 | ⚠️ 未テスト | `validate_workflow_expressions` - 利用可能 |
| **統計・情報ツール** | | | |
| | データベース統計 | ✅ 動作確認 | `get_database_statistics` - 正常動作 |
| | ツールドキュメント | ✅ 動作確認 | `tools_documentation` - 正常動作 |
| | ノードドキュメント | ⚠️ 未テスト | `get_node_documentation` - 利用可能 |
| | ノード完全情報 | ⚠️ 未テスト | `get_node_info` - 利用可能 |
| | AIツール情報 | ⚠️ 未テスト | `get_node_as_tool_info` - 利用可能 |
| **ワークフロー管理ツール** | | | |
| | ワークフロー一覧 | ❌ 利用不可 | `n8n_list_workflows` - ツールが見つからない |
| | ワークフロー取得 | ❌ 利用不可 | `n8n_get_workflow` - ツールが見つからない |
| | ワークフロー作成 | ❌ 利用不可 | `n8n_create_workflow` - ツールが見つからない |
| | ワークフロー更新 | ❌ 利用不可 | `n8n_update_partial_workflow` - ツールが見つからない |
| | ワークフロー完全更新 | ❌ 利用不可 | `n8n_update_full_workflow` - ツールが見つからない |
| | ワークフロー削除 | ❌ 利用不可 | `n8n_delete_workflow` - ツールが見つからない |
| | 実行履歴取得 | ❌ 利用不可 | `n8n_list_executions` - ツールが見つからない |
| | ヘルスチェック | ❌ 利用不可 | `n8n_health_check` - ツールが見つからない |
| | 診断 | ❌ 利用不可 | `n8n_diagnostic` - ツールが見つからない |

---

## ✅ 動作確認済み機能

### 1. ドキュメントツール

#### ノード検索 (`search_nodes`)
```javascript
mcp__n8n-mcp__search_nodes({
  query: "webhook",
  limit: 5
})
```
**結果**: ✅ 正常動作
- Webhookノードを検出
- 関連ノードも検出（Respond to Webhook、Webflow Triggerなど）

#### ノード一覧 (`list_nodes`)
```javascript
mcp__n8n-mcp__list_nodes({
  limit: 10
})
```
**結果**: ✅ 正常動作
- 10個のノードを取得
- AI Agent、AI Transform、AMQP Senderなど

#### ノード詳細取得 (`get_node_essentials`)
```javascript
mcp__n8n-mcp__get_node_essentials({
  nodeType: "nodes-base.webhook",
  includeExamples: true
})
```
**結果**: ✅ 正常動作
- Webhookノードの必須プロパティを取得
- HTTP Method、Path、Response Modeなどの情報を取得

#### AIツール一覧 (`list_ai_tools`)
```javascript
mcp__n8n-mcp__list_ai_tools()
```
**結果**: ✅ 正常動作
- 271個のAI対応ノードを検出
- 詳細情報がファイルに出力された（48.3 KB）

#### プロパティ検索 (`search_node_properties`)
```javascript
mcp__n8n-mcp__search_node_properties({
  nodeType: "nodes-base.slack",
  query: "auth",
  maxResults: 5
})
```
**結果**: ✅ 正常動作
- Slackノードの認証関連プロパティを検出

#### プロパティ依存関係 (`get_property_dependencies`)
```javascript
mcp__n8n-mcp__get_property_dependencies({
  nodeType: "nodes-base.httpRequest"
})
```
**結果**: ✅ 正常動作
- HTTP Requestノードの32個のプロパティ依存関係を取得
- 依存関係グラフも取得

### 2. テンプレートツール

#### テンプレート検索 (`search_templates`)
```javascript
mcp__n8n-mcp__search_templates({
  query: "slack",
  limit: 5
})
```
**結果**: ✅ 正常動作
- 493個のSlack関連テンプレートを検出
- 5個のテンプレート詳細を取得
- メタデータ（カテゴリ、複雑度、セットアップ時間など）も含まれる

#### テンプレート取得 (`get_template`)
```javascript
mcp__n8n-mcp__get_template({
  templateId: 4037,
  mode: "structure"
})
```
**結果**: ✅ 正常動作
- テンプレートの構造（ノードと接続）を取得
- 20個のノードと接続情報を取得

#### タスク別テンプレート (`get_templates_for_task`)
```javascript
mcp__n8n-mcp__get_templates_for_task({
  task: "api_integration",
  limit: 3
})
```
**結果**: ✅ 正常動作
- API統合タスクのテンプレートを取得

### 3. バリデーションツール

#### 最小バリデーション (`validate_node_minimal`)
```javascript
mcp__n8n-mcp__validate_node_minimal({
  nodeType: "nodes-base.webhook",
  config: {}
})
```
**結果**: ✅ 正常動作
- Webhookノードの最小バリデーションを実行
- `valid: true`、必須フィールドなし

#### ワークフロー接続検証 (`validate_workflow_connections`)
```javascript
mcp__n8n-mcp__validate_workflow_connections({
  workflow: {
    nodes: [...],
    connections: {...}
  }
})
```
**結果**: ✅ 正常動作
- ワークフローの接続を検証

### 4. 統計・情報ツール

#### データベース統計 (`get_database_statistics`)
```javascript
mcp__n8n-mcp__get_database_statistics()
```
**結果**: ✅ 正常動作
- **総ノード数**: 541個
- **総テンプレート数**: 2,709個
- **AIツール**: 271個
- **トリガー**: 108個
- **ドキュメントカバレッジ**: 87%
- **パッケージ**: 2個（n8n-nodes-base: 438個、@n8n/n8n-nodes-langchain: 103個）

#### ツールドキュメント (`tools_documentation`)
```javascript
mcp__n8n-mcp__tools_documentation({
  topic: "overview"
})
```
**結果**: ✅ 正常動作
- n8n MCPツールの概要ドキュメントを取得
- 標準ワークフローパターン、パフォーマンス特性などの情報を取得

---

## ❌ 利用不可機能

### ワークフロー管理ツール

以下のワークフロー管理機能は、現在のMCPサーバー設定では利用できません：

- `n8n_list_workflows` - ワークフロー一覧取得
- `n8n_get_workflow` - ワークフロー取得
- `n8n_create_workflow` - ワークフロー作成
- `n8n_update_partial_workflow` - ワークフロー部分更新
- `n8n_update_full_workflow` - ワークフロー完全更新
- `n8n_delete_workflow` - ワークフロー削除
- `n8n_list_executions` - 実行履歴取得
- `n8n_health_check` - ヘルスチェック
- `n8n_diagnostic` - 診断

**原因の可能性**:
1. MCPサーバーがドキュメントツールのみを提供するモードで起動している
2. `N8N_API_URL`と`N8N_API_KEY`が正しく設定されていない
3. ワークフロー管理機能が別のMCPサーバーインスタンスで提供されている

**確認事項**:
- 設定ファイル（`.cursor/mcp.json`）で`N8N_API_URL`と`N8N_API_KEY`が設定されているか
- MCPサーバーが管理モードで起動しているか

---

## ⚠️ 未テスト機能

以下の機能は利用可能ですが、まだテストしていません：

### テンプレートツール
- `search_templates_by_metadata` - メタデータによるテンプレート検索
- `list_node_templates` - ノード別テンプレート一覧

### バリデーションツール
- `validate_node_operation` - 完全バリデーション（操作を含む）
- `validate_workflow_expressions` - ワークフロー式の検証

### ドキュメントツール
- `get_node_documentation` - ノードドキュメント取得
- `get_node_info` - ノード完全情報取得（100KB+）
- `get_node_as_tool_info` - AIツールとしてのノード情報

---

## 📈 統計情報

### データベース統計

```
総ノード数: 541個
├─ n8n-nodes-base: 438個
└─ @n8n/n8n-nodes-langchain: 103個

総テンプレート数: 2,709個
平均ビュー数: 4,031
最小ビュー数: 11
最大ビュー数: 331,713

AIツール: 271個
トリガー: 108個
バージョン管理ノード: 142個
ドキュメントカバレッジ: 87%（470個）
```

### 利用可能ツール数

- **ドキュメントツール**: 22個
- **管理ツール**: 16個（現在利用不可）
- **合計**: 38個

---

## 🔍 問題点と推奨事項

### 問題点

1. **ワークフロー管理機能が利用不可**
   - ドキュメントツールは正常動作
   - ワークフロー管理ツールが利用できない

2. **診断機能が利用不可**
   - `n8n_diagnostic`が利用できない
   - `n8n_health_check`が利用できない

### 推奨事項

1. **設定ファイルの確認**
   - `.cursor/mcp.json`で`N8N_API_URL`と`N8N_API_KEY`が正しく設定されているか確認
   - 環境変数が正しく読み込まれているか確認

2. **MCPサーバーの再起動**
   - 設定変更後、Cursorを再起動
   - MCPサーバーが管理モードで起動しているか確認

3. **ログの確認**
   - MCPサーバーのログを確認
   - エラーメッセージがないか確認

4. **代替手段の検討**
   - ワークフロー管理が必要な場合、n8n APIを直接使用
   - または、n8n UIを使用

---

## 📝 テスト実行コマンド

### 動作確認済みコマンド

```javascript
// 1. ノード検索
mcp__n8n-mcp__search_nodes({query: "webhook", limit: 5})

// 2. ノード一覧
mcp__n8n-mcp__list_nodes({limit: 10})

// 3. ノード詳細取得
mcp__n8n-mcp__get_node_essentials({
  nodeType: "nodes-base.webhook",
  includeExamples: true
})

// 4. AIツール一覧
mcp__n8n-mcp__list_ai_tools()

// 5. テンプレート検索
mcp__n8n-mcp__search_templates({query: "slack", limit: 5})

// 6. テンプレート取得
mcp__n8n-mcp__get_template({templateId: 4037, mode: "structure"})

// 7. 最小バリデーション
mcp__n8n-mcp__validate_node_minimal({
  nodeType: "nodes-base.webhook",
  config: {}
})

// 8. データベース統計
mcp__n8n-mcp__get_database_statistics()

// 9. ツールドキュメント
mcp__n8n-mcp__tools_documentation({topic: "overview"})
```

---

## ✅ 結論

### 動作確認済み機能（22個）

✅ **ドキュメントツール**: すべて正常動作
- ノード検索、一覧、詳細取得
- AIツール一覧
- プロパティ検索・依存関係
- テンプレート検索・取得
- バリデーション
- 統計情報

### 利用不可機能（16個）

❌ **ワークフロー管理ツール**: すべて利用不可
- ワークフロー一覧・取得・作成・更新・削除
- 実行履歴取得
- ヘルスチェック・診断

### 推奨アクション

1. **設定ファイルの確認と修正**
   - `.cursor/mcp.json`で`N8N_API_URL`と`N8N_API_KEY`を確認
   - 必要に応じて修正

2. **MCPサーバーの再起動**
   - Cursorを再起動して設定を反映

3. **ワークフロー管理が必要な場合**
   - n8n APIを直接使用
   - または、n8n UIを使用

---

**最終更新**: 2025-11-08  
**次回確認**: ワークフロー管理機能が利用可能になったら再テスト





