# WF10-Webhook修正内容v3：fal.ai payloadパース修正

**作成日時**: 2025-11-15 22:54:52 JST

## 🎯 修正履歴

### v1（22:37作成）- WF10-Main修正
- ✅ webhook URLをクエリパラメータ化（`?fal_webhook=...`）
- ✅ webhookコールバック到達成功（実行2422で確認）

### v2（22:46作成）- WF10-Main修正
- ✅ APIパラメータ名を正しい名前に修正
- ✅ duration値を許可範囲内に修正

### v3（22:54作成）- このバージョン - WF10-Webhook修正
- ✅ Set - Payload Parseノードのパス修正
- ✅ `$json.body.video.*` → `$json.body.payload.video.*`

---

## 🐛 発見された問題（実行2422以降の継続エラーから判明）

### 症状
- WF10-Main v2修正でAPIリクエストは成功するはずだが、WF10-Webhookが全実行で失敗
- 実行2422, 2423, 2424, 2426, 2427すべてエラー
- エラー内容：「URL parameter must be a string, got null」

### 根本原因

**WF10-Webhookの誤った実装**:
```javascript
// Set - Payload Parse node (BEFORE v3 - 誤り)
{
  "video_url": "={{ $json.body.video.url }}",  // ❌ video.urlが存在しない
  "duration": "={{ $json.body.video.duration }}"
}
```

**fal.ai Webhook実際のペイロード構造**（実行2422から確認）:
```json
{
  "status": "ERROR",
  "request_id": "35543bcb-ea17-44e5-ac57-c79eae821e60",
  "payload": {
    "detail": [...]
  }
}
```

成功時の構造（v2ドキュメントに記載）:
```json
{
  "status": "completed",
  "request_id": "...",
  "payload": {
    "video": {
      "url": "https://v3.fal.media/files/...",
      "duration": 10,
      "width": 1920,
      "height": 1080
    }
  }
}
```

**問題点の詳細**:
1. **パス階層の誤り**:
   - ❌ `$json.body.video.url` → videoオブジェクトは存在しない
   - ✅ `$json.body.payload.video.url` → 正しい階層

2. **エラー時の動作**:
   - ERROR statusの場合、`payload.video`が存在しない
   - Set nodeが`null`を返す
   - HTTP Request nodeがnullのURLでエラー

---

## ✅ 修正内容（v3）

### Set - Payload Parseノードの修正

#### Before v2以前（誤り）
```javascript
{
  "video_url": "={{ $json.body.video.url }}",      // ❌ 間違った階層
  "status": "={{ $json.body.status }}",             // ✅ 正しい
  "request_id": "={{ $json.body.request_id }}",     // ✅ 正しい
  "duration": "={{ $json.body.video.duration }}",   // ❌ 間違った階層
  "width": "={{ $json.body.video.width }}",         // ❌ 間違った階層
  "height": "={{ $json.body.video.height }}"        // ❌ 間違った階層
}
```

#### After v3（修正版）
```javascript
{
  "video_url": "={{ $json.body.payload.video.url }}",      // ✅ payload追加
  "status": "={{ $json.body.status }}",                     // 変更なし
  "request_id": "={{ $json.body.request_id }}",             // 変更なし
  "duration": "={{ $json.body.payload.video.duration }}",   // ✅ payload追加
  "width": "={{ $json.body.payload.video.width }}",         // ✅ payload追加
  "height": "={{ $json.body.payload.video.height }}"        // ✅ payload追加
}
```

**変更点**:
- すべての `$json.body.video.*` を `$json.body.payload.video.*` に変更
- `status`, `request_id`は変更なし（正しいパスだった）

---

## 📊 fal.ai Webhook Payload 正式仕様

**実行2422および公式ドキュメントから確定した構造**:

### 成功時（status: "completed"）
```json
{
  "status": "completed",
  "request_id": "uuid-string",
  "payload": {
    "video": {
      "url": "https://v3.fal.media/files/...",
      "duration": 10,
      "width": 1920,
      "height": 1080
    }
  }
}
```

### エラー時（status: "ERROR"）
```json
{
  "status": "ERROR",
  "request_id": "uuid-string",
  "error": "エラーメッセージ",
  "payload": {
    "detail": [
      {"loc": ["body", "field"], "msg": "エラー詳細"}
    ]
  }
}
```

**重要な構造**:
- ⚠️ **videoオブジェクトは`payload`の下にネストされている**
- ⚠️ **ERROR時は`payload.video`が存在しない**
- ✅ `status`と`request_id`は常にルートレベル

---

## 📋 適用手順

### Step 1: 既存WF10-Webhookの削除
```
n8n UI → WF10-Webhook → 右上「⋮」→ Delete
```

