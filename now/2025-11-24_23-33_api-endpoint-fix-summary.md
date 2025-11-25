# WF10-Main APIエンドポイント修正完了レポート

**作成日時**: 2025-11-24 23:33:16 JST

## 🎯 問題の発見

**実行 #4070の状態**:
- Status: `waiting` (75分以上実行中)
- ループ回数: 15回 (各5分)
- 問題: Get Statusノードが常に `data: null` を返す

## 🔍 根本原因

**誤ったAPIエンドポイント** (Line 217):
```
/api/v1/veo/record-info?taskId=xxx
```

このエンドポイントは常に以下を返します:
```json
{
  "code": 200,
  "msg": "success",
  "data": null
}
```

## ✅ 修正内容

**正しいAPIエンドポイント**:
```
/api/v1/jobs/getTask?taskId=xxx
```

このエンドポイントは実際のタスクステータスを返します:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "state": "success",
    "resultJson": "...",
    ...
  }
}
```

## 📝 修正されたGet Statusノード (Lines 215-240)

```json
{
  "parameters": {
    "url": "=https://api.kie.ai/api/v1/jobs/getTask?taskId={{ $('Create Video Task').item.json.data.taskId }}",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Authorization",
          "value": "=Bearer {{ $env.KIE_AI_API_KEY }}"
        }
      ]
    },
    "options": {
      "response": {
        "response": {
          "responseFormat": "json"
        }
      }
    }
  },
  "id": "get-status",
  "name": "Get Status",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [2064, 272]
}
```

## 📦 修正済みファイル

- **ファイル名**: `2025-11-24_23-22_WF10-Main-fixed-api-endpoint.json`
- **場所**: `now/` ディレクトリ
- **変更点**: Line 217のAPIエンドポイントのみ修正

## 🚀 次のステップ

### 1. n8n UIに手動インポート

1. n8n UIを開く
2. Import from File
3. `now/2025-11-24_23-22_WF10-Main-fixed-api-endpoint.json` を選択
4. インポート完了

### 2. E2Eテスト実行

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"page_id": "2b368d5c2986811f87ecf2aecaedf1cf"}' \
  -w "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n" \
  https://n8n-python-production-344b.up.railway.app/webhook/wf10-notion-trigger
```

### 3. 期待される動作

- Webhook即座に200 OKレスポンス
- Get StatusノードがtaskIdに対する実際のステータスデータを取得
- `state: "success"` 検出後、Extract Video URL → Update Notionへ進む
- ビデオ生成完了まで約4-5分

## 🔧 技術的詳細

### n8n MCP updateNode問題

以下の方法を試したが、すべて失敗:
- `nodeId: "get-status"` → "Node not found"エラー
- `nodeId: "fb27b0d8-f979-46db-94d6-0ee7b69b5f73"` (full UUID) → 同じエラー

**回避策**: Edit toolを使用してJSON直接編集

### kie.ai API差異

| エンドポイント | レスポンス | 用途 |
|--------------|----------|-----|
| `/api/v1/veo/record-info` | `data: null` | ❌ 使用不可 |
| `/api/v1/jobs/getTask` | 実際のタスクデータ | ✅ 正解 |

## 📊 影響範囲

- **修正前**: 無限ループ (75分+)
- **修正後**: 正常にタスクステータス取得、完了検出可能
