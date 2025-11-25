# WF10-Main修正内容：fal.ai webhook対応

**作成日時**: 2025-11-15 22:37:25 JST

## 🐛 問題の詳細

### 症状
- WF10-Mainを実行すると、fal.ai APIへのリクエストは成功（IN_QUEUEレスポンス取得）
- しかし、fal.aiからのwebhookコールバックがWF10-Webhookに到達しない
- 実行2393（22:05 JST）：40分以上経過してもコールバックなし
- 実行2407（22:22 JST）：9分以上経過してもコールバックなし

### 根本原因

**WF10-Mainの誤った実装**:
```json
{
  "url": "https://queue.fal.run/fal-ai/runway-gen3/turbo/image-to-video",
  "jsonBody": {
    "prompt_image": "...",
    "prompt_text": "...",
    "duration": 20,
    "ratio": "16:9",
    "webhook_url": "https://n8n-python-production-344b.up.railway.app/webhook/wf10-runway-webhook"  // ❌ JSONボディ内のwebhook_url
  }
}
```

**fal.ai REST APIの正しい仕様**:
- webhook URLは**クエリパラメータ**`fal_webhook`として渡す必要がある
- JSONリクエストボディ内の`webhook_url`は無視される

**参照**: fal.ai公式ドキュメント
```bash
curl --request POST \
  --url 'https://queue.fal.run/fal-ai/flux/dev?fal_webhook=https://url.to.your.app/api/fal/webhook' \
  --header "Authorization: Key $FAL_KEY" \
  --header 'Content-Type: application/json' \
  --data '{ "prompt": "..." }'
```

---

## ✅ 修正内容

### HTTP Request - Runway Gen-3 APIノード

#### Before（誤り）
```javascript
{
  "url": "https://queue.fal.run/fal-ai/runway-gen3/turbo/image-to-video",
  "jsonBody": "={{ {\n  \"prompt_image\": $json.画像素材URL[0],\n  \"prompt_text\": $json.台本本文,\n  \"duration\": 20,\n  \"ratio\": \"16:9\",\n  \"webhook_url\": \"https://n8n-python-production-344b.up.railway.app/webhook/wf10-runway-webhook\"\n} }}"
}
```

#### After（修正版）
```javascript
{
  "url": "https://queue.fal.run/fal-ai/runway-gen3/turbo/image-to-video?fal_webhook=https://n8n-python-production-344b.up.railway.app/webhook/wf10-runway-webhook",
  "jsonBody": "={{ {\n  \"prompt_image\": $json.画像素材URL[0],\n  \"prompt_text\": $json.台本本文,\n  \"duration\": 20,\n  \"ratio\": \"16:9\"\n} }}"
}
```

**変更点**:
1. ✅ **URLにクエリパラメータ追加**: `?fal_webhook=https://n8n-python-production-344b.up.railway.app/webhook/wf10-runway-webhook`
2. ✅ **JSONボディから`webhook_url`削除**: fal.aiが無視するパラメータを除去

---

## 📋 適用手順

### Step 1: 既存WF10-Mainの削除
1. n8n UIで「WF10-Main: Runway Gen-3 ビデオ生成（fal.ai Queue API）」を開く
2. 右上の「⋮」メニュー → 「Delete」を選択
3. 削除を確認

### Step 2: 修正版ワークフローのインポート
1. n8n UIで「Workflows」ページに移動
2. 右上の「+ Add workflow」 → 「Import from file」を選択
3. ファイル選択: `now/2025-11-15_22-37_WF10-Main修正版-fal-webhook対応.json`
4. インポート完了を確認

### Step 3: 認証情報の再設定
1. インポート後、「HTTP Request - Runway Gen-3 API」ノードを開く
2. Credentials: 「fal.ai API Key」が正しく設定されているか確認
3. 必要に応じて再選択・再保存

### Step 4: ワークフロー保存
1. 右上の「Save」ボタンをクリック
2. 保存完了を確認

---

## 🧪 テスト手順

### Step 5: 修正版ワークフローのテスト実行
```bash
# n8n UIで「Test workflow」をクリック
# または「Execute Workflow」を実行
```

**期待される動作**:
1. HTTP Request nodeが成功（IN_QUEUE）
2. Set - Response Parse nodeが成功
3. **1-3分後**: WF10-Webhookにfal.aiからコールバックが到達
4. WF10-Webhookの実行リストに新しいexecution（status=completed）が表示される

### Step 6: WF10-Webhookの確認
```bash
# n8n UIで「WF10-Webhook: Runway結果受信」の実行履歴を確認
# 新しいexecutionが自動的に作成されているはず
```

**コールバックペイロード例**:
```json
{
  "status": "completed",
  "request_id": "2fa9fa00-39f0-4f35-9616-40fbef566fb2",
  "payload": {
    "video": {
      "url": "https://v3.fal.media/files/...",
      "duration": 20,
      "width": 1920,
      "height": 1080
    }
  }
}
```

---

## 📊 検証チェックリスト

- [ ] WF10-Mainの修正版インポート完了
- [ ] 認証情報（fal.ai API Key）が正しく設定されている
- [ ] テスト実行でIN_QUEUEレスポンス取得
- [ ] 1-3分以内にWF10-Webhookにコールバック到達
- [ ] WF10-Webhookが正常に動画URLを保存（`/tmp/runway-videos/`）
- [ ] Task 8完了 → Task 9（E2Eテスト）へ進行可能

---

## 🔄 次のステップ

修正版テストが成功したら：
- **Task 9**: 修正後のE2Eテスト実行（1回）
- **Task 10**: Phase 0-MVP検証（10回テスト）

---

**作成者**: Claude Code (SuperClaude)
**対応Issue**: WF10 webhook到達問題
**参照**: fal.ai REST API Documentation
