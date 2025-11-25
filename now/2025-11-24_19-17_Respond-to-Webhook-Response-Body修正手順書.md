# WF10 Respond to Webhook Response Body修正手順書

**作成日時**: 2025-11-24 19:16:57 JST
**対象ワークフロー**: WF10-Main: kie.ai Sora 2 ビデオ生成 (ID: kxKLB0EWlOhOjaOv)
**修正対象ノード**: Respond to Webhook (ID: 84a63b13-c451-4548-bcd6-a52b80360f02)

---

## 🎯 修正目的

E2Eテストが8秒でHTTP 200を返すが、レスポンスボディが空の問題を解決する。

---

## 🚨 根本原因の確定

### E2Eテスト結果（2025-11-24 19:13実行）

**ファイル**: `now/2025-11-24_19-13_e2e-test-after-webhook-response-node.txt`

```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100    47    0     0  100    47      0     34  0:00:01  0:00:01 --:--:--    34
...（略）...
100    47    0     0  100    47      0      5  0:00:09  0:00:08  0:00:01     0

HTTP Status: 200
Total Time: 8.340138s
```

**重要な発見**:
- `% Received` が最後まで `0` → **レスポンスボディが完全に空**
- HTTP Status: 200 ✅ → ノードは実行されている
- Total Time: 8.34秒 ✅ → 即座にレスポンス（6分ハングは解消）

### Respond to Webhookノードの現在の設定（誤り）

**ワークフロー構造取得結果**（`n8n_get_workflow`）:

```javascript
{
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ $json.data.taskId }}", // ❌ 誤り！taskIdのみ
    "options": {}
  },
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1.4,
  "position": [1824, 48],
  "id": "84a63b13-c451-4548-bcd6-a52b80360f02",
  "name": "Respond to Webhook"
}
```

**問題点**:
- `responseBody` が単一値 `$json.data.taskId` を返すだけ
- n8nはこれを有効なJSONとして解釈できず、空レスポンスを返している
- 正しいフォーマット: 完全なJSONオブジェクト `{ success, message, taskId, status, estimatedTime }`

---

## ✅ 正しい設定（修正後）

### Response Body（修正版）

```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $json.data.taskId,
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

**変更箇所**:
- ❌ `"={{ $json.data.taskId }}"` （単一値）
- ✅ `"={{ { ... } }}"` （完全なJSONオブジェクト）

**重要**:
- n8n式では `{{ }}` の中でJavaScriptオブジェクトリテラルを使用
- `$json.data.taskId` は引用符なしでそのまま埋め込む（文字列ではなく値として）
- 最外の `"={{ ... }}"` は必須（n8nパラメータの形式）

---

## 🔧 n8n UI経由の手動修正手順

### Step 1: n8n UIを開く

```
https://n8n-python-production-344b.up.railway.app
```

### Step 2: ワークフローを開く

- ワークフロー名: **WF10-Main: kie.ai Sora 2 ビデオ生成(Webhook Manual Trigger版)**
- ワークフローID: `kxKLB0EWlOhOjaOv`

### Step 3: Respond to Webhookノードをクリック

- キャンバス上の "Respond to Webhook" ノードをクリック
- 右側にノード設定パネルが開く

### Step 4: Response Bodyフィールドを修正

**現在の値**（誤り）:
```
={{ $json.data.taskId }}
```

**新しい値**（正しい）:
```
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $json.data.taskId,
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

**入力手順**:
1. Response Body フィールドをクリック
2. 既存の内容を全選択（Cmd+A / Ctrl+A）
3. 削除（Delete / Backspace）
4. 上記の新しい値を貼り付け
5. フィールド外をクリックして確定

### Step 5: 保存

- 右上の **Save** ボタンをクリック
- ワークフローが **Active** 状態（トグルON）であることを確認

---

## 🧪 修正後の検証手順

### E2Eテスト実行

```bash
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $json.data.taskId,
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

### 期待される結果

**即座のHTTPレスポンス**（~8-10秒）:
```json
HTTP Status: 200
Total Time: 8-10s

{
  "success": true,
  "message": "Video generation started",
  "taskId": "95831dbabc8ee28a0c2c5ced28b99953",
  "status": "processing",
  "estimatedTime": "4-5 minutes"
}
```

**curlの出力で確認**:
- `% Received` が **0以外** （例: 100 174）
- レスポンスボディにJSON文字列が表示される

---

## 📊 修正前後の比較

### 修正前（問題あり）

**テスト結果**:
```
100    47    0     0  100    47  ← % Received = 0（空レスポンス）
HTTP Status: 200
Total Time: 8.340138s
（レスポンスボディなし）
```

**設定**:
```javascript
"responseBody": "={{ $json.data.taskId }}" // 単一値のみ
```

### 修正後（期待）

**テスト結果**:
```
100   174  100   127  100    47  ← % Received = 127（JSONレスポンス）
HTTP Status: 200
Total Time: 8-10s
{
  "success": true,
  "message": "Video generation started",
  "taskId": "95831dbabc8ee28a0c2c5ced28b99953",
  "status": "processing",
  "estimatedTime": "4-5 minutes"
}
```

**設定**:
```javascript
"responseBody": "={{ {
  \"success\": true,
  \"message\": \"Video generation started\",
  \"taskId\": $json.data.taskId,
  \"status\": \"processing\",
  \"estimatedTime\": \"4-5 minutes\"
} }}" // 完全なJSONオブジェクト
```

---

## 📝 技術的考察

### なぜ空レスポンスが返されたか

1. **n8nのJSON検証**: Respond to Webhookノードは `respondWith: "json"` の場合、Response Bodyが有効なJSONオブジェクトであることを期待
2. **単一値の問題**: `$json.data.taskId` は文字列値であり、JSONオブジェクトではない
3. **n8nの動作**: 無効なJSONフォーマットを検出すると、空レスポンスを返す（エラーではなく）

### 学んだこと

- ✅ **JSONレスポンスの正しい形式**: n8n式 `={{ {...} }}` で完全なJSONオブジェクトを構築
- ✅ **変数の埋め込み方**: `"taskId": $json.data.taskId`（引用符なし）で値を直接埋め込む
- ✅ **検証の重要性**: Response Bodyの内容を必ず確認（単一値ではなくオブジェクト）

### MCP Tool制約

**n8n_update_partial_workflowの制約**:
- 今回のようなパラメータ修正では常に `"request/body must NOT have additional properties"` エラー
- 根本原因: MCP toolのバグまたはn8n API仕様の未対応
- 回避策: 手動UI編集のみ

---

## 🚀 次のステップ

1. ✅ Response Body修正手順書作成（本ドキュメント）
2. ⏳ n8n UIでResponse Bodyフィールドを修正
3. ⏳ E2Eテスト実行（修正後の検証）
4. ⏳ JSONレスポンス受信確認
5. ⏳ バックグラウンド実行の完了確認（15/15ノード）
6. ⏳ Notionページに動画URL登録確認
7. ⏳ ハング中の4つのバックグラウンドプロセスを終了

---

## 📚 参考資料

- **n8n Respond to Webhook Node**: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/
- **n8n式（Expressions）**: https://docs.n8n.io/code/expressions/
- **JSONオブジェクトリテラル**: JavaScriptの標準構文 `{ key: value, ... }`
- **前回の手順書**: `now/2025-11-24_03-17_Webhook-Response追加手順書-E2Eテストハング問題解決.md`（Response Body例）

---

**ドキュメント保存先**: `now/2025-11-24_19-17_Respond-to-Webhook-Response-Body修正手順書.md`
