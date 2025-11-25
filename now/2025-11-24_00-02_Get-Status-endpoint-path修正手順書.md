# WF10 Get Status ノード修正手順書 - APIエンドポイントパス修正

**作成日時**: 2025-11-24 00:02:05 JST
**対象ワークフロー**: WF10-Main: kie.ai Sora 2 ビデオ生成 (ID: kxKLB0EWlOhOjaOv)
**修正対象ノード**: Get Status (HTTP Request node)

---

## 🎯 修正目的

Get StatusノードのAPIエンドポイントパスを、kie.ai APIドキュメントに基づいた正しいパスに変更し、404エラーを解消する。

---

## 📋 現在の問題

### Execution #3921の実行結果

**Get Statusノードのエラー**:
```
GET https://api.kie.ai/api/v1/jobs/getStatus?job_id=2880a4b046c57a19110406e198dc1fa3
404 - Not Found
```

**エラー詳細**:
```html
<html><body>
<h1>Whitelabel Error Page</h1>
<p>This application has no explicit mapping for /error, so you are seeing this as a fallback.</p>
<div>There was an unexpected error (type=Not Found, status=404).</div>
</body></html>
```

**問題点**:
- ❌ APIがHTMLエラーページを返す（JSONではない）
- ❌ エンドポイント `/api/v1/jobs/getStatus` が存在しない
- ✅ TaskId参照は正常（`2880a4b046c57a19110406e198dc1fa3`が正しく抽出されている）

---

## ✅ kie.ai APIドキュメントの確認

**参照ドキュメント**: `now/2025-11-23_18-12_kie.ai-API完全ガイド-n8n設定.md` (行47-50)

**ドキュメント記載の正しいエンドポイント** (推定):
```
**Status Check** (推定):
GET /api/v1/veo/status/{taskId}
```

**重要な違い**:
1. **パス**: `/api/v1/jobs/getStatus` → `/api/v1/veo/status/`
2. **パラメータ形式**: クエリパラメータ `?job_id=` → パスパラメータ `/{taskId}`

---

## 🔧 n8n UI経由の手動修正手順

### Step 1: n8n UIを開く

```
https://n8n-python-production-344b.up.railway.app
```

### Step 2: ワークフローを開く

- ワークフロー名: **WF10-Main: kie.ai Sora 2 ビデオ生成(Webhook Manual Trigger版)**
- ワークフローID: `kxKLB0EWlOhOjaOv`

### Step 3: Get Statusノードをクリック

### Step 4: URLフィールドを編集

**現在の値** (WRONG):
```
=https://api.kie.ai/api/v1/jobs/getStatus?job_id={{ $('Create Video Task').item.json.data.taskId }}
```

**問題点**:
- ❌ エンドポイントパス `/api/v1/jobs/getStatus` が存在しない
- ❌ クエリパラメータ形式 `?job_id=` を使用している

**新しい値** (CORRECT):
```
=https://api.kie.ai/api/v1/veo/status/{{ $('Create Video Task').item.json.data.taskId }}
```

**変更点**:
- ✅ エンドポイントパス: `/api/v1/jobs/getStatus` → `/api/v1/veo/status/`
- ✅ パラメータ形式: クエリパラメータ削除、TaskIdをパスに直接追加

### Step 5: 保存

- **Saveボタン**をクリック
- ワークフローが**Active状態**（トグルON）であることを確認

---

## 🧪 修正後の期待される動作

### Get Status成功リクエスト（修正後）

**リクエストURL**:
```
GET https://api.kie.ai/api/v1/veo/status/2880a4b046c57a19110406e198dc1fa3
```

**リクエストヘッダー**:
```
Authorization: Bearer [KIE_AI_API_KEY]
```

### 期待されるレスポンス

**動画生成中**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "status": "processing",
    "progress": 45
  }
}
```

**動画生成完了**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "status": "completed",
    "videoUrl": "https://..."
  }
}
```

