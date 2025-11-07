# WF7 Phase4 - FAL API Video Rendering Status

## 📋 現在の状況 (2025-11-08)

### ワークフロー情報
- **Workflow ID**: `SDO8X6oR5W5y2s6A`
- **Workflow Name**: WF7 Phase4 - V2 Fixed
- **URL**: https://n8n-python-production-344b.up.railway.app/workflow/SDO8X6oR5W5y2s6A
- **Status**: Active
- **最終更新**: 2025-11-07T23:12:00.484Z

### 完了した修正

#### ✅ 1. ペイロード構築ノード (Node ID: `9f3272e3-7d13-4c0a-b2a2-684e62a2b642`)
**修正内容**: FAL API `/compose` エンドポイントが要求する `timestamp` と `duration` フィールドを追加

**修正済みコード**:
```javascript
// FAL API /compose エンドポイント用にペイロード構築
const scriptData = $('データ統合').item.json.scriptData;
const metadataItems = $input.all();
const articleId = $('データ統合').item.json.articleId;

// scriptDataのsegmentsからduration情報を取得
const segments = scriptData.segments || [];

// 各アセットからkeyframesを構築（timestampとdurationを追加）
let cumulativeTime = 0;
const keyframes = metadataItems.map((metaItem, index) => {
  const driveFileId = metaItem.json.driveFileId;
  const imageUrl = `https://drive.google.com/uc?export=download&id=${driveFileId}`;

  // 対応するセグメントのdurationを取得（デフォルトは5秒）
  const duration = segments[index]?.duration || 5;
  const timestamp = cumulativeTime;

  // 次のタイムスタンプ用に累積時間を更新
  cumulativeTime += duration;

  // FAL API /compose 形式: url, timestamp, duration
  return {
    url: imageUrl,
    timestamp: timestamp,
    duration: duration
  };
});

// FAL API /compose が期待するJSON構造
const videoJson = {
  tracks: [
    {
      id: "1",
      type: "video",
      keyframes: keyframes
    }
  ]
};

return {
  json: {
    json_string: JSON.stringify(videoJson),
    articleId: articleId
  }
};
```

**期待されるペイロード例**:
```json
{
  "tracks": [
    {
      "id": "1",
      "type": "video",
      "keyframes": [
        {
          "url": "https://drive.google.com/uc?export=download&id=1t3BFRFgHMLYhmfp9BobiNhdK3DlUhUaC",
          "timestamp": 0,
          "duration": 5
        },
        {
          "url": "https://drive.google.com/uc?export=download&id=1qyNTS3pX21H_EM6myRt9cvMBM5G1RDf7",
          "timestamp": 5,
          "duration": 5
        }
      ]
    }
  ]
}
```

#### ✅ 2. Get Image Result URL ノード (Node ID: `14d89d20-3adc-4438-b9e8-78fc0df9812e`)
**修正内容**: FAL API結果取得用の正しいエンドポイントURL

**正しいURL**:
```
=https://queue.fal.run/fal-ai/ffmpeg-api/compose/requests/{{ $json.request_id }}
```

**重要**:
- `/ffmpeg-api/compose` を使用（`/flux` ではない）
- 単一の等号 `=` で開始（`==` ではない）
- `request_id` を使用して手動でURL構築

### 🔍 既知の問題

#### API取得とUI表示の差異
- n8n MCP API経由で取得したワークフロー定義では、一部のノードで `==` が表示される
- UIでは正しく `=` として表示される
- この差異により、保存が必要な可能性がある

### ⏳ 保留中のタスク

1. **ワークフローの保存確認**
   - UIで修正内容が表示されている場合でも、明示的に保存ボタンをクリック
   - 保存により、API取得内容とUI表示内容の同期を確保

2. **新規テスト実行**
   - 最新のexecutionは #711 (error状態)
   - 修正後の新しいexecution (#712以降) がまだ作成されていない
   - UIから「Execute Workflow」ボタンで実行が必要

3. **動画生成成功の検証**
   - FAL APIから `video_url` が正常に返されることを確認
   - Google Driveへのアップロード成功を確認
   - Notion Hubへのメタデータ更新成功を確認

## 🧪 テストコマンド

### MCPツールを使用したテスト実行確認

```javascript
// 1. 最新のexecutionを確認
mcp__n8n-mcp__n8n_list_executions({
  workflowId: "SDO8X6oR5W5y2s6A",
  limit: 1
})

