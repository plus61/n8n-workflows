# WF-B（Analyze & Suggest Next Actions）再設計書

**最終更新**: 2025-11-23 22:05 JST（テンプレート調査統合版）
**作成**: Codex
**Phase 0検証**: ✅ 合格（標準JSONフロー、実装可能）
**テンプレート調査**: ✅ 完了（15件のn8n実装パターン分析済み）

---

## 0. 目的と適用範囲

### 基本目的
- `status=published` のnote記事行を評価し、次の打ち手をJSONで返す
- Slackへ通知して承認経路を通す
- 承認時に新規 `status=idea` 行を追加し、WF-Aに再投入する

### WF-Aとの連携仕様（詳細は§1-2参照）
- **WF-A入力**: `status=idea` の行を検出
- **WF-B出力 → WF-A入力マッピング**:
  - `next_keyword_idea` → `trending_keyword`
  - `next_segment` → `segment`

### 本書の目的
n8n AI Agentノードを安定動作させるための再設計書

### 安定動作の定義（KPI）
以下の5つのKPIで「安定動作」を定量評価（詳細は§2-2参照）:
1. **JSON出力成功率**: >= 95%
2. **平均応答時間**: <= 10秒
3. **Fallback発動率**: <= 10%
4. **エラー率**: <= 5%
5. **データ整合性スコア**: >= 98%

---

## 1. 前提・前提データ

### 1-1. Google Sheets設定

#### スプレッドシート情報
```yaml
スプレッドシートID: "1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII"
シート名: "editorial"
gid: 0
URL: https://docs.google.com/spreadsheets/d/1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII/edit#gid=0
```

#### Editorial Sheets完全スキーマ（20列）

**WF-A管理フィールド（1-8列）**:
```yaml
1. status: "idea|draft-generated|published"
2. trending_keyword: "string"
3. abstract: "string"
4. segment: "Cold|Middle|Hot|Current"
5. generated_title: "string"
6. generated_body: "string (markdown)"
7. generated_segment: "string"
8. validation_error: "string|null"
```

**note公開後メタデータ（9-13列）**:
```yaml
9. note_url: "string (URL)"
10. note_title: "string"
11. note_pv: "number (integer >= 0)"
12. note_likes: "number (integer >= 0)"
13. note_conversion: "number (float 0.0-1.0)"
```

**WF-B管理フィールド（14-17列）**:
```yaml
14. next_decision: "improve|pause|scale"
15. next_action: "string (max 200 chars)"
16. next_segment: "Cold|Middle|Hot|Current"
17. next_keyword_idea: "string (max 100 chars)"
```

**推奨追加フィールド（18-20列）**:
```yaml
18. analyzed_at: "timestamp"      # WF-B実行日時
19. approved_at: "timestamp"      # 承認日時
20. approved_by: "string"         # 承認者（Slack User ID）
```

### 1-2. WF-Aインターフェース仕様

#### WF-A基本情報
- **ワークフローID**: `7isXtFeTvjKuW5GD`
- **ワークフロー名**: "WF-A: Generate Note Drafts from Editorial Ideas"

#### WF-A入力条件
```yaml
トリガー: status=idea の行を検出
必須フィールド:
  - trending_keyword: "string" (必須)
  - segment: "Cold|Middle|Hot|Current" (デフォルト: Cold)
  - abstract: "string" (オプション)
```

#### WF-A出力フィールド
```yaml
更新対象:
  - generated_title: "string"
  - generated_body: "string (markdown)"
  - generated_segment: "string"
  - status: "draft-generated"  # 状態遷移
  - validation_error: "string|null"
```

#### WF-B → WF-A 再投入ロジック

**承認Webhook処理**:
```javascript
// Webhook: POST /webhook/wf-b-approval
// Payload: { action: "approve|reject", row_id: "string" }

if (action === "approve") {
  // Google Sheets: Add new row
  const newRow = {
    status: "idea",
    trending_keyword: $json.next_keyword_idea,  // マッピング
    abstract: "",
    segment: $json.next_segment,                // マッピング
    generated_title: "",
    generated_body: "",
    note_url: "",
    note_title: "",
    note_pv: 0,
    note_likes: 0,
    note_conversion: 0.0,
    next_decision: "",
    next_action: "",
    next_segment: "",
    next_keyword_idea: ""
  };

  await googleSheets.appendRow(newRow);
}
```

### 1-3. Config設定

#### Project Config Bノード
```yaml
設定項目:
  - mdc_content: "string" (プロジェクトルール全文、約5KB)
  - openai_api_key: n8n Credentials参照（環境変数使用禁止）
```

#### OpenAIモデル設定
```yaml
Primary: "gpt-4o-mini" (コスト優先)
Fallback: "gpt-4o" (長文・複雑分析時)
Fallback条件: needsFallback=ON + AI Agentの右ポートに接続
```

---

## 2. 入出力定義

### 2-1. 入力仕様

