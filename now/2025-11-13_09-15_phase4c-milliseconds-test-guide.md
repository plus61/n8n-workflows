# WF7 Phase4c - ミリ秒修正版テストガイド

**作成日時**: 2025-11-13 09:15:42 JST

## 修正内容

### 問題
- 生成された動画が0.28秒しかない（期待値：80秒）
- 原因：FAL FFmpeg APIはtimestampとdurationを**ミリ秒単位**で要求するが、コードは**秒単位**で送信していた

### 修正
**ファイル**: Code - Prepare FAL FFmpeg Payload ノード

```javascript
// 修正前（秒単位）
return {
  url: videoUrl,
  timestamp: timestamp,
  duration: duration
};

// 修正後（ミリ秒単位）
return {
  url: videoUrl,
  timestamp: timestamp * 1000,  // FIX: 秒→ミリ秒変換
  duration: duration * 1000      // FIX: 秒→ミリ秒変換
};
```

### デプロイ情報
- ワークフロー: `mfRdJJFJRKmeBjKv`
- 名前: "WF7 Phase4c - Video Concatenator (Milliseconds Fixed)"
- バージョン: 61
- 更新日時: 2025-11-13T00:15:25.965Z

## テスト手順

### 1. n8n UIでワークフローをアクティブ化

1. n8n UIを開く: https://n8n-python-production-344b.up.railway.app
2. "WF7 Phase4c - Video Concatenator (Milliseconds Fixed)" を開く
3. 「Execute workflow」ボタンをクリック（Webhookをアクティブ化）

### 2. Webhookにテストデータを送信

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-phase4c-video-concatenator \
  -H "Content-Type: application/json" \
  -d @/tmp/phase4c-test-payload-fal-urls.json \
  -w "\n\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n"
```

**期待される応答時間**: 12秒前後（10秒Wait + FAL API処理）

### 3. レスポンス確認

期待されるレスポンス:
```json
{
  "success": true,
  "script_id": "test-phase4c-with-fal-urls",
  "final_video_url": "https://v3b.fal.media/files/...",
  "thumbnail_url": "https://v3b.fal.media/files/...",
  "total_duration": 80,
  "video_count": 7,
  "status": "COMPLETED"
}
```

### 4. 生成された動画を確認

```bash
# 動画をダウンロード
VIDEO_URL="<final_video_url from response>"
curl -o /tmp/phase4c-result-fixed.mp4 "$VIDEO_URL"

# 動画の長さを確認
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /tmp/phase4c-result-fixed.mp4
```

**期待される動画の長さ**: **約80秒**

### 5. 実行ログの詳細確認

```bash
# 最新の実行IDを取得して詳細を確認
EXECUTION_ID="<latest execution id>"
```

n8n MCPで確認:
```javascript
mcp__n8n-mcp__n8n_get_execution({
  id: "<execution_id>",
  mode: "filtered",
  itemsLimit: 5
})
```

確認ポイント：
- "Code - Prepare FAL FFmpeg Payload" の出力
  - `keyframes[0].timestamp`: 0 (0秒 = 0ミリ秒)
  - `keyframes[0].duration`: **3000** (3秒 = 3000ミリ秒) ← これが重要！
  - `keyframes[1].timestamp`: **3000** (3秒 = 3000ミリ秒)
  - `keyframes[1].duration`: **10000** (10秒 = 10000ミリ秒)
  - 以降も同様にミリ秒単位になっていることを確認

## テストデータ

**ファイル**: `/tmp/phase4c-test-payload-fal-urls.json`

```json
{
  "pageId": "test-phase4c-with-fal-urls",
  "videos": [
    {"url": "https://v3b.fal.media/files/b/monkey/ErYQSu7MBuZB7NBS-3-_J_output.mp4", "duration": 3},
    {"url": "https://v3b.fal.media/files/b/zebra/TL6NZ5rSbpAZRT4P8IA0C_output.mp4", "duration": 10},
    {"url": "https://v3b.fal.media/files/b/penguin/j1KJr6fbJYTxTZkTIjLlS_output.mp4", "duration": 13},
    {"url": "https://v3b.fal.media/files/b/panda/lGTFA7_HybUaGORhadu0g_output.mp4", "duration": 13},
    {"url": "https://v3b.fal.media/files/b/monkey/TbW1zMlq-vfVL6fHGt-Lv_output.mp4", "duration": 14},
    {"url": "https://v3b.fal.media/files/b/zebra/jU_MCQ884eXvR9-nVVA4y_output.mp4", "duration": 20},
    {"url": "https://v3b.fal.media/files/b/zebra/WammM1aF25B-8q6Q6t-mJ_output.mp4", "duration": 7}
  ]
}
```

**合計**: 7本の動画、合計80秒

## 成功基準

✅ **全ての条件を満たす必要があります**:

1. Webhook実行が成功（HTTP 200 OK）
2. レスポンスに `final_video_url` が含まれる
3. 生成された動画の長さが **約80秒**
4. 実行ログで keyframes の timestamp と duration が**ミリ秒単位**（1000倍された値）

## トラブルシューティング

### 404 Error: Webhook not registered
- n8n UIで「Execute workflow」ボタンをクリックしてWebhookをアクティブ化

### 動画の長さがまだ短い
- 実行ログで keyframes を確認
- timestamp と duration が1000倍されているか確認
- されていない場合：ワークフローが正しくデプロイされていない可能性

### タイムアウト
- Wait時間が10秒のため、合計12秒前後かかる
- curl のタイムアウトを30秒に設定（`--max-time 30`）

## 参考情報

### 修正前の問題データ（Execution #1895）

```json
{
  "keyframes": [
    {"url": "...", "timestamp": 0, "duration": 3},      // 秒単位（誤り）
    {"url": "...", "timestamp": 3, "duration": 10},     // 秒単位（誤り）
    {"url": "...", "timestamp": 13, "duration": 13}     // 秒単位（誤り）
  ]
}
```

結果: 動画の長さ = **0.28秒**

### 修正後の期待データ

```json
{
  "keyframes": [
    {"url": "...", "timestamp": 0, "duration": 3000},     // ミリ秒単位（正しい）
    {"url": "...", "timestamp": 3000, "duration": 10000}, // ミリ秒単位（正しい）
    {"url": "...", "timestamp": 13000, "duration": 13000} // ミリ秒単位（正しい）
  ]
}
```

期待結果: 動画の長さ = **約80秒**
