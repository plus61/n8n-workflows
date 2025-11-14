# WF7 Phase4 親フロー簡素化実装計画

**作成日**: 2025-11-09  
**対象ワークフロー**: `r9Sp5n0mkUCcH8cw`  
**目的**: 48ノードを10-12ノードに簡素化

---

## 📋 現状確認

### Phase4a/bの呼び出し方法

現在のワークフローでは、Phase4a/bは**HTTP Requestノード**で呼び出しています：

- Phase4a: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator`
- Phase4b: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-image-to-video`

**結論**: Execute Sub-workflowノードではなく、HTTP Requestノードを使用する方針で進めます。

---

## 🎯 簡素化方針

### 削除対象ノード

1. **データ変換ノード（削除）**:
   - `レスポンスデータ準備`
   - `レスポンスデータ復元`
   - 一部の`Set`ノード（データ統合で完結可能なもの）

2. **FALポーリング機構（削除）**:
   - 親フロー内のFAL処理はPhase4bに移行済み
   - 残存している場合は削除

3. **重複エラーハンドリング（統合）**:
   - Phase4aエラー、Phase4bエラー、Phase4cエラーを1つに統合

### 保持・追加ノード

1. **Webhook**（保持）
2. **Notion API呼び出し**（保持）
3. **URL抽出**（保持、またはPhase4aに統合）
4. **データ統合**（保持）
5. **HTTP Request - Call Phase4a**（保持）
6. **IF - Phase4a Success Check**（保持）
7. **HTTP Request - Call Phase4b**（保持）
8. **IF - Phase4b Success Check**（保持）
9. **HTTP Request - Call Phase4c**（追加）
10. **IF - Phase4c Success Check**（追加、または統合IFに統合）
11. **Google Drive Upload**（保持）
12. **Notion更新**（保持）
13. **Respond to Webhook**（保持）
14. **エラーハンドリング**（統合）

---

## 🔧 実装手順

### Step 1: バックアップ

```bash
# 現在のワークフローをバックアップ
mcp_n8n-mcp_n8n_get_workflow({id: "r9Sp5n0mkUCcH8cw"})
# → workflows/archive/wf7-phase4-v3-before-simplify-YYYYMMDD.json
```

### Step 2: 不要ノード削除

**削除対象ノードID**:
- `レスポンスデータ準備`: `4b922f76-29fb-47e1-a41f-1bfc7946c43e`
- `レスポンスデータ復元`: `1458e53b-a9e8-47d8-a022-3d9171886a41`
- その他、FALポーリング機構の残存ノード

**削除方法**:
```bash
mcp_n8n-mcp_n8n_update_partial_workflow({
  id: "r9Sp5n0mkUCcH8cw",
  operations: [
    {
      type: "removeNode",
      nodeId: "4b922f76-29fb-47e1-a41f-1bfc7946c43e"
    },
    {
      type: "removeNode",
      nodeId: "1458e53b-a9e8-47d8-a022-3d9171886a41"
    }
  ]
})
```

### Step 3: Phase4c HTTP Requestノード追加

**Phase4c Webhook URL**: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4c-ffmpeg-concat`

**追加ノード**:
```json
{
  "id": "http-phase4c-call-node",
  "name": "HTTP Request - Call Phase4c",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.3,
  "position": [2208, -32],
  "parameters": {
    "method": "POST",
    "url": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4c-ffmpeg-concat",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ {\n  \"script_id\": $('Set - Phase4b Payload').item.json.script_id,\n  \"videos_metadata\": $('Set - Phase4b Payload').item.json.videos_metadata\n} }}",
    "options": {
      "timeout": 600000
    },
    "onError": "continueErrorOutput"
  }
}
```

### Step 4: エラーハンドリング統合

**統合IFノード**:
```json
{
  "id": "if-all-phases-success",
  "name": "IF - All Phases Success",
  "type": "n8n-nodes-base.if",
  "typeVersion": 2.2,
  "position": [2432, -32],
  "parameters": {
    "conditions": {
      "options": {
        "version": 2,
        "caseSensitive": true,
        "typeValidation": "strict"
      },
      "combinator": "and",
      "conditions": [
        {
          "id": "phase4a-success",
          "leftValue": "={{ $('Set - Phase4a Payload').item.json.phase4a_success }}",
          "rightValue": true,
          "operator": {
            "type": "boolean",
            "operation": "equals"
          }
        },
        {
          "id": "phase4b-success",
          "leftValue": "={{ $('Set - Phase4b Payload').item.json.phase4b_success }}",
          "rightValue": true,
          "operator": {
            "type": "boolean",
            "operation": "equals"
          }
        },
        {
          "id": "phase4c-success",
          "leftValue": "={{ $json.success }}",
          "rightValue": true,
          "operator": {
            "type": "boolean",
            "operation": "equals"
          }
        }
      ]
    },
    "onError": "continueErrorOutput"
  }
}
```

### Step 5: 接続更新

**新しい接続フロー**:
```
Set - Phase4b Payload
  ↓
HTTP Request - Call Phase4c
  ↓
IF - All Phases Success
  ├─ [true] → Google Drive Upload → Notion更新 → Respond to Webhook
  └─ [false] → エラー時Notion更新 → エラー時Webhook応答
```

---

## 📊 期待される結果

### ノード数

| 項目 | 現在 | 簡素化後 | 削減 |
|------|------|---------|------|
| **総ノード数** | 48個 | 14-16個 | **67-71%削減** |

### エラー・警告

| 項目 | 現在 | 簡素化後 |
|------|------|---------|
| **エラー数** | 5個 | 0個 |
| **警告数** | 65個 | <10個 |

---

## ⚠️ 注意事項

1. **Phase4cの実装**: Codeノードではファイルシステムアクセス不可のため、外部APIまたはExecute Commandノードが必要
2. **データ契約**: Phase4a/b/cの入力/出力データ契約を確認
3. **エラーハンドリング**: 各Phaseのエラー形式を統一

---

**作成者**: AI Assistant  
**次回更新**: 実装完了時




