# WF10 Response Body JSON構文エラー修正手順

**作成日時**: 2025-11-24 20:28:21 JST
**対象ワークフロー**: WF10-Main: kie.ai Sora 2 ビデオ生成 (ID: kxKLB0EWlOhOjaOv)
**修正対象ノード**: Respond to Webhook (ID: 84a63b13-c451-4548-bcd6-a52b80360f02)

---

## 🎯 根本原因の確定

### エラーメッセージ（n8n実行履歴より）

```
Invalid JSON in 'Response Body' field
Check that the syntax of the JSON in the 'Response Body' parameter is valid
```

**エラー発生ノード**: Respond to Webhook
**発生日時**: 2025/11/24 20:26:47

### スタックトレース
```
NodeOperationError: Invalid JSON in 'Response Body' field
    at ExecuteContext.execute (.../RespondToWebhook.node.ts:415:14)
    at WorkflowExecute.executeNode (.../workflow-execute.ts:1093:31)
```

---

## 🚨 問題の詳細

### 現在の設定（エラー）

```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $json.data.taskId,  // ❌ n8nがJSONとして評価できない
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

### なぜエラーが発生するか

1. **n8n式の評価タイミング**: `={{ }}` 内のJavaScriptオブジェクトは、まず**式として評価**されます
2. **`$json`の評価**: `$json.data.taskId`は変数として評価されますが、この時点で値が`undefined`または無効な形式の可能性
3. **JSON検証**: n8nは評価結果を**有効なJSONかどうか検証**します
4. **検証失敗**: `taskId`の値が不正なため、JSON全体が無効と判断される

### 根本原因

分岐フロー（Create Video Task → Wait + Respond to Webhook）において、Respond to Webhookノードが実行される時点で、`$json`が正しくCreate Video Taskの出力を参照できていない可能性があります。

---

## ✅ 修正方法（2つのオプション）

### オプション1：明示的なノード参照（推奨）

**最も確実な方法**です。分岐フローでも確実にデータを取得できます。

```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $('Create Video Task').item.json.data.taskId,  // ✅ 明示的参照
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

**利点**:
- 分岐フローでも確実にデータを取得
- エラーが発生しにくい
- 可読性が高い（どのノードからデータを取得しているか明確）

### オプション2：フォールバック値付き参照

```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $json.data?.taskId || "pending",  // ✅ Optional chaining + フォールバック
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

**利点**:
- データがない場合もエラーにならない
- デフォルト値で動作継続

**推奨**: **オプション1（明示的なノード参照）**を使用してください。

---

## 🔧 n8n UI経由の修正手順

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

**現在の値**（エラー）:
```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $json.data.taskId,
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

**新しい値**（推奨・オプション1）:
```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $('Create Video Task').item.json.data.taskId,
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

### Step 5: 保存＆再起動

1. 右上の **Save** ボタンをクリック
2. **Active** トグルを **OFF** にする（2-3秒待つ）
3. 再び **ON** にする

---

## 🧪 修正後の検証手順

### E2Eテスト実行

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"page_id": "2b368d5c2986811f87ecf2aecaedf1cf"}' \
  -w "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n" \
  https://n8n-python-production-344b.up.railway.app/webhook/wf10-notion-trigger
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
- n8n実行履歴でRespond to Webhookノードが**エラーなし**で完了

---

## 📊 修正前後の比較

### 修正前（Invalid JSON エラー）

**テスト結果**:
```
100    47    0     0  100    47  ← % Received = 0（空レスポンス）
HTTP Status: 200
Total Time: 9.613228s
（レスポンスボディなし）
```

**n8n実行履歴**:
```
❌ Respond to Webhook: Invalid JSON in 'Response Body' field
```

**設定**:
```javascript
"taskId": $json.data.taskId,  // ❌ JSON構文エラー
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

**n8n実行履歴**:
```
✅ Respond to Webhook: 正常完了
```

**設定**:
```javascript
"taskId": $('Create Video Task').item.json.data.taskId,  // ✅ 明示的参照
```

---

## 📝 技術的考察

### なぜ明示的なノード参照が必要か

1. **分岐フローの特性**: Create Video Taskノードが2つの出力（Wait + Respond to Webhook）を持つ場合、各出力ノードの`$json`コンテキストは独立
2. **データ伝播の制約**: 分岐後の各ノードは、直前のノードのデータを`$json`で参照できるが、分岐元のノードのデータは明示的に指定する必要がある
3. **n8nの実行モデル**: Respond to Webhookノードが実行される時点で、`$json`はCreate Video Taskではなく、**Webhook Triggerのデータ**を参照している可能性がある

### 学んだこと

- ✅ **分岐フローでのデータ参照**: `$('Node Name').item.json.path`で明示的に参照する
- ✅ **n8n式の検証**: Response Bodyは有効なJSONでなければならない
- ✅ **エラーメッセージの確認**: n8n実行履歴のエラー詳細を必ず確認する
- ✅ **Optional chaining**: `$json.data?.taskId`でundefinedエラーを防ぐ

---

## 🚀 次のステップ

1. ✅ JSON構文エラー修正手順書作成（本ドキュメント）
2. ⏳ n8n UIでResponse Bodyフィールドを修正（明示的ノード参照）
3. ⏳ E2Eテスト実行（修正後の検証）
4. ⏳ JSONレスポンス受信確認
5. ⏳ バックグラウンド実行の完了確認（15/15ノード）
6. ⏳ Notionページに動画URL登録確認
7. ⏳ ハング中の4つのバックグラウンドプロセスを終了

---

## 📚 参考資料

- **n8n Respond to Webhook Node**: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/
- **n8n式（Expressions）**: https://docs.n8n.io/code/expressions/
- **n8nノード参照**: `$('NodeName').item.json.path` 構文
- **Optional chaining**: JavaScriptの`?.`演算子（undefined安全アクセス）
- **エラー情報**: n8n実行履歴のOUTPUTタブ「Error details」セクション

---

**ドキュメント保存先**: `now/2025-11-24_20-28_Response-Body-JSON構文エラー修正手順.md`
