// WF-B: Function - Validate Schema 修正版
// 作成日時: 2025-11-24 01:59:04 JST
// 目的: AI AgentのJSON文字列出力をパース・バリデーション
// 修正内容:
//   1. AI Agentの{output: "JSON string"}形式に対応
//   2. テンプレートリテラルの構文エラー修正（文字列連結使用）
//   3. Markdownコードブロッククリーンアップ追加

// AI AgentのJSON文字列出力をパース
const aiOutput = $input.item.json.output;

// JSON文字列をパース
let parsedData;
try {
  const cleanedOutput = aiOutput.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
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

return {
  json: {
    ...parsedData,
    validation_passed: true,
    validated_at: new Date().toISOString()
  }
};