---

## ✅ 検証手順

### 修正完了後のE2Eテスト

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"page_id": "2b368d5c2986811f87ecf2aecaedf1cf"}' \
  -w "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n" \
  https://n8n-python-production-344b.up.railway.app/webhook/wf10-notion-trigger \
  > now/2025-11-24_00-02_e2e-test-after-endpoint-fix.txt 2>&1

cat now/2025-11-24_00-02_e2e-test-after-endpoint-fix.txt
```

### 期待される結果

- ✅ **HTTP Status**: 200 OK
- ✅ **Get Status成功**: 200応答、statusフィールド取得
- ✅ **Poll Video Status**: ループ動作開始、completed待機
- ✅ **実行完了ノード**: 14/14 (100%)

---

## 📊 データフロー図（修正後）

```
Create Video Task (HTTP Request)
  → POST https://api.kie.ai/api/v1/jobs/createTask
  → response: {
      code: 200,
      data: {
        taskId: "2880a4b046c57a19110406e198dc1fa3",
        recordId: "2880a4b046c57a19110406e198dc1fa3"
      }
    }
  ↓
Wait (5秒)
  ↓
Get Status (HTTP Request) ✅ 修正箇所
  → GET https://api.kie.ai/api/v1/veo/status/2880a4b046c57a19110406e198dc1fa3
  → エンドポイントパス変更: /jobs/getStatus → /veo/status/
  → パラメータ形式変更: クエリ → パス
  → response: { code: 200, data: { status: "processing" } } ✅
  ↓
Poll Video Status (Loop Until)
  → Get Statusを繰り返し実行
  → status === "completed" まで待機
  ↓
Update Notion Page (完了時)
```

---

## 🔍 参考：エンドポイント形式の比較

### 現在の形式（WRONG）

**URL構造**:
```
https://api.kie.ai/api/v1/jobs/getStatus?job_id={taskId}
```

**特徴**:
- ❌ パス: `/api/v1/jobs/getStatus`
- ❌ パラメータ: クエリパラメータ `?job_id=`
- ❌ 結果: 404 Not Found（エンドポイント存在しない）

### 正しい形式（CORRECT）

**URL構造**:
```
https://api.kie.ai/api/v1/veo/status/{taskId}
```

**特徴**:
- ✅ パス: `/api/v1/veo/status/`
- ✅ パラメータ: パスパラメータ（TaskIdをURL末尾に追加）
- ✅ 結果: 200 OK（期待される応答）

---

## ⚠️ 注意事項

### ドキュメントの制約

- kie.ai APIドキュメントでは、このエンドポイントが**「推定」**とマークされています
- 実際のAPIの挙動と異なる可能性があります
- 修正後もエラーが発生する場合は、kie.ai公式ドキュメントを参照してください

### 代替エンドポイントの可能性

修正後も404が発生する場合、以下のエンドポイントを試してください：

1. `/api/v1/jobs/status/{taskId}`
2. `/api/v1/task/status/{taskId}`
3. `/api/v1/status/{taskId}`

---

## 🚀 次のステップ

1. ✅ この手順書に従ってGet Statusノードを修正
2. ⏳ E2Eテストを実行
3. ⏳ Poll Video Statusのループ動作確認
4. ⏳ 全14ノード完走確認（100%達成目標）
5. ⏳ Google Sheets統合の再開検討

---

## 📝 修正履歴

### 2025-11-24 00:02 - エンドポイントパス修正

**修正前**:
```
GET /api/v1/jobs/getStatus?job_id={taskId}
```

**修正後**:
```
GET /api/v1/veo/status/{taskId}
```

**理由**: kie.ai APIドキュメント（行49）に基づく正しいエンドポイントパスへの変更

---

**ドキュメント保存先**: `now/2025-11-24_00-02_Get-Status-endpoint-path修正手順書.md`
