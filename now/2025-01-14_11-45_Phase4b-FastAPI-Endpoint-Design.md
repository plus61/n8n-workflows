# Phase4b FastAPI Endpoint Design

**作成日時**: 2025-11-14 11:45:49 JST

## 概要

n8nのPython Code Nodeでsubprocess.run()がブロックされる問題を解決するため、既存のFastAPIサーバー（render_server.py）に新しいエンドポイント `/generate-single-video` を追加する。

## 背景

### 問題
- Phase4b実行でエラー: "RuntimeError: Blocked for security reasons"
- n8nのPython Code Nodeでsubprocess実行が禁止されている
- ワークフローID: hfhZijyKIt1DjI1V

### 解決策
- FastAPIサーバーはn8nサンドボックス外で動作するため、subprocess使用可能
- 既存の `/concat-videos` エンドポイントで実証済み

## エンドポイント仕様

### URL
```
POST /generate-single-video
```

### Request Model
```python
class GenerateSingleVideoRequest(BaseModel):
    """Single video generation request for Phase4b"""
    section: str                # "hook", "intro", "point1", etc.
    duration: int               # Video duration in seconds (3-20)
    image_url: str              # Cloudinary image URL
    motion_prompt: str          # Motion description (currently unused)
    text: str                   # Subtitle text
    script_id: str              # Notion script ID
```

### Response Model
```python
{
    "success": true,
    "section": "hook",
    "duration": 3,
    "videoData": "base64_encoded_video_data...",
    "video_size_bytes": 1234567,
    "script_id": "2aa68d5c-2986-81b0-b488-e2d7ee8026b7",
    "motion_prompt": "dramatic zoom in effect",
    "text": "フックテキスト",
    "filename": "video_hook.mp4",
    "mimeType": "video/mp4"
}
```

## 処理フロー

### 1. 画像ダウンロード
```python
response = requests.get(image_url, timeout=30)
response.raise_for_status()
```

### 2. FFmpeg動画生成
```bash
ffmpeg -loop 1 -i input.png -t {duration} \
    -c:v libx264 -pix_fmt yuv420p \
    -vf scale=1080:1920 \
    -r 30 -y output.mp4
```

**パラメータ**:
- `-loop 1`: 静止画をループ
- `-i input.png`: 入力画像
- `-t {duration}`: 動画の長さ（秒）
- `-c:v libx264`: H.264コーデック
- `-pix_fmt yuv420p`: 互換性のためのピクセルフォーマット
- `-vf scale=1080:1920`: 縦型動画（Instagram Reels用）
- `-r 30`: 30fps
- `-y`: 上書き確認なし

### 3. Base64エンコード
```python
with open(output_path, 'rb') as f:
    video_data = f.read()
video_b64 = base64.b64encode(video_data).decode('utf-8')
```

### 4. 一時ファイルクリーンアップ
```python
os.remove(input_path)
os.remove(output_path)
```

## エラーハンドリング

### タイムアウト設定
- 画像ダウンロード: 30秒
- FFmpeg実行: 60秒（duration * 2 + 10秒のマージン）

### エラーケース
1. **画像ダウンロード失敗**
   - HTTPException(500, detail="画像ダウンロード失敗: {error}")

2. **FFmpeg実行失敗**
   - HTTPException(500, detail="FFmpeg実行エラー: {stderr}")

3. **FFmpegタイムアウト**
   - HTTPException(504, detail="FFmpeg実行タイムアウト")

4. **出力ファイル生成失敗**
   - HTTPException(500, detail="動画ファイルが生成されませんでした")

## Phase4bワークフロー統合

### 既存ノード構成
1. **Execute Workflow Trigger** (受信)
2. **Code - Generate Video with ffmpeg** ← ❌ ブロックされる
3. **HTTP Request - Upload to Cloudinary** (Cloudinaryアップロード)
4. **Code - Build Video Metadata** (メタデータ結合)

### 修正後ノード構成
1. **Execute Workflow Trigger** (受信)
2. **HTTP Request - Generate Video** ← ✅ FastAPI呼び出し
3. **HTTP Request - Upload to Cloudinary** (変更なし)
4. **Code - Build Video Metadata** (変更なし)

