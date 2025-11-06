# WF5実装 重要インシデント ナレッジベース

**作成日**: 2025-10-27
**ワークフロー**: WF5 - トピック抽出AI
**最終ステータス**: ✅ Workflow executed successfully

---

## 📋 目次

1. [インシデント#1: JSON parameter needs to be valid JSON エラー](#インシデント1-json-parameter-needs-to-be-valid-json-エラー)
2. [インシデント#2: GPT-4レスポンスのJSON parse失敗](#インシデント2-gpt-4レスポンスのjson-parse失敗)
3. [インシデント#3: 認証設定の不一致](#インシデント3-認証設定の不一致)
4. [n8nベストプラクティス総括](#n8nベストプラクティス総括)

---

## インシデント#1: JSON parameter needs to be valid JSON エラー

### 🚨 重要度: **CRITICAL**

### 問題の概要

HTTP Requestノードの`jsonBody`パラメータで、JSONオブジェクトリテラル内にn8n式（`{{ }}`）を直接埋め込むとエラーが発生する。

### エラーメッセージ

```
Problem in node 'GPT-4 API - トピック抽出'
JSON parameter needs to be valid JSON
```

```
Problem in node 'Slack - トピック通知'
JSON parameter needs to be valid JSON
```

### 発生した原因

**❌ 誤ったアプローチ（失敗）**:

HTTP RequestノードのjsonBodyで、JSONオブジェクトリテラル構造内にJavaScript式を直接埋め込もうとした。

```json
{
  "jsonBody": "={
    \"model\": \"gpt-4-turbo-preview\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": \"以下のデータ...\" + JSON.stringify($json.articles) + \"...\"
      }
    ]
  }"
}
```

**なぜ失敗するか**:
- n8nは`jsonBody`フィールドを「有効なJSON文字列」として検証する
- JSONオブジェクトリテラル内にJavaScript式（`JSON.stringify()`、テンプレートリテラル、`$json`参照など）を含めると、**JSON構文として無効**と判定される
- `=`プレフィックスでExpression modeを有効にしても、n8nはまずJSON構文検証を行うため、混在構造は受け付けられない

### 試した失敗パターン

#### パターン1: 文字列連結（失敗）
```javascript
"content": "..." + JSON.stringify($json.articles) + "..."
```
→ JSON構文エラー

#### パターン2: テンプレートリテラル（失敗）
```javascript
"content": `...${JSON.stringify($json.articles)}...`
```
→ JSON構文エラー（同じ問題）

### ✅ 正しい解決策

**n8nの推奨パターン: Function node + Pass-through pattern**

#### Step 1: Functionノードで完全なペイロードを構築

```javascript
// Function - GPT-4リクエスト構築
const articles = $input.first().json.articles;

const prompt = `以下の人気note記事データから、トレンドトピックを抽出してください。

【データ】
${JSON.stringify(articles, null, 2)}

【分析観点】
...
`;

return [{
  json: {
    model: "gpt-4-turbo-preview",
    messages: [
      {
        role: "system",
        content: "あなたはコンテンツストラテジストです。"
      },
      {
        role: "user",
        content: prompt
      }
    ],
    temperature: 0.7,
    max_tokens: 1500
  }
}];
```

#### Step 2: HTTP Requestノードでシンプルにパススルー

```json
{
  "parameters": {
    "url": "https://api.openai.com/v1/chat/completions",
    "method": "POST",
    "authentication": "none",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {"name": "Authorization", "value": "Bearer YOUR_API_KEY"},
        {"name": "Content-Type", "value": "application/json"}
      ]
    },
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ $json }}"
  }
}
```

### なぜこのパターンが正しいか

1. **関心の分離**: データ構築（Function）とHTTP送信（HTTP Request）を分離
2. **JSON検証回避**: HTTP Requestノードは単純な`={{ $json }}`式のみを受け取るため、JSON構文検証をパス
3. **n8n公式推奨**: n8nドキュメントとコミュニティで推奨される標準パターン
4. **保守性向上**: 複雑なロジックはFunctionノードに集約され、デバッグが容易

### 適用範囲

このパターンは以下の場合に必須:
- ✅ 動的なJSON構築（変数、配列、オブジェクトの組み立て）
- ✅ 複雑なデータ変換を含むAPIリクエスト
- ✅ 条件分岐を含むペイロード生成
- ✅ テンプレートリテラルや文字列連結が必要な場合

### 実装結果

**WF5での適用箇所**:
1. **Node 4b (Function - GPT-4リクエスト構築)** → Node 5 (GPT-4 API)
2. **Node 11b (Function - Slack通知ペイロード構築)** → Node 11 (Slack通知)

---

## インシデント#2: GPT-4レスポンスのJSON parse失敗

### 🚨 重要度: **HIGH**

### 問題の概要

GPT-4 APIがJSON形式で返すように指示しても、マークダウンコードブロック（```json ... ```）で囲んで返すため、`JSON.parse()`が失敗する。

### エラーメッセージ

```
Problem in node 'Function - GPT-4レスポンスパース'
GPT-4レスポンスのJSON parse失敗: ```json
{
  "trendKeywords": [],
  "userNeeds": "",
  "nextTopics": []
}
```
```

### 発生した原因

**GPT-4の挙動**:
- プロンプトで「必ずJSON形式のみで出力してください。それ以外のテキストは含めないでください。」と明示的に指示
- しかし、GPT-4はマークダウン形式でコードブロックとして整形して返す習慣がある
- これは親切な挙動だが、プログラムでパースする場合は邪魔になる

**元のコード**:
```javascript
const gptResponse = $input.first().json;
const content = gptResponse.choices[0].message.content;

let analysis;
try {
  analysis = JSON.parse(content); // ❌ マークダウンコードブロックがあるとエラー
} catch (e) {
  throw new Error(`GPT-4レスポンスのJSON parse失敗: ${content}`);
}

return [{ json: analysis }];
```

### ✅ 正しい解決策

**マークダウンコードブロックを除去してからパース**:

```javascript
const gptResponse = $input.first().json;
let content = gptResponse.choices[0].message.content;

// マークダウンコードブロックを除去
content = content.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim();

let analysis;
try {
  analysis = JSON.parse(content); // ✅ クリーンなJSONをパース
} catch (e) {
  throw new Error(`GPT-4レスポンスのJSON parse失敗: ${content}`);
}

return [{ json: analysis }];
```

### 技術的詳細

**正規表現の説明**:
- `/```json\s*/g`: "```json" とその後の空白文字を除去（開始コードブロック）
- `/```\s*/g`: "```" とその後の空白文字を除去（終了コードブロック）
- `g`フラグ: グローバルマッチ（複数箇所を置換）
- `.trim()`: 前後の空白を削除

### 代替アプローチ

**Option 1: プロンプト改善（試したが効果なし）**:
```
必ずJSON形式のみで出力してください。
マークダウンコードブロック（```）は使用しないでください。
それ以外のテキストは含めないでください。
```
→ GPT-4の挙動を完全には制御できない

**Option 2: より堅牢なパース処理（推奨）**:
```javascript
// マークダウン、その他のノイズを除去
content = content
  .replace(/```json\s*/g, '')
  .replace(/```\s*/g, '')
  .replace(/^[^{]*/g, '')  // 最初の { までを除去
  .replace(/[^}]*$/g, '')  // 最後の } 以降を除去
  .trim();
```

### ベストプラクティス

GPT-4などのLLM APIからJSONを受け取る場合:
1. ✅ **常にクリーニング処理を実装する**（マークダウンコードブロック除去）
2. ✅ **エラーハンドリングで生のレスポンスを出力**（デバッグ容易性）
3. ✅ **プロンプトでJSON形式を明示**（成功率向上）
4. ⚠️ **LLMの出力を100%制御できると期待しない**

### 適用結果

**WF5での実装**:
- Node 6 (Function - GPT-4レスポンスパース) に実装
- GPT-4のレスポンスを確実にパースできるようになった

---

## インシデント#3: 認証設定の不一致

### 🚨 重要度: **MEDIUM**

### 問題の概要

新規作成したWF5のHTTP Requestノードで、認証設定を`genericCredentialType`にしたことで、Notion APIの認証ヘッダーが正しく送信されなかった。

### エラーメッセージ

```
notion queryのheder authも設定されておらずエラーです
header name must be a non-empty string
```

### 発生した原因

**誤った設定**:
```json
{
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth"
}
```

この設定では、n8nは**認証情報を別途Credentials設定から取得しようとする**ため、直接指定した`headerParameters`の値が無視される。

### ✅ 正しい解決策

**動作しているWF4の設定を参照**:
```json
{
  "authentication": "none",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {"name": "Authorization", "value": "Bearer ntn_..."},
      {"name": "Notion-Version", "value": "2022-06-28"},
      {"name": "Content-Type", "value": "application/json"}
    ]
  }
}
```

### 認証方式の理解

| 設定 | 挙動 | 使用ケース |
|------|------|------------|
| `authentication: "none"` | ヘッダーを直接`headerParameters`から読み取る | APIキーを直接指定する場合 |
| `authentication: "genericCredentialType"` | n8n Credentialsストアから認証情報を取得 | 認証情報を再利用する場合 |
| `authentication: "predefinedCredentialType"` | 特定サービス用の認証（OAuth等） | Slack, Google等の公式統合 |

### ベストプラクティス

**開発・テスト段階**:
- ✅ `authentication: "none"` + 直接ヘッダー指定
- 理由: デバッグが容易、設定が明確

**本番運用段階**:
- ✅ `authentication: "genericCredentialType"` + Credentials管理
- 理由: セキュリティ向上（APIキーをワークフローJSONに含めない）

### 実装結果

**WF5での修正箇所**:
1. Node 2 (Notion Query)
2. Node 5 (GPT-4 API)
3. Node 9 (Notion Create)
4. Node 11 (Slack通知)

すべて`authentication: "none"`に統一し、動作確認完了。

---

## n8nベストプラクティス総括

### 🎯 重要な学び

#### 1. **複雑なJSONペイロード = Function node + Pass-through pattern**

```
Function Node (ペイロード構築)
  ↓ {{ $json }}
HTTP Request Node (シンプルなパススルー)
```

**メリット**:
- JSON構文検証エラーを回避
- デバッグが容易（Functionノードで出力確認可能）
- 保守性向上（ロジックが分離されている）

#### 2. **LLM APIのレスポンス処理**

```javascript
// 常にクリーニング処理を実装
content = content
  .replace(/```json\s*/g, '')
  .replace(/```\s*/g, '')
  .trim();

// エラーハンドリングで生のレスポンスを出力
try {
  analysis = JSON.parse(content);
} catch (e) {
  throw new Error(`JSON parse失敗: ${content}`);
}
```

#### 3. **認証設定の使い分け**

| 環境 | 推奨設定 | 理由 |
|------|----------|------|
| 開発・テスト | `authentication: "none"` | デバッグ容易性 |
| 本番運用 | Credentials管理 | セキュリティ |

#### 4. **動作確認済みワークフローを参照する**

- 新規ワークフロー作成時は、類似する既存ワークフロー（WF4等）の設定を参照
- 特に認証、エラーハンドリング、リトライ設定などの共通パターンを再利用

#### 5. **段階的なデバッグアプローチ**

1. ノード単位で実行して出力を確認
2. エラーメッセージから生のデータを確認
3. 参照ワークフローとの差分を比較
4. 公式ドキュメントとコミュニティを活用

---

## 📚 参考リソース

### n8n公式ドキュメント
- [HTTP Request Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [Function Node](https://docs.n8n.io/code-examples/expressions/function-nodes/)
- [Expressions](https://docs.n8n.io/code-examples/expressions/)

### 関連ドキュメント
- [Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md](../Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md)
- [phase2-wf5-test-execution-guide.md](./phase2-wf5-test-execution-guide.md)

---

## ✅ 最終結果

**ワークフローID**: `jhhxhXABBwXxQ1GJ`
**ステータス**: ✅ **Workflow executed successfully**

### 修正サマリー

| インシデント | 対応ノード | 解決策 |
|-------------|-----------|--------|
| JSON parameter error | GPT-4 API, Slack通知 | Function node + Pass-through pattern |
| JSON parse失敗 | GPT-4レスポンスパース | マークダウンコードブロック除去処理 |
| 認証設定不一致 | 全HTTP Request | `authentication: "none"` に統一 |

### ノード構成（最終版）

12ノード構成:
1. Schedule Trigger
2. Notion Query - 過去30日の記事取得
3. Function - スコアリング
4. Function - トップ10記事抽出
5. **Function - GPT-4リクエスト構築** ← 追加
6. GPT-4 API - トピック抽出
7. Function - GPT-4レスポンスパース ← 修正
8. Function - トピックデータ前処理
9. Loop - トピック登録
10. Notion - トピックマスタ更新
11. Wait - レート制限対策
12. **Function - Slack通知ペイロード構築** ← 追加
13. Slack - トピック通知

---

**作成者**: Claude Code
**最終更新**: 2025-10-27
**検証済み**: ✅ Workflow executed successfully
