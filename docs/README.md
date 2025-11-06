# ドキュメント

n8nワークフロー開発・運用に関するドキュメント集

## 📚 ドキュメント一覧

### [mcp/](mcp/)
MCP使用ガイド集

- **[n8n-mcp-usage-guide.md](mcp/n8n-mcp-usage-guide.md)** - n8n-MCP詳細使用ガイド
  - コア原則（サイレント実行、並列実行、テンプレート優先）
  - 8ステップワークフロープロセス
  - バリデーション戦略（4レベル）
  - バッチ操作とCRITICAL構文
  - 最も人気のあるn8nノード20選

- **[zie619-n8n-workflows-guide.md](mcp/zie619-n8n-workflows-guide.md)** - Zie619 n8n-workflows MCP使用ガイド
  - 世界最大のn8nワークフローコレクション（2,053ワークフロー）へのアクセス
  - 365ユニークインテグレーションの活用方法
  - カテゴリー別・トリガー別・複雑度別の高度な検索
  - 実践的なユースケース別ガイド（LINE CRM、レポート自動化など）
  - ワークフローのインポートとカスタマイズ手順

### [prompt-design-guide.md](prompt-design-guide.md) ⭐ START HERE
**プロンプト設計指針書** - 要件定義からプロンプト作成まで

- **3ステップのワークフロー**: 要件定義 → プロンプト整形 → 実行と改善
- **要件定義テンプレート**: そのままコピーして使える
- **MCP選択基準**: フローチャートとクイックリファレンス
- **プロンプト構造テンプレート**: 5種類の用途別テンプレート
- **実践例3つ**: LINE CRM、パフォーマンス改善、AIエージェント生成
- **完全チェックリスト**: 各ステップの確認項目

### [prompt-templates.md](prompt-templates.md)
最適なプロンプトテンプレート集

- 全MCPとナレッジベースを活用するプロンプト例（15パターン）
- ワークフロー作成・改善・トラブルシューティング
- AIエージェント構築・運用最適化・高度な活用
- プロンプト作成のベストプラクティス
- 実践ワークフローと成功事例

### [best-practices.md](best-practices.md)
n8nワークフロー開発のベストプラクティス

- ワークフロー設計の原則
- エラーハンドリング
- セキュリティ対策
- パフォーマンス最適化

### [mcp-integration-guide.md](mcp-integration-guide.md)
n8n MCP統合ガイド

- n8n MCPの概要とセットアップ
- 主要機能（ノード検索、ワークフロー管理、テンプレート活用、バリデーション）
- MCP連携パターン（Sequential、Playwright、Context7、Magic）
- 実践例（Webhook、Slack通知、データベース統合）
- トラブルシューティング
- ベストプラクティス

### [n8n-workflows-generator-prompt.md](n8n-workflows-generator-prompt.md)
n8n Workflows Generator プロンプト

- スクリーンショットからワークフローJSONを生成
- 動的フェーズ生成（3-15フェーズ）
- スマート適応ルール
- 視覚分析・再構築パターン
- 完全な実装ガイド

### [AI Agent Army Generator](../workflows/ai-agents/agent-army-generator-prompt.md)
AIエージェント軍生成プロンプト

- ビジネス要件から6-8個の専門AIエージェントを自動設計
- マスターコーディネーター + 専門エージェント3個を完全実装
- 実在するn8nノードと検証済みAPIのみを使用
- 100%インポート可能なワークフローJSON生成
- RetroFuture Gadgetryの事例を参考

### [node-knowledge-base.json](node-knowledge-base.json)
n8nノード知識ベース

- 主要ノードの定義（Webhook、Set、HTTP Request、IF）
- ノードフィールドの詳細仕様
- よくある問題パターンと解決策

### [node-patterns.md](node-patterns.md)
よく使うノードパターン集

- HTTP Requestノードの使い方
- Function/Code ノードのパターン
- Switch/IF ノードの条件分岐
- データ変換パターン

### [troubleshooting.md](troubleshooting.md)
トラブルシューティングガイド

- よくあるエラーと解決方法
- デバッグ手法
- ログの読み方
- パフォーマンス問題の対処

### [api-references.md](api-references.md)
外部API仕様メモ

- LINE Messaging API
- Notion API
- その他連携API

### [knowledge/](knowledge/) 🆕
**実践から生まれたナレッジベース** - ワークフロー構築の失敗と成功から学ぶ

