# WF10 Check Status修正手順書 - 根本原因解決（state vs status）

**作成日時**: 2025-11-24 02:45:32 JST
**対象ワークフロー**: WF10-Main: kie.ai Sora 2 ビデオ生成 (ID: kxKLB0EWlOhOjaOv)
**修正対象ノード**: Check Status (IF node), Extract Video URL (Edit Fields node)

---

## 🎯 修正目的

kie.ai動画生成完了検出の根本的な問題を解決し、ワークフローを14/14ノード完走させる。

---

## 🚨 根本原因の特定

### テンプレートワークフロー分析結果

**参照テンプレート**: [Sora 2 Automation](https://n8n-python-production-344b.up.railway.app/workflow/WRi0cqT7m4Obdx1V)

**重要な発見**:
- kie.ai APIは `state` フィールドを使用（`status` ではない）
- 完了時の値は `"success"`（`"completed"` ではない）

---

## 📊 kie.ai APIレスポンス構造（正しい理解）

### 動画生成完了時のレスポンス

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "717658893257b412440f795a64f09e83",
    "model": "sora-2-text-to-video",
    "state": "success",  // ← "state"フィールド（"status"ではない）
    "param": "{...}",
    "resultJson": "{\"resultUrls\":[\"https://videos.openai.com/vg-assets/...\"]}",  // ← 動画URLはここ
    "costTime": 265,
    "completeTime": 1759591553634
  }
}
```

---

## ❌ 現在の誤った設定

### 修正箇所1: Check Status - フィールド名（誤り）

```javascript
{
  "leftValue": "={{ $json.data.status }}",  // ❌ 誤り！
  "rightValue": "completed",                 // ❌ 誤り！
  "operator": "equals"
}
```

**問題点**:
- `$json.data.status` → `undefined`（`status`フィールドは存在しない）
- 正しいフィールド名: `$json.data.state`
- 正しい値: `"success"`

**結果**:
- `undefined === "completed"` → 常に `false`
- 動画生成が完了しても、永遠にLoop側に進む

### 修正箇所2: Extract Video URL - パス（誤り）

```javascript
{
  "name": "video_url",
  "value": "={{ $json.output.video_url }}",  // ❌ 誤り！
  "type": "string"
}
```

**問題点**:
- `$json.output.video_url` → `undefined`（`output`フィールドは存在しない）
- 正しいパス: `JSON.parse($json.data.resultJson).resultUrls[0]`

---

## ✅ 正しい設定（テンプレートから学んだこと）

### 修正1: Check Status（修正後）

```javascript
{
  "leftValue": "={{ $json.data.state }}",  // ✅ 修正！
  "rightValue": "success",                  // ✅ 修正！
  "operator": "equals"
}
```

**変更箇所**:
- ❌ `$json.data.status` → ✅ `$json.data.state`
- ❌ `"completed"` → ✅ `"success"`

### 修正2: Extract Video URL（修正後）

```javascript
{
  "name": "video_url",
  "value": "={{ JSON.parse($json.data.resultJson).resultUrls[0] }}",  // ✅ 修正！
  "type": "string"
}
```

**変更箇所**:
- ❌ `$json.output.video_url`
- ✅ `JSON.parse($json.data.resultJson).resultUrls[0]`

**解説**:
- `resultJson` は文字列なので `JSON.parse()` が必要
- パース後の `resultUrls` 配列の最初の要素を取得

---

## 🔧 n8n UI経由の手動修正手順

### Step 1: n8n UIを開く

```
https://n8n-python-production-344b.up.railway.app
```

### Step 2: ワークフローを開く

- ワークフロー名: **WF10-Main: kie.ai Sora 2 ビデオ生成(Webhook Manual Trigger版)**
- ワークフローID: `kxKLB0EWlOhOjaOv`

### Step 3: Check Statusノードをクリック

### Step 4: Check Statusノードの条件式を修正

**現在の設定**:
- **Conditions** セクション
- **Value 1 (左辺)**: `={{ $json.data.status }}`
- **Operator**: `is equal to`
- **Value 2 (右辺)**: `completed`

**新しい設定**:
- **Value 1 (左辺)**: `={{ $json.data.state }}`
- **Operator**: `is equal to`（変更なし）
- **Value 2 (右辺)**: `success`

### Step 5: Extract Video URLノードをクリック

### Step 6: Extract Video URLノードの式を修正

**現在の設定**:
- **Assignments** セクション
- **Name**: `video_url`
- **Value**: `={{ $json.output.video_url }}`

**新しい設定**:
- **Name**: `video_url`（変更なし）
- **Value**: `={{ JSON.parse($json.data.resultJson).resultUrls[0] }}`

### Step 7: 保存

- 右上の **Save** ボタンをクリック
- ワークフローが **Active** 状態（トグルON）であることを確認

---

## 🧪 修正後の期待される動作

### データフロー（修正後）

```
Create Video Task
  → POST /api/v1/jobs/createTask
  → response: { code: 200, data: { taskId: "xxx" } }
  ↓