#### 入力データソース
```yaml
データソース: Google Sheets "editorial"
フィルタ条件: status === "published"
処理方式: Split In Batches (batchSize=1)
```

#### 入力データバリデーション
```yaml
trending_keyword:
  - 必須: true
  - 型: string
  - 制約: 非NULL、max_length=100

abstract:
  - 必須: false
  - 型: string
  - デフォルト: ""

segment:
  - 必須: false
  - 型: enum[Cold, Middle, Hot, Current]
  - デフォルト: "Cold"

note_pv:
  - 必須: false
  - 型: integer
  - 制約: >= 0
  - デフォルト: 0

note_likes:
  - 必須: false
  - 型: integer
  - 制約: >= 0
  - デフォルト: 0

note_conversion:
  - 必須: false
  - 型: float
  - 制約: 0.0 <= x <= 1.0
  - デフォルト: 0.0
```

### 2-2. 出力仕様

#### Output Parserスキーマ（厳密版）

**JSON Schema（draft-07準拠）**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "next_decision": {
      "type": "string",
      "enum": ["improve", "pause", "scale"],
      "description": "次の打ち手の方向性"
    },
    "next_action": {
      "type": "string",
      "maxLength": 200,
      "minLength": 1,
      "description": "具体的なアクション（200文字以内）"
    },
    "next_segment": {
      "type": "string",
      "enum": ["Cold", "Middle", "Hot", "Current"],
      "description": "推奨セグメント"
    },
    "next_keyword_idea": {
      "type": "string",
      "maxLength": 100,
      "minLength": 1,
      "description": "次のキーワード案（100文字以内）"
    },
    "insights": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 200
      },
      "minItems": 2,
      "maxItems": 4,
      "description": "分析インサイト（2-4個）"
    },
    "reasoning": {
      "type": "string",
      "maxLength": 500,
      "minLength": 1,
      "description": "判断理由（500文字以内）"
    }
  },
  "required": [
    "next_decision",
    "next_action",
    "next_segment",
    "next_keyword_idea",
    "insights",
    "reasoning"
  ],
  "additionalProperties": false
}
```

#### Slack通知フォーマット

```markdown
📊 **[Analysis] Published Article Review**

**記事情報**:
- キーワード: {trending_keyword}
- セグメント: {segment}
- PV: {note_pv} / いいね: {note_likes} / CV率: {note_conversion}

**分析結果**:
📍 **Decision**: {next_decision}
🎯 **Next Action**: {next_action}
📊 **Next Segment**: {next_segment}
💡 **Keyword Idea**: {next_keyword_idea}

**Insights**:
• {insights[0]}
• {insights[1]}
...

**Reasoning**: {reasoning}

**Row ID**: {row_id}
**Sheet URL**: https://docs.google.com/spreadsheets/d/1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII/edit#gid=0&range=A{row_id}

[Approve] [Reject]
```

#### 安定動作KPI（定量評価指標）

**KPI 1: JSON出力成功率**:
```yaml
指標名: json_output_success_rate
目標値: >= 95%
計測方法: Output Parserスキーマ検証合格率
アラート閾値: < 90%
```

**KPI 2: 平均応答時間**:
```yaml
指標名: avg_response_time
目標値: <= 10秒（通常）、<= 30秒（Fallback時）
計測方法: AI Agent実行開始〜完了
アラート閾値: > 30秒が連続3回
```

**KPI 3: Fallback発動率**:
```yaml
指標名: fallback_activation_rate
目標値: <= 10%
計測方法: gpt-4o Fallback実行割合
アラート閾値: > 15%
```

**KPI 4: エラー率**:
```yaml
指標名: error_rate
目標値: <= 5%
計測方法: Error Output経由実行割合
アラート閾値: > 10%
```

**KPI 5: データ整合性スコア**:
```yaml
指標名: data_integrity_score
目標値: >= 98%
計測方法: 全バリデーションチェック合格率
アラート閾値: < 95%
```

**KPI計測実装** (推奨):
- Google Sheets `analytics_summary` シートで日次集計
- Slack日次レポート自動送信
- 詳細は `2025-11-23_21-21_WFB-Critical項目対応完了レポート.md` の§2参照

---

## 3. ノード構成（推奨）

### 全体フロー
```
1) Trigger (Manual/Cron)
   ↓
2) Google Sheets - Get editorial
   ↓
3) Function - Filter published
   ↓
4) Split In Batches (batchSize=1, delay=500-1000ms)
   ↓
5) Project Config B
   ↓
6) Merge (Sheets + Config)
   ↓
7) Function - Preprocess
   ↓
8) AI Agent (gpt-4o-mini)
   ├─ [成功] → 9) Output Parser
   └─ [Fallback] → AI Agent (gpt-4o) → 9) Output Parser
              ↓
           10) Function - Validate Schema
              ├─ [成功] → 11) Google Sheets Update
              └─ [失敗] → Error Handler
                     ↓
                  12) Slack Notify
                     ↓
                  13) Webhook Approval
