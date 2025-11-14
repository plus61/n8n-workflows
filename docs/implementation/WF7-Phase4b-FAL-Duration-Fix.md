# WF7 Phase4b FAL Compose API Duration修正手順

**作成日**: 2025-01-12
**ワークフロー**: `mfRdJJFJRKmeBjKv` (WF7 Phase4b - Single Video Generator)
**問題**: 生成された動画が1x1ピクセル、0.04秒になる

---

## 🔍 根本原因

FAL Compose APIの`duration`パラメータは**ミリ秒単位**で指定する必要があるが、現在の実装では**秒単位**（3, 10, 12）で渡していた。

### 検証済みAPI仕様

```json
{
  "tracks": [{
    "id": "string",
    "type": "video",
    "keyframes": [{
      "url": "string",
      "timestamp": 0,        // ミリ秒
      "duration": 3000       // ミリ秒（必須）
    }]
  }]
}
```

**公式ドキュメント**: https://fal.ai/models/fal-ai/ffmpeg-api/compose/api

---

## 🔧 修正手順（n8n UI）

### Step 1: ワークフローを開く

1. **n8n UIにアクセス**: https://n8n-python-production-344b.up.railway.app
2. **ワークフロー検索**: "WF7 Phase4b - Single Video Generator" または ID `mfRdJJFJRKmeBjKv`
3. **ワークフローを開く**

### Step 2: コードノードを編集

1. **"Code - Prepare FAL Payload"** ノードをクリック
2. **コードエディタを開く**
3. **14行目を修正**:

```javascript
// ❌ 修正前（14行目）
duration: slide.duration

// ✅ 修正後（14行目）
duration: slide.duration * 1000  // Convert seconds to milliseconds
```

### Step 3: 完全なコード（参考用）

```javascript
const input = $input.first().json;
const slide = input.slide_metadata;
const scriptId = input.script_id;
const slideIndex = input.slide_index;

// ✅ FIX: Convert duration from seconds to milliseconds
const payload = {
  tracks: [
    {
      id: "1",
      type: "video",
      keyframes: [
        {
          url: slide.image_url,
          timestamp: 0,
          duration: slide.duration * 1000  // Convert seconds to milliseconds
        }
      ]
    }
  ]
};

return {
  json: {
    fal_payload: JSON.stringify(payload),
    slide_metadata: slide,
    script_id: scriptId,
    slide_index: slideIndex,
    image_url: slide.image_url
  }
};
```

### Step 4: 保存して有効化

1. **"Save"** ボタンをクリック
2. ワークフローが`active: true`であることを確認（子ワークフローなのでfalseでOK）

---

## ✅ テスト実行

### テストペイロード

```bash
curl -X POST 'https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-phase4b-orchestrator' \
  -H 'Content-Type: application/json' \
  -d @/tmp/test-phase4b-v1-payload.json
```

**ペイロード内容**: `/tmp/test-phase4b-v1-payload.json`

### 期待される結果

```json
{
  "success": true,
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://v3b.fal.media/files/.../output.mp4"
    }
  ]
}
```

### 動画検証

```bash
# 動画をダウンロード
curl -s "https://v3b.fal.media/files/.../output.mp4" -o /tmp/test-video.mp4

# メタデータを確認
ffprobe -v error -show_format -show_streams /tmp/test-video.mp4

# 期待される結果
# width=1920 (not 1)
# height=1080 (not 1)
# duration=3.000000 (not 0.04)
# nb_frames=90 (30fps × 3秒, not 1)
```

---

## 📊 修正前後の比較

| 項目 | 修正前 | 修正後 |
|------|--------|--------|
| **duration値** | 3 (秒) | 3000 (ミリ秒) |
| **解像度** | 1x1 | 1920x1080 |
| **動画時間** | 0.04秒 | 3.0秒 |
| **フレーム数** | 1 | 90 (30fps) |
| **ファイルサイズ** | 1.5KB | 数MB |

---

## 🚨 注意事項

### ❌ やってはいけないこと

1. **新しいワークフローとしてインポート**: 親ワークフロー `hfhZijyKIt1DjI1V` が古いIDを参照しているため動作しない
2. **webhookIdの変更**: `phase4b-single-wait` と `phase4b-single-retry` は変更しない
3. **credential IDの変更**: `voV5kURaCkiUjLTZ` (fal) は維持

### ✅ 正しいアプローチ

- **既存ワークフロー `mfRdJJFJRKmeBjKv` を直接編集**
- **1行だけ修正**: `duration: slide.duration` → `duration: slide.duration * 1000`
- **他のコードは変更しない**

---

## 🔄 親ワークフローとの連携

### 親ワークフロー: `wHaKi98mTlUvFIOR` (Orchestrator)

- **役割**: 7枚のスライドを並列処理
- **子ワークフロー呼び出し**: `mfRdJJFJRKmeBjKv` を7回並列実行
- **変更不要**: 親ワークフローの修正は不要

### データフロー

```
Phase4a Output (7 slides)
  ↓
Parent: wHaKi98mTlUvFIOR
  ↓ (Split into 7 parallel executions)
Child: mfRdJJFJRKmeBjKv × 7
  ↓ (Each generates one video)
Parent: Aggregate results
  ↓
Output: 7 video URLs
```

---

## 📝 トラブルシューティング

### エラー: "Cannot read properties of undefined (reading 'image_url')"

**原因**: 入力データ構造が期待と異なる

**解決策**:
1. Execute Workflow Triggerが正しくデータを受け取っているか確認
2. `$input.first().json` の構造を確認:
   ```json
   {
     "slide_metadata": {
       "section": "hook",
       "duration": 3,
       "image_url": "https://...",
       "motion_prompt": "...",
       "text": "..."
     },
     "script_id": "...",
     "slide_index": 0
   }
   ```

### エラー: "Video URL not found in FAL API response"

**原因**: FAL APIのレスポンス構造が変更された可能性

**解決策**: `Code - Build Video Metadata` ノードで以下を確認:
```javascript
const videoUrl = resultData.output?.video_url || resultData.video_url || resultData.result?.video_url;
```

---

## ✅ 完了チェックリスト

- [ ] n8n UIでワークフロー `mfRdJJFJRKmeBjKv` を開く
- [ ] "Code - Prepare FAL Payload" ノードを編集
- [ ] `duration: slide.duration * 1000` に修正
- [ ] ワークフローを保存
- [ ] テストペイロードで実行
- [ ] 生成された動画をダウンロードして検証
- [ ] ffprobeで解像度・時間・フレーム数を確認
- [ ] 7枚全てのスライドで正常動作を確認

---

## 📚 関連ドキュメント

- **FAL Compose API仕様**: https://fal.ai/models/fal-ai/ffmpeg-api/compose/api
- **Phase4 現状整理**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/docs/implementation/WF7-Phase4-Current-Status.md`
- **修正済みワークフローJSON**: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-phase4b-single-video-generator-FIXED.json` (参考用のみ、使用しない)
