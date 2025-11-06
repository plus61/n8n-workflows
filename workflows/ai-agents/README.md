# AIエージェントワークフロー

n8nのLangChainノードを使用したAIエージェント実装例

---

## 📋 ワークフロー一覧

RetroFuture Gadgetryビジネスを運営するための包括的なAIエージェント軍。各エージェントは特定のビジネス機能に特化しています。

> 💡 **新しいAIエージェント軍を生成したい場合**:
> - 📖 [クイックスタートガイド](QUICKSTART.md) - 5分で始める（初心者向け）
> - 📚 [詳細プロンプト](agent-army-generator-prompt.md) - 完全なドキュメント（詳細設定）
> 
> このプロンプトを使用すると、あなた独自のビジネス要件に基づいた複数のAIエージェントシステムを自動生成できます。

### [retrofuture-master-assistant.json](retrofuture-master-assistant.json)

**RetroFuture マスターアシスタント**

全てのエージェントを統括するマスターエージェント。顧客の問い合わせを分析し、適切な専門エージェントにルーティングします。

#### 主要機能
- クエリの意図分析
- 適切なエージェントへのルーティング
- 複数エージェント間の調整
- 統合レスポンスの生成

---

### [retrofuture-custom-orders-agent.json](retrofuture-custom-orders-agent.json)

**RetroFuture Gadgetry カスタムオーダーエージェント**

カスタムガジェット注文を管理するAIエージェント。デザインコンサルテーションから配送まで、オーダーメイドのスチームパンク、アールデコ、レトロフューチャー風デバイスのリクエストを処理します。

#### 主要機能

**注文管理**
- カスタムオーダー作成
- パーソナライゼーションオプション設定
- 製造タイムライン設定
- 注文進捗追跡

**デザイン設定**
- カスタム仕様のキャプチャ
- 素材選択
- 彫刻詳細
- 特別機能のセットアップ

**統合サービス**
- Airtable: 注文パイプライン管理
- Gmail: 注文確認とデザインモックアップの送信
- Google Sheets: 在庫管理とコスト計算
- Slack: 職人チームへの通知

#### 製品カテゴリ

**ガジェットタイプ**
- スチームパンクUSBドライブ
- アールデコスマートウォッチ
- ディーゼルパンク携帯ケース
- アトムパンクデスクアクセサリー
- サイバーパンクゲーミング周辺機器

**カスタマイゼーションオプション**
- 真鍮・銅仕上げ
- 再生木材インレイ
- ヴィンテージレザーラッピング
- カスタムギアメカニズム
- レーザー彫刻
- カスタムパティーナ仕上げ
- イルミネーションオプション

#### ビジネスルール

- 最低注文金額: $150
- リードタイム: 2-6週間
- ラッシュオーダー: +50%追加料金
- 限定版: 最大50ユニット

#### 使用ノード

1. **Custom Orders Agent** (`@n8n/n8n-nodes-langchain.agent`)
   - メインのAIエージェント
   - GPT-4oを使用

2. **OpenAI Chat Model** (`@n8n/n8n-nodes-langchain.lmChatOpenAi`)
   - 言語モデル: gpt-4o

3. **Create Custom Order** (`@n8n/n8n-nodes-langchain.toolHttpRequest`)
   - カスタムオーダーAPI呼び出し

4. **Configure Design** (`@n8n/n8n-nodes-langchain.toolHttpRequest`)
   - デザイン設定API呼び出し

5. **Create Order Record** (`n8n-nodes-base.airtableTool`)
   - Airtableに注文記録を作成

6. **Send Order Confirmation** (`n8n-nodes-base.gmailTool`)
   - Gmail経由で確認メール送信

7. **Track Order** (`n8n-nodes-base.googleSheetsTool`)
   - Google Sheetsで注文追跡

8. **Notify Artisan Team** (`n8n-nodes-base.slackTool`)
   - Slackで職人チームに通知

9. **Get Order Status** (`@n8n/n8n-nodes-langchain.toolHttpRequest`)
   - 注文ステータス取得

#### セットアップ手順

