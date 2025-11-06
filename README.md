# n8n Workflows ナレッジベース

n8nワークフローの設計パターン、ベストプラクティス、再利用可能なテンプレート集

## 📋 目次

- [概要](#概要)
- [リポジトリ構造](#リポジトリ構造)
- [ワークフロー一覧](#ワークフロー一覧)
- [使い方](#使い方)
- [MCP統合](#mcp統合)

## 🎯 概要

このリポジトリは、n8nワークフローの開発・運用におけるナレッジを体系的に管理するためのものです。

### 目的

- ✅ ワークフロー設計パターンの蓄積
- ✅ トラブルシューティング事例の記録
- ✅ ベストプラクティスの共有
- ✅ 再利用可能なテンプレートの提供
- ✅ バージョン管理による安全な運用
- ✅ **検証完了ワークフローの確実なバックアップ** → [バックアップポリシー](docs/workflow-backup-policy.md)

## 📁 リポジトリ構造

```
n8n-workflows/
├── README.md                          # このファイル
├── .n8n-config.json                   # n8nインスタンス設定 ⭐
├── workflows/                         # ワークフロー格納ディレクトリ
│   ├── backups/                      # バックアップディレクトリ ⭐
│   │   ├── YYYYMMDD_HHMMSS/         # 日次・定期バックアップ
│   │   ├── verified/                # 検証済みマイルストーン
│   │   └── archive/                 # 廃止ワークフロー
│   ├── line-crm/                     # LINE CRM統合
│   ├── wf7-sns-video-automation/     # WF7動画生成パイプライン
│   └── templates/                    # 再利用可能なテンプレート
├── templates/                         # n8nコミュニティテンプレート ⭐ NEW
│   ├── 00-index.json                 # テンプレートカタログ
│   ├── ai-video/                     # AI動画自動化テンプレート
│   ├── content-creation/             # コンテンツ生成テンプレート
│   ├── data-processing/              # データ処理テンプレート
│   ├── social-media/                 # SNS自動化テンプレート
│   └── business-automation/          # ビジネス自動化テンプレート
├── experiments/                       # テンプレート実験用 ⭐ NEW
│   └── YYYY-MM-DD-experiment-name/
├── docs/                             # ドキュメント
│   ├── templates/                    # テンプレートドキュメント ⭐ NEW
│   │   ├── README.md                # テンプレートライブラリガイド
│   │   └── quick-start.md           # クイックスタート
│   ├── workflow-backup-policy.md    # バックアップポリシー ⭐
│   ├── best-practices.md            # ベストプラクティス
│   ├── node-patterns.md             # ノードパターン集
│   ├── troubleshooting.md           # トラブルシューティング
│   └── api-references.md            # API仕様メモ
├── scripts/                          # ユーティリティスクリプト
│   ├── build-template-index.js      # テンプレートインデックス生成 ⭐ NEW
│   └── find-template.js             # テンプレート検索CLI ⭐ NEW
└── assets/                           # 画像・スクリーンショット
```

## 🔧 ワークフロー一覧

### LINE CRM統合

- **LINE Lead Pipeline - Notion**: LINE友だち追加・メッセージ・リッチメニューをNotionに記録
- **LINE Step Delivery**: 段階的な情報配信システム
- **LINE Rich Menu Integration**: リッチメニュー連携

詳細: [workflows/line-crm/README.md](workflows/line-crm/README.md)

### AIエージェント軍

- **RetroFuture Gadgetry**: カスタムガジェット製造ビジネス向けの8つの専門AIエージェント
  - Master Assistant（マスターコーディネーター）
  - Custom Orders（カスタムオーダー管理）
  - Sales & Design（営業・デザイン）
  - Customer Experience（カスタマーサポート）
  - Artisan Production（職人製造）
  - Workshop Technical（ワークショップ技術）
  - Supply Chain（サプライチェーン）
  - Order Analytics（オーダー分析）

詳細: [workflows/ai-agents/README.md](workflows/ai-agents/README.md)

> 💡 あなた独自のAIエージェント軍を生成: [AI Agent Army Generator](workflows/ai-agents/agent-army-generator-prompt.md)

## ⚙️ n8nインスタンス設定

**プロジェクト全体で統一されたn8nインスタンスURLを使用するため、`.n8n-config.json`で中央管理しています。**

### 現在のインスタンス
- **URL**: `https://n8n-python-production-344b.up.railway.app`
- **プラットフォーム**: Railway
- **Webhook Base**: `https://n8n-python-production-344b.up.railway.app/webhook`

### 環境変数（Railway）
```bash
N8N_HOST=n8n-python-production-344b.up.railway.app
N8N_EDITOR_BASE_URL=https://n8n-python-production-344b.up.railway.app
WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app
```

> ⚠️ **重要**: 古いインスタンス（`primary-production-cb87.up.railway.app`）は使用禁止です。全ての参照は新インスタンスに統一されています。

詳細: [.n8n-config.json](.n8n-config.json)

## 🚀 使い方

### ⚡ クイックスタート

**最も効率的な始め方**（3ステップ）:

#### 1. **[プロンプト設計指針書](docs/prompt-design-guide.md)を読む** ⭐⭐⭐ まずはここ！
   - 要件定義の書き方（コピー可能なテンプレート）
   - プロンプトへの変換ルール（フローチャート）
   - 実践例3つ（LINE CRM、パフォーマンス改善、AIエージェント）

   **推奨フロー**:
   ```
   要件定義を書く → プロンプトに整形 → Cursor/Claudeで実行
   ```

#### 2. **[プロンプトテンプレート集](docs/prompt-templates.md)で具体例を見る** ⭐⭐
   - すぐに使える15種類のプロンプト例
   - ワークフロー作成・改善・トラブルシューティング
   - 全MCPとナレッジベースの活用方法

#### 3. **実際に試す**
   - テンプレートをコピー
   - 自分の要件を記入
   - Cursor/Claudeで実行
   - 結果を確認して改善

**詳細を学ぶ**:
   - [ベストプラクティス](docs/best-practices.md)
   - [MCP統合ガイド](docs/mcp-integration-guide.md)

---

### 🔍 n8nコミュニティテンプレート活用 ⭐ NEW

**399+のコミュニティテンプレートから学び、再利用する**

#### クイックアクセス
```bash
# テンプレート検索
node scripts/find-template.js "AI video automation"

# カテゴリ一覧
node scripts/find-template.js --list-categories

# 対話的検索
node scripts/find-template.js --interactive
```

#### 主なカテゴリ
- 🎬 **AI Video Automation** (10 templates) - 動画生成・編集・公開
- ✍️ **Content Creation** - コンテンツ生成・SEO最適化
- 🔄 **Data Processing** - ETLパイプライン・データ変換
- 📱 **Social Media** - SNS管理・スケジューリング
- 💼 **Business Automation** - CRM統合・営業プロセス

#### ドキュメント
- 📚 [テンプレートライブラリガイド](docs/templates/README.md)
- ⚡ [クイックスタートガイド](docs/templates/quick-start.md)
- 🎯 [wf7統合例](docs/templates/README.md#integration-patterns)

**使用例**: wf7へのElevenLabs音声合成統合
```bash
# 1. 音声テンプレート検索
node scripts/find-template.js "ElevenLabs voice"

# 2. テンプレート詳細取得（Claude Code内）
mcp__n8n-mcp__get_template({ templateId: 3553, mode: "structure" })

# 3. 実験環境でテスト
mkdir experiments/2025-11-05-elevenlabs-test

# 4. 成功したら本番統合
```

### 1. ワークフローのインポート

1. 対象ワークフローの`.json`ファイルをダウンロード
2. n8nの管理画面で「Import from File」を選択
3. ダウンロードしたJSONファイルをアップロード
4. 必要な認証情報(API Key等)を設定

### 2. ドキュメントの参照

各ワークフローディレクトリ内の`README.md`に以下の情報が記載されています:

- 設計思想
- セットアップ手順
- 設定項目
- 使用例
- トラブルシューティング

### 3. カスタマイズ

テンプレートをベースに、自分のユースケースに合わせてカスタマイズできます。

## 🔌 MCP統合

Claude Code / Cursorから直接このリポジトリにアクセスできます。

### Claude Desktop設定

`~/Library/Application Support/Claude/claude_desktop_config.json`に追加:

```json
{
  "mcpServers": {
    "n8n-workflows": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://gitmcp.io/plus61/n8n-workflows"]
    }
  }
}
```

### Cursor設定

`.cursor/mcp.json`に追加:

```json
{
  "mcpServers": {
    "n8n-workflows": {
      "command": "/Users/[ユーザー名]/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "mcp-remote", "https://gitmcp.io/plus61/n8n-workflows"]
    }
  }
}
```

### 使用例

Claude / Cursorで以下のように質問できます:

- 「LINE CRMワークフローの設計パターンを教えて」
- 「Notionへのデータ登録でエラーが出た時の対処法は?」
- 「リッチメニュー統合のベストプラクティスは?」

## 📝 コントリビューション

新しいワークフローやドキュメントの追加は大歓迎です!

### 追加手順

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/new-workflow`)
3. 変更をコミット (`git commit -am 'Add new workflow'`)
4. ブランチにプッシュ (`git push origin feature/new-workflow`)
5. プルリクエストを作成

## 📄 ライセンス

MIT License

## 🔗 関連リンク

- [n8n公式ドキュメント](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [LINE Messaging API](https://developers.line.biz/ja/docs/messaging-api/)
- [Notion API](https://developers.notion.com/)

---

最終更新: 2025-10-26
