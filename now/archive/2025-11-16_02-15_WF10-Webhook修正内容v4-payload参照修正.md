# WF10-Webhook修正内容v4：payload参照修正とERRORハンドリング

**作成日時**: 2025-11-16 02:15:43 JST

## 🎯 修正履歴

### v1（初期バージョン）
- ✅ 基本的なwebhook受信とファイル保存機能

### v2（fs module修正）
- ✅ Node.js fs moduleをn8n Write Binary Fileノードに変更

### v3（2025-11-15 22:54作成）
- ✅ payload構造を理解してパース処理を追加
- ❌ **致命的バグ**: `$json.body.*` 参照が全て間違っている

### v4（2025-11-16 02:15作成）- このバージョン
- ✅ **payload参照を修正**: `$json.body.*` → `$json.*`
- ✅ **null-safe演算子追加**: `$json.payload?.video?.url` でERROR時の安全性確保

---

## 🐛 v3で発見された致命的バグ

### エラー症状

**実行履歴分析結果**:
- WF10-Main実行2487: 17:06:25成功（IN_QUEUEレスポンス取得）
- WF10-Webhook実行2488-2493: すべてERRORステータス（17:06-17:09）

**curlテスト結果**:
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf10-runway-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "request_id": "test-data-parse-fix",
    "payload": {
      "video": {
        "url": "https://example.com/test.mp4",
        "duration": 20,
        "width": 1920,
        "height": 1080
      }
    }
  }'

# 結果（2分後）
{"message":"Error in workflow"}
HTTP Status: 500
```

**ユーザー報告スクリーンショット**:
- "HTTP Request - Download Video" ノードエラー
- "URL parameter must be a string, got null"

### バグの根本原因

**問題コード（v3のSet - Payload Parseノード）**:
```json
{
  "id": "video_url",
  "name": "video_url",
  "value": "={{ $json.body.payload.video.url }}",  // ❌ WRONG
  "type": "string"
}
```

**根本原因**:
- n8n Webhook Triggerは受信したJSONを**直接`$json`に格納**
- `$json.body`という階層は存在しない
- したがって、`$json.body.status`、`$json.body.payload.video.url`等はすべて`undefined`となる

**正しいデータ構造**:
```
Webhook受信データ:
{
  "status": "completed",
  "request_id": "abc-123",
  "payload": {
    "video": {
      "url": "https://...",
      "duration": 10
    }
  }
}

n8n内部での参照:
$json.status              // ✅ "completed"
$json.request_id          // ✅ "abc-123"
$json.payload.video.url   // ✅ "https://..."

$json.body.status         // ❌ undefined
$json.body.payload        // ❌ undefined
```

**影響**:
- Set - Payload Parseノードで`video_url`が`undefined`（null）に
- HTTP Request - Download Videoノードが「URL parameter must be a string, got null」エラー
- ワークフロー全体が500エラーで失敗

---

## ✅ v4での修正内容

### 修正1: payload参照の完全修正

#### Before v3（間違った参照）
```json
{
  "assignments": [
    {
      "id": "video_url",
      "name": "video_url",
      "value": "={{ $json.body.payload.video.url }}",  // ❌
      "type": "string"
    },
    {
      "id": "status",
      "name": "status",
      "value": "={{ $json.body.status }}",  // ❌
      "type": "string"
    },
    {
      "id": "request_id",
      "name": "request_id",
      "value": "={{ $json.body.request_id }}",  // ❌
      "type": "string"
    },
    {
      "id": "duration",
      "name": "duration",
      "value": "={{ $json.body.payload.video.duration }}",  // ❌
      "type": "number"
    },
    {
      "id": "width",
      "name": "width",
      "value": "={{ $json.body.payload.video.width }}",  // ❌
      "type": "number"
    },
    {
      "id": "height",
      "name": "height",
      "value": "={{ $json.body.payload.video.height }}",  // ❌
      "type": "number"
    }
  ]
}
```

#### After v4（正しい参照 + null-safe）
```json
{
  "assignments": [
    {
      "id": "video_url",
      "name": "video_url",
      "value": "={{ $json.payload?.video?.url }}",  // ✅
      "type": "string"
    },
    {
      "id": "status",
      "name": "status",
      "value": "={{ $json.status }}",  // ✅
      "type": "string"
    },
    {
      "id": "request_id",
      "name": "request_id",
      "value": "={{ $json.request_id }}",  // ✅
      "type": "string"
    },
    {
      "id": "duration",
      "name": "duration",
      "value": "={{ $json.payload?.video?.duration }}",  // ✅
      "type": "number"
    },
    {
      "id": "width",
      "name": "width",
      "value": "={{ $json.payload?.video?.width }}",  // ✅
      "type": "number"
    },
    {
      "id": "height",
      "name": "height",
      "value": "={{ $json.payload?.video?.height }}",  // ✅
      "type": "number"
    }
  ]
}
```

### 修正2: null-safe演算子（`?.`）による安全性向上

**目的**: ERROR時に`payload.video`が存在しない場合でもエラーにならない

**ERRORレスポンス例**:
```json
{
  "status": "ERROR",
  "request_id": "abc-123",
  "payload": {
    "detail": "Could not load image from url: ..."
  }
}
```

この場合、`$json.payload.video`は存在しないが、`$json.payload?.video?.url`は`undefined`を返してエラーにならない。

**結果**:
- `video_url`: `undefined`（nullではないが、後続処理でスキップ可能）
- `status`: `"ERROR"`（正しく取得）
- `request_id`: `"abc-123"`（正しく取得）

---

## 📊 修正箇所一覧

| フィールド | v3（誤） | v4（正） |
|----------|---------|---------|
| video_url | `$json.body.payload.video.url` | `$json.payload?.video?.url` |
| status | `$json.body.status` | `$json.status` |
| request_id | `$json.body.request_id` | `$json.request_id` |
| duration | `$json.body.payload.video.duration` | `$json.payload?.video?.duration` |
| width | `$json.body.payload.video.width` | `$json.payload?.video?.width` |
| height | `$json.body.payload.video.height` | `$json.payload?.video?.height` |

**すべての参照**: `$json.body.*` → `$json.*`
**ネストされたpayload**: `?.` 演算子で安全にアクセス

---

## 📋 適用手順

### Step 1: 既存WF10-Webhookの削除
```
n8n UI → WF10-Webhook → 右上「⋮」→ Delete
```

### Step 2: 修正版v4のインポート
```
Workflows → + Add workflow → Import from file
→ now/2025-11-16_02-15_WF10-Webhook修正版v4-payload参照修正.json
```

### Step 3: 認証情報の確認
```
HTTP Request - Download Videoノードを開く
→ Credentials: 「fal」が設定されているか確認
```

### Step 4: ワークフローを保存して有効化
```
右上「Save」→ 「Active」スイッチをONに
```

### Step 5: 手動テスト（オプション）
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf10-runway-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "request_id": "manual-test-v4",
    "payload": {
      "video": {
        "url": "https://v3.fal.media/files/example/test.mp4",
        "duration": 10,
        "width": 1920,
        "height": 1080
      }
    }
  }'

# 期待される結果: HTTP 200 OK
# n8n実行履歴で成功確認
```