```

### 各ノード詳細設定

#### 1) Trigger
```yaml
タイプ: Manual Trigger（開発時）
推奨: Schedule Trigger（本番）
  - 頻度: 1日1回（深夜1時など）
  - Cron: "0 1 * * *"
```

#### 2) Google Sheets - Get editorial
```yaml
Operation: Read
Document ID: 1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII
Sheet Name: editorial (gid=0)
Options:
  - Include Header Row: true
```

#### 3) Function - Filter published
```javascript
// Filter rows where status == 'published'
const items = $input.all();

return items
  .filter(item => item.json.status === 'published')
  .map((item, index) => ({
    json: {
      ...item.json,
      row_id: index + 2,  // ヘッダー行除く
      sheet_url: `https://docs.google.com/spreadsheets/d/1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII/edit#gid=0&range=A${index + 2}`
    }
  }));
```

#### 4) Split In Batches
```yaml
Batch Size: 1
Options:
  - Reset: false
  - Delay Between Batches: 500-1000ms (レート制限対策)
```

#### 5) Project Config B
```yaml
Type: Set (n8n-nodes-base.set v3.4)
Assignments:
  - project_name: "Contents Engine講座"
  - default_segment: "Cold"
  - mdc_content: "## 生成ルールの適用範囲..." (全文、約5KB)
```

#### 6) Merge (Sheets + Config)
```yaml
Mode: Combine
Combine By: Combine All
```

#### 7) Function - Preprocess
```javascript
// デフォルト値埋め、mdc parse
return items.map(item => {
  const j = item.json;
  return {
    json: {
      row_id: j.row_id,
      sheet_url: j.sheet_url,
      mdc: JSON.parse(j.mdc_content),  // JSON parse
      row: {
        status: j.status,
        trending_keyword: j.trending_keyword,
        abstract: j.abstract || "",
        segment: j.segment || j.default_segment || "Cold",
        generated_title: j.generated_title,
        generated_body: j.generated_body,
        note_url: j.note_url,
        note_title: j.note_title,
        note_pv: j.note_pv ?? 0,
        note_likes: j.note_likes ?? 0,
        note_conversion: j.note_conversion ?? 0.0
      }
    }
  };
});
```

#### 8) AI Agent (Primary: gpt-4o-mini)

**Prompt**:
```
You are a data-driven marketing analyst.

Context:
- Project MDC: {{$json.mdc}}
- Published row: {{$json.row}}

Task:
1) Decide next_decision (improve|pause|scale) based on PV, conversion, segment fit.
2) Suggest one concrete next_action (<=200 chars) and one next_keyword_idea (<=100 chars).
3) Choose next_segment (Cold/Middle/Hot/Current).
4) Return 2-4 bullet insights (each <=200 chars) and concise reasoning (<=500 chars).

Output: JSON matching the connected output parser schema.
```

**System Message**:
```
You are a marketing analyst. Respect MDC tone and segment policies.
Prioritize actionable next steps with minimal hallucination.

CRITICAL: Your response MUST be valid JSON matching this exact schema:
{
  "next_decision": "improve|pause|scale",
  "next_action": "string (max 200 chars)",
  "next_segment": "Cold|Middle|Hot|Current",
  "next_keyword_idea": "string (max 100 chars)",
  "insights": ["string", "string", ...],  // 2-4 items, each max 200 chars
  "reasoning": "string (max 500 chars)"
}

Do NOT include any text outside this JSON structure.
```

**Options**:
```yaml
Model: gpt-4o-mini
Require Specific Output Format: true  # Output Parserスキーマ強制
Max Iterations: 8
Enable Streaming: false
Return Intermediate Steps: false  # 本番はfalse（デバッグ時のみtrue）
Batch Processing:
  - Batch Size: 1
```

**Fallback設定**:
```yaml
Needs Fallback: true
Fallback Model: gpt-4o (右ポートに接続)
```

#### 9) AI Output Parser (JSON)

**設定**:
```yaml
Type: AI Output Parser
Parser: JSON
Schema: § 2-2 の JSON Schema を貼り付け
```

**接続**:
- AI Agentの「Output」ポート → Output Parserの「Input」ポート
- Output Parserをキャンバス右側に配置（AI Agent右側）

#### 10) Function - Validate Schema（二重検証）

```javascript
// Output Parser後の追加検証
const json = $input.first().json;
const validationErrors = [];

// 1. 必須キー検証
const requiredKeys = ['next_decision', 'next_action', 'next_segment', 'next_keyword_idea', 'insights', 'reasoning'];
for (const key of requiredKeys) {
  if (!(key in json)) {
    validationErrors.push(`Missing required key: ${key}`);
  }
}

// 2. next_decision enum検証
if (!['improve', 'pause', 'scale'].includes(json.next_decision)) {
  validationErrors.push(`Invalid next_decision: ${json.next_decision}. Must be improve|pause|scale.`);
}

// 3. next_segment enum検証
if (!['Cold', 'Middle', 'Hot', 'Current'].includes(json.next_segment)) {
  validationErrors.push(`Invalid next_segment: ${json.next_segment}. Must be Cold|Middle|Hot|Current.`);
}

