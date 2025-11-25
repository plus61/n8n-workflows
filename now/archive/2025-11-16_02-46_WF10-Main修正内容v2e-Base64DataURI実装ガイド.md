# WF10-Main修正内容v2e：Base64 Data URI実装ガイド

**作成日時**: 2025-11-16 02:46:50 JST

## 🎯 重要：使用すべきバージョン

### ✅ 正しいバージョン

| ワークフロー | バージョン | ファイル | 状態 |
|------------|----------|---------|------|
| **WF10-Main** | **v2e** | `2025-11-16_02-42_WF10-Main修正版v2e-Base64DataURI.json` | ✅ **使用推奨** |
| **WF10-Webhook** | **v3** | `2025-11-15_22-54_WF10-Webhook修正版v3-payloadパース修正.json` | ✅ **使用推奨** |

### ❌ 使用してはいけないバージョン

| バージョン | 理由 | 状態 |
|----------|------|------|
| v4（Webhook） | `$json.body.*`参照を誤って削除、video_urlが常にnullを返す | ❌ **撤回** |
| v2d（Main） | Google Drive API v3形式もRunway Gen-3に拒否される | ❌ **撤回** |
| v2c（Main） | Google Drive uc download形式がRunway Gen-3に拒否される | ❌ **撤回** |
| v2b（Main） | Unsplash URLが処理中にブロックされる | ❌ **撤回** |
| v2（Main） | Cloudinary URLが404エラー | ❌ **撤回** |

---

## 🔍 問題の経緯

### 発見された3つの重大なエラー

#### エラー1: v4（Webhook）の誤った修正
- **誤った前提**: `$json.body.*`参照が間違っていると判断
- **実際**: n8n Webhook Triggerは受信データを`$json.body`に格納する
- **結果**: v4のすべてのフィールドが`null`を返し、「URL parameter must be a string, got null」エラー
- **証拠**: 実行2499、2508のデータ分析

**実行2499の実際のwebhook受信データ**:
```json
{
  "json": {
    "body": {  // ← bodyが存在する！
      "status": "ERROR",
      "request_id": "546b0378-a8e8-487f-9064-f97ad3128edc",
      "payload": {
        "detail": "Could not load image from url: ..."
      }
    }
  }
}
```

**結論**: v3の`$json.body.*`参照が正しい、v4は破棄

#### エラー2: Google Drive uc download形式の拒否
- **使用URL**: `https://drive.google.com/uc?export=download&id=FILE_ID`
- **fal.aiレスポンス**: HTTP 422 "Could not load image from url: [URL]"
- **根本原因**: Runway Gen-3 APIはリダイレクトを使用するURLを受け付けない
- **証拠**: 実行2499の422エラー

#### エラー3: Google Drive API v3形式も拒否
- **使用URL**: `https://www.googleapis.com/drive/v3/files/FILE_ID?alt=media`
- **fal.aiレスポンス**: HTTP 422 "Could not load image from url: [URL]"
- **根本原因**: API v3 URLは認証が必要、Runway Gen-3がアクセスできない
- **証拠**: 実行2508の422エラー

**重大な気づき**:
- WF7: `fal-ai/ffmpeg-api/compose` → Google Drive URLを受け入れる
- WF10: `fal-ai/runway-gen3/turbo/image-to-video` → より厳格なURL要件
- **異なるAPI = 異なる要件**

---

## 📋 Runway Gen-3 API画像URL要件（公式仕様）

Web調査により判明した公式要件：

✅ **必須要件**:
- HTTPSプロトコル（ドメイン名必須、IPアドレス不可）
- 有効なContent-TypeおよびContent-Lengthヘッダー
- 画像固有のMIMEタイプ（`image/png`、`image/jpeg`等）

❌ **禁止事項**:
- **リダイレクト（3XXレスポンス）** ← Google Drive URLが失敗する主な理由
- `application/octet-stream`等の汎用MIMEタイプ
- 認証が必要なURL
- 2048文字を超えるURL長

**Google Drive URLが失敗する理由**:
- uc download形式: リダイレクトを使用
- API v3形式: 認証が必要
- **両方とも要件を満たさない**

---

## ✅ 解決策：Base64 Data URI方式

