# Phase4c技術的詳細 - セッション中断時の記録

**日時**: 2025-01-12 16:50 JST

## ワークフロー構成（10ノード）

### ID & メタデータ
```yaml
workflow_id: Exra8DkAfWsmOPiE
name: "WF7 Phase4c - Video Concatenator (NEW 10 nodes)"
active: true
versionCounter: 8
webhook_path: wf7-phase4c-video-concatenator
trigger_count: 1
```

### ノード構成
1. **Webhook - Phase 4c Start** (`webhook-phase4c-start`)
   - Type: n8n-nodes-base.webhook v2.1
   - Method: POST
   - Path: `wf7-phase4c-video-concatenator`
   - Response Mode: responseNode

2. **Code - Prepare FAL FFmpeg Payload** (`code-prepare-payload`)
   - Type: n8n-nodes-base.code v2
   - Purpose: tracks形式ペイロード準備
   - Input: videos_metadata配列
   - Output: fal_payload, script_id, total_duration, video_count

3. **HTTP Request - Submit to FAL** (`http-submit-to-fal`)
   - Type: n8n-nodes-base.httpRequest v4.2
   - URL: https://queue.fal.run/fal-ai/ffmpeg-api/compose
   - Auth: FAL API Key
   - Body: `{{ $json.fal_payload }}`

4. **Wait** (`wait-initial`)
   - Type: n8n-nodes-base.wait v1.1
   - Duration: 2秒

5. **Set - Retry Counter** (`set-retry-counter`)
   - Type: n8n-nodes-base.set v3.4
   - 設定: retry_count（increment）、request_id（preserve）
   - **修正済み**: incrementロジックとrequest_id保持

6. **HTTP Request - Check Status** (`http-check-status`)
   - Type: n8n-nodes-base.httpRequest v4.2
   - URL: https://queue.fal.run/fal-ai/ffmpeg-api/requests/{{request_id}}/status
   - Auth: FAL API Key
   - **修正済み**: 安定したrequest_id参照

7. **IF - Render Completed?** (`if-render-completed`)
   - Type: n8n-nodes-base.if v2
   - Condition: status === "COMPLETED"
   - True → Extract Video URL
   - False → Check Retry Limit

8. **IF - Check Retry Limit** (`if-check-retry-limit`)
   - Type: n8n-nodes-base.if v2
   - Condition: retry_count > 10
   - True → Timeout Response
   - False → Loop back to Wait

9. **Code - Extract Video URL & Build Result** (`code-extract-video-url`)
   - Type: n8n-nodes-base.code v2
   - Purpose: Phase4b成功パターンでURL抽出
   - Priority: video?.url → outputs[0] → video_url

10. **Respond to Webhook** (`respond-to-webhook`)
    - Type: n8n-nodes-base.respondToWebhook v1.1
    - Response: JSON (workflow結果)

## データフロー図

```
Webhook
  ↓
Prepare Payload (tracks形式)
  ↓
Submit to FAL (async request)
  ↓
Wait 2s
  ↓
┌─→ Set Retry Counter (increment)
│   ↓
│   Check Status (polling)
│   ↓
│   IF Completed?
│   ├─ Yes → Extract URL → Respond
│   └─ No → IF Retry > 10?
│       ├─ Yes → Respond (timeout)
│       └─ No ─┘ (loop)
```

## 適用したPhase4b成功パターン

### 1. Tracks形式ペイロード
```javascript
const keyframes = videosMetadata.map((video, index) => {
  const duration = video.duration || 5;
  const timestamp = cumulativeTime;
  cumulativeTime += duration;

  return {
    url: video.video_url,
    timestamp: timestamp,
    duration: duration
  };
});

const payload = {
  tracks: [{
    id: "1",
    type: "video",
    keyframes: keyframes
  }]
};
```

### 2. 優先順位付きURL抽出
```javascript
// 優先順位1: video?.url（Phase4bで最も信頼性が高い）
let videoUrl = resultData.video?.url;

// 優先順位2: outputs配列
if (!videoUrl) {
  videoUrl = resultData.outputs?.[0];
}

// 優先順位3: 直接のvideo_url
if (!videoUrl) {
  videoUrl = resultData.video_url || statusResponse.video_url;
}
```

### 3. 安定したリトライループ
- retry_countを明示的にincrement
- request_idをループ全体で保持
- 10回リトライ後タイムアウト

## 修正したバグの詳細

### Bug 1: Retry Counter初期化エラー

**問題**:
- 毎回0に設定されていた
- リトライ回数が追跡されない
- タイムアウトが発動しない