// 4. 文字数検証
if (json.next_action && json.next_action.length > 200) {
  validationErrors.push(`next_action exceeds 200 chars: ${json.next_action.length} chars`);
}

if (json.next_keyword_idea && json.next_keyword_idea.length > 100) {
  validationErrors.push(`next_keyword_idea exceeds 100 chars: ${json.next_keyword_idea.length} chars`);
}

// 5. insights配列検証
if (!Array.isArray(json.insights)) {
  validationErrors.push(`insights is not an array: ${typeof json.insights}`);
} else if (json.insights.length < 2 || json.insights.length > 4) {
  validationErrors.push(`insights must have 2-4 items, got ${json.insights.length}`);
}

// 6. reasoning文字数検証
if (json.reasoning && json.reasoning.length > 500) {
  validationErrors.push(`reasoning exceeds 500 chars: ${json.reasoning.length} chars`);
}

// 7. エラーがある場合は例外スロー（Error Handlerへ）
if (validationErrors.length > 0) {
  throw new Error(`Schema validation failed:\n${validationErrors.join('\n')}`);
}

// 8. 検証成功時
return {
  json: {
    ...json,
    validation_passed: true,
    validated_at: new Date().toISOString()
  }
};
```

#### 11) Google Sheets - Update
```yaml
Operation: Update
Document ID: 1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII
Sheet Name: editorial (gid=0)
Columns Mapping:
  - next_decision: {{ $json.next_decision }}
  - next_action: {{ $json.next_action }}
  - next_segment: {{ $json.next_segment }}
  - next_keyword_idea: {{ $json.next_keyword_idea }}
  - analyzed_at: {{ $now }}
```

**推奨**: insights, reasoning は別列に格納
```yaml
  - insights_json: {{ JSON.stringify($json.insights) }}
  - reasoning: {{ $json.reasoning }}
```

#### 12) Slack Notify - Analysis
```yaml
Channel: #content-ops
Text: § 2-2 の Slack通知フォーマット参照
Options:
  - Attachments:
    - Actions:
      - [Approve] → Webhook URL
      - [Reject] → Webhook URL
```

#### 13) Webhook Approval（WF-B → WF-A 再投入）

**Webhook URL**: `https://n8n.example.com/webhook/wf-b-approval`

**Payload**:
```json
{
  "action": "approve|reject",
  "row_id": "string",
  "next_keyword_idea": "string",
  "next_segment": "string"
}
```

**処理ロジック**: § 1-2 参照

---

## 3-2. テンプレート調査に基づく実装パターン

**参照**: `now/2025-11-23_21-57_WFB-テンプレート調査レポート.md` (15件のテンプレート分析)

### パターン分類と適用箇所

#### パターン1: AI Agent + Google Sheets統合（3つのアプローチ）

**1-1. Direct Append方式（最もシンプル）**
- **適用箇所**: § 3 ノード11（Google Sheets Update）
- **参照テンプレート**: Template #2 (ID: 4606) - Travel Agent
- **実装方法**:
  ```javascript
  // Google Sheets: Append Row
  {
    operation: "append",
    documentId: "1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII",
    sheetName: "editorial",
    columns: {
      mappingMode: "defineBelow",
      value: {
        next_decision: "={{ $json.next_decision }}",
        next_action: "={{ $json.next_action }}",
        next_segment: "={{ $json.next_segment }}",
        next_keyword_idea: "={{ $json.next_keyword_idea }}",
        analyzed_at: "={{ $now }}",
        insights_json: "={{ JSON.stringify($json.insights) }}",
        reasoning: "={{ $json.reasoning }}"
      }
    }
  }
  ```

**1-2. Lookup + Conditional Update方式（データ整合性重視）**
- **適用箇所**: § 3 ノード11の代替実装（重複防止が必要な場合）
- **参照テンプレート**: Template #9 (ID: 4150) - Agent Routing
- **実装方法**:
  ```javascript
  // 1. Google Sheets: Lookup Row (trending_keyword でマッチング)
  // 2. IF: 行が存在するか確認
  // 3a. 存在する場合: Update Row
  // 3b. 存在しない場合: Append Row
  ```

**1-3. Self-Modifying Workflow方式（高度な実装）**
- **適用箇所**: Phase 3の拡張機能（将来実装）
- **参照テンプレート**: Template #9 - Specialized Sub-Workflows
- **実装方法**: 分析結果に基づいてワークフロー自体を動的に変更

#### パターン2: Output Parser設定（3つのアプローチ）

**2-1. Structured Output Parser（推奨）**
- **適用箇所**: § 3 ノード9（AI Output Parser）
- **参照テンプレート**: Template #9 (ID: 4150) - Auto-fixing + Structured Parser
- **実装設定**:
  ```yaml
  Type: AI Output Parser
  Parser: Structured Output Parser (Auto-fixing)
  Schema: draft-07 JSON Schema（§ 2-2参照）
  Options:
    - Enable Auto-fixing: true  # 軽微なエラー自動修正
    - Max Retries: 3
  ```
