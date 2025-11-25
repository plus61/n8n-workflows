# WF-B クリティカル修正ナレッジ

**作成日時**: 2025-11-24 18:13:30 JST
**対象ワークフロー**: WF-B: Analyze & Suggest Next Actions
**検証環境**: Railway n8n (https://n8n-python-production-344b.up.railway.app)

## 概要

AI Agent + Code ノードを使用したJSON出力パイプラインにおける3つのクリティカルな問題と解決策。これらは**Phase 4型インシデント**（データフロー・構文エラーによる実行時失敗）の典型例。

---

## 🚨 Critical Fix 1: Code ノードでのテンプレートリテラル構文エラー

### 問題

**症状**:
```
SyntaxError: Invalid or unexpected token
evalmachine.<anonymous>:30
  throw new Error(`Missing required fields: ${missingFields.join(',
                                                                 ^^^
```

**根本原因**:
- Code ノード（JavaScript）内でバッククォート文字列が複数行にまたがると構文エラー
- n8nのCode実行環境がテンプレートリテラルの改行を正しく処理できない

### 解決策

❌ **NG例** - テンプレートリテラル使用:
```javascript
throw new Error(`Missing required fields: ${missingFields.join(',
')}`);
```

✅ **OK例** - 文字列連結使用:
```javascript
throw new Error('Missing required fields: ' + missingFields.join(', '));
```

### ベストプラクティス

```javascript
// Code ノード内のエラーメッセージは文字列連結で構築
const validationErrors = [];

if (missingFields.length > 0) {
  throw new Error('Missing required fields: ' + missingFields.join(', '));
}

if (!['improve', 'pause', 'scale'].includes(data.next_decision)) {
  validationErrors.push('Invalid next_decision: ' + data.next_decision);
}

if (validationErrors.length > 0) {
  throw new Error('Schema validation failed: ' + validationErrors.join(', '));
}
```

**キーポイント**:
- 動的な値を含むエラーメッセージは `+` 演算子で連結
- `Array.join()` で配列を文字列化
- バッククォートは使用しない

---

## 🚨 Critical Fix 2: AI Agent JSON出力のパース処理

### 問題

**AI Agent出力形式**:
```json
{
  "output": "{\"next_decision\":\"improve\",\"next_action\":\"...\",\"insights\":[...]}"
}
```

- AI Agentは `{output: "JSON文字列"}` 形式で返す
- 直接 `$json` では構造化データとしてアクセス不可

### 解決策

**Function - Validate Schema の実装**:

```javascript
// AI AgentのJSON文字列出力をパース
const aiOutput = $input.item.json.output;

// Markdownコードブロック除去
let parsedData;
try {
  const cleanedOutput = aiOutput
    .replace(/```json\n?/g, '')
    .replace(/```\n?/g, '')
    .trim();
  parsedData = JSON.parse(cleanedOutput);
} catch (error) {
  throw new Error('JSON parse failed: ' + error.message);
}

// スキーマバリデーション
const requiredFields = ['next_decision', 'next_action', 'next_segment', 'next_keyword_idea', 'insights', 'reasoning'];
const missingFields = requiredFields.filter(field => !(field in parsedData));

if (missingFields.length > 0) {
  throw new Error('Missing required fields: ' + missingFields.join(', '));
}

// バリデーション詳細チェック
const validationErrors = [];

if (!['improve', 'pause', 'scale'].includes(parsedData.next_decision)) {
  validationErrors.push('Invalid next_decision: ' + parsedData.next_decision);
}

if (!['Cold', 'Middle', 'Hot', 'Current'].includes(parsedData.next_segment)) {
  validationErrors.push('Invalid next_segment: ' + parsedData.next_segment);
}

if (parsedData.next_action && parsedData.next_action.length > 200) {
  validationErrors.push('next_action exceeds max length (200 chars)');
}

if (parsedData.next_keyword_idea && parsedData.next_keyword_idea.length > 100) {
  validationErrors.push('next_keyword_idea exceeds max length (100 chars)');
}

if (!Array.isArray(parsedData.insights) || parsedData.insights.length < 2 || parsedData.insights.length > 4) {
  validationErrors.push('insights must have 2-4 items');
}

if (parsedData.reasoning && parsedData.reasoning.length > 500) {
  validationErrors.push('reasoning exceeds max length (500 chars)');
}

if (validationErrors.length > 0) {
  throw new Error('Schema validation failed: ' + validationErrors.join(', '));
}

// フラットな構造でGoogle Sheetsに渡す
return {
  json: {
    ...parsedData,
    validation_passed: true,
    validated_at: new Date().toISOString()
  }
};
```

### データフロー

```
AI Agent → {output: "JSON string"}
    ↓
Function - Validate Schema:
  1. $input.item.json.output 抽出
  2. Markdownコードブロック除去
  3. JSON.parse()
  4. スキーマバリデーション（enum, length, array size）
  5. フラット化して返却
    ↓
Google Sheets Update → ={{ $json.next_decision }} でアクセス可能
```

---

## 🚨 Critical Fix 3: AI Agent プロンプトの式評価エラー

### 問題

**症状**:
AI Agentが記事データを受け取れず、以下のような応答を返す:
```json
{
  "output": "Please provide the article data in JSON format so I can perform the analysis..."
}
```

**根本原因**:

❌ **NG例** - 文字列連結が式評価されない:
```javascript
="You are a data-driven marketing analyst.\n\nPUBLISHED ARTICLE DATA:\n" + JSON.stringify($json.row, null, 2) + "\n\nANALYSIS TASK:..."
```

- `=` で始まっても `{{ }}` がないため、n8nは式として評価しない
- `JSON.stringify()` が実行されず、リテラル文字列として渡される

### 解決策

✅ **OK例1** - テンプレートリテラル（推奨）:
```javascript
={{ `You are a data-driven marketing analyst.

PUBLISHED ARTICLE DATA:
${JSON.stringify($json.row, null, 2)}

ANALYSIS TASK:
Based on the above article data, provide your analysis in STRICT JSON format.

CRITICAL REQUIREMENTS:
1. Your response must be ONLY a valid JSON object
2. NO markdown code blocks (no \`\`\`json\`\`\`)
3. NO additional text before or after the JSON
4. Use the exact field names specified below

DECISION CRITERIA:
- "improve": PV < 1000 OR conversion < 1%
- "pause": PV < 100 AND conversion < 0.5% AND segment is Cold
- "scale": PV > 3000 AND conversion > 2%

REQUIRED JSON STRUCTURE:
{
  "next_decision": "improve" | "pause" | "scale",
  "next_action": "One concrete action (max 200 chars)",
  "next_segment": "Cold" | "Middle" | "Hot" | "Current",
  "next_keyword_idea": "One keyword suggestion (max 100 chars)",
  "insights": [
    "Insight 1 (max 200 chars)",
    "Insight 2 (max 200 chars)",
    "Insight 3 (max 200 chars, optional)",
    "Insight 4 (max 200 chars, optional)"
  ],
  "reasoning": "Concise explanation of your decision (max 500 chars)"
}

Remember: Return ONLY the JSON object, nothing else.` }}
```

**構文ポイント**:
- `={{ }}` で全体をラップ → n8nが式として評価
- バッククォート `` ` `` でテンプレートリテラル開始
- `${変数}` で変数展開
- 内部のバッククォートはエスケープ: `\`\`\`json\`\`\``

✅ **OK例2** - 配列join（より安全）:
```javascript
={{ [
  "You are a data-driven marketing analyst.",
  "",
  "PUBLISHED ARTICLE DATA:",
  JSON.stringify($json.row, null, 2),
  "",
  "ANALYSIS TASK:",
  "Based on the above article data, provide your analysis in STRICT JSON format.",
  // ... 各行を配列要素として列挙
].join("\n") }}
```

### ベストプラクティス

**AI Agent プロンプトの黄金律**:

1. **式評価の明示**: `={{ }}` で必ずラップ
2. **変数展開**: テンプレートリテラルまたはarray join使用
3. **プロンプト構造**:
   ```javascript
   ={{ `[役割定義]

   INPUT DATA:
   ${JSON.stringify($json.data, null, 2)}

   TASK:
   [具体的なタスク指示]

   OUTPUT FORMAT:
   [JSON構造の明示]

   CONSTRAINTS:
   [制約条件]` }}
   ```

4. **JSON出力の強制**:
   - "Your response must be ONLY a valid JSON object"
   - "NO markdown code blocks"
   - "Use the exact field names specified below"

---

## 🔄 完全なデータフローパターン

### WF-B成功パターン

```
1. Google Sheets Get
   ↓
   row_data: {status, trending_keyword, abstract, segment, ...}

2. Function - Filter published
   ↓
   filtered_rows with row_id, sheet_url

3. Split In Batches (size=1)
   ↓
   単一行データ

4. Project Config
   ↓
   config: {project_name, default_segment}

5. Merge (combine all)
   ↓
   row_data + config

6. Function - Preprocess
   ↓
   {row_id, sheet_url, row: {...}}

7. AI Agent (gpt-4o-mini)
   prompt: ={{ `...${JSON.stringify($json.row, null, 2)}...` }}
   ↓
   {output: "JSON string"}

8. Function - Validate Schema
   const aiOutput = $input.item.json.output;
   const cleanedOutput = aiOutput.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
   const parsedData = JSON.parse(cleanedOutput);
   // validate...
   return {json: {...parsedData, validation_passed: true}};
   ↓
   {next_decision, next_action, next_segment, next_keyword_idea, insights[], reasoning, validation_passed, validated_at}

9. Google Sheets Update (Append Row)
   next_decision: ={{ $json.next_decision }}
   next_action: ={{ $json.next_action }}
   next_segment: ={{ $json.next_segment }}
   next_keyword_idea: ={{ $json.next_keyword_idea }}
   insights_json: ={{ JSON.stringify($json.insights) }}
   reasoning: ={{ $json.reasoning }}
   analyzed_at: ={{ $json.validated_at }}
   ↓
   Google Sheets書き込み成功

10. Loop Back → Split In Batches (次の行へ)
```

---

## 📋 Phase 0チェックリスト更新

### AI Agent + JSON出力パイプラインの追加検証項目

**設計段階**:
- [ ] AI Agentの出力形式を確認（`{output: "JSON string"}` 形式）
- [ ] Output Parser使用 vs 手動パース処理の選択
- [ ] JSONスキーマの明示的な定義
- [ ] 文字数制限・enum値の設計

**実装段階**:
- [ ] AI Agent プロンプト: `={{ }}` で式評価を明示
- [ ] 変数展開: テンプレートリテラルまたはarray join使用
- [ ] Function - Validate Schema: `$input.item.json.output` 抽出処理
- [ ] Markdownコードブロッククリーンアップ（```json```除去）
- [ ] エラーメッセージ: 文字列連結（`+`）使用、テンプレートリテラル禁止

**テスト段階**:
- [ ] AI Agentが実際のデータを受け取っているか確認
- [ ] JSON parseエラーの有無
- [ ] スキーマバリデーション通過確認
- [ ] 下流ノード（Google Sheets等）でフィールドアクセス可能か

---

## 🎯 再発防止のための原則

### 1. Code ノード JavaScript 記述原則

```javascript
// ✅ DO: 文字列連結でエラーメッセージ構築
throw new Error('Error: ' + variable);

// ❌ DON'T: テンプレートリテラルの複数行
throw new Error(`Error: ${variable}
more text`);
```

### 2. AI Agent プロンプト記述原則

```javascript
// ✅ DO: {{ }} + テンプレートリテラル
={{ `prompt text ${variable} more text` }}

// ✅ DO: {{ }} + array join
={{ ["line1", variable, "line2"].join("\n") }}

// ❌ DON'T: 文字列連結が式評価されない
="text" + variable + "more text"
```

### 3. AI Agent 出力処理原則

```javascript
// ✅ DO: .output抽出 → clean → parse → validate
const aiOutput = $input.item.json.output;
const cleanedOutput = aiOutput.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
const parsedData = JSON.parse(cleanedOutput);
// validate schema...
return {json: {...parsedData}};

// ❌ DON'T: 直接 $json にアクセス
const data = $json.next_decision; // undefined
```

---

## 📚 参考リソース

**成果物**:
- `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-24_01-59_function-validate-schema-fixed.js` - 完全なバリデーション実装
- `/Users/yuichiroooosuger/Desktop/n8n-workflows/now/2025-11-23_22-22_WF-B-backup.json` - 修正前のワークフロー

**検証実行**:
- Execution 3952: Function - Validate Schema構文エラー
- Execution 3955: Google Sheets Update設定エラー
- Execution 3959: AI Agent式評価エラー
- Execution 3962: 全ノード成功（✅ 本番稼働可能）

**AI分析結果例** (Execution 3962):
```json
{
  "next_decision": "pause",
  "next_action": "Reassess content quality and targeting for Cold segment; consider updating article with more engaging visuals and examples.",
  "next_segment": "Cold",
  "next_keyword_idea": "AI導入 効果",
  "insights": [
    "Current article has zero PV and conversions, indicating low engagement.",
    "Segment is Cold, which typically requires awareness-raising strategies.",
    "Trending keyword is relevant but the content lacks traction.",
    "Improvement needed before scaling."
  ],
  "reasoning": "PV is 0 and conversion is 0%, both below thresholds for improvement or scaling; segment is Cold, meeting criteria for pause to reassess strategy before further promotion."
}
```

---

## ✅ 検証完了

- ✅ Code ノード構文エラー解決
- ✅ AI Agent JSON出力パース処理実装
- ✅ AI Agent プロンプト式評価修正
- ✅ Google Sheets フィールドマッピング修正
- ✅ 完全パイプライン実行成功（Execution 3962）

**WF-Bは本番環境で稼働可能です**。