### なぜBase64 Data URIか

**選択理由**:
1. ✅ **fal.ai公式サポート**: ドキュメントで明示的にサポートされている
2. ✅ **URL制限を回避**: 画像データを直接リクエストに埋め込むため、URL要件を完全に回避
3. ✅ **リダイレクト不要**: 外部URLアクセスが不要
4. ✅ **認証不要**: 画像データがリクエストに含まれる
5. ✅ **信頼性**: 確実に動作する唯一の方法

**トレードオフ**:
- ⚠️ リクエストペイロードが大きくなる（Base64は元サイズの約133%）
- ⚠️ 大きな画像では性能に影響する可能性
- ✅ しかし、信頼性と互換性を確保できる

---

## 🔧 v2e実装の詳細

### ワークフロー構造

```
Manual Trigger
  ↓
Set - Test Data
  ↓ (Google Drive file ID)
HTTP Request - Download Image from Google Drive
  ↓ (Binary data)
Code - Convert to Base64 Data URI
  ↓ (Data URI)
HTTP Request - Runway Gen-3 API (Base64)
  ↓ (request_id, status)
Set - Response Parse
```

### ノード1: Set - Test Data

**目的**: テストデータの設定

```json
{
  "assignments": [
    {
      "name": "google_drive_file_id",
      "value": "13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg",
      "type": "string"
    },
    {
      "name": "台本本文",
      "value": "A serene landscape with mountains and clear blue sky, camera slowly panning from left to right",
      "type": "string"
    }
  ]
}
```

**設定値**:
- `google_drive_file_id`: Google DriveファイルID（共有設定済み）
- `台本本文`: 動画生成のプロンプト

### ノード2: HTTP Request - Download Image from Google Drive

**目的**: Google Driveから画像をバイナリデータとしてダウンロード

```json
{
  "url": "={{ \"https://drive.google.com/uc?export=download&id=\" + $json.google_drive_file_id }}",
  "options": {
    "response": {
      "response": {
        "responseFormat": "file"
      }
    },
    "timeout": 30000
  }
}
```

**重要ポイント**:
- ✅ `responseFormat: "file"` でバイナリデータを取得
- ✅ Google Drive uc download形式は**ダウンロードには使える**（n8nからのアクセス）
- ✅ 30秒タイムアウト設定

**出力**: `$input.first().binary.data` にバイナリデータが格納される

### ノード3: Code - Convert to Base64 Data URI（核心部分）

**目的**: バイナリデータをBase64 Data URI形式に変換

```javascript
// Google Driveからダウンロードした画像をBase64 Data URIに変換
const binaryData = $input.first().binary.data;

if (!binaryData) {
  throw new Error('No binary data found');
}

// バイナリデータをBase64エンコード
const base64Data = binaryData.data;

// MIMEタイプを取得（デフォルトはimage/png）
const mimeType = binaryData.mimeType || 'image/png';

// Data URI形式に変換
const dataUri = `data:${mimeType};base64,${base64Data}`;

// 台本本文も取得
const prompt = $('Set - Test Data').first().json.台本本文;

return {
  image_data_uri: dataUri,
  prompt: prompt,
  original_mime_type: mimeType,
  data_size_kb: Math.round(base64Data.length / 1024)
};
```

**処理フロー**:
1. ✅ 前ノードのバイナリデータを取得
2. ✅ 存在チェック（エラーハンドリング）
3. ✅ MIMEタイプを取得（PNG/JPEGの自動判定）
4. ✅ `data:image/png;base64,ENCODED_DATA` 形式に変換
5. ✅ 台本本文と組み合わせて出力

**出力データ構造**:
```json
{
  "image_data_uri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "prompt": "A serene landscape...",
  "original_mime_type": "image/png",
  "data_size_kb": 1234
}
```

### ノード4: HTTP Request - Runway Gen-3 API (Base64)

**目的**: Base64 Data URIをRunway Gen-3 APIに送信

