# WF10 Get Status ノード修正手順書 - taskId参照修正

**作成日時**: 2025-11-23 23:23:26 JST
**対象ワークフロー**: WF10-Main: kie.ai Sora 2 ビデオ生成 (ID: kxKLB0EWlOhOjaOv)
**修正対象ノード**: Get Status (HTTP Request node)

---

## 🎯 修正目的

Get StatusノードでCreate Video Taskが返す正しいフィールド名`data.taskId`を参照し、kie.ai APIに正しいjob_idパラメータを送信する。

---

## 📋 現在の問題

### Execution #3918の実行結果

**Get Statusノードのエラー**:
```
GET https://api.kie.ai/api/v1/jobs/getStatus?job_id=
404 - Not Found
```

**問題点**:
- ❌ `job_id`パラメータが空（空文字列）
- ❌ 存在しないフィールド`job_id`を参照している

---

## ✅ Create Video Taskの実際の出力（Execution #3918）

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "ae29755fc21b96331de974907978f3b2",
    "recordId": "ae29755fc21b96331de974907978f3b2"
  }
}
```

**重要**:
- ✅ フィールド名は`data.taskId`（`job_id`ではない）
- ✅ taskIdとrecordIdは同じ値

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
=https://api.kie.ai/api/v1/jobs/getStatus?job_id={{ $('Create Video Task').item.json.job_id }}
```

**問題**: `job_id`フィールドが存在しない → 空文字列になる

**新しい値** (CORRECT):
```
=https://api.kie.ai/api/v1/jobs/getStatus?job_id={{ $('Create Video Task').item.json.data.taskId }}
```

**変更点**:
- ❌ `.job_id` → ✅ `.data.taskId`

### Step 5: 保存

- **Saveボタン**をクリック
- ワークフローが**Active状態**（トグルON）であることを確認

---

## 🧪 修正後の期待される動作

### Get Status成功リクエスト（修正後）

```
GET https://api.kie.ai/api/v1/jobs/getStatus?job_id=ae29755fc21b96331de974907978f3b2
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
  > now/2025-11-23_23-23_e2e-test-after-taskid-fix.txt 2>&1

cat now/2025-11-23_23-23_e2e-test-after-taskid-fix.txt
```

### 期待される結果

- ✅ **HTTP Status**: 200 OK
- ✅ **Get Status成功**: 200応答、statusフィールド取得
- ✅ **Poll Video Status**: ループ動作、completed待機
- ✅ **実行完了ノード**: 14/14 (100%)

---

## 📊 データフロー図（修正後）

```
Create Video Task (HTTP Request)
  → POST https://api.kie.ai/api/v1/jobs/createTask
  → response: {
      code: 200,
      data: {
        taskId: "ae29755fc21b96331de974907978f3b2",
        recordId: "ae29755fc21b96331de974907978f3b2"
      }
    }
  ↓
Wait (5秒)
  ↓
Get Status (HTTP Request) ✅ 修正箇所
  → GET https://api.kie.ai/api/v1/jobs/getStatus?job_id=ae29755fc21b96331de974907978f3b2
  → 正しいtaskIdを使用
  → response: { code: 200, data: { status: "processing" } } ✅
  ↓
Poll Video Status (Loop Until)
  → Get Statusを繰り返し実行
  → status === "completed" まで待機
  ↓
Update Notion Page (完了時)
```

---

## 🔍 参考：n8n式の構造

**Create Video Taskの出力構造**:
```javascript
{
  code: 200,
  msg: "success",
  data: {           // ← dataオブジェクト
    taskId: "...",  // ← 正しいフィールド
    recordId: "..."
  }
}
```

**n8n式での参照方法**:
```javascript
// ❌ 間違い（dataオブジェクトを無視）
$('Create Video Task').item.json.job_id      // → undefined → 空文字列

// ✅ 正しい（dataオブジェクトを経由）
$('Create Video Task').item.json.data.taskId // → "ae29755fc21b96331de974907978f3b2"
```

---

## 🚀 次のステップ

1. ✅ この手順書に従ってGet Statusノードを修正
2. ⏳ E2Eテストを実行
3. ⏳ Poll Video Statusのループ動作確認
4. ⏳ 全14ノード完走確認（100%達成目標）
5. ⏳ Google Sheets統合の再開検討

---

**ドキュメント保存先**: `now/2025-11-23_23-23_Get-Status-taskId修正手順書.md`
