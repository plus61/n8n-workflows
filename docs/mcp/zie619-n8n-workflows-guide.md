# Zie619 n8n-workflows MCP 使用ガイド

世界最大のn8nワークフローコレクション（2,053ワークフロー、365インテグレーション）へのアクセス方法

参照: [Zie619/n8n-workflows GitHub Repository](https://github.com/Zie619/n8n-workflows)

---

## 📋 目次

- [概要](#概要)
- [MCP設定](#mcp設定)
- [基本的な使用方法](#基本的な使用方法)
- [高度な検索テクニック](#高度な検索テクニック)
- [ワークフローの活用](#ワークフローの活用)
- [カテゴリー別リファレンス](#カテゴリー別リファレンス)
- [トラブルシューティング](#トラブルシューティング)

---

## 📖 概要

### Zie619/n8n-workflowsとは

世界最大級のn8nワークフローコレクションで、以下の特徴があります：

**統計情報**:
- 📊 **2,053ワークフロー** - 包括的なコレクション
- 🔌 **365ユニークインテグレーション** - あらゆるサービスに対応
- 📈 **29,445ノード** - 豊富な実装例
- 🏷️ **15カテゴリー** - 体系的な分類

**主な機能**:
- ✅ フルテキスト検索（SQLite FTS5）
- ✅ カテゴリー別フィルタリング
- ✅ トリガータイプ別検索
- ✅ 複雑度別フィルター
- ✅ Mermaidダイアグラム生成
- ✅ RESTful API

### なぜこのリポジトリを使うのか

1. **実証済みのワークフロー** - 実際に動作する2,000以上の例
2. **幅広いカバレッジ** - ほぼすべてのn8nインテグレーション
3. **学習リソース** - ベストプラクティスとパターン
4. **時間節約** - ゼロから構築する必要なし
5. **コミュニティ駆動** - 継続的な更新と改善

---

## 🔧 MCP設定

### 前提条件

既にCursor/Claude Desktop AppでMCP設定が完了していることを確認してください。

**確認方法**:

```bash
# Cursorの場合
cat .cursor/mcp.json | grep "n8n-workflows-docs"

# Claude Desktop Appの場合
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | grep "n8n-workflows-docs"
```

### 設定内容

`.cursor/mcp.json`または`claude_desktop_config.json`に以下が含まれていることを確認：

```json
{
  "mcpServers": {
    "n8n-workflows-docs": {
      "command": "/Users/[ユーザー名]/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "mcp-remote", "https://gitmcp.io/Zie619/n8n-workflows/blob/main/README.md"]
    }
  }
}
```

### 動作確認

MCPが正しく設定されているか確認：

**Cursorの場合**:
- 右下のMCP接続ステータスを確認
- `n8n-workflows-docs`が接続済みと表示される

**Claude Desktop Appの場合**:
- チャットで「@n8n-workflows-docs」とメンションできる

---

## 🚀 基本的な使用方法

### 1. ワークフロー検索の基本

#### テキスト検索

**Claude/Cursorに質問**:

```
@n8n-workflows-docs Telegramを使った自動化ワークフローを探して
```

**具体的な使用例**:

```
# メッセージング関連
@n8n-workflows-docs LINEとNotionを連携したワークフローはありますか？

# データ処理
@n8n-workflows-docs Googleスプレッドシートのデータを自動処理する例を教えて

# API統合
@n8n-workflows-docs SlackとAirtableを連携する方法は？

# スケジュール実行
@n8n-workflows-docs 毎日自動実行されるワークフローの例は？
```

### 2. カテゴリー別検索

#### 15の主要カテゴリー

1. **Messaging** - Telegram, Discord, Slack, LINE
2. **CRM & Sales** - HubSpot, Salesforce, Pipedrive
3. **Data & Analytics** - Google Sheets, Excel, データ処理
4. **Marketing & Email** - Mailchimp, SendGrid, メール自動化
5. **Productivity** - Notion, Trello, Asana, タスク管理
6. **Social Media** - LinkedIn, Twitter, Facebook, Instagram
7. **AI & ML** - OpenAI, GPT, 機械学習
8. **E-commerce** - Shopify, WooCommerce, 決済
9. **Cloud Storage** - Google Drive, Dropbox, S3
10. **Finance** - Stripe, PayPal, 会計
11. **Development** - GitHub, GitLab, CI/CD
12. **Monitoring** - アラート, ログ, 監視
13. **Forms & Surveys** - Google Forms, Typeform
14. **Media** - 画像処理, 動画, メディア配信
15. **Database** - PostgreSQL, MySQL, MongoDB

**使用例**:

```
# カテゴリー指定
@n8n-workflows-docs Messagingカテゴリーのワークフローを10個教えて

# 複数サービス組み合わせ
@n8n-workflows-docs NotionとGoogleスプレッドシートを使ったProductivityワークフローは？

# 特定インテグレーション
@n8n-workflows-docs OpenAIを使ったAI関連ワークフローを探して
```

### 3. トリガータイプ別検索

**4つのトリガータイプ**:

- **Webhook** (519ワークフロー) - 外部イベントで起動
- **Scheduled** (226ワークフロー) - スケジュール実行
- **Manual** (477ワークフロー) - 手動実行
- **Complex** (831ワークフロー) - 複数トリガー/高度なロジック

**使用例**:

```
# Webhookトリガー
@n8n-workflows-docs Webhookトリガーを使ったLINE連携の例は？

# スケジュール実行
@n8n-workflows-docs 毎日実行されるデータ収集ワークフローを探して

# 手動実行
@n8n-workflows-docs 必要な時だけ実行するレポート生成ワークフローは？
```

### 4. 複雑度別検索

**ワークフローの複雑度**:

- **Simple** - 5ノード以下
- **Medium** - 6-15ノード
- **Complex** - 16ノード以上

**使用例**:

```
# シンプルなワークフロー（学習用）
@n8n-workflows-docs 初心者向けのシンプルなSlack通知ワークフローは？

# 中程度の複雑さ
@n8n-workflows-docs 中程度の複雑さのデータ処理ワークフローを教えて

# 複雑なワークフロー（エンタープライズ向け）
@n8n-workflows-docs 複雑なマルチステップのCRMワークフローを探して
```

---

## 🎯 高度な検索テクニック

### 1. 複数条件での検索

```
@n8n-workflows-docs 
以下の条件でワークフローを探して：
- Webhookトリガー
- NotionとSlackを使用
- 中程度の複雑さ
```

### 2. 特定のユースケース

```
# リード管理
@n8n-workflows-docs リード情報をNotionに自動登録するワークフローは？

# レポート自動化
@n8n-workflows-docs 週次レポートを自動生成してSlackに送信する方法は？

# データ同期
@n8n-workflows-docs Google SheetsとAirtableのデータを同期するワークフローは？

# エラー通知
@n8n-workflows-docs エラー発生時にSlack通知を送るパターンを教えて
```

### 3. インテグレーション組み合わせ

```
# 3サービス連携
@n8n-workflows-docs LINE、Notion、Slackの3つを連携したワークフローは？

# データフロー
@n8n-workflows-docs Webhookで受信 → 処理 → Notionに保存 → Slack通知の流れを持つワークフローは？
```

### 4. ノード数での検索

```
# 大規模ワークフロー
@n8n-workflows-docs 30ノード以上の複雑なワークフローの例は？

# 効率的なワークフロー
@n8n-workflows-docs 最小限のノードで最大限の効果を出すワークフローは？
```

---

## 💡 ワークフローの活用

### インポート手順

#### 1. ワークフローJSONの取得

**MCPを使用して取得**:

```
@n8n-workflows-docs [ファイル名]のワークフローJSONをダウンロードしたい
```

**または直接GitHubから**:

1. [Zie619/n8n-workflows](https://github.com/Zie619/n8n-workflows/tree/main/workflows)にアクセス
2. 目的のワークフローを検索
3. JSONファイルをダウンロード

#### 2. n8nへのインポート

```bash
# n8n管理画面で
1. 左メニュー > Workflows
2. 右上の「...」メニュー > Import from File
3. ダウンロードしたJSONファイルを選択
4. インポート完了
```

#### 3. カスタマイズ

**重要: セキュリティチェック**

- [ ] すべての認証情報を削除/置き換え
- [ ] APIキーとトークンを更新
- [ ] Webhook URLを自分のものに変更
- [ ] 個人情報やセンシティブデータを削除

**推奨カスタマイズ**:

```
1. ノード名を日本語化（オプション）
2. エラーハンドリングを追加/強化
3. 自分のユースケースに合わせてロジックを調整
4. テスト実行で動作確認
```

### ワークフロー命名規則

**Zie619リポジトリの命名パターン**:

```
[ID]_[Service1]_[Service2]_[Purpose]_[Trigger].json

例:
2051_Telegram_Webhook_Automation_Webhook.json
  ↓ 自動で変換
"Telegram Webhook Automation"
```

**理解のポイント**:

- **ID** - ワークフローの識別番号
- **Service** - 使用するサービス名（複数可）
- **Purpose** - ワークフローの目的
- **Trigger** - トリガータイプ（Webhook/Scheduled/Manual）

---

## 📚 カテゴリー別リファレンス

### Messaging & Communication

**主要サービス**:
- Telegram (多数のワークフロー)
- Discord (コミュニティ自動化)
- Slack (ビジネス通知)
- LINE (日本市場向け)

**典型的なユースケース**:

```
# ボット作成
@n8n-workflows-docs Telegramボットのワークフロー例を教えて

# 通知システム
@n8n-workflows-docs イベント発生時にDiscordに通知するワークフローは？

# チャット統合
@n8n-workflows-docs 複数のチャットプラットフォームを統合する方法は？
```

### Productivity & Project Management

**主要サービス**:
- Notion (データベース、ドキュメント)
- Trello (カンバン管理)
- Asana (タスク管理)
- Airtable (データベース)

**典型的なユースケース**:

```
# タスク自動化
@n8n-workflows-docs メール受信時にNotionにタスクを作成するワークフローは？

# プロジェクト管理
@n8n-workflows-docs GitHubのIssueをTrelloカードに同期する方法は？

# レポート生成
@n8n-workflows-docs Notionデータベースから週次レポートを生成するワークフローは？
```

### Data & Analytics

**主要サービス**:
- Google Sheets (データ管理)
- Excel (データ処理)
- PostgreSQL/MySQL (データベース)
- Google Analytics (分析)

**典型的なユースケース**:

```
# データ収集
@n8n-workflows-docs 複数ソースからデータを収集してGoogle Sheetsに統合するワークフローは？

# データ処理
@n8n-workflows-docs CSVデータを変換して別のフォーマットで保存する方法は？

# ダッシュボード更新
@n8n-workflows-docs 自動的にダッシュボードデータを更新するワークフローは？
```

### AI & Machine Learning

**主要サービス**:
- OpenAI (GPT、ChatGPT)
- Hugging Face (モデル)
- Google AI (各種AI API)

**典型的なユースケース**:

```
# テキスト生成
@n8n-workflows-docs OpenAI GPTを使ってコンテンツを自動生成するワークフローは？

# 画像処理
@n8n-workflows-docs 画像を自動的に分析・分類するワークフローは？

# センチメント分析
@n8n-workflows-docs 顧客フィードバックを自動分析するワークフローは？
```

### E-commerce & Payment

**主要サービス**:
- Shopify (ECプラットフォーム)
- WooCommerce (WordPress EC)
- Stripe (決済)
- PayPal (決済)

**典型的なユースケース**:

```
# 注文処理
@n8n-workflows-docs 新規注文時に自動的に処理を開始するワークフローは？

# 在庫管理
@n8n-workflows-docs 在庫が少なくなったら通知するワークフローは？

# 売上レポート
@n8n-workflows-docs 日次売上レポートを自動生成するワークフローは？
```

### Marketing & Email

**主要サービス**:
- Mailchimp (メールマーケティング)
- SendGrid (メール配信)
- Gmail (メール)
- HubSpot (マーケティングオートメーション)

**典型的なユースケース**:

```
# キャンペーン自動化
@n8n-workflows-docs メールキャンペーンを自動的に送信するワークフローは？

# リード育成
@n8n-workflows-docs リードに段階的なメールを送信するワークフローは？

# エンゲージメント追跡
@n8n-workflows-docs メール開封やクリックを追跡するワークフローは？
```

---

## 🔍 実践例：ユースケース別

### ユースケース1: LINE CRM統合

**目的**: LINE友だち追加時にNotionに自動記録

**検索クエリ**:

```
@n8n-workflows-docs LINEのWebhookを受信してNotionに保存するワークフローを探して
```

**学ぶべきポイント**:
- Webhook受信の設定方法
- データ変換のパターン
- Notion APIの使い方
- エラーハンドリング

### ユースケース2: 定期レポート生成

**目的**: 毎週月曜日に売上レポートを生成してSlackに送信

**検索クエリ**:

```
@n8n-workflows-docs スケジュール実行でデータを集計してSlackに送信するワークフローは？
```

**学ぶべきポイント**:
- スケジュールトリガーの設定
- データ集計のロジック
- レポートフォーマット
- Slack通知のベストプラクティス

### ユースケース3: マルチチャネル通知

**目的**: 重要なイベント発生時に複数のチャネルに通知

**検索クエリ**:

```
@n8n-workflows-docs 1つのイベントで複数のチャネル（Slack、Email、Discord）に通知するワークフローは？
```

**学ぶべきポイント**:
- 並列処理のパターン
- エラーハンドリング（一部失敗しても続行）
- 通知フォーマットの統一
- リトライロジック

### ユースケース4: データ同期

**目的**: Google SheetsとAirtableのデータを双方向同期

**検索クエリ**:

```
@n8n-workflows-docs Google SheetsとAirtableのデータを同期するワークフローは？
```

**学ぶべきポイント**:
- 双方向同期のロジック
- 衝突解決戦略
- 差分検出の方法
- パフォーマンス最適化

### ユースケース5: AIエージェント連携

**目的**: OpenAI GPTを使った自動応答システム

**検索クエリ**:

```
@n8n-workflows-docs OpenAI GPTを使って質問に自動応答するワークフローは？
```

**学ぶべきポイント**:
- OpenAI APIの統合
- プロンプトエンジニアリング
- コンテキスト管理
- レスポンスのフォーマット

---

## ⚙️ API使用例（上級者向け）

### 直接API呼び出し

Zie619リポジトリは独自のAPIを提供しています：

#### 1. ワークフロー検索

```bash
# テキスト検索
curl "http://localhost:8000/api/workflows?q=telegram+automation"

# フィルター付き検索
curl "http://localhost:8000/api/workflows?trigger=Webhook&complexity=high"

# カテゴリー検索
curl "http://localhost:8000/api/workflows/category/messaging"
```

#### 2. 統計情報取得

```bash
# データベース統計
curl "http://localhost:8000/api/stats"

# レスポンス例:
{
  "total": 2053,
  "active": 215,
  "inactive": 1838,
  "triggers": {
    "Complex": 831,
    "Webhook": 519,
    "Manual": 477,
    "Scheduled": 226
  },
  "total_nodes": 29445,
  "unique_integrations": 365
}
```

#### 3. カテゴリー一覧

```bash
# 利用可能なカテゴリー
curl "http://localhost:8000/api/categories"
```

#### 4. ワークフローダウンロード

```bash
# ワークフローJSON取得
curl "http://localhost:8000/api/workflows/{filename}/download" -o workflow.json
```

#### 5. Mermaidダイアグラム生成

```bash
# ワークフローの視覚化
curl "http://localhost:8000/api/workflows/{filename}/diagram"
```

### ローカルセットアップ（オプション）

独自のインスタンスを立ち上げる場合：

```bash
# リポジトリをクローン
git clone https://github.com/Zie619/n8n-workflows.git
cd n8n-workflows

# 依存関係をインストール
pip install -r requirements.txt

# サーバー起動
python run.py

# アクセス
# http://localhost:8000
```

---

## 🛠️ トラブルシューティング

### 問題1: MCPが接続できない

**症状**:
```
Error: Cannot connect to n8n-workflows-docs
```

**解決策**:

```bash
# 1. MCP設定を確認
cat .cursor/mcp.json | grep n8n-workflows-docs

# 2. npxのパスを確認
which npx

# 3. Cursorを再起動
# Cmd+Q で完全終了 → 再起動

# 4. MCPサーバーの再接続
# Cursorの右下 > MCP > Reconnect
```

### 問題2: ワークフローが見つからない

**症状**:
```
指定したワークフローが見つかりません
```

**解決策**:

```
# 1. より一般的なキーワードで検索
@n8n-workflows-docs Telegramに関連するワークフロー全般を教えて

# 2. カテゴリーから探す
@n8n-workflows-docs Messagingカテゴリーのワークフローを一覧表示して

# 3. 類似のインテグレーションで検索
@n8n-workflows-docs LINEではなくTelegramのワークフローは？
```

### 問題3: インポートしたワークフローが動作しない

**症状**:
```
ワークフローをインポートしたが実行時にエラー
```

**解決策チェックリスト**:

- [ ] **認証情報**: すべての認証情報を設定したか？
- [ ] **Webhook URL**: 自分のn8n URLに変更したか？
- [ ] **カスタムノード**: 必要なカスタムノードをインストールしたか？
- [ ] **n8nバージョン**: 互換性のあるn8nバージョンか？
- [ ] **API変更**: 外部サービスのAPIが変更されていないか？

**デバッグ手順**:

```
1. 各ノードを個別にテスト実行
2. エラーメッセージを確認
3. n8nのログを確認
4. 必要に応じてノードを再設定
```

### 問題4: 大量のワークフローから選べない

**症状**:
```
2,053個もあってどれを使えばいいかわからない
```

**解決策**:

```
# ステップ1: 自分のユースケースを明確化
具体的な質問をする：
@n8n-workflows-docs 
私のユースケース：
- LINEのWebhookを受信
- データをNotionに保存
- エラー時はSlack通知
このようなワークフローはありますか？

# ステップ2: シンプルなものから始める
@n8n-workflows-docs 
初心者向けのシンプルなWebhook受信ワークフローを教えて

# ステップ3: 徐々に複雑化
基本ワークフローを理解したら、より高度な例を探す
```

### 問題5: 特定のインテグレーションが見つからない

**症状**:
```
使いたいサービスのワークフローが見つからない
```

**解決策**:

```
# 1. 類似サービスを探す
@n8n-workflows-docs 
[使いたいサービス]に類似したサービスのワークフローはありますか？
例: Notionの代わりにAirtableのワークフロー

# 2. 汎用的なパターンを探す
@n8n-workflows-docs 
Webhookを受信してデータベースに保存する汎用的なパターンを教えて

# 3. カスタムノードを確認
一部のワークフローはカスタムノードを使用している可能性
```

---

## 📊 統計と推奨事項

### ワークフロートリガー分布

```
Complex:    831 (40.5%) - 複雑なビジネスロジック
Webhook:    519 (25.3%) - イベント駆動
Manual:     477 (23.2%) - オンデマンド実行
Scheduled:  226 (11.0%) - 定期実行
```

**推奨**:

- **学習**: まずManualトリガーのシンプルなワークフローから
- **実装**: Webhookトリガーで実用的な自動化
- **運用**: Scheduledトリガーで定期処理
- **最適化**: Complexパターンで高度な自動化

### 人気のインテグレーション Top 20

1. **HTTP Request** - 汎用API呼び出し
2. **Webhook** - イベント受信
3. **Set** - データ変換
4. **IF** - 条件分岐
5. **Function** - カスタムロジック
6. **Telegram** - メッセージング
7. **Google Sheets** - データ管理
8. **Discord** - コミュニティ
9. **Slack** - ビジネス通知
10. **OpenAI** - AI統合
11. **Notion** - データベース
12. **Airtable** - データ管理
13. **Gmail** - メール
14. **GitHub** - 開発ワークフロー
15. **Typeform** - フォーム
16. **Schedule** - 定期実行
17. **MySQL/PostgreSQL** - データベース
18. **Google Drive** - ファイル管理
19. **Stripe** - 決済
20. **HubSpot** - CRM

---

## 🎓 学習パス

### 初級レベル（1-2週間）

**目標**: 基本的なワークフローの理解と実装

```
ステップ1: シンプルなワークフローを探す
@n8n-workflows-docs 5ノード以下のシンプルなWebhook受信ワークフローを教えて

ステップ2: インポートとテスト
- ワークフローをインポート
- 各ノードの役割を理解
- テストデータで実行

ステップ3: カスタマイズ
- ノード名を変更
- データフローを追跡
- エラーハンドリングを追加

ステップ4: 実装
- 自分のユースケースに適用
- 本番環境でテスト
```

### 中級レベル（2-4週間）

**目標**: 複数サービス連携と複雑なロジック

```
ステップ1: 複数インテグレーション
@n8n-workflows-docs 3つ以上のサービスを連携するワークフローの例は？

ステップ2: データ変換
- 複雑なデータ変換パターンを学ぶ
- Functionノードの活用
- エラーハンドリングの強化

ステップ3: 条件分岐
- IF/Switchノードの使い方
- 複数の実行パスの管理
- ループ処理

ステップ4: 最適化
- パフォーマンスチューニング
- バッチ処理の実装
```

### 上級レベル（1-2ヶ月）

**目標**: エンタープライズグレードのワークフロー構築

```
ステップ1: 複雑なワークフロー分析
@n8n-workflows-docs 30ノード以上の複雑なエンタープライズワークフローを教えて

ステップ2: アーキテクチャパターン
- マイクロサービス的なワークフロー設計
- エラーリカバリー戦略
- モニタリングとアラート

ステップ3: AIエージェント統合
- LangChain統合
- マルチエージェントシステム
- コンテキスト管理

ステップ4: スケーリング
- 大量データの処理
- 並列実行の最適化
- リソース管理
```

---

## 🔗 関連リソース

### 公式ドキュメント

- [Zie619/n8n-workflows GitHub](https://github.com/Zie619/n8n-workflows) - メインリポジトリ
- [n8n公式ドキュメント](https://docs.n8n.io/) - n8nの公式ドキュメント
- [n8n Community](https://community.n8n.io/) - コミュニティフォーラム

### このプロジェクト内の関連ドキュメント

- [n8n-MCP使用ガイド](n8n-mcp-usage-guide.md) - n8n-MCPの詳細使用方法
- [MCP統合ガイド](../mcp-integration-guide.md) - MCP統合の全体像
- [ベストプラクティス](../best-practices.md) - n8nワークフローのベストプラクティス
- [AI Agent Army Generator](../../workflows/ai-agents/agent-army-generator-prompt.md) - AIエージェント生成プロンプト

### 技術スタック

**Zie619リポジトリの技術**:
- SQLite Database (FTS5フルテキスト検索)
- FastAPI Backend (RESTful API)
- Python 3.7+ (サーバーサイド)
- Responsive HTML5 Frontend (ブラウザUI)

---

## 💡 ベストプラクティス

### 1. ワークフロー選択

```
✅ 推奨:
- 自分のユースケースに近いものを選ぶ
- シンプルなものから始める
- アクティブなワークフローを優先
- ノード数が適切なものを選ぶ

❌ 避ける:
- 過度に複雑なものをいきなり使う
- 未検証のワークフローを本番環境で使う
- カスタムノード依存が多いものを避ける（最初は）
```

### 2. カスタマイズ

```
✅ 推奨:
- 段階的にカスタマイズ
- 各変更をテスト
- コメントを追加して理解を深める
- バージョン管理で変更を追跡

❌ 避ける:
- 一度に大量の変更
- テストなしで本番適用
- 元のロジックを理解せずに変更
```

### 3. セキュリティ

```
✅ 推奨:
- すべての認証情報を置き換える
- Webhook URLを確認
- センシティブデータを削除
- 本番環境でテスト

❌ 避ける:
- サンプルの認証情報をそのまま使用
- 個人情報を含むワークフローの共有
- 未検証のワークフローを本番で使用
```

### 4. 学習アプローチ

```
✅ 推奨:
- 各ノードの役割を理解
- データフローを追跡
- エラーハンドリングパターンを学ぶ
- コミュニティで質問

❌ 避ける:
- ブラックボックスとして使用
- エラーを無視
- ドキュメントを読まない
```

---

## 🎯 まとめ

### Zie619/n8n-workflowsの価値

1. **2,053の実証済みワークフロー** - 膨大な学習リソース
2. **365のインテグレーション** - あらゆるサービスに対応
3. **体系的な分類** - 探しやすい15カテゴリー
4. **高速検索** - SQLite FTS5による即時検索
5. **継続的更新** - コミュニティ駆動の改善

### MCPの利点

- **シームレスなアクセス** - Cursor/Claude Desktop Appから直接検索
- **コンテキスト保持** - 会話の中でワークフローを探せる
- **即座の参照** - コーディング中にすぐに例を確認
- **学習加速** - 実例からベストプラクティスを学べる

### 次のステップ

1. **MCP設定を確認** - 正しく接続されているか
2. **簡単な検索から始める** - よく使うサービスで検索
3. **ワークフローをインポート** - 実際に動かしてみる
4. **カスタマイズ** - 自分のユースケースに適用
5. **コミュニティに貢献** - 改善案や新しいワークフローを共有

---

**作成日**: 2025-10-26  
**最終更新**: 2025-10-26  
**バージョン**: 1.0  
**参照**: [Zie619/n8n-workflows](https://github.com/Zie619/n8n-workflows)