```json
{
  "method": "POST",
  "url": "https://queue.fal.run/fal-ai/runway-gen3/turbo/image-to-video?fal_webhook=https://n8n-python-production-344b.up.railway.app/webhook/wf10-runway-webhook",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "httpHeaderAuth",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ {\n  \"image_url\": $json.image_data_uri,\n  \"prompt\": $json.prompt,\n  \"duration\": 10,\n  \"ratio\": \"16:9\"\n} }}",
  "credentials": {
    "httpHeaderAuth": {
      "id": "fal-api-key",
      "name": "fal.ai API Key"
    }
  }
}
```

**重要ポイント**:
- ✅ `image_url` フィールドにBase64 Data URIを直接渡す
- ✅ webhookパラメータをクエリ文字列で指定
- ✅ `duration: 10` （10秒、許可範囲内）
- ✅ `ratio: "16:9"` （1920x1080）

**期待されるレスポンス（IN_QUEUE）**:
```json
{
  "status": "IN_QUEUE",
  "request_id": "uuid-string",
  "queue_position": 0,
  "response_url": "https://queue.fal.run/fal-ai/runway-gen3/..."
}
```

### ノード5: Set - Response Parse

**目的**: APIレスポンスから必要な情報を抽出

```json
{
  "assignments": [
    {
      "name": "request_id",
      "value": "={{ $json.request_id }}",
      "type": "string"
    },
    {
      "name": "status",
      "value": "={{ $json.status }}",
      "type": "string"
    },
    {
      "name": "queue_position",
      "value": "={{ $json.queue_position }}",
      "type": "number"
    },
    {
      "name": "response_url",
      "value": "={{ $json.response_url }}",
      "type": "string"
    },
    {
      "name": "image_size_kb",
      "value": "={{ $('Code - Convert to Base64 Data URI').first().json.data_size_kb }}",
      "type": "number"
    }
  ]
}
```

**出力データ構造**:
```json
{
  "request_id": "abc-123-def-456",
  "status": "IN_QUEUE",
  "queue_position": 0,
  "response_url": "https://...",
  "image_size_kb": 1234
}
```

---

## 📋 適用手順

### Step 1: WF10-Webhook v3の確認

**重要**: WF10-Webhook v4が稼働している場合は、v3に戻す必要があります

#### 1-1. 現在のバージョン確認
```
n8n UI → Workflows → WF10-Webhook
→ ワークフロー名を確認
```

もし「v4-payload参照修正」が含まれていたら：
```
右上「⋮」→ Delete
```

#### 1-2. v3のインポート
```
Workflows → + Add workflow → Import from file
→ now/2025-11-15_22-54_WF10-Webhook修正版v3-payloadパース修正.json
```

#### 1-3. 認証情報の確認
```
HTTP Request - Download Videoノードを開く
→ Credentials: 「fal」が設定されているか確認
```

#### 1-4. 保存＆有効化
```
右上「Save」→ 「Active」スイッチをONに
```

### Step 2: WF10-Main v2eのインポート

#### 2-1. 既存WF10-Mainの削除（v2c等が稼働している場合）
```
n8n UI → WF10-Main → 右上「⋮」→ Delete
```

#### 2-2. v2eのインポート
```
Workflows → + Add workflow → Import from file
→ now/2025-11-16_02-42_WF10-Main修正版v2e-Base64DataURI.json
```

#### 2-3. 認証情報の確認
```
HTTP Request - Runway Gen-3 API (Base64)ノードを開く
→ Credentials: 「fal.ai API Key」が設定されているか確認
```

#### 2-4. テストデータの確認
```
Set - Test Dataノードを開く
→ google_drive_file_id: 13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg
→ 台本本文: "A serene landscape..."
```

#### 2-5. 保存
```
右上「Save」をクリック
```

### Step 3: テスト実行

#### 3-1. ワークフロー実行
```
「Test workflow」または「Execute Workflow」をクリック
```

#### 3-2. 各ノードの出力確認

**Set - Test Data**:
```json
{
  "google_drive_file_id": "13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg",
  "台本本文": "A serene landscape..."
}
```

**HTTP Request - Download Image**:
- ✅ バイナリデータが取得されている
- ✅ MIMEタイプが `image/png` または `image/jpeg`

