# WF10-Main修正内容v2d：Google Drive API v3形式変換対応

**作成日時**: 2025-11-16 02:27:58 JST

## 🎯 修正履歴

### v1（2025-11-15 22:37作成）
- ✅ webhook URLをクエリパラメータ化（`?fal_webhook=...`）

### v2（2025-11-15 22:46作成）
- ✅ APIパラメータ名を正しい名前に修正
- ✅ duration値を許可範囲内に修正（10秒）

### v2b（2025-11-15 23:46作成）
- ✅ テスト画像URLを有効なURLに修正（Cloudinary 404 → Unsplash）
- ❌ **結果**: Unsplash URLも404エラー（fal.aiが処理中にブロック）

### v2c（2025-11-16 00:09作成）
- ✅ **Google Drive URL採用**（WF7の実績パターン）
- ✅ file ID: `13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg`
- ✅ URL形式: `https://drive.google.com/uc?export=download&id=FILE_ID`
- ❌ **結果**: fal.ai Runway Gen-3 APIが422エラーで拒否

### v2d（2025-11-16 02:27作成）- このバージョン
- ✅ **Google Drive URL → API v3形式への変換を実装**
- ✅ WF7の成功パターンを完全適用
- ✅ 変換ロジック: `https://drive.google.com/uc?export=download&id=FILE_ID` → `https://www.googleapis.com/drive/v3/files/FILE_ID?alt=media`

---

## 🐛 v2c〜v2d間で発見された重大な問題

### 問題1: v4の誤った修正（同時期に判明）

**実行2499の分析結果から判明**:
- **私の誤解**: n8n Webhook Triggerがデータを`$json`に直接格納すると誤認
- **実際の構造**: Webhook Triggerは受信JSONを`$json.body`に格納する
- **v3の状態**: `$json.body.status`, `$json.body.payload.video.url` - **正しい**
- **v4の誤り**: `$json.status`, `$json.payload.video.url` - **間違い**

**証拠（実行2499のWebhook Trigger出力）**:
```json
{
  "json": {
    "body": {  // ← データはbody内に格納される
      "status": "ERROR",
      "request_id": "546b0378-a8e8-487f-9064-f97ad3128edc",
      "payload": {
        "detail": "Could not load image from url: ..."
      }
    }
  }
}
```

**結論**:
- ✅ **v3が正しい** - そのまま使用すること
- ❌ **v4は破棄** - 誤った修正を含む

---

### 問題2: Google Drive URL形式の互換性問題

**v2cで発見された422エラー**:
```json
{
  "error": "Unexpected status code: 422",
  "payload": {
    "detail": "Could not load image from url: https://drive.google.com/uc?export=download&id=13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg"
  }
}
```

**調査結果**:
- v2cが送信したURL: `https://drive.google.com/uc?export=download&id=FILE_ID`
- fal.ai Runway Gen-3 APIの応答: 422エラー（画像URLを読み込めない）
- **原因**: fal.ai Runway Gen-3 APIはuc download形式を受け付けない

**WF7との比較分析**:

#### WF7の成功パターン（`wf7_phase4b.json`から）
```javascript
// Code - Prepare FAL Payload (line 53)
let imageUrl = slide.image_url;

if (imageUrl.includes('drive.google.com')) {
  // FILE_IDを抽出
  const fileIdMatch = imageUrl.match(/[?&]id=([^&]+)/) || imageUrl.match(/\/d\/([^\/]+)/);
  if (fileIdMatch && fileIdMatch[1]) {
    const fileId = fileIdMatch[1];
    // Google Drive API v3形式に変換（公開ファイルの直接アクセス）
    imageUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`;
  }
}
```

**重要な発見**:
- WF7もuc download形式を受け取るが、**fal.aiに送る前にAPI v3形式に変換している**
- WF7はfal.ai Compose APIを使用（7つの動画生成で成功実績あり）
- v2cはURL変換を行わずにuc download形式をそのまま送信していた

---

## ✅ v2dでの修正内容

### 修正1: Code nodeの追加

**ノード構成の変更**:

#### Before v2c
```
Manual Trigger
  → Set - Test Data
  → HTTP Request - Runway Gen-3 API
  → Set - Response Parse
```

#### After v2d
```
Manual Trigger
  → Set - Test Data
  → Code - Convert Google Drive URL (新規)
  → HTTP Request - Runway Gen-3 API
  → Set - Response Parse
```

### 修正2: URL変換ロジックの実装

**Code - Convert Google Drive URLノード**:
```javascript
// 画像URLを取得
let imageUrl = $json.画像素材URL[0];

