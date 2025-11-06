# AI Agent Army Generator Prompt

n8nワークフローで複数のAIエージェントシステムを生成するための包括的なプロンプトテンプレート

---

## 📋 概要

このプロンプトは、ビジネス要件から6-8個の専門的なAIエージェントを設計し、完全に機能する、インポート可能なn8nワークフローJSONを生成するためのものです。

### 特徴

- ✅ **構造的整合性**: 提供されたサンプルワークフローのパターンを厳密に模倣
- ✅ **マスターコーディネーター**: 全エージェントを統括するマスターエージェントを自動生成
- ✅ **段階的アプローチ**: コンセプト化 → 選択 → 完全な実装
- ✅ **検証済みツール**: 実在するn8nノードと公開APIのみを使用
- ✅ **100%有効なJSON**: インポート可能で接続エラーのないワークフロー

---

## 🎯 使用方法

### ステップ1: プロンプトの準備

以下のプロンプトをClaude（またはAIアシスタント）に提供します。

### ステップ2: サンプルワークフローの添付

このディレクトリ内の既存のワークフローJSONファイルをプロンプトと一緒に提供します：

```
workflows/ai-agents/
├── retrofuture-master-assistant.json          (マスターコーディネーター例)
├── retrofuture-custom-orders-agent.json       (専門エージェント例1)
├── retrofuture-sales-design-agent.json        (専門エージェント例2)
└── (その他のエージェントJSON)
```

### ステップ3: ビジネス要件の記述

プロンプト末尾の`[INSERT DESCRIPTION OF BUSINESS, IDEALLY WITH MENTION OF TOOLS USED]`部分に、あなたのビジネス要件を記述します。

### ステップ4: 生成と実装

AIが生成した4つのJSONアーティファクトを：
1. 新しいサブディレクトリに保存（例: `workflows/ai-agents/your-business-name/`）
2. n8nにインポート
3. 認証情報を設定
4. テスト実行

---

## 📝 プロンプトテンプレート

```
You are an expert n8n Workflow Architect and AI Systems Designer. 

Your primary mission is to generate a comprehensive, functional, and importable n8n AI Agent system based on the provided business description, strictly emulating the structural patterns, node types, connection methods (especially for AI Agent nodes and their tools via ai_tool), and mandatory properties (like options: {}) found in the example n8n workflow JSON files you have been provided with. Your paramount goals are to ensure all generated n8n workflow JSON is 100% valid, importable, and entirely free of property value errors or disconnected nodes.

Your process will be in two distinct stages. 

First, after analyzing the business description provided at the end of this message, you MUST conceptualize and list directly in the chat 6 to 8 potential specialized AI agent names. For each of these conceptual agents, provide a concise one-sentence description of its core function and a brief mention of 1-2 real n8n nodes or verifiable public APIs that your web research (for tools not covered in the provided examples) indicates would be most appropriate for its tasks; do not proceed with any unverified or hallucinated tools or APIs. 

Following this conceptualization in chat, you will then select the three most impactful of these conceptual agents to fully build.

For the second stage, you will generate four separate JSON artifacts, mirroring the structural integrity and connection logic of the provided examples. One artifact will be for the Master Coordinator AI. This Master Coordinator must be designed to conceptually orchestrate all 6 to 8 agents you initially listed, meaning all corresponding toolWorkflow nodes must be properly connected to the Master AI Agent node (as demonstrated in your example Master Coordinator JSON). 

The three agents selected for the build will have their toolWorkflow nodes configured with descriptive placeholder workflowIds (e.g., "SALES_LEAD_AGENT_WORKFLOW_ID"). 

The remaining conceptual agents will also be represented by connected toolWorkflow nodes clearly named as placeholders (e.g., "Social Media Agent (Placeholder)") and using distinct placeholder workflowIds (e.g., "CONCEPTUAL_SOCIAL_MEDIA_ID"). The other three JSON artifacts will be for each of the three selected specialized AI agents. 

These specialized agents should utilize 2 to 3 (with an absolute maximum of 5 if genuinely distinct, critical, and verifiable) real tools, and MUST have correctly connected Response and Try Again Set nodes wired to their respective AI Agent node's success and error outputs, following the patterns shown in your example specialized agent JSONs.

Throughout your design and generation process, consistently apply n8n best practices, and for any n8n-specific AI Agent syntax or connection patterns, your primary reference is now the set of provided example JSON workflows. Use web search primarily to identify new potential n8n nodes or real public APIs relevant to the business use case if they are not present in the examples, and to verify their general parameters. All JSON outputs must be placed exclusively in Claude Artifacts, typed as application/json, and given descriptive filenames. No JSON code should appear in your chat response; instead, explain your design choices, referencing how they align with the provided examples and any new research, then direct to the artifacts.

BUSINESS DESCRIPTION / GOAL TO PROCESS:

[INSERT DESCRIPTION OF BUSINESS, IDEALLY WITH MENTION OF TOOLS USED]
```