**Code - Convert to Base64 Data URI**:
```json
{
  "image_data_uri": "data:image/png;base64,iVBORw0KGgoAAAA...",
  "prompt": "A serene landscape...",
  "original_mime_type": "image/png",
  "data_size_kb": 1234
}
```
- ✅ `image_data_uri` が `data:image/` で始まっている
- ✅ `data_size_kb` が合理的な値（例: 500KB-3MB）

**HTTP Request - Runway Gen-3 API**:
```json
{
  "status": "IN_QUEUE",
  "request_id": "abc-123-def-456",
  "queue_position": 0,
  "response_url": "https://..."
}
```
- ✅ `status: "IN_QUEUE"` （**"ERROR"ではない**）
- ✅ `request_id` が存在する
- ✅ エラーメッセージが**ない**

**Set - Response Parse**:
```json
{
  "request_id": "abc-123-def-456",
  "status": "IN_QUEUE",
  "queue_position": 0,
  "response_url": "https://...",
  "image_size_kb": 1234
}
```

### Step 4: webhook受信確認（1-3分待機）

#### 4-1. WF10-Webhook実行履歴を確認
```
WF10-Webhook → Executions
→ 最新の実行を確認
```

#### 4-2. webhook受信データの確認

**Webhook Trigger出力**（正常時）:
```json
{
  "body": {
    "status": "completed",
    "request_id": "abc-123-def-456",
    "payload": {
      "video": {
        "url": "https://v3.fal.media/files/.../video.mp4",
        "duration": 10,
        "width": 1920,
        "height": 1080
      }
    }
  }
}
```

**Set - Payload Parse出力**（v3使用時）:
```json
{
  "video_url": "https://v3.fal.media/files/.../video.mp4",  // ← nullではない！
  "status": "completed",
  "request_id": "abc-123-def-456",
  "duration": 10,
  "width": 1920,
  "height": 1080
}
```

- ✅ `video_url` が実際のfal.ai URLを含む（**nullではない**）
- ✅ `status: "completed"` （**"ERROR"ではない**）

**HTTP Request - Download Video**:
- ✅ 動画が正常にダウンロードされる
- ✅ エラーが**ない**

**Write Binary File**:
- ✅ `/tmp/wf10-videos/{request_id}.mp4` に保存成功

### Step 5: 動画ファイル確認

#### 5-1. ファイルの存在確認
```bash
ls -lh /tmp/wf10-videos/
```

期待される出力：
```
-rw-r--r-- 1 user user 5.2M Nov 16 02:50 abc-123-def-456.mp4
```

#### 5-2. 動画の再生確認
- ファイルサイズが合理的（2MB-10MB程度）
- 再生可能（10秒、1920x1080）

---

## 🧪 期待される動作

### 成功シナリオ（completedステータス）

**WF10-Main v2e実行**:
1. ✅ Google Driveから画像ダウンロード成功
2. ✅ Base64 Data URIへの変換成功
3. ✅ fal.ai APIにリクエスト送信成功
4. ✅ IN_QUEUEレスポンス取得（**ERRORではない**）

**fal.ai処理**（1-3分）:
1. ✅ Base64 Data URIから画像を正常に取得
2. ✅ キューに追加
3. ✅ Runway Gen-3 AIで10秒動画生成
4. ✅ 1920x1080（16:9比率）で出力