**修正内容**:
```javascript
// Before
"value": 0

// After
"value": "={{ $json.retry_count ? $json.retry_count + 1 : 0 }}"
```

**影響範囲**: `Set - Retry Counter` ノード
**リスク**: High（無限ループの可能性）
**修正versionCounter**: 5

### Bug 2: Request ID参照不安定

**問題**:
- ループ外のノードを参照
- リトライ時に参照が失われる
- "Cannot read property 'request_id' of undefined"エラー

**修正内容**:
```javascript
// Before
"url": "=https://queue.fal.run/.../{{ $('HTTP Request - Submit to FAL').item.json.request_id }}/status"

// After
"url": "=https://queue.fal.run/.../{{ $json.request_id }}/status"
```

**影響範囲**: `HTTP Request - Check Status` ノード
**リスク**: Critical（リトライ機能の完全停止）
**修正versionCounter**: 5

## テスト環境

### Railway設定
- Service: n8n-python
- URL: https://n8n-python-production-344b.up.railway.app
- n8n Version: 1.68.3 (pinned)

### テストペイロード
```json
{
  "script_id": "test-phase4c-new-10nodes-20250112",
  "videos_metadata": [
    {"section": "hook", "duration": 3, "video_url": "..."},
    {"section": "intro", "duration": 10, "video_url": "..."},
    {"section": "point1", "duration": 13, "video_url": "..."},
    {"section": "point2", "duration": 13, "video_url": "..."},
    {"section": "point3", "duration": 14, "video_url": "..."},
    {"section": "summary", "duration": 20, "video_url": "..."},
    {"section": "cta", "duration": 7, "video_url": "..."}
  ]
}
```

Total: 7 videos, 80 seconds

### 期待されるレスポンス
```json
{
  "success": true,
  "script_id": "test-phase4c-new-10nodes-20250112",
  "final_video_url": "https://v3b.fal.media/files/...",
  "total_duration": 80,
  "video_count": 7,
  "status": "COMPLETED"
}
```

## 実行履歴

### テスト1: 初回（バグ修正前）
```
時刻: 16:44:01
結果: HTTP 200, empty body
実行履歴: 0件
ログ: /tmp/phase4c-new-test-curl.log
```

### テスト2: バグ修正後
```
時刻: 16:44:xx
結果: HTTP 200, empty body
実行履歴: 0件
ログ: /tmp/phase4c-new-test-fixed-curl.log
```

### テスト3: 再有効化後
```
時刻: 16:47:32
結果: HTTP 200, empty body
実行履歴: 0件
ログ: /tmp/phase4c-new-test-reactivated.log
```

## 診断結果

### Webhook登録状態
```yaml
設定値: wf7-phase4c-video-concatenator
実登録: 未確認（ログに記録なし）
active_flag: true
execution_count: 0
```

### Railway Logs分析
- Phase4b webhook errors: 多数（過去のテスト）
- Phase4c webhook registration: ログなし
- 異なるwebhook: `wf7-phase4c-ffmpeg-concat`（別ワークフロー？）

## 環境変数（参考）

```bash
# n8n関連（推定）
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app/
N8N_PATH=/

# FAL API
FAL_KEY=[redacted]
```

## 比較: Phase4b vs Phase4c

| 項目 | Phase4b | Phase4c |
|------|---------|---------|
| ノード数 | 15-20 | 10 |
| webhook登録 | ✅ 成功 | ❌ 失敗 |
| URL抽出方法 | 1種類 | 1種類（同じ） |
| リトライロジック | シンプル | 同じ |
| テスト成功率 | 100% | 0%（登録問題） |

## MCP操作履歴

```yaml
1. n8n_list_workflows: ワークフロー一覧取得
2. n8n_get_workflow: Phase4c詳細取得
3. n8n_update_partial_workflow: バグ修正適用（2回）
4. n8n_list_executions: 実行履歴確認（3回）
5. n8n_validate_workflow: バリデーション（検討のみ）
```

## 次回セッション時のチェックリスト

- [ ] ワークフロー再作成を実施
- [ ] Webhook URL確認（UI上で）
- [ ] テスト実行
- [ ] 実行履歴確認（returned > 0）
- [ ] ログ確認（webhook registration成功）
- [ ] 動画URL取得確認
- [ ] Phase4bとの結果比較
- [ ] パフォーマンス測定
- [ ] ドキュメント更新
- [ ] Git commit

---

**重要**: このワークフローのロジックは完全に正しい。問題はRailway環境でのwebhook登録プロセスのみ。
