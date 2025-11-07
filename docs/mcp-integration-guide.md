# n8n MCP統合ガイド

**作成日**: 2025-10-26
**目的**: Claude Code経由でn8nワークフローを管理するためのリファレンス

---

## 📋 目次

1. [概要](#概要)
2. [セットアップ確認](#セットアップ確認)
3. [主要機能](#主要機能)
4. [MCP連携パターン](#mcp連携パターン)
5. [実践例](#実践例)
6. [トラブルシューティング](#トラブルシューティング)

---

## 概要

### n8n MCP とは

n8n MCP (Model Context Protocol) サーバーは、Claude Code から n8n ワークフローを直接管理できるツールです。

**主な利点:**
- ワークフローの作成・更新・削除をコード化
- ノード設定のバリデーション
- テンプレートからの迅速な実装
- 他MCPサーバーとの連携による高度な自動化

### システム構成

```
Claude Code (CLI)
  ↓
n8n MCP Server (npx -y n8n-mcp)
  ↓
n8n Instance (Railway: https://n8n-python-production-344b.up.railway.app)
```

---

## セットアップ確認

### 環境変数

```bash
# ~/.claude/.env に設定
export N8N_API_URL="https://n8n-python-production-344b.up.railway.app"
export N8N_API_KEY="your-api-key-here"
```

### MCP接続確認

```bash
claude mcp list
# 出力:
# n8n-mcp: npx -y n8n-mcp - ✓ Connected
```

### 診断コマンド

```javascript
// n8n MCPの詳細診断
mcp__n8n-mcp__n8n_diagnostic({verbose: true})
```

**期待される結果:**
- API接続: ✓ Connected
- 利用可能ツール: 38個(ドキュメント22 + 管理16)
- バージョン: 2.18.6+

---

## 主要機能

### 1. ノード検索・情報取得

#### キーワード検索
```javascript
mcp__n8n-mcp__search_nodes({
  query: "slack",
  limit: 5
})
```

#### ノード詳細取得
```javascript
// 基本情報(5KB程度)
mcp__n8n-mcp__get_node_essentials({
  nodeType: "nodes-base.webhook",
  includeExamples: true
})

// 完全なスキーマ(100KB+)
mcp__n8n-mcp__get_node_info({
  nodeType: "nodes-base.slack"
})
```

#### AIノードリスト
```javascript
mcp__n8n-mcp__list_ai_tools()
// 263個のAI対応ノードを返却
```

### 2. ワークフロー管理

#### ワークフロー作成
```javascript
mcp__n8n-mcp__n8n_create_workflow({
  name: "My Workflow",
  nodes: [
    {
      id: "webhook-1",
      name: "Webhook",
      type: "n8n-nodes-base.webhook",
      typeVersion: 2,
      position: [250, 300],
      parameters: {
        httpMethod: "POST",
        path: "my-endpoint"
      }
    }
  ],
  connections: {}
})
```

#### ワークフロー一覧取得
```javascript
mcp__n8n-mcp__n8n_list_workflows({
  limit: 10,
  active: true  // アクティブなワークフローのみ
})
```

#### ワークフロー更新(部分更新)
```javascript
// ノード追加
mcp__n8n-mcp__n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [
    {
      type: "addNode",
      node: {
        name: "Slack Notification",
        type: "n8n-nodes-base.slack",
        position: [500, 300],
        parameters: {
          resource: "message",
          operation: "post",
          channel: "#alerts"
        }
      }
    },
    {
      type: "addConnection",
      source: "Webhook",
      target: "Slack Notification"
    }
  ]
})
```

### 3. テンプレート活用

#### テンプレート検索
```javascript
mcp__n8n-mcp__search_templates({
  query: "slack notification",
  limit: 10
})
```

#### テンプレート取得
```javascript
mcp__n8n-mcp__get_template({
  templateId: 5021,
  mode: "full"  // "nodes_only" | "structure" | "full"
})
```

### 4. バリデーション

#### ノード設定検証
```javascript
// 最小バリデーション(必須フィールドのみ)
mcp__n8n-mcp__validate_node_minimal({
  nodeType: "nodes-base.webhook",
  config: {}
})

// 完全バリデーション
mcp__n8n-mcp__validate_node_operation({
  nodeType: "nodes-base.slack",
  config: {
    resource: "message",
    operation: "post"
  },
  profile: "ai-friendly"
})
```

#### ワークフロー検証
```javascript
mcp__n8n-mcp__validate_workflow({
  workflow: workflowObject,
  options: {
    validateNodes: true,
    validateConnections: true,
    validateExpressions: true
  }
})
```

---

## MCP連携パターン

### パターン1: Sequential + n8n
**ユースケース**: 複雑なビジネスロジックの設計と実装

```
1. Sequential MCPでワークフロー設計
   - 要件分析
   - フロー最適化
   - エラーハンドリング設計

2. n8n MCPで実装
   - ノード作成
   - 接続設定
   - デプロイ
```

**例: フォーム送信処理**
```javascript
// Sequential で設計
mcp__sequential__sequentialthinking({
  thought: "フォーム送信→検証→通知→保存のフローを最適化",
  // ...
})

// n8n で実装
mcp__n8n-mcp__n8n_create_workflow({
  name: "Form Submission Handler",
  nodes: [
    // Webhook, Code (Validation), IF, Slack, PostgreSQL, Respond
  ],
  connections: {
    // フロー接続
  }
})
```

### パターン2: Playwright + n8n
**ユースケース**: E2Eテスト結果の自動通知

```
1. Playwright でテスト実行
   browser_snapshot() → browser_click() → browser_evaluate()

2. 結果をn8n Webhookに送信
   HTTP POST → Webhook URL

3. n8nで結果処理
   Webhook → Code (分析) → IF (判定) → Slack/Jira
```

### パターン3: Context7 + n8n
**ユースケース**: API仕様に基づくHTTP Request設定

```
1. Context7でAPI仕様取得
   get-library-docs({library: "openai-api"})

2. n8nでHTTP Requestノード設定
   - エンドポイントURL
   - 認証ヘッダー
   - リクエストボディ
```

### パターン4: Magic + n8n
**ユースケース**: フロントエンド→バックエンド統合

```
1. Magic でUIコンポーネント生成
   21st_magic_component_builder({message: "contact form"})

2. n8nでバックエンド処理
   Webhook → Validation → Email → Database
```

---

## 実践例

### 例1: シンプルなWebhookワークフロー

**要件**: GETリクエストを受けて、JSON形式でレスポンスを返す

```javascript
mcp__n8n-mcp__n8n_create_workflow({
  name: "Simple API Endpoint",
  nodes: [
    {
      id: "webhook-node",
      name: "Webhook",
      type: "n8n-nodes-base.webhook",
      typeVersion: 2,
      position: [250, 300],
      parameters: {
        httpMethod: "GET",
        path: "api/hello",
        responseMode: "responseNode"
      }
    },
    {
      id: "code-node",
      name: "Process",
      type: "n8n-nodes-base.code",
      typeVersion: 2,
      position: [450, 300],
      parameters: {
        mode: "runOnceForAllItems",
        jsCode: `
          return [{
            json: {
              message: "Hello World",
              timestamp: new Date().toISOString()
            }
          }];
        `
      }
    },
    {
      id: "respond-node",
      name: "Respond",
      type: "n8n-nodes-base.respondToWebhook",
      typeVersion: 1,
      position: [650, 300],
      parameters: {options: {}}
    }
  ],
  connections: {
    "Webhook": {
      "main": [[{"node": "Process", "type": "main", "index": 0}]]
    },
    "Process": {
      "main": [[{"node": "Respond", "type": "main", "index": 0}]]
    }
  }
})
```

**結果**:
- Webhook URL: `https://n8n-python-production-344b.up.railway.app/webhook/api/hello`
- レスポンス例: `{"message": "Hello World", "timestamp": "2025-10-26T..."}`

### 例2: Slack通知ワークフロー

**要件**: フォーム送信時にSlackに通知

```javascript
// 1. 既存ワークフローにSlackノードを追加
mcp__n8n-mcp__n8n_update_partial_workflow({
  id: "existing-workflow-id",
  operations: [
    {
      type: "addNode",
      node: {
        name: "Notify Slack",
        type: "n8n-nodes-base.slack",
        position: [800, 300],
        typeVersion: 2,
        parameters: {
          resource: "message",
          operation: "post",
          channel: "#notifications",
          text: "New form submission received!"
        }
      }
    },
    {
      type: "addConnection",
      source: "Process",
      target: "Notify Slack"
    }
  ]
})
```

### 例3: データベース統合

**要件**: PostgreSQLにデータを保存

```javascript
// PostgreSQLノードを追加
mcp__n8n-mcp__n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [
    {
      type: "addNode",
      node: {
        name: "Save to DB",
        type: "n8n-nodes-base.postgres",
        position: [1000, 300],
        typeVersion: 2,
        parameters: {
          operation: "insert",
          table: "submissions",
          columns: "name, email, message"
        }
      }
    },
    {
      type: "addConnection",
      source: "Notify Slack",
      target: "Save to DB"
    }
  ]
})
```

---

## トラブルシューティング

### よくある問題

#### 1. ワークフローがアクティブ化されない

**原因**: n8n MCP の `activate` operationは存在しない

**解決策**:
- n8n WebUI で手動アクティブ化: `https://n8n-python-production-344b.up.railway.app/workflow/{workflow-id}`
- または、n8n APIを直接呼び出し(curlやaxios)

#### 2. ノードバリデーションエラー

**原因**: 必須パラメータ不足、型不一致

**解決策**:
```javascript
// まず最小バリデーション
mcp__n8n-mcp__validate_node_minimal({
  nodeType: "nodes-base.slack",
  config: {}
})

// エラーメッセージを確認し、必須フィールドを追加
```

#### 3. Webhook URLが不明

**解決策**:
```javascript
// ワークフローの詳細を取得
mcp__n8n-mcp__n8n_get_workflow({id: "workflow-id"})

// Webhook nodeのpath parameterを確認
// URL: https://{n8n-url}/webhook/{path}
```

#### 4. MCP接続エラー

**診断コマンド**:
```bash
# MCP接続状態確認
claude mcp list

# n8n MCP診断
mcp__n8n-mcp__n8n_diagnostic({verbose: true})
```

**チェック項目**:
- [ ] `N8N_API_URL` 環境変数が設定されているか
- [ ] `N8N_API_KEY` が正しいか
- [ ] n8nインスタンスがオンラインか
- [ ] ファイアウォール設定

### デバッグのベストプラクティス

1. **段階的な実装**: 小さなワークフローから始める
2. **バリデーション**: 各ステップでバリデーションを実行
3. **ログ確認**: n8nの実行履歴を確認
4. **テスト実行**: Webhookは curl でテスト

```bash
# Webhookテスト例
curl -X GET "https://n8n-python-production-344b.up.railway.app/webhook/api/hello"
```

---

## ベストプラクティス

### 1. ワークフロー設計

- **Single Responsibility**: 1つのワークフローは1つの目的
- **エラーハンドリング**: IF ノードで成功/失敗を分岐
- **ログ記録**: 重要なステップでデータをログ保存

### 2. ノード命名

- **明確な名前**: "Process Data" より "Validate Email Format"
- **一貫性**: プロジェクト全体で命名規則を統一

### 3. セキュリティ

- **認証情報**: n8nのCredentials機能を活用
- **環境変数**: API Key等は環境変数で管理
- **Webhook保護**: 認証ヘッダーやトークン検証を実装

### 4. パフォーマンス

- **並列処理**: 独立したタスクは並列実行
- **バッチ処理**: Split In Batches ノードで大量データ処理
- **キャッシング**: 頻繁にアクセスするデータはキャッシュ

---

## 参考リンク

- [n8n公式ドキュメント](https://docs.n8n.io/)
- [n8n MCP GitHub](https://github.com/n8n-io/n8n-mcp)
- [n8n Community](https://community.n8n.io/)
- [n8n Templates](https://n8n.io/workflows)

---

## 更新履歴

- **2025-10-26**: 初版作成
  - 基本セットアップ
  - 主要機能リファレンス
  - MCP連携パターン
  - 実践例とトラブルシューティング