- **[n8n-workflow-construction-knowledge.md](knowledge/n8n-workflow-construction-knowledge.md)** ⭐ 必読
  - HTTP Request Node v4 設定ルール（`specifyBody`の正しい使い方）
  - n8n式構文のベストプラクティス（`={{ }}`の罠を避ける）
  - ノード参照とデータアクセスの正しい方法
  - ワークフロー更新戦略（部分更新vs完全更新）
  - テストとデバッグアプローチ（TDD、段階的テスト）
  - Notion API統合の実践的ガイド
  - 完全なチェックリスト（設計→実装→テスト→デバッグ）
  - **出典**: WF6構築時の実際のエラーと解決方法（Execution 816-823）

## 🎯 使い方

### 🚀 初めての方（推奨順序）

1. **[prompt-design-guide.md](prompt-design-guide.md)を読む** ⭐⭐⭐ まずはここから！
   - 要件定義の書き方を学ぶ（テンプレートあり）
   - プロンプトへの変換方法を理解
   - 実践例を見ながら試す
   
2. **[prompt-templates.md](prompt-templates.md)で具体例を学ぶ** ⭐⭐
   - すぐに使える15パターンを確認
   - 自分のケースに近いものを見つける
   
3. **[best-practices.md](best-practices.md)で基本を理解** ⭐
   - ワークフロー設計の原則
   - エラーハンドリングとセキュリティ
   
4. **[mcp-integration-guide.md](mcp-integration-guide.md)でMCP統合を学習**
   - MCP全体の概要
   - セットアップ方法
   
5. **[mcp/n8n-mcp-usage-guide.md](mcp/n8n-mcp-usage-guide.md)で詳細を学習**
   - n8n-MCPの高度な使用方法
   - バリデーション戦略
   
6. **実際にワークフローを作成**
   - prompt-design-guideのテンプレートを使用
   - 要件定義 → プロンプト整形 → 実行
   
7. **問題が発生したら[troubleshooting.md](troubleshooting.md)を参照**

### n8n-MCPを使用する場合

1. [mcp/README.md](mcp/README.md)でMCP全体の概要を確認
2. [mcp/n8n-mcp-usage-guide.md](mcp/n8n-mcp-usage-guide.md)で詳細な使用手順を確認
3. コア原則に従ってワークフローを構築:
   - サイレント実行
   - 並列実行
   - テンプレート優先
   - 多層バリデーション
   - デフォルト値を信頼しない

### スクリーンショットからワークフロー生成

1. [n8n-workflows-generator-prompt.md](n8n-workflows-generator-prompt.md)のプロンプトを使用
2. ワークフローのスクリーンショットを提供
3. 生成されたJSONをn8nにインポート
4. 認証情報を設定して実行

### AIエージェント軍の自動生成

1. [AI Agent Army Generator](../workflows/ai-agents/agent-army-generator-prompt.md)のプロンプトを使用
2. あなたのビジネス要件を記述（使用ツール含む）
3. 6-8個のエージェント案が提示される
4. 最重要3個のエージェントとマスターコーディネーターのJSONが生成される
5. n8nにインポートして、Workflow IDを設定
6. 認証情報を設定してテスト

### 経験者の方

- **ワークフロー構築前に**: [knowledge/n8n-workflow-construction-knowledge.md](knowledge/n8n-workflow-construction-knowledge.md)で既知の罠を確認
- **デバッグ時に**: [knowledge/](knowledge/)ディレクトリで類似エラーパターンを検索
- 新しいパターンを発見したら[node-patterns.md](node-patterns.md)に追加
- トラブルシューティング事例を[troubleshooting.md](troubleshooting.md)に記録
- **重要な知見は**: [knowledge/](knowledge/)ディレクトリに体系的に整理
- API仕様の変更を[api-references.md](api-references.md)に反映
- MCP連携の新しいパターンを[mcp-integration-guide.md](mcp-integration-guide.md)に追加
- 新しいMCP使用手順を[mcp/](mcp/)ディレクトリに追加

## 🔄 ドキュメントの更新

ドキュメントは常に最新の状態に保つことが重要です:

- ✅ 新しいパターンを発見したら即座に記録
- ✅ エラー解決方法を見つけたら共有
- ✅ **実践から得られた知見は[knowledge/](knowledge/)に体系化**
- ✅ API仕様変更があれば更新
- ✅ ベストプラクティスは定期的に見直し
- ✅ MCP使用手順を継続的に改善

## 💡 コントリビューション

ドキュメントの改善提案は大歓迎です!

1. 誤字・脱字の修正
2. 説明の追加・改善
3. 新しいパターンの追加
4. 実例の追加
5. 新しいMCP使用ガイドの追加

プルリクエストをお待ちしています。

---

最終更新: 2025-10-29