##### 1. 認証情報の設定

**必要な認証情報**:
- OpenAI API Key
- RetroFuture API Key
- Airtable API Key
- Gmail OAuth2
- Google Sheets OAuth2
- Slack OAuth2

##### 2. API設定

**RetroFuture API**:
- ベースURL: `https://api.retrofuturegadgetry.com/v2`
- エンドポイント:
  - `POST /orders` - 注文作成
  - `POST /design/configure` - デザイン設定
  - `GET /orders/{orderId}/status` - ステータス取得

##### 3. Airtable設定

**必要なテーブル**:
- Orders: 注文管理
- Customers: 顧客情報
- Inventory: 在庫管理

##### 4. Google Sheets設定

**必要なシート**:
- Order Tracking: 注文追跡
- Material Inventory: 素材在庫
- Cost Calculations: コスト計算

##### 5. Slack設定

**必要なチャネル**:
- #custom-orders: 一般的な注文通知
- #rush-orders: 緊急注文アラート
- #design-approvals: デザイン承認

#### 使用方法

##### 基本的な注文フロー

1. **トリガー**: 別のワークフローから実行
2. **エージェント処理**: ユーザークエリを解析
3. **注文作成**: APIを通じて注文を作成
4. **デザイン設定**: カスタマイゼーションを設定
5. **記録作成**: Airtableに記録
6. **確認送信**: Gmailで顧客に確認
7. **追跡開始**: Google Sheetsで追跡
8. **チーム通知**: Slackで職人チームに通知

##### クエリ例

```json
{
  "query": "I want to order a steampunk USB drive with brass finish and custom engraving 'JD 2025'"
}
```

```json
{
  "query": "What's the status of my order #12345?"
}
```

```json
{
  "query": "I need 10 art deco smartwatches with copper finish for a corporate gift, rush delivery needed"
}
```

#### エラーハンドリング

- **成功**: `Response`ノードで結果を返す
- **エラー**: `Try Again`ノードでエラーメッセージを返す
- **エージェントエラー**: `continueErrorOutput`で継続

#### パフォーマンス最適化

**推奨設定**:
- タイムアウト: 60秒
- リトライ: 3回
- 並列実行: 無効（順次処理）

#### トラブルシューティング

##### よくある問題

**1. API認証エラー**
```
Error: 401 Unauthorized
```
**解決策**: RetroFuture API Keyを確認

**2. Airtable接続エラー**
```
Error: Cannot connect to Airtable
```
**解決策**: Airtable認証情報を再設定

**3. Gmail送信エラー**
```
Error: Failed to send email
```
**解決策**: Gmail OAuth2スコープを確認

**4. エージェントタイムアウト**
```
Error: Execution timed out
```
**解決策**: タイムアウト設定を延長

#### カスタマイズ

##### システムメッセージの変更

`Custom Orders Agent`ノードの`systemMessage`を編集:
- 製品カテゴリの追加
- ビジネスルールの変更
- カスタマイゼーションオプションの追加

##### ツールの追加

新しいツールノードを追加して`ai_tool`接続を作成:
1. 新しいツールノードを追加
2. `Custom Orders Agent`の`ai_tool`入力に接続
3. ツールの説明とパラメータを設定

##### 通知のカスタマイズ

`Send Order Confirmation`ノードを編集:
- メールテンプレートの変更
- 添付ファイルの追加
- CC/BCCの設定

#### ベストプラクティス

1. **明確なツール説明**: 各ツールの`toolDescription`を明確に記述
2. **適切なエラーハンドリング**: すべてのAPIコールにエラーハンドリングを実装
3. **詳細なログ**: 重要なステップでログを記録
4. **テスト**: 本番環境前に十分なテスト
5. **監視**: 実行ログを定期的に確認

#### 拡張アイデア

- **在庫自動チェック**: 注文前に在庫を自動確認
- **価格自動計算**: カスタマイゼーションに基づいて価格を自動計算
- **デザインプレビュー生成**: AIでデザインモックアップを自動生成
- **職人スキルマッチング**: 注文の複雑さに基づいて最適な職人を自動割り当て
- **進捗写真自動送信**: 製造段階で自動的に進捗写真を送信