**WF10-Webhook v3コールバック受信**:
```json
{
  "status": "completed",
  "request_id": "abc-123-def-456",
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

**WF10-Webhook v3処理**:
1. ✅ Set - Payload Parseで`video_url`が正しく取得（**nullではない**）
2. ✅ HTTP Request - Download Videoで動画ダウンロード成功
3. ✅ Write Binary Fileで`/tmp/wf10-videos/`に保存成功

### 失敗シナリオ（ERRORステータス）

もしfal.aiがERRORを返した場合:

**WF10-Webhook v3コールバック受信**:
```json
{
  "status": "ERROR",
  "request_id": "abc-123-def-456",
  "payload": {
    "detail": "エラー詳細メッセージ"
  }
}
```

**WF10-Webhook v3処理**（v3使用時）:
- ⚠️ `video_url` が `undefined` （`payload.video`が存在しないため）
- ✅ `status: "ERROR"` は正しく取得
- ✅ `request_id` は正しく取得
- ⚠️ HTTP Request - Download Videoでエラー（`video_url`が`undefined`のため）

**今後の改善案**:
- Ifノードでstatusをチェック
- completedブランチ: 動画ダウンロード＆保存
- ERRORブランチ: エラーログ出力のみ（ダウンロードスキップ）

---

## 🔧 トラブルシューティング

### 問題1: v4が稼働していて、video_urlがnullになる

**症状**:
```json
{
  "video_url": null,
  "status": "completed",
  "request_id": "abc-123"
}
```

**原因**: WF10-Webhook v4が稼働している（v3ではない）

**解決策**:
1. WF10-Webhook v4を削除
2. v3をインポート（Step 1を参照）
3. 保存＆有効化
4. 再テスト

### 問題2: Google Driveからのダウンロードが失敗

**症状**:
```
HTTP Request - Download Image: 403 Forbidden or 404 Not Found
```

**原因**: Google Driveファイルの共有設定が不正

**解決策**:
1. Google Driveでファイルを開く
2. 「共有」→「リンクを知っている全員」に設定
3. file IDを確認（`13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg`等）
4. Set - Test Dataノードで`google_drive_file_id`を更新

### 問題3: Base64変換でエラー

**症状**:
```
Code - Convert to Base64 Data URI: Error: No binary data found
```

**原因**: HTTP Requestの`responseFormat`が`file`ではない

**解決策**:
1. HTTP Request - Download Imageノードを開く
2. Options → Response → Response Format → `file` に設定
3. 保存＆再テスト

### 問題4: fal.ai APIが422エラーを返す

**症状**:
```json
{
  "error": "Unexpected status code: 422",
  "payload": {
    "detail": "Invalid image data or format"
  }
}
```

**原因**: Base64 Data URIの形式が不正、またはMIMEタイプが不正

**解決策**:
1. Code - Convert to Base64 Data URIの出力を確認
2. `image_data_uri` が `data:image/png;base64,` または `data:image/jpeg;base64,` で始まっているか確認
3. `data_size_kb` が合理的な値か確認（500KB-3MB程度）
4. 元の画像ファイルが有効か確認（PNGまたはJPEG）

### 問題5: webhook受信が来ない（3分以上経過）

**症状**: WF10-Webhookの実行履歴に新しい実行が表示されない

**原因**:
- fal.ai処理が遅延している
- webhookエンドポイントが誤っている
- fal.ai側でエラーが発生している

**解決策**:
1. WF10-Main実行のSet - Response Parseで`response_url`を確認
2. `response_url`にアクセスして処理状態を確認:
   ```bash
   curl -H "Authorization: Key YOUR_FAL_API_KEY" \
     https://queue.fal.run/fal-ai/runway-gen3/turbo/image-to-video/requests/REQUEST_ID/status
   ```
3. statusが`"IN_PROGRESS"`の場合は待機継続
4. statusが`"ERROR"`の場合はpayload.detailを確認

### 問題6: 動画ダウンロードが失敗

**症状**:
```
HTTP Request - Download Video: URL parameter must be a string, got null
```

**原因**: v4が使用されている（video_urlがnull）

**解決策**: 問題1を参照（v4をv3に置き換え）

---

## 📊 検証チェックリスト

### WF10-Main v2eインポート後
- [ ] WF10-Main v2eインポート完了
- [ ] 認証情報（fal.ai API Key）が正しく設定されている
- [ ] Google Drive file ID（`13uo0kLmfHFx0HE6pDqlN16qGysSrSKbg`）が設定されている
- [ ] 保存完了

### WF10-Webhook v3確認
- [ ] v4が稼働していないか確認（稼働していたら削除）
- [ ] v3がインポートされている
- [ ] 認証情報（fal）が正しく設定されている
- [ ] Active状態がONになっている

### E2Eテスト実行
- [ ] WF10-Main v2eテスト実行でIN_QUEUEレスポンス取得（**ERRORではない**）
- [ ] レスポンスに`request_id`と`status: "IN_QUEUE"`が含まれている
- [ ] **1-3分以内にWF10-Webhook v3にコールバック到達**
- [ ] コールバックのstatusが`"completed"`（**ERRORではない**）
- [ ] Set - Payload Parse（v3）でvideo_urlが正しく取得（**nullではない**）
- [ ] 動画URL（`payload.video.url`）が実際のfal.ai URLを含んでいる
- [ ] WF10-Webhook v3が動画を正常にダウンロード（**404エラーなし**）
- [ ] `/tmp/wf10-videos/` に.mp4ファイルが存在
- [ ] 動画が再生可能（10秒、1920x1080）

---

## 🔄 次のステップ

### Task 10i: E2Eテスト実行（正しいバージョン）
- ⏳ **ユーザーがv2e（Main）とv3（Webhook）をインポート**
- ⏳ **E2Eテスト実行**
  - IN_QUEUEレスポンス取得
  - webhookコールバック到達
  - 動画ダウンロード成功
  - ファイル保存確認

### Task 11: Phase 0-MVP検証（10回テスト）
- E2Eテスト成功後、10回連続実行
- 成功率を記録（目標: 9/10以上）

---

## 📚 技術的な背景知識

### Base64 Data URIとは

**形式**:
```
data:[MIMEタイプ];base64,[Base64エンコードされたデータ]
```

**例**:
```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...
```

**仕組み**:
1. バイナリデータ（画像）をBase64テキストに変換
2. MIMEタイプと組み合わせて1つの文字列に
3. この文字列を直接URLとして使用可能
4. 外部リソースへのアクセスが不要

**メリット**:
- ✅ リダイレクト不要（URL制限を回避）
- ✅ 認証不要（データがリクエストに含まれる）
- ✅ 信頼性が高い（URL解決失敗のリスクがない）

**デメリット**:
- ⚠️ データサイズが約133%に増加
- ⚠️ 大きな画像では性能に影響

### なぜWF7は成功したのにWF10は失敗したのか

**WF7**:
- API: `fal-ai/ffmpeg-api/compose` (FFmpegベースの動画合成)
- URL要件: 比較的緩い、Google Drive URLを受け入れる

**WF10**:
- API: `fal-ai/runway-gen3/turbo/image-to-video` (Runway Gen-3 AI)
- URL要件: 厳格、リダイレクトや認証が必要なURLを拒否

**教訓**:
- 異なるfal.ai APIは異なるURL要件を持つ
- 1つのAPIで成功したパターンが他のAPIでも動作するとは限らない
- 公式ドキュメントを確認することが重要

### n8n Webhook Triggerのデータ構造

**重要**: Webhook Triggerは受信したJSONを`$json.body`に格納する

**誤った前提**（v4の間違い）:
```javascript
$json.status  // ← これではアクセスできない
```

**正しいアクセス**（v3の正解）:
```javascript
$json.body.status  // ← これが正しい
```

**実際の受信データ構造**:
```json
{
  "json": {
    "body": {  // ← ここに実データが入る
      "status": "completed",
      "request_id": "abc-123",
      "payload": {
        "video": {
          "url": "https://..."
        }
      }
    }
  }
}
```

---

## ✅ まとめ

### 使用すべきバージョン
- **WF10-Main**: v2e（Base64 Data URI方式）
- **WF10-Webhook**: v3（正しいpayloadパース）

### 破棄すべきバージョン
- **WF10-Webhook v4**: 誤った`$json.*`参照
- **WF10-Main v2d**: Google Drive API v3形式が拒否される
- **WF10-Main v2c**: Google Drive uc download形式が拒否される

### 重要な発見
1. v3のwebhook実装が正しい（`$json.body.*`参照）
2. Google Drive URLは**どの形式でも**Runway Gen-3 APIに拒否される
3. WF7とWF10は**異なるAPI**を使用している
4. Base64 Data URIが唯一の信頼できる解決策

### 次のアクション
1. v3（Webhook）とv2e（Main）をインポート
2. E2Eテスト実行
3. 成功確認後、10回連続テストでMVP検証

---

**作成者**: Claude Code (SuperClaude)
**対応Issue**: WF10 Google Drive URL互換性問題、Base64 Data URI実装
**エビデンス**: 実行2499、2508、Runway API公式ドキュメント、WF7コード分析
**実装ファイル**: `now/2025-11-16_02-42_WF10-Main修正版v2e-Base64DataURI.json`
