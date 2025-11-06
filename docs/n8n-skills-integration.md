# n8n-skills Integration Guide

**Status**: ✅ Active and Integrated
**Last Updated**: 2025-11-05
**Skills Version**: Latest from [czlonkowski/n8n-skills](https://github.com/czlonkowski/n8n-skills)

## 概要

このプロジェクトは、Claude Code で n8n ワークフロー開発を効率化するために **n8n-skills** を統合しています。これにより、以下が自動的に活性化されます：

- ✅ 正しい n8n 式構文 ({{}} パターン)
- ✅ n8n-mcp MCP ツールの効果的な使用方法
- ✅ 実績のあるワークフローパターン
- ✅ バリデーションエラーの解釈と修正
- ✅ ノード設定の運用ガイダンス
- ✅ JavaScript/Python Code ノードのベストプラクティス

## 統合されている7つのスキル

### 1. **n8n Expression Syntax**
正しい n8n 式構文とよくあるパターンを教えます。

**自動活性化**: 式の記述、{{}} 構文、$json/$node 変数アクセス、式エラーのトラブルシューティング

**主な機能**:
- コア変数 ($json, $node, $now, $env)
- **重要な注意点**: Webhook データは `$json.body` の下
- よくある間違いカタログと修正方法
- 式を使うべきでない場合 (Code ノード!)

### 2. **n8n MCP Tools Expert** (最優先)
n8n-mcp MCP ツールを効果的に使用するためのエキスパートガイド。

**自動活性化**: ノード検索、設定検証、テンプレートアクセス、ワークフロー管理

**主な機能**:
- ツール選択ガイド (どのツールをどのタスクに使うか)
- nodeType フォーマットの違い (nodes-base.* vs n8n-nodes-base.*)
- バリデーションプロファイル (minimal/runtime/ai-friendly/strict)
- スマートパラメータ (IF ノードの branch="true")
- 自動サニタイゼーションシステムの説明

### 3. **n8n Workflow Patterns**
5つの実績あるアーキテクチャパターンを使用してワークフローを構築。

**自動活性化**: ワークフロー作成、ノード接続、自動化設計

**主な機能**:
- 5つの実績パターン (webhook 処理、HTTP API、データベース、AI、スケジュール)
- ワークフロー作成チェックリスト
- 2,653+ の n8n テンプレートからの実例
- 接続のベストプラクティス

### 4. **n8n Validation Expert**
バリデーションエラーを解釈し、修正をガイド。

**自動活性化**: バリデーション失敗、ワークフローエラーのデバッグ、誤検知の処理

**主な機能**:
- バリデーションループワークフロー
- 実際のエラーカタログ
- 自動サニタイゼーション動作の説明
- 誤検知ガイド

### 5. **n8n Node Configuration**
操作を考慮したノード設定ガイダンス。

**自動活性化**: ノード設定、プロパティ依存関係の理解、AI ワークフローのセットアップ

**主な機能**:
- プロパティ依存ルール (例: sendBody → contentType)
- 操作固有の要件
- AI 接続タイプ (AI Agent ワークフロー用の8タイプ)
- 一般的な設定パターン

### 6. **n8n Code JavaScript**
n8n Code ノードで効果的な JavaScript コードを記述。

**自動活性化**: Code ノードでの JavaScript 記述、エラーのトラブルシューティング、$helpers での HTTP リクエスト、日付処理

**主な機能**:
- データアクセスパターン ($input.all(), $input.first(), $input.item)
- **重要な注意点**: Webhook データは `$json.body` の下
- 正しい戻り値フォーマット: `[{json: {...}}]`
- 組み込み関数 ($helpers.httpRequest(), DateTime, $jmespath())
- トップ5エラーパターンと解決策 (失敗の62%以上をカバー)

### 7. **n8n Code Python**
n8n Code ノードで Python コードを記述し、制限を理解。

**自動活性化**: Code ノードでの Python 記述、Python の制限理解、標準ライブラリの操作

**主な機能**:
- **重要**: 95%のケースで JavaScript を使用
- Python データアクセス (_input, _json, _node)
- **重要な制限**: 外部ライブラリなし (requests, pandas, numpy)
- 標準ライブラリリファレンス (json, datetime, re など)
- 欠けているライブラリの回避策

## スキルの統合方法

スキルは `~/.claude/skills/` にシンボリックリンクとして配置されています：

```bash
~/.claude/skills/
├── n8n-code-javascript/      -> /Users/.../n8n-workflows/n8n-skills/skills/n8n-code-javascript/
├── n8n-code-python/           -> /Users/.../n8n-workflows/n8n-skills/skills/n8n-code-python/
├── n8n-expression-syntax/     -> /Users/.../n8n-workflows/n8n-skills/skills/n8n-expression-syntax/
├── n8n-mcp-tools-expert/      -> /Users/.../n8n-workflows/n8n-skills/skills/n8n-mcp-tools-expert/
├── n8n-node-configuration/    -> /Users/.../n8n-workflows/n8n-skills/skills/n8n-node-configuration/
├── n8n-validation-expert/     -> /Users/.../n8n-workflows/n8n-skills/skills/n8n-validation-expert/
└── n8n-workflow-patterns/     -> /Users/.../n8n-workflows/n8n-skills/skills/n8n-workflow-patterns/
```

## 使用方法

スキルは関連するクエリが検出されると **自動的に活性化** されます：

```
"n8n の式の書き方は？"
→ 活性化: n8n Expression Syntax

"Slack ノードを見つけて"
→ 活性化: n8n MCP Tools Expert

"webhook ワークフローを構築"
→ 活性化: n8n Workflow Patterns

"バリデーションが失敗する理由は？"
→ 活性化: n8n Validation Expert

"HTTP Request ノードの設定方法は？"
→ 活性化: n8n Node Configuration

"Code ノードで webhook データにアクセスする方法は？"
→ 活性化: n8n Code JavaScript

"Python Code ノードで pandas を使える？"
→ 活性化: n8n Code Python
```

### スキルの連携

複数のスキルが **シームレスに連携** します。

**例**: "webhook から Slack へのワークフローを構築して検証"

1. **n8n Workflow Patterns** が webhook 処理パターンを特定
2. **n8n MCP Tools Expert** が webhook と Slack ノードを検索
3. **n8n Node Configuration** がノード設定をガイド
4. **n8n Code JavaScript** が正しい .body アクセスで webhook データ処理を支援
5. **n8n Expression Syntax** が他のノードでのデータマッピングを支援
6. **n8n Validation Expert** が最終ワークフローを検証

## スキルの更新

スキルを最新版に更新するには：

```bash
cd /Users/yuichiroooosuger/Desktop/n8n-workflows/n8n-skills
git pull origin main
```

シンボリックリンクを使用しているため、更新は自動的に反映されます。

## プロジェクト固有の統合

### wf7 (Video Script Generator) との統合

wf7 ワークフローでは、以下のスキルが特に有用です：

- **n8n Webhook Data Access**: Phase1 での Webhook データ処理
- **n8n Code JavaScript**: Phase2 での Google Drive 画像収集スクリプト
- **n8n Workflow Patterns**: 全体的なワークフロー構造
- **n8n Validation Expert**: Railway デプロイ前のバリデーション

### 関連ドキュメント

- [n8n Workflow Construction Knowledge](./knowledge/n8n-workflow-construction-knowledge.md)
- [wf7 Phase4 Troubleshooting Guide](./knowledge/wf7-phase4-troubleshooting-guide.md)
- [Google Drive OAuth2 Setup Guide](./setup/google-drive-oauth2-setup-guide.md)

## トラブルシューティング

### スキルが活性化しない場合

1. シンボリックリンクが正しいか確認:
   ```bash
   ls -la ~/.claude/skills/
   ```

2. SKILL.md ファイルが存在するか確認:
   ```bash
   cat ~/.claude/skills/n8n-mcp-tools-expert/SKILL.md | head -10
   ```

3. Claude Code を再起動

### スキルの競合

複数のスキルが同時に活性化される場合、それらは **連携して動作** するように設計されています。各スキルは特定のドメインに特化しています。

## リソース

- **n8n-skills リポジトリ**: https://github.com/czlonkowski/n8n-skills
- **n8n-mcp MCP サーバー**: https://github.com/czlonkowski/n8n-mcp
- **n8n 公式ドキュメント**: https://docs.n8n.io/

## クレジット

**Conceived by Romuald Członkowski**
- Website: [www.aiadvisors.pl/en](https://www.aiadvisors.pl/en)
- Part of the [n8n-mcp project](https://github.com/czlonkowski/n8n-mcp)

---

**Last verified**: 2025-11-05 11:01 JST