---

### [retrofuture-sales-design-agent.json](retrofuture-sales-design-agent.json)

**RetroFuture セールス&デザインエージェント**

営業とデザインコンサルテーションを担当。顧客のニーズを理解し、最適な製品提案とデザインアドバイスを提供します。

#### 主要機能
- 製品カタログ案内
- デザイン提案
- 見積もり作成
- カスタマイゼーションオプションの説明

---

### [retrofuture-customer-experience-agent.json](retrofuture-customer-experience-agent.json)

**RetroFuture カスタマーエクスペリエンスエージェント**

顧客サポートと満足度管理を担当。問い合わせ対応、クレーム処理、フィードバック収集を行います。

#### 主要機能
- カスタマーサポート
- 問い合わせ対応
- クレーム処理
- 満足度調査

---

### [retrofuture-artisan-production-agent.json](retrofuture-artisan-production-agent.json)

**RetroFuture 職人製造エージェント**

製造プロセスと職人チームの管理を担当。製造スケジュール、品質管理、職人のスキルマッチングを行います。

#### 主要機能
- 製造スケジュール管理
- 職人割り当て
- 品質管理
- 製造進捗追跡

---

### [retrofuture-workshop-technical-agent.json](retrofuture-workshop-technical-agent.json)

**RetroFuture ワークショップ技術エージェント**

技術的な問題とワークショップ運営を担当。設備管理、技術サポート、製造ツールの最適化を行います。

#### 主要機能
- 設備メンテナンス管理
- 技術トラブルシューティング
- ツール在庫管理
- 製造プロセス最適化

---

### [retrofuture-supply-chain-agent.json](retrofuture-supply-chain-agent.json)

**RetroFuture サプライチェーンエージェント**

サプライチェーンと在庫管理を担当。素材調達、在庫最適化、サプライヤー管理を行います。

#### 主要機能
- 素材在庫管理
- 発注管理
- サプライヤー調整
- 在庫最適化

---

### [retrofuture-order-analytics-agent.json](retrofuture-order-analytics-agent.json)

**RetroFuture オーダー分析エージェント**

ビジネス分析とレポーティングを担当。売上分析、トレンド予測、KPIダッシュボードの生成を行います。

#### 主要機能
- 売上分析
- トレンド分析
- KPIレポート生成
- 予測分析

---

## 🎯 AIエージェントのベストプラクティス

### システムメッセージの設計

1. **明確な役割定義**: エージェントの役割と責任を明確に
2. **利用可能なツール**: すべてのツールを明示的にリスト
3. **ビジネスルール**: 制約と条件を明確に記述
4. **コンテキスト情報**: 現在の日時などの動的情報を含める

### ツール設計

1. **単一責任**: 各ツールは1つの明確な目的を持つ
2. **明確な説明**: `toolDescription`を詳細に記述
3. **適切なパラメータ**: 必要なパラメータを明確に定義
4. **エラーハンドリング**: 各ツールで適切なエラー処理

### パフォーマンス

1. **タイムアウト設定**: 適切なタイムアウトを設定
2. **並列実行**: 可能な場合は並列実行を検討
3. **キャッシュ活用**: 頻繁にアクセスするデータをキャッシュ
4. **ログ最適化**: 必要なログのみを記録

### セキュリティ

1. **認証情報管理**: n8nの認証情報機能を使用
2. **入力検証**: ユーザー入力を常に検証
3. **権限管理**: 最小権限の原則を適用
4. **監査ログ**: 重要な操作をログに記録

---

## 🔗 関連ドキュメント

- [n8n LangChain公式ドキュメント](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/)
- [n8n-MCP使用ガイド](../../docs/mcp/n8n-mcp-usage-guide.md)
- [ベストプラクティス](../../docs/best-practices.md)
- [ノードパターン](../../docs/node-patterns.md)

---

**作成日**: 2025-10-26  
**最終更新**: 2025-10-26  
**カテゴリ**: AIエージェント、LangChain、カスタムオーダー管理