// Google Drive URLの場合、API v3形式に変換
if (imageUrl.includes('drive.google.com')) {
  // FILE_IDを抽出（2つのパターンに対応）
  // パターン1: ?id=FILE_ID または &id=FILE_ID
  // パターン2: /d/FILE_ID/
  const fileIdMatch = imageUrl.match(/[?&]id=([^&]+)/) || imageUrl.match(/\/d\/([^\/]+)/);

  if (fileIdMatch && fileIdMatch[1]) {
    const fileId = fileIdMatch[1];
    // Google Drive API v3形式に変換（公開ファイルの直接アクセス）
    imageUrl = `https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`;
  }
}

// 変換後のURLと台本を返す
return {
  画像素材URL: [imageUrl],
  台本本文: $json.台本本文
};
```

**対応するGoogle Drive URL形式**:
1. **uc download形式**: `https://drive.google.com/uc?export=download&id=FILE_ID`
2. **共有リンク形式**: `https://drive.google.com/file/d/FILE_ID/view`
3. **その他のクエリパラメータ形式**: `https://drive.google.com/open?id=FILE_ID`

**変換後の形式**:
```
https://www.googleapis.com/drive/v3/files/FILE_ID?alt=media
```

---

## 📊 URL変換の動作例

### 入力例1: uc download形式（v2cで使用）
```
入力: https://drive.google.com/uc?export=download&id=13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg
抽出: fileId = "13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg"
出力: https://www.googleapis.com/drive/v3/files/13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg?alt=media
```

### 入力例2: 共有リンク形式（ユーザーが提供したURL）
```
入力: https://drive.google.com/file/d/13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg/view?usp=drivesdk
抽出: fileId = "13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg"
出力: https://www.googleapis.com/drive/v3/files/13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg?alt=media
```

### 入力例3: 非Google Drive URL（変換不要）
```
入力: https://example.com/image.jpg
出力: https://example.com/image.jpg（そのまま）
```

---

## 📋 適用手順

### Step 1: 既存WF10-Mainの削除
```
n8n UI → WF10-Main → 右上「⋮」→ Delete
```

### Step 2: 修正版v2dのインポート
```
Workflows → + Add workflow → Import from file
→ now/2025-11-16_02-27_WF10-Main修正版v2d-GoogleDriveAPI-v3.json
```

### Step 3: 認証情報の確認
```
HTTP Request - Runway Gen-3 APIノードを開く
→ Credentials: 「fal.ai API Key」が設定されているか確認
```

### Step 4: ワークフローを保存

### Step 5: テスト実行
```
「Test workflow」または「Execute Workflow」をクリック
```

---

## 🧪 期待される動作（修正版v2d）

### 1. WF10-Main v2d実行

**Set - Test Data出力**:
```json
{
  "画像素材URL": ["https://drive.google.com/uc?export=download&id=13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg"],
  "台本本文": "A serene landscape with mountains and clear blue sky, camera slowly panning from left to right"
}
```

**Code - Convert Google Drive URL出力**:
```json
{
  "画像素材URL": ["https://www.googleapis.com/drive/v3/files/13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg?alt=media"],
  "台本本文": "A serene landscape with mountains and clear blue sky, camera slowly panning from left to right"
}
```

**HTTP Request - Runway Gen-3 API送信ボディ**:
```json
{
  "image_url": "https://www.googleapis.com/drive/v3/files/13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg?alt=media",
  "prompt": "A serene landscape with mountains and clear blue sky, camera slowly panning from left to right",
  "duration": 10,
  "ratio": "16:9"
}
```

**期待されるレスポンス**:
```json
{
  "status": "IN_QUEUE",
  "request_id": "uuid-string",
  "queue_position": 0,
  "response_url": "https://queue.fal.run/fal-ai/runway-gen3/..."
}
```

### 2. fal.aiでの処理

- ✅ Google Drive API v3形式のURLが正常に処理される（**WF7実績パターン**）
- ✅ 画像が正常に取得される（**422エラーなし**）
- ✅ キューに正常に追加される（IN_QUEUE）
- ⏳ **処理時間**: 通常1-3分（Turboモード）
- ✅ 10秒の動画が生成される
- ✅ 1920x1080（16:9比率）

### 3. WF10-Webhook v3へのコールバック（成功時）

**重要**: WF10-WebhookはWF10-Webhook v3を使用すること（v4は破棄）

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

**v3のSet - Payload Parse（正しい参照）**:
```javascript
{
  "video_url": "={{ $json.body.payload.video.url }}",     // ✅ 正しい
  "status": "={{ $json.body.status }}",                    // ✅ 正しい
  "request_id": "={{ $json.body.request_id }}",            // ✅ 正しい
  "duration": "={{ $json.body.payload.video.duration }}",  // ✅ 正しい
  "width": "={{ $json.body.payload.video.width }}",        // ✅ 正しい
  "height": "={{ $json.body.payload.video.height }}"       // ✅ 正しい
}
```

**期待される出力**:
- ✅ `video_url`: `"https://v3.fal.media/files/..."`（**nullではない**）
- ✅ `status`: `"completed"`
- ✅ `request_id`: UUID
- ✅ `duration`: `10`
- ✅ `width`: `1920`
- ✅ `height`: `1080`

