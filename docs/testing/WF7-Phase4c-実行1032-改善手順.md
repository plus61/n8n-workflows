# WF7 Phase4c 実行1032 改善手順

**作成日**: 2025-11-09  
**対象ワークフロー**: `chPw11OY5sex6d9I` (WF7 Phase4c - Perfect Implementation)  
**実行ID**: 1032  
**問題**: `Download Video`ノードで422エラー発生

---

## 🔍 問題の詳細

### エラー内容
- **ノード**: `Download Video`
- **エラー**: `422 - Field required: tracks`
- **原因**: `Extract Video URL`ノードで`response_url`を`video_url`として抽出しているが、`response_url`は動画ファイルではなく、リクエスト情報を返すエンドポイント

### 実行結果の分析

1. **`Get Result`ノード**: 成功（`response_url`にGETリクエストを送信）
2. **`Extract Video URL`ノード**: `response_url`を`video_url`として抽出（❌ 誤り）
3. **`Download Video`ノード**: `response_url`に対してGETリクエストを送信 → 422エラー

### 問題の根本原因

`Get Result`ノードのレスポンスから動画URLを正しく抽出できていません。`response_url`は動画ファイルではなく、リクエスト情報を返すエンドポイントです。

---

## 🔧 修正手順

### Step 1: `Extract Video URL`ノードを修正

1. n8n UIでワークフロー `chPw11OY5sex6d9I` を開く
2. `Extract Video URL`ノードを選択
3. **Code**タブを開く
4. 以下のコードに置き換え：

```javascript
// Get Resultのレスポンスからvideo_urlを抽出
const resultData = $input.first().json;

// デバッグ用: レスポンス構造をログ出力（n8nの実行ログで確認可能）
console.log('Get Result response keys:', Object.keys(resultData));
console.log('Get Result response preview:', JSON.stringify(resultData).substring(0, 500));

// FAL API /composeエンドポイントのレスポンスからvideo_urlを抽出
// 複数のパターンを試す
let videoUrl = null;

// パターン1: output.video.url (標準的なFAL APIレスポンス)
if (resultData.output?.video?.url) {
  videoUrl = resultData.output.video.url;
}
// パターン2: output.video_url
else if (resultData.output?.video_url) {
  videoUrl = resultData.output.video_url;
}
// パターン3: output.url (直接)
else if (resultData.output?.url) {
  videoUrl = resultData.output.url;
}
// パターン4: video.url (直接)
else if (resultData.video?.url) {
  videoUrl = resultData.video.url;
}
// パターン5: video_url (直接、ただしresponse_urlではない)
else if (resultData.video_url && !resultData.video_url.includes('/requests/')) {
  videoUrl = resultData.video_url;
}
// パターン6: result.video_url
else if (resultData.result?.video_url) {
  videoUrl = resultData.result.video_url;
}
// パターン7: url (直接、ただしresponse_urlやstatus_urlではない)
else if (resultData.url && !resultData.url.includes('/requests/') && !resultData.url.includes('/status')) {
  videoUrl = resultData.url;
}
// パターン8: response_urlが実際の動画URLの場合（.mp4で終わる）
else if (resultData.response_url && resultData.response_url.endsWith('.mp4')) {
  videoUrl = resultData.response_url;
}

if (!videoUrl) {
  // デバッグ情報を含むエラー
  const availableKeys = Object.keys(resultData);
  const responsePreview = JSON.stringify(resultData, null, 2).substring(0, 2000);
  throw new Error(
    'Video URL not found in FAL API response.\n' +
    'Available top-level keys: ' + availableKeys.join(', ') + '\n' +
    'Response preview: ' + responsePreview
  );
}

return [{
  json: {
    video_url: videoUrl,
    raw_response: resultData,
    request_id: $('Fetch Status').item.json.request_id,
    script_id: $('ペイロード構築').item.json.script_id || 'unknown'
  }
}];
```

### Step 2: ワークフローを保存

1. 右上の **"Save"** ボタンをクリック
2. 保存完了を確認

---

## 🧪 テスト実行

### Step 1: Pin Dataを確認

`When clicking 'Test workflow'`ノードのPin Dataが設定されていることを確認（7本の動画URL）

### Step 2: テスト実行

1. 右上の **"Test workflow"** ボタンをクリック
2. 実行結果を確認

### Step 3: 各ノードの確認

1. **Get Result**: レスポンス構造を確認（実行ログで`Get Result response keys`を確認）
2. **Extract Video URL**: `video_url`が正しく抽出されているか確認
3. **Download Video**: 動画がダウンロードできているか確認

---

## ⚠️ 注意事項

### `Get Result`ノードのレスポンス構造

`Get Result`ノードのレスポンス構造が不明確な場合、実行ログで`Get Result response keys`と`Get Result response preview`を確認してください。

### デバッグ方法

1. `Extract Video URL`ノードの実行ログを確認
2. `raw_response`フィールドに`Get Result`ノードの完全なレスポンスが含まれています
3. エラーメッセージに`Available top-level keys`が表示されます

### 代替案

もし`Get Result`ノードのレスポンスに動画URLが含まれていない場合：

1. **FAL APIのドキュメントを確認**: `/compose`エンドポイントの正しい使用方法を確認
2. **別のエンドポイントを使用**: `/compose`以外のエンドポイントを使用する可能性を検討
3. **手動で動画URLを取得**: `response_url`に対してcurlコマンドでGETリクエストを送信し、結果を確認

---

## 📝 修正完了（2025-11-09 13:02）

### 実施した修正

1. ✅ **`Get Result`ノードのURLを修正**
   - 変更前: `={{ $json.response_url }}`
   - 変更後: `=https://queue.fal.run/fal-ai/ffmpeg-api/requests/{{ $json.request_id }}/result`
   - 理由: `response_url`はリクエスト情報を返すエンドポイントであり、実際の動画URLは`/result`エンドポイントから取得する必要がある

2. ✅ **`Extract Video URL`ノードのコードを修正**
   - 成功実例（`wf7_phase4b.json`）に基づいて、`output.video_url`を優先的に抽出するように修正
   - 複数のパターンに対応（`output.video_url`, `output.video.url`, `output.url`など）

### 次のステップ

1. ⏳ テスト実行して動作確認
2. ⏳ `Get Result`ノードのレスポンス構造を確認（実行ログで`Get Result response keys`を確認）
3. ⏳ `video_url`が正しく抽出されているか確認
4. ⏳ `Download Video`ノードで動画がダウンロードできているか確認

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-09 13:02