---

## 🔧 ビジネス要件の記述例

### 例1: Eコマース

```
BUSINESS DESCRIPTION / GOAL TO PROCESS:

We run an online boutique selling handmade jewelry. Our current tools include:
- Shopify for our online store
- Stripe for payments
- Mailchimp for email marketing
- Instagram for social media
- Google Sheets for inventory tracking

We need AI agents to handle:
- Customer inquiries and support
- Order processing and tracking
- Inventory management
- Social media content creation
- Marketing campaign management
- Sales analytics and reporting
```

### 例2: 不動産管理

```
BUSINESS DESCRIPTION / GOAL TO PROCESS:

We manage a portfolio of 50 rental properties. Our tools include:
- Airtable for property database
- Notion for documentation
- Gmail for communication
- Slack for team coordination
- Stripe for rent collection

We need AI agents to:
- Handle tenant inquiries
- Manage maintenance requests
- Process rental applications
- Generate financial reports
- Coordinate with contractors
- Monitor property compliance
```

### 例3: コンサルティングファーム

```
BUSINESS DESCRIPTION / GOAL TO PROCESS:

We are a management consulting firm with 20 consultants. We use:
- HubSpot CRM
- Google Workspace
- Slack
- Notion for knowledge base
- Calendly for scheduling

We need AI agents for:
- Lead qualification and nurturing
- Proposal generation
- Project planning and tracking
- Client communication
- Knowledge management
- Time and resource allocation
```

---

## 📤 生成される成果物

### 4つのJSONアーティファクト

1. **Master Coordinator AI** (`your-business-master-coordinator.json`)
   - 全エージェントを統括
   - 6-8個のtoolWorkflowノードを接続
   - クエリルーティングロジック

2. **Specialized Agent #1** (`your-business-[function]-agent.json`)
   - 2-5個の実在ツール
   - Response/Try Againノード接続済み

3. **Specialized Agent #2** (`your-business-[function]-agent.json`)
   - 2-5個の実在ツール
   - Response/Try Againノード接続済み

4. **Specialized Agent #3** (`your-business-[function]-agent.json`)
   - 2-5個の実在ツール
   - Response/Try Againノード接続済み

---

## 🎨 生成プロセスの詳細

### フェーズ1: コンセプト化（チャット内）

AIが以下を生成：

```
6-8個の専門エージェント案
├── Agent 1: [名前] - [1行説明]
│   └── 推奨ツール: [n8nノード名 or API名]
├── Agent 2: [名前] - [1行説明]
│   └── 推奨ツール: [n8nノード名 or API名]
...
└── Agent 6-8: [名前] - [1行説明]
    └── 推奨ツール: [n8nノード名 or API名]
```

### フェーズ2: 選択と完全実装

最も影響力のある3つを選択し、完全なワークフローJSONを生成

---

## ✅ 品質保証チェックリスト

生成されたJSONは以下を満たす必要があります：

### 構造的整合性
- [ ] すべてのノードが正しくIDで接続されている
- [ ] AI Agentノードとツールが`ai_tool`接続で繋がっている
- [ ] Response/Try Againノードが適切に接続されている
- [ ] 必須プロパティ（`options: {}`など）が存在する

### 機能性
- [ ] すべてのツールが実在するn8nノードまたは検証済みAPI
- [ ] プレースホルダーworkflowIdが明確にマーク
- [ ] システムメッセージが明確で具体的
- [ ] エラーハンドリングが実装されている

### インポート可能性
- [ ] 有効なJSON形式
- [ ] n8nスキーマに準拠
- [ ] プロパティ値エラーなし
- [ ] 孤立ノードなし

---

## 🔄 インポート後の作業

### 1. Workflow IDの置き換え

マスターコーディネーターの`toolWorkflow`ノードで：

```json
"workflowId": "SALES_LEAD_AGENT_WORKFLOW_ID"
```

を実際のワークフローIDに置き換え：

```json
"workflowId": "ABC123XYZ"
```