- **メリット**: n8n内蔵の自動修正機能で99%の成功率
- **デメリット**: n8n 1.50.0以降でのみ利用可能（互換性確認必要）

**2-2. Manual Validation Loop（堅牢性重視）**
- **適用箇所**: § 3 ノード10（Function - Validate Schema）の強化版
- **参照テンプレート**: Template #6 (ID: 4316) - Reliable AI Output Without Structured Output Parser
- **実装方法**:
  ```javascript
  // Function: Manual Schema Validation with Retry Loop
  const json = $input.first().json;
  const runIndex = $runIndex || 0;
  const MAX_RETRIES = 3;

  const errors = [];

  // Enum validation
  if (!['improve', 'pause', 'scale'].includes(json.next_decision)) {
    errors.push('Invalid next_decision');
  }

  // Length validation
  if (json.next_action?.length > 200) {
    errors.push('next_action exceeds max length');
  }

  // Array validation
  if (!Array.isArray(json.insights) ||
      json.insights.length < 2 || json.insights.length > 4) {
    errors.push('insights must have 2-4 items');
  }

  if (errors.length > 0 && runIndex < MAX_RETRIES) {
    // Retry logic: Re-execute AI Agent with error feedback
    return {
      json: {
        retry: true,
        runIndex: runIndex + 1,
        errors: errors,
        original_input: $('Preprocess').first().json  // 元データを再送
      }
    };
  }

  if (errors.length > 0 && runIndex >= MAX_RETRIES) {
    // Max retries reached → Error Handler
    throw new Error(`Schema validation failed after ${MAX_RETRIES} retries:\n${errors.join('\n')}`);
  }

  // Validation success
  return {
    json: {
      ...json,
      validation_passed: true,
      validated_at: new Date().toISOString()
    }
  };
  ```
- **メリット**: n8nバージョン非依存、完全制御可能
- **デメリット**: 実装コスト高、リトライロジックが複雑

**2-3. Hybrid方式（推奨実装）**
- **適用箇所**: § 3 ノード9 + ノード10の組み合わせ
- **参照テンプレート**: Template #9 (Auto-fixing) + Template #6 (Manual Validation)
- **実装方法**:
  - ノード9: Structured Output Parser（一次検証）
  - ノード10: Manual Validation（二重検証）
  - 両方合格で初めて次ステップへ
- **メリット**: 自動修正 + 厳密検証の二段構え、最高の堅牢性
- **デメリット**: トークン消費やや増加

#### パターン3: Split In Batches実装（2つのアプローチ）

**3-1. Sequential Processing（標準）**
- **適用箇所**: § 3 ノード4（Split In Batches）
- **参照テンプレート**: Template #4 (ID: 3835) - Google Sheets Data Analysis
- **実装設定**:
  ```yaml
  Batch Size: 1
  Options:
    - Reset: false
    - Delay Between Batches: 500-1000ms  # レート制限対策
  ```
- **用途**: OpenAI API レート制限回避、Google Sheetsへの順次書き込み

**3-2. Batch Processing（高速化）**
- **適用箇所**: Phase 2の拡張機能（大量データ処理時）
- **参照テンプレート**: Template #7 (ID: 5146) - Robust JSON Parser
- **実装設定**:
  ```yaml
  Batch Size: 5-10  # 並列処理
  Options:
    - Reset: false
    - Delay Between Batches: 2000-3000ms
  ```
- **用途**: 100行以上の一括分析、夜間バッチ処理

#### パターン4: Error Handling（2つのアプローチ）

**4-1. Automatic Retry（OpenAI/Sheets API）**
- **適用箇所**: § 5 リトライ設定（全ノード共通）
- **参照テンプレート**: Template #9 - Routing with Auto-fixing
- **実装設定**: § 5 の設定そのまま（exponential backoff, 3回リトライ）

**4-2. Validation Fallback（スキーマエラー）**
- **適用箇所**: § 3 ノード10 → Error Handler
- **参照テンプレート**: Template #6 - Manual Validation Loop
- **実装方法**: § 5 Error Handler の実装そのまま（Slack通知 + 手動介入）

### 実装優先度マトリクス

| パターン | 優先度 | 実装時期 | 理由 |
|---------|-------|---------|------|
| 2-3. Hybrid Output Parser | 高 | Phase 1（即座） | 最高の堅牢性、検証合格率99%+ |
| 1-1. Direct Append | 高 | Phase 1（即座） | シンプル、実装コスト低 |
| 3-1. Sequential Processing | 高 | Phase 1（即座） | レート制限回避に必須 |
| 4-1. Automatic Retry | 高 | Phase 1（即座） | API安定性向上に必須 |
| 4-2. Validation Fallback | 高 | Phase 1（即座） | エラー通知・手動介入に必須 |
| 2-1. Structured Output Parser単体 | 中 | Phase 1（検証後） | n8nバージョン確認後に判断 |
| 1-2. Lookup + Conditional Update | 中 | Phase 2（1週間以内） | データ整合性要件が出た場合 |
| 3-2. Batch Processing | 低 | Phase 2-3（2-3ヶ月） | 大量データ処理が必要になった場合 |
| 1-3. Self-Modifying Workflow | 低 | Phase 3（3-6ヶ月） | 高度な自動化が求められた場合 |

