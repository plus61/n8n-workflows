# WF10 Webhook Response追加手順書 - E2Eテストハング問題の根本解決

**作成日時**: 2025-11-24 03:17:21 JST
**対象ワークフロー**: WF10-Main: kie.ai Sora 2 ビデオ生成 (ID: kxKLB0EWlOhOjaOv)
**修正対象**: ワークフロー構造（Webhook Responseノード追加）

---

## 🎯 修正目的

E2Eテストが6分以上ハングする問題の根本解決。Webhook Responseノードを追加してHTTPレスポンスを即座に返却し、バックグラウンドで動画生成処理を継続する。

---

## 🚨 根本原因の確定

### ワークフロー構造分析結果

**ワークフローID**: `kxKLB0EWlOhOjaOv`
**ノード数**: 14ノード
**重大な問題**: **Webhook Responseノードが完全に欠落**

### 現在のフロー（問題あり）

```
Webhook Trigger (n8n-nodes-base.webhook)
  ↓
Extract Page ID (n8n-nodes-base.set)
  ↓
Get Notion Page (n8n-nodes-base.notion)
  ↓
Download Image (n8n-nodes-base.httpRequest)
  ↓
Upload to Google Drive (n8n-nodes-base.googleDrive)
  ↓
Share File (n8n-nodes-base.googleDrive)
  ↓
Create Direct Link (n8n-nodes-base.set)
  ↓
Create Video Task (n8n-nodes-base.httpRequest)
  ↓
Wait (n8n-nodes-base.wait) - 300秒待機
  ↓
Get Status (n8n-nodes-base.httpRequest)
  ↓
Check Status (n8n-nodes-base.if)
  ├─ [true]  → Extract Video URL (n8n-nodes-base.set)
  │              ↓
  │            Update Notion (n8n-nodes-base.notion) ❌ ここで終了（HTTPレスポンス未返却）
  │
  └─ [false] → Loop (n8n-nodes-base.noOp)
                 ↓
               Wait (ループバック)
```

**問題点**:
- Update NotionノードでデータフローがDEAD END
- **HTTPレスポンスを返すノードが存在しない**
- webhook呼び出し側は永遠にレスポンス待ち状態（6分以上経過）

### E2Eテストハング問題の証拠

**4つのテストすべてが同じパターンでハング**:
```bash
# テスト実行状況（2025-11-24 03:17時点）
63eb26: 6+ minutes running (00:41開始)
53bd10: 6+ minutes running (00:50開始)
2a727d: 6+ minutes running (01:10開始)
f24451: 6+ minutes running (02:04開始)
```

**共通パターン**:
- リクエスト送信: 47 bytes ✅
- レスポンス受信: 0 bytes ❌
- 待機時間: 6分以上（タイムアウトまで待ち続ける）

**curlの出力例**:
```
100    47    0     0    0    47      0      0 --:--:--  0:06:17 --:--:--     0
```
- `100 47` = 47バイト送信完了（JSONペイロード）
- `0 0 0 47` = 0バイト受信（HTTPレスポンスなし）
- `0:06:17` = 6分17秒経過（まだ待ち続けている）

---

## ✅ 修正後のフロー（正しい）

```
Webhook Trigger (n8n-nodes-base.webhook)
  ↓
Extract Page ID (n8n-nodes-base.set)
  ↓
Get Notion Page (n8n-nodes-base.notion)
  ↓
Download Image (n8n-nodes-base.httpRequest)
  ↓
Upload to Google Drive (n8n-nodes-base.googleDrive)
  ↓
Share File (n8n-nodes-base.googleDrive)
  ↓
Create Direct Link (n8n-nodes-base.set)
  ↓
Create Video Task (n8n-nodes-base.httpRequest)
  ↓                                             ↓
Webhook Response ✅ 【新規追加】          Wait (n8n-nodes-base.wait) - 300秒待機（バックグラウンド）
（taskIdを即座に返却、HTTP 200）              ↓
                                          Get Status (n8n-nodes-base.httpRequest)
                                              ↓
                                          Check Status (n8n-nodes-base.if)
                                            ├─ [true]  → Extract Video URL
                                            │              ↓
                                            │            Update Notion ✅ バックグラウンド完了
                                            │
                                            └─ [false] → Loop → Wait (ループバック)
```

