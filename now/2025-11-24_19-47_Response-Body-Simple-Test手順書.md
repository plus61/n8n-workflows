# WF10 Response Body シンプルテスト手順書

**作成日時**: 2025-11-24 19:47:00 JST
**対象ワークフロー**: WF10-Main: kie.ai Sora 2 ビデオ生成 (ID: kxKLB0EWlOhOjaOv)
**修正対象ノード**: Respond to Webhook (ID: 84a63b13-c451-4548-bcd6-a52b80360f02)

---

## 🎯 テスト目的

データ参照（`$json.data.taskId`）を除外した**シンプルなJSON**でResponse Bodyが正しく返されるかを検証する。

---

## 🔍 現状分析

### 現在の設定（データ参照あり）
```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $json.data.taskId,  // ← データ参照
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

### テスト結果
- ✅ HTTP Status: 200（7.52秒）
- ❌ Response Body: 空（`% Received 0`）

### 仮説
Respond to Webhookノードが**Create Video Taskノードのデータ**を正しく参照できていない可能性。分岐フローでのデータ伝播に問題がある。

---

## 🧪 シンプルテスト：データ参照なし

### Step 1: n8n UIを開く

```
https://n8n-python-production-344b.up.railway.app
```

### Step 2: Respond to Webhookノードを開く

- ワークフロー: **WF10-Main: kie.ai Sora 2 ビデオ生成(Webhook Manual Trigger版)**
- ノード名: **Respond to Webhook**

### Step 3: Response Bodyをシンプルなテスト値に変更

**現在の値**（データ参照あり）:
```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $json.data.taskId,
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

**テスト値**（データ参照なし）:
```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "status": "processing"
} }}
```

**変更手順**:
1. Response Body フィールドをクリック
2. 既存の内容を全選択（Cmd+A / Ctrl+A）
3. 削除
4. 上記の**テスト値**を貼り付け
5. フィールド外をクリックして確定

### Step 4: 保存＆再起動

1. 右上の **Save** ボタンをクリック
2. **Active** トグルを **OFF** にする（2-3秒待つ）
3. 再び **ON** にする

---

## ✅ 期待される結果

### シンプルテストが成功する場合

**E2Eテスト結果**:
```
HTTP Status: 200
Total Time: 7-10s

{
  "success": true,
  "message": "Video generation started",
  "status": "processing"
}
```

**結論**: データ参照（`$json.data.taskId`）が問題の原因。

**次のステップ**: 明示的なノード参照に修正
```javascript
={{ {
  "success": true,
  "message": "Video generation started",
  "taskId": $('Create Video Task').item.json.data.taskId,  // ← 明示的参照
  "status": "processing",
  "estimatedTime": "4-5 minutes"
} }}
```

---

### シンプルテストも失敗する場合

**E2Eテスト結果**:
```
HTTP Status: 200
Total Time: 7-10s
（Response Body: 空）
```

**結論**: Response Bodyの式評価そのものに問題がある。

**次のステップ**: さらにシンプルな固定値テスト
```javascript
{ "test": "success" }
```
（n8n式 `={{ }}` を使わない）

---

## 🔄 テスト実行コマンド

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"page_id": "2b368d5c2986811f87ecf2aecaedf1cf"}' \
  -w "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n" \
  https://n8n-python-production-344b.up.railway.app/webhook/wf10-notion-trigger
```

---

## 📊 デバッグ手順（テスト失敗時）

### 1. n8n実行履歴を確認

1. n8n UIで **Executions** タブを開く
2. 最新の実行を確認
3. Respond to Webhookノードをクリック
4. 出力データを確認（エラーメッセージがあるか）

### 2. Respond to Webhookノードのログ確認

- ノード実行時のエラーメッセージ
- データ型の不一致
- 式評価エラー

### 3. Webhook Triggerの設定再確認

**必須設定**:
```javascript
{
  "responseMode": "responseNode"  // ← 必須
}
```

これが `"lastNode"` や `"firstEntryNode"` になっていると、Respond to Webhookノードが無視されます。

---

## 📝 記録フォーマット

テスト完了後、以下を `CURRENT_STATE.md` に追記してください：

```markdown
## 2025-11-24 19:50 - Response Body シンプルテスト

### テスト結果
- ✅/❌ シンプルなJSON（データ参照なし）: [結果]
- HTTP Status: [200/500]
- Response Body: [空/JSON受信]

### 結論
- [データ参照が問題 / 式評価そのものが問題 / その他]

### 次のアクション
- [明示的ノード参照に修正 / 固定値テスト / Railway環境確認]
```

---

**ドキュメント保存先**: `now/2025-11-24_19-47_Response-Body-Simple-Test手順書.md`