### Phase 1実装推奨構成（今日中）

**採用パターン**:
1. **Output Parser**: パターン2-3（Hybrid方式）
   - Structured Output Parser（一次検証）
   - Manual Validation（二重検証、§ 3 ノード10そのまま）

2. **Google Sheets統合**: パターン1-1（Direct Append）
   - § 3 ノード11の実装そのまま

3. **Batch処理**: パターン3-1（Sequential Processing）
   - § 3 ノード4の実装そのまま

4. **Error Handling**: パターン4-1 + 4-2
   - § 5の設定そのまま

**実装手順**:
1. ✅ テンプレート調査完了（Session 10K）
2. 🔄 WFB再設計書更新（現在作業中）
3. 次: n8nキャンバスでノード配置開始
4. 次: AI Agent + Output Parserノード設定
5. 次: Pindataでテスト実行（§ 7 テストケース1-2）

---

## 4. ツール利用（任意）

### Calculatorツール
```yaml
用途: CVR計算など簡易算術
接続方法: AI Agent の「Tools」ポートに接続
例:
  - CVR = note_conversion / note_pv
  - ROI計算
```

### HTTP Requestツール
```yaml
用途: GA4やnote APIからリアルタイムデータ取得
注意: 不要なら接続しない（外部リサーチ抑止でコスト削減）
接続方法: AI Agent の「Tools」ポートに接続
```

---

## 5. エラー処理とリトライ

### リトライ設定（全ノード共通）
```yaml
OpenAI/Sheets/Slack:
  - Retry on Fail: 3回
  - Backoff Strategy: exponential
  - Wait Between Tries:
    - 1回目: 2秒
    - 2回目: 4秒
    - 3回目: 8秒
```

### JSONパース失敗時

**Output Parserエラー**:
- Output Parserでスキーマ不一致を検出
- Error Outputポートへ分岐

**Function検証エラー**:
- § 3 ノード10の二重検証で追加検証
- エラー時は例外スロー → Error Handler

### Error Handler

```javascript
// Function: Error Handler - Schema Validation Failure
const errorData = $input.first().json;
const timestamp = new Date().toISOString();

return {
  json: {
    channel: '#content-ops',
    text: `🚨 *WF-B スキーマ検証エラー*

*時刻*: ${timestamp}
*Row Data*:
- Keyword: ${errorData.row?.trending_keyword || 'N/A'}
- Segment: ${errorData.row?.segment || 'N/A'}
- PV: ${errorData.row?.note_pv || 0}

*エラー詳細*:
\`\`\`
${errorData.error?.message || 'Unknown Error'}
\`\`\`

*AI出力（Raw）*:
\`\`\`json
${JSON.stringify(errorData, null, 2)}
\`\`\`

手動で確認・再実行してください。
Sheet: ${errorData.sheet_url || 'N/A'}`
  }
};
```

### レートリミット対策
```yaml
Split In Batches:
  - batchSize: 1（順次処理）
  - delay: 500-1000ms

OpenAI API:
  - Max Iterations: 8（過剰リクエスト抑制）
  - レート制限: 500 RPM（gpt-4o-mini）
```

---

## 6. 運用チェックリスト

### 実装時チェック
- [ ] Output Parserがキャンバス右側に接続されている
- [ ] AI Agentで「Require Specific Output Format」がON
- [ ] `segment` 未設定時に前処理で `Cold` が入る（Function 7）
- [ ] Slack送信時にRowID/URLを含む（Function 3）
- [ ] Fallback設定: needsFallback=ON + 右ポートにgpt-4o

### Google Sheets設定チェック
- [ ] スプレッドシートID: `1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII`
- [ ] シート名: `editorial` (gid=0)
- [ ] 20列スキーマが正しく設定されている

### OpenAI認証チェック
- [ ] n8n Credentialsに登録済み
- [ ] 環境変数 `$env.OPENAI_API_KEY` を使用していない
- [ ] HTTP Requestノード認証: `predefinedCredentialType: openAiApi`

### Slack通知チェック
- [ ] Webhook URLが設定されている（プレースホルダーでない）
- [ ] チャンネル: `#content-ops`
- [ ] Approve/Reject Actionが動作する

### KPIモニタリングチェック
- [ ] Google Sheets `analytics_summary` シート作成（推奨）
- [ ] 日次集計Functionの実装（推奨）
- [ ] Slack日次レポート設定（推奨）

---

## 7. テスト

### テストケース定義