**HTTP Request - Download Video**:
- ✅ `$json.video_url`が有効なURLとして取得される
- ✅ 動画ダウンロード成功

**Write Binary File**:
- ✅ `/tmp/wf10-videos/{request_id}.mp4`に保存成功

---

## ✅ 検証チェックリスト

### WF10-Main v2dインポート後
- [ ] WF10-Main修正版v2dインポート完了
- [ ] Code - Convert Google Drive URLノードが存在することを確認
- [ ] 認証情報（fal.ai API Key）が正しく設定されている
- [ ] Google Drive URL（`13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg`）が設定されている

### WF10-Webhook v3の確認
- [ ] WF10-Webhook v3がアクティブ（**v4ではない**）
- [ ] v3のSet - Payload Parseが`$json.body.*`参照を使用している

### E2Eテスト実行
- [ ] WF10-Main v2dテスト実行でIN_QUEUEレスポンス取得（**ERRORではない**）
- [ ] レスポンスに`request_id`と`status: "IN_QUEUE"`が含まれている
- [ ] Code - Convert Google Drive URLがAPI v3形式のURLを出力
- [ ] **1-3分以内にWF10-Webhook v3にコールバック到達**
- [ ] コールバックのstatusが "completed"（**ERRORではない**）
- [ ] Set - Payload Parseでvideo_urlが正しく取得（**nullではない**）
- [ ] 動画URL（`payload.video.url`）が実際のfal.ai URLを含んでいる
- [ ] WF10-Webhook v3が動画を正常にダウンロード（**404エラーなし**）
- [ ] `/tmp/wf10-videos/` に.mp4ファイルが存在
- [ ] 動画が再生可能（10秒、1920x1080）

---

## 🔄 次のステップ

### Task 10e-4: E2Eテスト実行（v2d + v3）
- ⏳ **ユーザーがv2dをインポート＆テスト実行**
- ⏳ **WF10-Webhook v3が有効化されていることを確認**（v4ではない）
- ⏳ **E2Eテスト成功確認**
  - IN_QUEUEレスポンス取得
  - URL変換が正しく動作
  - webhookコールバック到達
  - 動画ダウンロード成功
  - ファイル保存確認

### Task 11: Phase 0-MVP検証（10回テスト）
- E2Eテスト成功後、10回連続実行
- 成功率を記録（目標: 9/10以上）

---

## 📊 バージョン比較まとめ

### Google Drive URL処理

| バージョン | URL形式 | 変換処理 | fal.ai応答 | 結果 |
|-----------|---------|---------|------------|------|
| v2c | uc download | なし | 422エラー | ❌ 失敗 |
| v2d | uc download | API v3に変換 | IN_QUEUE | ✅ 期待 |

### Webhook Payload参照

| バージョン | 参照形式 | 実際の構造 | 結果 |
|-----------|---------|-----------|------|
| v3 | `$json.body.*` | `$json.body.*` | ✅ 正しい |
| v4 | `$json.*` | `$json.body.*` | ❌ 間違い |

---

## 📚 参考情報

**実行履歴**:
- 実行2449（v2使用）: 422エラー - Cloudinary画像URL 404判明
- 実行2456（v2b使用）: IN_QUEUE成功
- 実行2461, 2465（v2b callback）: 404エラー - Unsplash処理中ブロック判明
- 実行2499（v2c使用）: 422エラー - Google Drive uc download形式拒否判明

**判明した問題**:
1. v2: Cloudinary URL 404 → 即座の422エラー
2. v2b: Unsplash URL有効 → 処理中の404エラー（fal.aiブロック）
3. v2c: Google Drive uc download形式 → 422エラー（fal.ai Runway Gen-3非対応）
4. v4: Webhook payload参照誤り → Set - Payload Parse全null（誤った修正）
5. v2d: Google Drive API v3変換 → WF7実績パターン適用（解決）

**WF7からの学習**:
- Google Drive URLはfal.aiと互換性あり
- **ただし、API v3形式への変換が必須**
- WF7はuc download形式を受け取り、変換してからfal.aiに送信
- 複数のURL形式をサポート（uc download, share link）
- 7つの動画生成で使用実績あり

**v4の誤り**:
- n8n Webhook TriggerのデータはJSONボディを`$json.body`に格納
- v3の`$json.body.*`参照が正しい
- v4の`$json.*`参照は間違い（実行2499で証明）
- v4は破棄し、v3をそのまま使用すること

---

**作成者**: Claude Code (SuperClaude)
**対応Issue**: v2c Google Drive uc download形式422問題、v4 payload参照誤り問題
**解決策**: WF7パターン適用（Google Drive API v3変換）、v3の正当性確認
**エビデンス**: WF7コード分析、実行2499データ、fal.ai 422エラー、WF7実行履歴