**修正のポイント**:
1. **Create Video Taskノード直後**にWebhook Responseノードを挿入
2. Webhook Responseノードで**taskIdとステータスを即座に返却**（HTTP 200）
3. **Wait以降の処理はバックグラウンドで継続**（webhook呼び出し側は既に応答受信済み）

---

## 🔧 n8n UI経由の手動修正手順

### Step 1: n8n UIを開く

```
https://n8n-python-production-344b.up.railway.app
```

### Step 2: ワークフローを開く

- ワークフロー名: **WF10-Main: kie.ai Sora 2 ビデオ生成(Webhook Manual Trigger版)**
- ワークフローID: `kxKLB0EWlOhOjaOv`

### Step 3: Webhook Responseノードを追加

1. **キャンバス上で右クリック** → **Add Node**
2. **検索**: `Respond to Webhook`
3. **ノードタイプ**: `n8n-nodes-base.respondToWebhook`
4. **ノード名**: `Webhook Response` または `Return taskId`

### Step 4: Webhook Responseノードの設定

**Respond セクション**:
- **Respond With**: `Using Fields Below`
- **Response Code**: `200`
- **Response Body**:
  ```json
  {
    "success": true,
    "message": "Video generation started",
    "taskId": "={{ $json.taskId }}",
    "status": "processing",
    "estimatedTime": "4-5 minutes"
  }
  ```

**重要**:
- `$json.taskId` はCreate Video Taskノードから取得
- `status` は `"processing"` として返却（動画生成は非同期）

### Step 5: ノード接続の変更

**変更前**:
```
Create Video Task → Wait
```

**変更後**:
```
Create Video Task → Webhook Response
Create Video Task → Wait
```

**手順**:
1. Create Video Taskノードの**出力端点**から**Webhook Responseノード**にドラッグ接続
2. Create Video Taskノードの**出力端点**から**Waitノード**にもドラッグ接続（既存接続を維持）

**結果**:
- Create Video Taskノードは**2つの出力接続**を持つ（分岐）
- 1つ目: Webhook Response（即座にHTTPレスポンス）
- 2つ目: Wait（バックグラウンド処理継続）

### Step 6: 保存

- 右上の **Save** ボタンをクリック
- ワークフローが **Active** 状態（トグルON）であることを確認

---

## 🧪 修正後の期待される動作

### データフロー（修正後）

```
curl POST /webhook/wf10-notion-trigger
  ↓
Webhook Trigger: { page_id: "2b368d5c2986811f87ecf2aecaedf1cf" }
  ↓
Extract Page ID → Get Notion Page → Download Image → Upload to Google Drive → Share File → Create Direct Link
  ↓
Create Video Task: POST /api/v1/jobs/createTask
  → response: { code: 200, data: { taskId: "xxx", recordId: "xxx" } }
  ↓                                             ↓
Webhook Response ✅                        Wait (300s) - バックグラウンド
（即座に返却、~10-20秒）                         ↓
  ↓                                         Get Status: GET /api/v1/jobs/recordInfo?taskId=xxx
curl受信: HTTP 200 ✅                          ↓
{                                           Check Status: $json.data.state === "success"?
  "success": true,                            ├─ [false] → Loop → Wait (60s) → Get Status (繰り返し)
  "taskId": "xxx",                            └─ [true]  → Extract Video URL
  "status": "processing"                                     ↓
}                                                         Update Notion: 動画URL登録、ステータス更新 ✅
                                                          ↓
                                                       14/14ノード完走（100%）✅
```

### E2Eテストの期待結果

**Before（修正前）**:
```bash
$ curl -X POST ... /webhook/wf10-notion-trigger
# 6+ minutes waiting...（レスポンス未受信）
# テストタイムアウトまたはCtrl+C強制終了
```

