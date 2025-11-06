# MCP使用ガイド集

Model Context Protocol (MCP)サーバーの使用手順とベストプラクティス

---

## 📚 利用可能なMCPガイド

### [n8n-mcp-usage-guide.md](n8n-mcp-usage-guide.md)
n8n-MCP詳細使用ガイド

**内容**:
- コア原則（サイレント実行、並列実行、テンプレート優先）
- 8ステップワークフロープロセス
- バリデーション戦略（4レベル）
- バッチ操作とCRITICAL構文
- 最も人気のあるn8nノード20選

**重要な警告**:
- ⚠️ デフォルト値を信頼しない
- ⚠️ addConnection構文の正しい使い方
- ⚠️ IFノードのマルチアウトプットルーティング

### [zie619-n8n-workflows-guide.md](zie619-n8n-workflows-guide.md)
Zie619 n8n-workflows MCP 使用ガイド

**内容**:
- 世界最大のn8nワークフローコレクション（2,053ワークフロー）へのアクセス
- 365ユニークインテグレーションの活用方法
- カテゴリー別・トリガー別・複雑度別の高度な検索
- 実践的なユースケース別ガイド
- ワークフローのインポートとカスタマイズ手順

**主要カテゴリー**:
- 💬 Messaging（Telegram, Discord, Slack, LINE）
- 📊 CRM & Sales（HubSpot, Salesforce）
- 📈 Data & Analytics（Google Sheets, データ処理）
- 🤖 AI & ML（OpenAI, GPT）
- 🛒 E-commerce（Shopify, Stripe）

### [troubleshooting-continueonerror.md](troubleshooting-continueonerror.md)
n8n-mcp トラブルシューティング: continueOnFail削除問題

**内容**:
- continueOnFail削除失敗の根本原因解説
- n8n API仕様制限の理解
- continueOnFail + onError 共存の仕様
- 3つの解決策と実装判断マトリックス
- n8n-mcpの制約とベストプラクティス

**主要トピック**:
- 🔍 n8n APIのパーシャルアップデート制限
- ⚠️ プロパティ削除の正しい手順
- ✅ レガシーAPIとモダンAPIの共存対応
- 📊 実装判断マトリックス（工数・リスク・クリーン度）

---

## 🎯 MCPの選び方

### タスク別推奨MCP

| タスク | 推奨MCP | 用途 |
|--------|---------|------|
| ワークフロー自動化 | n8n-mcp | n8nワークフローの作成・管理 |
| ワークフロー例の検索 | n8n-workflows-docs | 2,053の実証済みワークフロー検索 |
| コード管理 | github-mcp | リポジトリ操作、PR作成 |
| データベース管理 | notion-mcp, supabase-mcp | データCRUD操作 |
| 複雑な思考プロセス | sequential-thinking | 段階的問題解決 |
| ブラウザ自動化 | playwright-mcp | E2Eテスト、スクレイピング |
| ドキュメント検索 | context7-mcp | API仕様、ライブラリドキュメント |

---

## 🔄 MCP連携パターン

### パターン1: Sequential Thinking + n8n-MCP
**ユースケース**: 複雑なビジネスロジックの設計と実装

```
1. Sequential Thinkingで設計
   - 要件分析
   - フロー最適化
   - エラーハンドリング設計

2. n8n-MCPで実装
   - ノード作成
   - 接続設定
   - デプロイ
```

### パターン2: GitHub + n8n-MCP
**ユースケース**: ワークフローのバージョン管理

```
1. n8n-MCPでワークフロー作成
2. GitHub MCPでリポジトリに保存
3. 変更履歴を追跡
4. チーム間で共有
```

### パターン3: Notion + n8n-MCP
**ユースケース**: データ駆動型ワークフロー

```
1. Notion MCPでデータ取得
2. n8n-MCPでワークフロー生成
3. Notionに結果を保存
4. ダッシュボードで可視化
```

### パターン4: n8n-workflows-docs + n8n-MCP
**ユースケース**: 実証済みパターンの活用と実装

```
1. n8n-workflows-docsで類似ワークフロー検索
   - 2,053ワークフローから最適な例を探す
   - ベストプラクティスとパターンを学ぶ
   
2. n8n-MCPで実装
   - 参考にしたパターンを自環境に適用
   - カスタマイズと最適化
   
3. 検証とデプロイ
   - テスト実行
   - 本番環境へのデプロイ
```

---

## 🔧 セットアップ

### Claude Desktop設定

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "/path/to/npx",
      "args": ["-y", "n8n-mcp"],
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Cursor設定

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "/path/to/npx",
      "args": ["-y", "n8n-mcp"],
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your-api-key"
      }
    }
  }
}
```

---

## 📝 使用手順の標準構造

各MCPガイドには以下を含める:

### 1. 基本情報
- 目的
- 前提条件
- 制約事項

### 2. コア原則
- 重要なルール
- ベストプラクティス
- アンチパターン

### 3. 標準フロー
- ステップバイステップの手順
- 各ステップの目的
- 期待される結果

### 4. 実践例
- 具体的なユースケース
- コード例
- トラブルシューティング

### 5. 関連ドキュメント
- 他MCPとの連携
- 参考リンク

---

## 💡 ベストプラクティス

### 1. MCPの組み合わせ
- 単一MCPで完結しない場合は複数を組み合わせる
- 各MCPの強みを活かす
- データフローを明確にする

### 2. エラーハンドリング
- 各MCP呼び出しでエラーチェック
- フォールバック戦略を用意
- ログを適切に記録

### 3. パフォーマンス
- 並列実行可能な操作は並列化
- 不要な呼び出しを避ける
- キャッシュを活用

### 4. セキュリティ
- 認証情報を環境変数で管理
- 最小権限の原則
- ログに機密情報を含めない

---

## 🆕 新しいMCPガイドの追加

新しいMCPのガイドを追加する際は、以下のテンプレートを使用:

```markdown
# [MCP名] 使用ガイド

## 📋 基本情報
### 目的
### 前提条件
### 制約事項

## 🎯 コア原則
### 原則1
### 原則2

## 🔄 標準フロー
### ステップ1
### ステップ2

## 📚 実践例
### 例1
### 例2

## ⚠️ 重要な警告

## 🔗 関連ドキュメント
```

---

## 🔗 関連ドキュメント

- [n8n MCP統合ガイド](../mcp-integration-guide.md)
- [ベストプラクティス](../best-practices.md)
- [ノードパターン](../node-patterns.md)
- [トラブルシューティング](../troubleshooting.md)

---

## 📞 サポート

問題が発生した場合:

1. 該当MCPのガイドを確認
2. トラブルシューティングセクションを参照
3. 関連ドキュメントを確認
4. GitHubでIssueを作成

---

**作成日**: 2025-10-26  
**最終更新**: 2025-10-26  
**メンテナー**: AI Assistant
