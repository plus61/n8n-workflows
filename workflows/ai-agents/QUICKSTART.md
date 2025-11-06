# AI Agent Army Generator - クイックスタートガイド

5分で始めるAIエージェント軍の自動生成

---

## 🚀 3ステップで開始

### ステップ1: プロンプトを準備（30秒）

[agent-army-generator-prompt.md](agent-army-generator-prompt.md)を開き、プロンプトテンプレートをコピーします。

### ステップ2: サンプルとビジネス要件を添付（2分）

1. **サンプルワークフローを添付**:
   - このディレクトリの`retrofuture-*.json`ファイル（特に`retrofuture-master-assistant.json`と任意の専門エージェント2-3個）

2. **ビジネス要件を記述**:
   プロンプト末尾の`[INSERT DESCRIPTION OF BUSINESS...]`部分に記述

```
例:
BUSINESS DESCRIPTION / GOAL TO PROCESS:

We run an online boutique selling handmade jewelry. Our tools:
- Shopify (online store)
- Stripe (payments)
- Mailchimp (email marketing)
- Instagram (social media)
- Google Sheets (inventory)

Need AI agents for:
- Customer support
- Order processing
- Inventory management
- Social media content
- Marketing campaigns
- Sales analytics
```

### ステップ3: AIに送信して生成（2分）

1. Claude（推奨）またはChatGPTにプロンプトを送信
2. 6-8個のエージェント案が提示される
3. 4つのJSONアーティファクトが生成される:
   - マスターコーディネーター（1個）
   - 専門エージェント（3個）

---

## 📥 生成後の実装（10-15分）

### 1. JSONファイルの保存

生成された4つのJSONを保存:
```
workflows/ai-agents/your-business-name/
├── your-business-master-coordinator.json
├── your-business-agent-1.json
├── your-business-agent-2.json
└── your-business-agent-3.json
```

### 2. n8nにインポート

各JSONファイルを順番にインポート:
1. 専門エージェント3個を先にインポート
2. 各ワークフローIDをメモ（例: `ABC123XYZ`）
3. 最後にマスターコーディネーターをインポート

### 3. Workflow IDの接続

マスターコーディネーターの編集:
1. `toolWorkflow`ノードを開く
2. プレースホルダーID（例: `SALES_AGENT_WORKFLOW_ID`）を実際のIDに置き換え
3. 保存

### 4. 認証情報の設定

必要な認証情報を設定:
- OpenAI API Key（すべてのエージェント）
- サービス固有のAPI Key（Airtable、Gmail、Slackなど）

### 5. テスト実行

1. 専門エージェントを個別にテスト
2. マスターコーディネーターからのルーティングをテスト
3. 本番データで最終確認

---

## ✅ 成功の確認

- [ ] 4つのワークフローがn8nにインポートされている
- [ ] マスターコーディネーターがすべてのエージェントに接続されている
- [ ] すべての認証情報が設定されている
- [ ] テスト実行が成功している
- [ ] エラーハンドリングが動作している

---

## 💡 よくある使用例

### Eコマース
```
Need agents for: customer support, order processing, 
inventory management, social media, marketing, analytics
```

### 不動産管理
```
Need agents for: tenant inquiries, maintenance requests, 
rental applications, financial reports, contractor coordination
```

### コンサルティング
```
Need agents for: lead qualification, proposal generation, 
project planning, client communication, knowledge management
```

### SaaS企業
```
Need agents for: onboarding, technical support, 
feature requests, billing, user analytics, churn prevention
```

---

## 🆘 トラブルシューティング

### JSONがインポートできない
→ JSONバリデーターで確認、またはn8n-MCPの`validate_workflow`を使用

### エージェントが応答しない
→ システムメッセージとツール説明を確認、OpenAI API Keyを確認

### ツールが動作しない
→ 実在するツールか確認、認証情報を確認

### Workflow IDが見つからない
→ n8nのワークフロー一覧でIDを確認（URLにも表示）

---

## 📚 次のステップ

- [詳細ガイド](agent-army-generator-prompt.md) - 完全な説明とカスタマイズ方法
- [README.md](README.md) - RetroFuture Gadgetryの事例
- [n8n Best Practices](../../docs/best-practices.md) - n8nベストプラクティス

---

**所要時間**: 初回セットアップ 15-20分  
**難易度**: 初級〜中級  
**推奨AI**: Claude 3.5 Sonnet以上