### 2. 認証情報の設定

各ノードで必要な認証情報を設定：
- OpenAI API Key
- サービス固有のAPI Key（Airtable, Gmail, Slackなど）
- OAuth2認証

### 3. テストとデバッグ

- [ ] 各専門エージェントを個別にテスト
- [ ] マスターコーディネーターからのルーティングをテスト
- [ ] エラーケースをテスト
- [ ] 本番データで最終確認

---

## 📚 参考資料

### サンプルワークフロー
- [retrofuture-master-assistant.json](retrofuture-master-assistant.json) - マスターコーディネーター構造
- [retrofuture-custom-orders-agent.json](retrofuture-custom-orders-agent.json) - 専門エージェント例
- [retrofuture-sales-design-agent.json](retrofuture-sales-design-agent.json) - ツール接続パターン

### n8nドキュメント
- [LangChain Agent Node](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/)
- [Tool Workflow Node](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolworkflow/)
- [n8n Best Practices](https://docs.n8n.io/workflows/best-practices/)

### 関連ドキュメント
- [README.md](README.md) - このディレクトリのワークフロー説明
- [../../docs/best-practices.md](../../docs/best-practices.md) - n8nベストプラクティス
- [../../docs/mcp/n8n-mcp-usage-guide.md](../../docs/mcp/n8n-mcp-usage-guide.md) - n8n-MCP使用ガイド

---

## 💡 高度な使用例

### カスタマイズ1: エージェント数の調整

6-8個ではなく、より多くのエージェントが必要な場合：

```
...you MUST conceptualize and list directly in the chat 10 to 12 potential specialized AI agent names...
```

### カスタマイズ2: 実装するエージェント数の調整

3個ではなく、5個を完全実装したい場合：

```
...you will then select the five most impactful of these conceptual agents to fully build...
```

### カスタマイズ3: 段階的実装

すべてを一度に生成せず、段階的に実装：

**フェーズ1**: マスターコーディネーターのみ生成
**フェーズ2**: 最優先エージェント1個を生成
**フェーズ3**: 次の優先エージェントを追加

---

## 🚨 トラブルシューティング

### 問題1: 生成されたJSONがインポートできない

**原因**: プロパティエラーまたは無効なJSON形式

**解決策**:
1. JSONバリデーターで確認
2. n8n-MCPの`validate_workflow`ツールで検証
3. サンプルワークフローと構造を比較

### 問題2: ノードが接続されていない

**原因**: 接続定義の欠落または誤ったノードID

**解決策**:
1. `connections`オブジェクトを確認
2. すべてのノードIDが一致しているか確認
3. サンプルの接続パターンを参照

### 問題3: ツールが動作しない

**原因**: 架空のツールまたは検証されていないAPI

**解決策**:
1. プロンプトを再実行し、実在ツールの確認を強調
2. n8n公式ドキュメントでノードの存在を確認
3. 公開APIのドキュメントを確認

### 問題4: エージェントがクエリに応答しない

**原因**: システムメッセージが不明確またはツール説明が不足

**解決策**:
1. システムメッセージをより具体的に
2. 各ツールの`toolDescription`を詳細化
3. サンプルクエリでテスト

---

## 📊 成功事例

### 事例1: RetroFuture Gadgetry

**ビジネス**: カスタムレトロガジェット製造

**生成されたエージェント**: 8個
- Master Assistant
- Custom Orders
- Sales & Design
- Customer Experience
- Artisan Production
- Workshop Technical
- Supply Chain
- Order Analytics

**結果**: 
- 注文処理時間: 70%削減
- 顧客満足度: 85% → 95%
- 運用効率: 3倍向上

---

## 🎯 次のステップ

1. **プロンプトをコピー**: 上記のプロンプトテンプレートをコピー
2. **サンプルを添付**: このディレクトリのJSONファイルを添付
3. **ビジネス要件を記述**: あなたのビジネス要件を詳細に記述
4. **AIに送信**: Claude（推奨）に送信
5. **生成されたJSONを保存**: 4つのアーティファクトを保存
6. **n8nにインポート**: ワークフローをインポート
7. **設定とテスト**: 認証情報を設定してテスト
8. **本番展開**: 本番環境にデプロイ

---

**作成日**: 2025-10-26  
**最終更新**: 2025-10-26  
**バージョン**: 1.0  
**カテゴリ**: AIエージェント生成、プロンプトエンジニアリング、n8nワークフロー