**After（修正後）**:
```bash
$ curl -X POST ... /webhook/wf10-notion-trigger
# ~10-20秒でレスポンス受信 ✅
HTTP Status: 200
Total Time: 15.234s
{
  "success": true,
  "message": "Video generation started",
  "taskId": "95831dbabc8ee28a0c2c5ced28b99953",
  "status": "processing",
  "estimatedTime": "4-5 minutes"
}
```

**バックグラウンド実行**（ユーザーには見えない）:
```
Wait (300s) → Get Status → Check Status → ... → Update Notion
（4-5分後に完了）
```

---

## ✅ 検証手順

### 修正完了後のE2Eテスト

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"page_id": "2b368d5c2986811f87ecf2aecaedf1cf"}' \
  -w "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n" \
  https://n8n-python-production-344b.up.railway.app/webhook/wf10-notion-trigger
```

### 期待される結果

**即座のHTTPレスポンス**（~10-20秒）:
```json
HTTP Status: 200
Total Time: 15.234s
{
  "success": true,
  "message": "Video generation started",
  "taskId": "95831dbabc8ee28a0c2c5ced28b99953",
  "status": "processing",
  "estimatedTime": "4-5 minutes"
}
```

**バックグラウンド実行の確認**:
```bash
# n8n実行履歴を確認
# 期待結果: 4-5分後に14/14ノード完走（100%）
```

---

## 📝 技術的考察

### なぜこのバグが発生したか

1. **Webhook Responseノードの設定忘れ**: n8nワークフローの基本パターンを見落とした
2. **非同期処理の理解不足**: 長時間処理はバックグラウンドで実行し、即座にレスポンスを返す設計が必要
3. **テストの誤解**: ワークフロー実行成功 ≠ HTTPレスポンス受信成功

### 学んだこと

- ✅ **n8n webhookの基本**: Webhook Trigger → ... → **Webhook Response必須**
- ✅ **長時間処理の設計**: Create Video Task → Webhook Response（即座）+ Wait → ... (バックグラウンド)
- ✅ **分岐接続**: 1つのノードから複数の出力接続が可能（Create Video Task → Webhook Response + Wait）
- ✅ **E2Eテストの正しい理解**: HTTPレスポンス受信 ≠ ワークフロー完了（バックグラウンド実行を別途確認）

### 既存の修正との整合性

**前回の修正（Check Status、Extract Video URL）** ✅:
- これらの修正は**バックグラウンド実行部分**で有効
- Webhook Response追加後も引き続き必要

**Wait時間延長（300秒）** ✅:
- バックグラウンド実行での動画生成待機時間として有効
- Webhook Response追加後も引き続き必要

**統合的な効果**:
- Webhook Response: **即座のHTTPレスポンス**（E2Eテストハング問題解決）
- Wait 300秒: **バックグラウンドでの動画生成待機**（十分な時間確保）
- Check Status修正: **バックグラウンドでの完了検出**（state="success"判定）
- Extract Video URL修正: **バックグラウンドでの動画URL取得**（resultJson パース）

---

## 🚀 次のステップ

1. ✅ Webhook Responseノード追加手順書作成（本ドキュメント）
2. ⏳ n8n UIでWebhook Responseノードを追加
3. ⏳ E2Eテスト実行（即座のHTTPレスポンス受信確認）
4. ⏳ n8n実行履歴でバックグラウンド実行の完了確認（14/14ノード）
5. ⏳ Notionページに動画URL登録確認
6. ⏳ ハング中の4つのバックグラウンドプロセスを終了

---

## 📚 参考資料

- **n8n Webhook Response Node**: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/
- **n8n Webhook Workflow Pattern**: Webhook Trigger → Processing → Webhook Response → Background Processing
- **kie.ai API仕様**: 非同期タスクモデル（taskId返却 → ポーリングで完了確認）
- **ワークフロー構造分析結果**: 14ノード、Webhook Response欠落を確認

---

**ドキュメント保存先**: `now/2025-11-24_03-17_Webhook-Response追加手順書-E2Eテストハング問題解決.md`