// 2. 特定のexecutionの詳細を取得
mcp__n8n-mcp__n8n_get_execution({
  id: "712", // 新しいexecution IDに置き換え
  mode: "summary" // または "full" for complete data
})

// 3. ワークフローの現在の状態を確認
mcp__n8n-mcp__n8n_get_workflow({
  id: "SDO8X6oR5W5y2s6A"
})
```

### Webhookトリガー（テストモード）

**注意**: テストモードは、n8nのUIで「Execute Workflow」を一度クリックしてwebhookをアクティブ化する必要があります。

```bash
# Webhookエンドポイント（現在404を返す - 手動実行が推奨）
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-video-script
```

**エラー例**:
```json
{
  "code": 404,
  "message": "The requested webhook \"wf7-video-script\" is not registered.",
  "hint": "Click the 'Execute workflow' button on the canvas, then try again. (In test mode, the webhook only works for one call after you click this button)"
}
```

### 手動実行（推奨）

1. ブラウザで https://n8n-python-production-344b.up.railway.app/workflow/SDO8X6oR5W5y2s6A を開く
2. 画面右上の「Execute Workflow」ボタン（▶️）をクリック
3. 実行完了を待つ（通常数秒〜数十秒）
4. MCPツールで結果を確認

## 📊 期待される結果

### 成功時のフロー

1. **Submit to FAL**:
   ```json
   {
     "status": "IN_QUEUE",
     "request_id": "uuid-here",
     "response_url": "https://queue.fal.run/fal-ai/ffmpeg-api/requests/uuid-here"
   }
   ```

2. **Fetch Status** (ポーリング):
   ```json
   {
     "status": "IN_PROGRESS"
   }
   ```

3. **Get Image Result URL** (完了時):
   ```json
   {
     "status": "COMPLETED",
     "video_url": "https://fal.media/files/..."
   }
   ```

4. **DriveへUL**:
   ```json
   {
     "id": "drive-file-id",
     "webViewLink": "https://drive.google.com/file/d/..."
   }
   ```

5. **Notion更新**:
   ```json
   {
     "properties": {
       "Status": { "select": { "name": "VideoReady" } },
       "Video URL": { "url": "https://drive.google.com/..." }
     }
   }
   ```

### エラー時の確認ポイント

#### 422 エラー (Field required)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "tracks", 0, "keyframes", 0, "timestamp"],
      "msg": "Field required"
    }
  ]
}
```
**原因**: ペイロード構築ノードで `timestamp` または `duration` が欠落
**確認**: ペイロード構築ノードのコードが最新版になっているか

#### Invalid URL エラー
```
Invalid URL: ==https://... URL must start with "http" or "https".
```
**原因**: URL表現に `==` (double equals) が使用されている
**確認**: Get Image Result URL ノードのURLが `=https://...` (single equals) になっているか

## 🔄 次のステップ

1. **保存確認**: n8nのUIでワークフローを明示的に保存
2. **テスト実行**: UIから「Execute Workflow」をクリック
3. **結果確認**: MCPツールで新しいexecutionの結果を取得
4. **成功検証**:
   - FAL APIから正常にvideo_urlが返されるか
   - Google Driveへのアップロードが成功するか
   - Notion Hubのステータスが「VideoReady」に更新されるか

## 📚 関連ドキュメント

- [FAL API Compose Endpoint Documentation](https://fal.ai/models/fal-ai/ffmpeg-api/compose)
- [n8n Workflow Construction Knowledge](/docs/knowledge/n8n-workflow-construction-knowledge.md)
- [WF7 Implementation Guide](/workflows/wf7-sns-video-automation/IMPLEMENTATION_GUIDE.md)

## 🐛 トラブルシューティング

### Q: executionリストに新しいexecutionが表示されない
**A**: UIで「Execute Workflow」ボタンを押していない可能性があります。MCPツールからはワークフローを直接実行できません。

### Q: UI表示とAPI取得内容が異なる
**A**: ワークフローを明示的に保存してください。保存後、API取得内容が最新になります。

### Q: webhookが404を返す
**A**: テストモードではwebhookは一時的です。UIから手動実行を推奨します。本番環境ではワークフローをアクティブにすることで永続的なwebhookになります。