#### ケース1: 低パフォーマンス記事（改善または一時停止）
```yaml
入力:
  status: "published"
  trending_keyword: "AI活用"
  note_pv: 0
  note_likes: 0
  note_conversion: 0.0
  segment: "Cold"

期待出力:
  next_decision: "improve" | "pause"
  next_action: "具体的な改善策（200文字以内）"
  insights: 2-4個の配列
```

#### ケース2: 高パフォーマンス記事（スケール）
```yaml
入力:
  status: "published"
  trending_keyword: "生成AI"
  note_pv: 5000
  note_likes: 200
  note_conversion: 0.08
  segment: "Hot"

期待出力:
  next_decision: "scale"
  next_action: "拡大施策（200文字以内）"
  insights: 2-4個の配列
```

#### ケース3: Output Parserなしテスト（負荷テスト）
```yaml
目的: Output Parserの必要性検証
手順:
  1. Output Parserノードを無効化
  2. AI Agentを実行
  3. 出力がJSONでないことを確認

期待結果: テキスト形式で返り、スキーマ検証が働かない
```

#### ケース4: Slack承認→WF-A再投入テスト
```yaml
手順:
  1. WF-Bを実行
  2. Slack通知でApproveをクリック
  3. editorial シートに新規行が追加されることを確認
  4. WF-Aが `status=idea` を検出して実行されることを確認

期待結果:
  - 新規行: status=idea
  - trending_keyword = WF-B.next_keyword_idea
  - segment = WF-B.next_segment
```

### テストデータセット（Pindata用）

**ケース1用データ**:
```json
{
  "status": "published",
  "trending_keyword": "AI活用",
  "abstract": "",
  "segment": "Cold",
  "note_pv": 0,
  "note_likes": 0,
  "note_conversion": 0.0
}
```

**ケース2用データ**:
```json
{
  "status": "published",
  "trending_keyword": "生成AI",
  "abstract": "生成AIの最新トレンド",
  "segment": "Hot",
  "note_pv": 5000,
  "note_likes": 200,
  "note_conversion": 0.08
}
```

---

## 8. 今後の拡張（テンプレート調査に基づくロードマップ）

### Phase 1: 基本実装（今日中）✅ 優先度: 最高

**実装内容**:
- **AI Agent + Output Parser**: Hybrid方式（§ 3-2 パターン2-3）
  - Structured Output Parser（一次検証）
  - Manual Validation Function（二重検証）
- **Google Sheets統合**: Direct Append方式（§ 3-2 パターン1-1）
- **Batch処理**: Sequential Processing（§ 3-2 パターン3-1）
- **Error Handling**: Automatic Retry + Validation Fallback（§ 3-2 パターン4-1/4-2）

**実装チェックリスト**:
- [ ] n8nキャンバスでノード配置（13ノード）
- [ ] AI Agent Prompt設定（§ 3 ノード8参照）
- [ ] Output Parser設定（§ 2-2 JSON Schema貼り付け）
- [ ] Google Sheets接続テスト（spreadsheet ID: 1Gdqn7krlhpgKi__3h6xKjOm0XZ12usftoorXJTD7LII）
- [ ] Pindataでテスト実行（§ 7 テストケース1-2）
- [ ] KPI初期値記録（§ 2-2 KPI 5項目）

**期待成果**:
- JSON出力成功率: ≥95%
- 平均応答時間: ≤10秒
- WF-B基本機能完全動作

**実装時間**: 2-3時間（今日の22:00-24:00想定）

---

### Phase 2: KPIモニタリング + データ整合性強化（1週間以内）⚠️ 優先度: 高

**実装内容**:
1. **KPIモニタリング実装**:
   - Google Sheets `analytics_summary` シート作成
   - Function: 日次集計ロジック（5つのKPI計算）
   - Schedule Trigger: 毎日深夜2時に集計実行
   - Slack日次レポート送信（§ 2-2参照）

2. **データ整合性強化**:
   - **Lookup + Conditional Update方式**導入（§ 3-2 パターン1-2）
   - 重複行検出・防止ロジック
   - `trending_keyword` ユニーク制約チェック

3. **GA4 Data API連携**:
   - note記事のPV/Conversion自動更新
   - 毎日深夜1時にGA4データ取得
   - editorial シートの `note_pv`, `note_likes`, `note_conversion` を更新

**実装チェックリスト**:
- [ ] `analytics_summary` シート設計（7列: date, json_success_rate, avg_response_time, fallback_rate, error_rate, data_integrity_score, total_executions）
- [ ] 日次集計Functionコード作成（§ 2-2 KPI計算式参照）
- [ ] Slack Webhook URL設定（日次レポート送信用）
- [ ] Lookup + Conditional Update フロー実装
- [ ] GA4 Data API認証設定
- [ ] GA4データ取得Functionコード作成

**期待成果**:
- KPI可視化による運用品質の定量評価
- データ重複ゼロ化
- 分析精度向上（最新PVデータ利用）

**実装時間**: 4-5時間（1週間以内に分散実施）

---