Wait (60秒)
  ↓
Get Status
  → GET /api/v1/jobs/recordInfo?taskId=xxx
  → response: { code: 200, data: { state: "processing" } }
  ↓
Check Status ✅ 修正箇所1
  → 条件: $json.data.state === "success"
  → false → Loop側
  ↓
Loop → Wait (60秒) → Get Status → Check Status
  ↓
  （動画生成完了後）
  ↓
Get Status
  → response: {
      code: 200,
      data: {
        state: "success",
        resultJson: "{\"resultUrls\":[\"https://...\"]}"
      }
    }
  ↓
Check Status
  → 条件: $json.data.state === "success"
  → true → Extract Video URL側 ✅
  ↓
Extract Video URL ✅ 修正箇所2
  → JSON.parse($json.data.resultJson).resultUrls[0]
  → video_url = "https://videos.openai.com/..."
  ↓
Update Notion Page
  → Notionページに動画URL登録
  → ステータス更新: "Completed"
  ↓
✅ 14/14ノード完走（100%）
```

---

## ✅ 検証手順

### 修正完了後のE2Eテスト

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"page_id": "2b368d5c2986811f87ecf2aecaedf1cf"}' \
  https://n8n-python-production-344b.up.railway.app/webhook/wf10-notion-trigger
```

### 期待される結果

1. **Create Video Task**: taskId生成成功
2. **Wait**: 60秒待機
3. **Get Status（初回）**: `{ data: { state: "processing" } }` または `{ data: { state: "pending" } }`
4. **Check Status**: `data.state !== "success"` → Loop
5. **Loop**: 60秒待機 → 再度Get Status
6. **Get Status（N回目）**: `{ data: { state: "success", resultJson: "..." } }`
7. **Check Status**: `data.state === "success"` → Extract Video URL ✅
8. **Extract Video URL**: `JSON.parse(...).resultUrls[0]` でvideoUrl取得成功 ✅
9. **Update Notion**: Notionページ更新成功 ✅
10. **最終結果**: 14/14ノード完走（100%）✅

---

## 📝 技術的考察

### なぜこのバグが見逃されたか

1. **ドキュメント不足**: kie.ai公式ドキュメントで `state` vs `status` が明確でない
2. **推測ベースの実装**: APIレスポンスを直接確認せず、推測で実装した
3. **テンプレート参照の遅れ**: 既存の成功事例を最初から参照しなかった

### 学んだこと

- ❌ **推測ベースの修正は危険**: APIレスポンス構造を必ず確認してから実装
- ✅ **テンプレート参照の重要性**: 成功している実装を最初から参照すべき
- ✅ **フィールド名の厳密な確認**: `state` と `status` のような微妙な違いに注意
- ✅ **条件式のテスト**: n8n UIのテスト機能で条件式を検証すべき

---

## 🚀 次のステップ

1. ✅ Check Status条件式修正（本手順書）
   - `$json.data.status` → `$json.data.state`
   - `"completed"` → `"success"`
2. ✅ Extract Video URL修正（本手順書）
   - `$json.output.video_url` → `JSON.parse($json.data.resultJson).resultUrls[0]`
3. ⏳ n8n UIでCheck StatusノードとExtract Video URLノードを修正
4. ⏳ E2Eテスト実行
5. ⏳ 14/14ノード完走確認（100%達成目標）
6. ⏳ Notionページに動画URL登録確認
7. ⏳ Google Sheets統合の再開検討

---

## 📚 参考資料

- **テンプレートワークフロー**: [Sora 2 Automation (WRi0cqT7m4Obdx1V)](https://n8n-python-production-344b.up.railway.app/workflow/WRi0cqT7m4Obdx1V)
- **kie.ai 公式APIドキュメント**: https://docs.kie.ai/
- **エンドポイント**: `/api/v1/jobs/recordInfo?taskId={taskId}`
- **レスポンス構造**: `{ code: number, msg: string, data: { state: string, resultJson: string } }`
- **完了時の値**: `state: "success"`, `resultJson: "{\"resultUrls\":[\"https://...\"]}" `

---

**ドキュメント保存先**: `now/2025-11-24_02-45_Check-Status-state-vs-status-修正手順書.md`