---

## 🧪 期待される動作（修正版v4）

### 1. completedステータス（成功時）

**fal.aiからのコールバック**:
```json
{
  "status": "completed",
  "request_id": "abc-123",
  "payload": {
    "video": {
      "url": "https://v3.fal.media/files/.../video.mp4",
      "duration": 10,
      "width": 1920,
      "height": 1080
    }
  }
}
```

**Set - Payload Parse処理後**:
- ✅ `video_url`: `"https://v3.fal.media/files/.../video.mp4"`（**nullではない**）
- ✅ `status`: `"completed"`
- ✅ `request_id`: `"abc-123"`
- ✅ `duration`: `10`
- ✅ `width`: `1920`
- ✅ `height`: `1080`

**HTTP Request - Download Video**:
- ✅ `$json.video_url`が有効なURLとして取得される
- ✅ 動画ダウンロード成功

**Write Binary File**:
- ✅ `/tmp/wf10-videos/abc-123.mp4`に保存成功

### 2. ERRORステータス（失敗時）

**fal.aiからのコールバック**:
```json
{
  "status": "ERROR",
  "request_id": "def-456",
  "payload": {
    "detail": "Could not load image from url: ..."
  }
}
```

**Set - Payload Parse処理後**:
- ✅ `video_url`: `undefined`（`payload.video`が存在しないためnull-safeで`undefined`）
- ✅ `status`: `"ERROR"`
- ✅ `request_id`: `"def-456"`
- ✅ `duration`: `undefined`
- ✅ `width`: `undefined`
- ✅ `height`: `undefined`

**HTTP Request - Download Video**:
- ⚠️ `$json.video_url`が`undefined`のため、URLエラーが発生
- **現状**: ワークフロー全体が失敗（エラー処理未実装）
- **今後の改善案**: Ifノードでstatusをチェックし、ERRORの場合はダウンロードをスキップ

---

## 🔄 次のステップ

### Task 10d-4: v2c+v4でのE2Eテスト実行
- ✅ **v4インポート＆有効化**
- ✅ **v2c（WF10-Main with Google Drive URL）インポート**
- ⏳ **WF10-Main v2c実行**
  - fal.ai APIにリクエスト送信（Google Drive画像URL使用）
  - IN_QUEUEレスポンス取得確認
- ⏳ **fal.ai処理待機（1-3分）**
- ⏳ **WF10-Webhook v4コールバック受信確認**
  - statusが`"completed"`（**ERRORではない**）
  - video_urlが実際のfal.ai URLを含む（**nullではない**）
  - 動画ダウンロード成功
  - `/tmp/wf10-videos/`にファイル保存確認
- ⏳ **動画再生確認**（10秒、1920x1080）

### Task 11: Phase 0-MVP検証（10回テスト）
- E2Eテスト成功後、10回連続実行
- 成功率を記録（目標: 9/10以上）

---

## 📚 参考情報

**バグ発見の経緯**:
1. ユーザーからスクリーンショット報告：「URL parameter must be a string, got null」
2. 実行履歴分析：実行2488-2493がすべてERROR
3. curlテスト実行：500エラー、`{"message":"Error in workflow"}`
4. v3 JSON読み込み：`$json.body.*`参照を発見
5. 根本原因特定：Webhook Triggerは`$json`に直接格納（`$json.body`は存在しない）

**v3とv4の比較**:
- v3: すべてのpayload参照が`$json.body.*`（間違い）
- v4: すべてのpayload参照が`$json.*`（正しい） + null-safe演算子

**null-safe演算子の効果**:
- ERROR時に`payload.video`が存在しない場合も安全に処理
- `undefined`を返してエラーを回避
- 後続のエラーハンドリング実装の基盤を提供

**今後の改善案**:
- Ifノードでstatusをチェック
- completedブランチ: 動画ダウンロード＆保存
- ERRORブランチ: エラーログ出力のみ（ダウンロードスキップ）

---

**作成者**: Claude Code (SuperClaude)
**対応Issue**: WF10-Webhook v3 payload参照バグ（$json.body誤参照）
**エビデンス**: 実行履歴2488-2493、curlテスト500エラー、ユーザースクリーンショット