### Phase 3: 承認フロー最適化 + 高度な自動化（2-3ヶ月以内）💡 優先度: 中

**実装内容**:
1. **承認フロー最適化**:
   - 承認スキップトグル実装（A/Bテスト運用）
   - 自動再投入条件ルール（例: `next_decision=scale` かつ `note_pv>1000` なら自動承認）
   - 承認履歴ログ（editorial シート `approved_at`, `approved_by` 記録）

2. **Batch Processing高速化**:
   - **Batch Processing方式**導入（§ 3-2 パターン3-2）
   - 100行以上の大量データ処理に対応
   - 夜間バッチ処理スケジュール（深夜0時-4時に集中実行）

3. **Self-Modifying Workflow実装**:
   - **Self-Modifying Workflow方式**導入（§ 3-2 パターン1-3）
   - 分析結果に基づくワークフロー動的変更
   - 例: `next_decision=scale` の場合、WF-A実行頻度を自動増加

**実装チェックリスト**:
- [ ] A/Bトグル設定（Project Config Bノードに追加）
- [ ] 自動承認条件ルールFunction実装
- [ ] 承認履歴ログ機能実装
- [ ] Batch Size=5-10でのパフォーマンステスト
- [ ] Self-Modifying Workflowプロトタイプ検証

**期待成果**:
- 承認作業時間50%削減
- 大量データ処理時間75%短縮（100行を1時間以内で処理）
- ワークフロー自己最適化による自動化レベル向上

**実装時間**: 8-10時間（2-3ヶ月以内に段階実施）

---

### Phase 4: タスク管理連携 + インテリジェント分析（3-6ヶ月以内）🚀 優先度: 低

**実装内容**:
1. **タスク管理連携**:
   - `next_action` を直接Notion/Jiraへタスク生成
   - アクション完了トラッキング
   - editorial シート `action_completed_at` 記録

2. **インテリジェント分析強化**:
   - RAG（Retrieval-Augmented Generation）導入
   - 過去の成功パターン学習
   - セグメント別最適戦略の自動提案

3. **Multi-Agent Routing**:
   - 複数AI Agentの並列実行（分析視点の多様化）
   - 例: マーケティング視点Agent + SEO視点Agent → 統合判断

**実装チェックリスト**:
- [ ] Notion/Jira API連携設定
- [ ] タスク生成Functionコード作成
- [ ] RAGベクトルDB選定（Pinecone/Weaviate/Qdrant）
- [ ] 過去データインデックス作成
- [ ] Multi-Agent Routingフロー設計
- [ ] 統合判断ロジック実装

**期待成果**:
- アクション実行率80%達成（タスク管理連携による）
- 分析精度90%向上（RAG学習による）
- 意思決定の多角化・高度化

**実装時間**: 15-20時間（3-6ヶ月以内に段階実施）

---

## 9. Phase 0検証結果

### データサイズ検証
```yaml
入力データサイズ: < 7KB/行（mdc_content含む）
AI Agent入力: < 8KB/リクエスト
OpenAI API応答: < 5KB
総データサイズ: < 15KB/実行

結論: ✅ 全てJSON形式、バイナリデータなし
```

### アーキテクチャ決定
```yaml
推奨アーキテクチャ: 標準JSONフロー
Binary Data使用: ❌ 不要
ノード構成妥当性: ✅ 全ノードが標準フローに適合
```

### リスク評価
```yaml
特定リスク:
  - AI API応答時間変動（5-30秒）: Fallback設定で対策
  - レートリミット（500 RPM）: Split In Batches + delay で対策
  - JSONパース失敗: Output Parser + Function二重検証で対策
  - Google Sheets競合: batchSize=1 で順次処理

総合評価: ✅ 全リスクに対策あり
```

### Phase 0検証総合判定
```
✅ WF-Bは標準JSONフローとして実装可能
✅ Phase 0検証に合格
✅ 実装開始可能
```

---

## 10. 参照ドキュメント

### Critical項目対応完了レポート
`now/2025-11-23_21-21_WFB-Critical項目対応完了レポート.md`
- Q1: WF-A仕様確認とインターフェース定義（詳細）
- Q2: 安定動作KPI定義（計測実装例）
- Q4: Output Parserスキーマ厳密化（JSON Schema全文）
- Phase 0検証（データサイズ・リスク評価詳細）

### WF-A/WF-B要件適合性分析レポート
`now/2025-11-22_11-27_WF-A-B要件適合性分析レポート.md`
- WF-AとWF-Bの既知の問題点
- P0（Critical）対応項目リスト
- Editorial Sheetsスキーマ不整合の詳細

### 設計仕様書
`now/コンテンツ自動運用システム_設計仕様書_v0.2.md`
- 全体システムアーキテクチャ
- DMMモデル（Belief構造）
- セグメント別コンテンツルール

---

**ドキュメント作成者**: Claude Code
**最終レビュー**: 2025-11-23 21:21 JST
**Phase 0検証**: ✅ 合格
**実装ステータス**: 設計完了、実装開始可能