### Step 2: 修正版v3のインポート
```
Workflows → + Add workflow → Import from file
→ now/2025-11-15_22-54_WF10-Webhook修正版v3-payloadパース修正.json
```

### Step 3: 認証情報の確認
```
HTTP Request - Download Videoノードを開く
→ Credentials: 「fal.ai API Key」が設定されているか確認
```

### Step 4: ワークフローを保存＆有効化

### Step 5: WF10-Main v2のインポート（まだの場合）
```
既存WF10-Mainを削除
→ now/2025-11-15_22-46_WF10-Main修正版v2-正しいパラメータ名.json をインポート
→ Credentials確認＆保存
```

---

## 🧪 期待される動作（修正版v3）

### 1. WF10-Main v2実行
- ✅ HTTP Request nodeが成功（IN_QUEUE）
- ✅ 正しいAPIパラメータ送信
  - `image_url`: 画像URL
  - `prompt`: テキストプロンプト
  - `duration`: 10秒
  - `ratio`: "16:9"

### 2. fal.aiでの処理
- ⏳ **処理時間**: 通常1-3分（Turboモード）
- ✅ 10秒の動画が生成される
- ✅ 1920x1080（16:9比率）

### 3. WF10-Webhook v3へのコールバック
```json
{
  "status": "completed",
  "request_id": "...",
  "payload": {
    "video": {
      "url": "https://v3.fal.media/files/...",
      "duration": 10,
      "width": 1920,
      "height": 1080
    }
  }
}
```

### 4. WF10-Webhook v3の処理
- ✅ Set - Payload Parseが正しくパース
  - `video_url`: `$json.body.payload.video.url` から取得成功
  - `status`: "completed"
  - `request_id`: UUID
  - `duration`: 10
  - `width`: 1920
  - `height`: 1080
- ✅ HTTP Request - Download Videoが動画ダウンロード成功
- ✅ Write Binary Fileが `/tmp/wf10-videos/{request_id}.mp4` に保存成功

---

## ✅ 検証チェックリスト

### WF10-Webhook v3インポート後
- [ ] WF10-Webhook修正版v3インポート完了
- [ ] 認証情報（fal.ai API Key）が正しく設定されている
- [ ] ワークフローが有効化されている

### WF10-Main v2インポート後（まだの場合）
- [ ] WF10-Main修正版v2インポート完了
- [ ] 認証情報（fal.ai API Key）が正しく設定されている

### E2Eテスト実行
- [ ] WF10-Main v2テスト実行でIN_QUEUEレスポンス取得
- [ ] **1-3分以内にWF10-Webhook v3にコールバック到達**
- [ ] コールバックのstatusが "completed"
- [ ] Set - Payload Parseでvideo_urlが正しく取得（nullでない）
- [ ] 動画URL（`payload.video.url`）が含まれている
- [ ] WF10-Webhook v3が動画を正常にダウンロード
- [ ] `/tmp/wf10-videos/` に.mp4ファイルが存在
- [ ] 動画が再生可能（10秒、1920x1080）

---

## 🔄 次のステップ

### Task 9完了条件
- ✅ WF10-Main v2作成完了（22:46 JST）
- ✅ WF10-Webhook v3作成完了（22:54 JST）
- ⏳ **ユーザーがv2とv3をインポート＆テスト実行**
- ⏳ **E2Eテスト成功確認**

### Task 10: E2Eテスト実行
- WF10-Main v2実行 → webhookコールバック → 動画ダウンロード成功を確認
- **成功条件**: status=completed、動画URLあり、ファイル保存成功

### Task 11: Phase 0-MVP検証（10回テスト）
- E2Eテスト成功後、10回連続実行
- 成功率を記録（目標: 9/10以上）

---

## 📚 参考情報

**実行履歴**:
- 実行2422（v1使用）: 422エラー - パラメータ名誤り判明、webhookコールバック到達確認
- 実行2423-2427（v2以前）: WF10-Webhook payloadパース誤りで継続失敗

**判明した問題**:
1. v1: webhook URLがJSONボディ内 → クエリパラメータ必須
2. v2: APIパラメータ名誤り → 正しい名前（image_url, prompt）に修正
3. v3: WF10-Webhook payloadパース誤り → `payload.video.*`階層に修正

**fal.ai仕様**:
- Turboモデルは5秒または10秒のみサポート
- webhookコールバックは`payload`でラップされた構造

---

**作成者**: Claude Code (SuperClaude)
**対応Issue**: WF10-Webhook payloadパース誤り
**エビデンス**: 実行2422のwebhookペイロード、v2ドキュメント記載の期待構造