### Node 2の新しい設定
```json
{
  "method": "POST",
  "url": "https://n8n-python-production-344b.up.railway.app/generate-single-video",
  "authentication": "none",
  "contentType": "json",
  "jsonBody": {
    "section": "={{ $json.section }}",
    "duration": "={{ $json.duration }}",
    "image_url": "={{ $json.image_url }}",
    "motion_prompt": "={{ $json.motion_prompt }}",
    "text": "="{{ $json.text }}",
    "script_id": "={{ $json.script_id }}"
  },
  "options": {
    "timeout": 90000
  }
}
```

### Node 3の期待入力（変更なし）
FastAPIレスポンスから以下を使用：
- `cloudinary_file`: `data:video/mp4;base64,{videoData}`
- `cloudinary_upload_preset`: "n8n_meo_wf7_slide"
- `cloudinary_cloud_name`: "drzmodro8"
- `cloudinary_folder`: "n8n_meo_wf7_slide"

### Node 4の期待入力（変更なし）
- FastAPIレスポンスメタデータ
- Cloudinaryアップロードレスポンス

## 実装計画

### Step 1: Pydanticモデル追加
render_server.pyに追加（line 200付近）

### Step 2: エンドポイント実装
render_server.pyに追加（line 283付近、/healthの前）

### Step 3: デプロイ
Railway自動デプロイ（git push後）

### Step 4: ワークフロー修正
n8n UIでNode 2をHTTP Requestに変更

### Step 5: テスト
- 単一スライドテスト
- Phase4a→Phase4b統合テスト（7スライド）

## テストデータ

### 単一スライドテスト
```json
{
  "section": "hook",
  "duration": 3,
  "image_url": "https://res.cloudinary.com/drzmodro8/image/upload/v1763015200/n8n_meo_wf7_slide/fd4zupp1yes4of1ccwtg.png",
  "motion_prompt": "dramatic zoom in effect, professional business style",
  "text": "フックテキストがありません",
  "script_id": "2aa68d5c-2986-81b0-b488-e2d7ee8026b7"
}
```

### 期待される出力
```json
{
  "success": true,
  "section": "hook",
  "duration": 3,
  "videoData": "AAAAIGZ0eXBpc29tAAACAG...",
  "video_size_bytes": 150000,
  "script_id": "2aa68d5c-2986-81b0-b488-e2d7ee8026b7",
  "motion_prompt": "dramatic zoom in effect, professional business style",
  "text": "フックテキストがありません",
  "filename": "video_hook.mp4",
  "mimeType": "video/mp4"
}
```

## 既存パターンとの一貫性

### /concat-videos との比較
| 項目 | /concat-videos | /generate-single-video |
|------|----------------|------------------------|
| **入力** | 7つの動画URL | 1つの画像URL + duration |
| **処理** | 動画ダウンロード→結合 | 画像ダウンロード→動画生成 |
| **FFmpeg** | concat | loop + scale |
| **出力** | base64動画データ | base64動画データ |
| **エラー処理** | HTTPException | HTTPException |
| **タイムアウト** | 600秒 | 90秒 |

## セキュリティ考慮事項

### 入力検証
- duration: 1-20秒に制限
- image_url: Cloudinary URLのみ許可（ホワイトリスト）
- section: 固定値リストのみ許可

### リソース制限
- タイムアウト: 90秒
- 一時ファイル: 確実にクリーンアップ
- メモリ: FFmpegのメモリ使用量を監視

### エラー情報
- 内部パスを露出しない
- ユーザーフレンドリーなエラーメッセージ
- 詳細なログは標準出力に記録

## 成功基準

### 機能要件
- ✅ 3-20秒の動画を正確な長さで生成
- ✅ 1080x1920（縦型）解像度
- ✅ 30fps、H.264コーデック
- ✅ Base64エンコードで返却

### 非機能要件
- ✅ 90秒以内に処理完了
- ✅ エラー時も適切なレスポンス
- ✅ 一時ファイルの確実なクリーンアップ
- ✅ 既存エンドポイントとの一貫性

### 統合要件
- ✅ Phase4bワークフローと完全互換
- ✅ Node 3, 4は変更不要
- ✅ Phase4a→Phase4b→Phase4c E2E動作

## 参考情報

### 既存ファイル
- FastAPIサーバー: `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/render_server.py`
- Phase4bワークフロー: hfhZijyKIt1DjI1V

### 関連ドキュメント
- `/Users/yuichiroooosuger/Desktop/n8n-workflows/docs/implementation/WF7-Phase4b-FAL-Duration-Fix.md`

### テスト実行
- Phase4a Webhook: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator`
- テストペイロード: `{"script_id": "2aa68d5c-2986-81b0-b488-e2d7ee8026b7"}`
