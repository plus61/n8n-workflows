# WF7 動画レンダリング CLI

縦型ショート動画（1080×1920、30fps）を生成するPython CLIツールです。

## 機能

- ✅ JSON設定ベースの動画生成
- ✅ テンプレートシステム
- ✅ テキストオーバーレイ（テロップ）
- ✅ 背景動画/画像の合成
- ✅ BGM追加
- ✅ 字幕burn-in（SRT対応）
- ✅ サムネイル自動生成
- ✅ Dockerコンテナ化

## セットアップ

### ローカル環境

```bash
# 依存関係インストール
pip install -r requirements.txt

# ffmpegインストール（macOS）
brew install ffmpeg

# ffmpegインストール（Ubuntu）
sudo apt-get install ffmpeg
```

### Docker環境

```bash
# イメージビルド
docker build -t wf7-renderer .

# コンテナ実行
docker run -v $(pwd)/data:/data wf7-renderer \
  --script /data/script.json \
  --assets /data/assets.json \
  --template hook01 \
  --out /data/video.mp4
```

## 使用方法

### 基本的な使い方

```bash
python render_video.py \
  --script ./data/script.json \
  --assets ./data/assets.json \
  --template default \
  --out ./output/video.mp4
```

### 字幕付き動画

```bash
python render_video.py \
  --script ./data/script.json \
  --assets ./data/assets.json \
  --subtitle ./data/subtitle.srt \
  --template hook01 \
  --out ./output/video.mp4
```

## 入力ファイル形式

### script.json

```json
{
  "articleId": "note-abc123",
  "version": "1.0",
  "segments": [
    {
      "section": "hook",
      "telop": "MEO対策で集客アップ！",
      "narration": "こんにちは、今日はMEO対策について解説します。",
      "assetTag": "local business",
      "duration": 10
    },
    {
      "section": "pain",
      "telop": "お店が見つからない...",
      "narration": "多くの店舗が検索結果に表示されない問題を抱えています。",
      "assetTag": "empty store",
      "duration": 10
    },
    {
      "section": "solution",
      "telop": "Googleビジネスプロフィールを最適化",
      "narration": "Googleビジネスプロフィールを最適化することで、検索結果での表示順位が向上します。",
      "assetTag": "google maps",
      "duration": 15
    },
    {
      "section": "cta",
      "telop": "今すぐ最適化を始めよう！",
      "narration": "詳しくは概要欄のリンクからどうぞ。",
      "assetTag": "call to action",
      "duration": 10
    }
  ]
}
```

### assets.json

```json
{
  "articleId": "note-abc123",
  "version": "1.0",
  "assets": [
    {
      "assetTag": "local business",
      "assetIndex": 0,
      "fileUrl": "https://drive.google.com/.../asset0.jpg",
      "source": "pexels"
    },
    {
      "assetTag": "empty store",
      "assetIndex": 1,
      "fileUrl": "https://drive.google.com/.../asset1.jpg",
      "source": "unsplash"
    }
  ]
}
```

### templates/{template_id}.json

```json
{
  "font_family": "Arial",
  "font_size": 60,
  "text_color": [255, 255, 255],
  "text_bg_color": [0, 0, 0, 180],
  "text_position": "top",
  "animation": "fade",
  "bgm": "/path/to/bgm.mp3"
}
```

## 出力

- `video.mp4`: 完成動画（1080×1920、30fps、H.264）
- `video_thumb.jpg`: サムネイル画像（1080×1920）

## Cloud Run デプロイ

```bash
# イメージビルド & プッシュ
gcloud builds submit --tag gcr.io/PROJECT_ID/wf7-renderer

# Cloud Run デプロイ
gcloud run deploy wf7-renderer \
  --image gcr.io/PROJECT_ID/wf7-renderer \
  --platform managed \
  --region asia-northeast1 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 30m \
  --max-instances 4
```

## パフォーマンス

- **1本あたりの処理時間**: 約10分
- **同時処理数**: 最大4本（Cloud Run）
- **コスト**: 約2.5円/本（Cloud Run）

## トラブルシューティング

### ffmpegエラー

```bash
# ffmpegバージョン確認
ffmpeg -version

# 再インストール
brew reinstall ffmpeg  # macOS
sudo apt-get install --reinstall ffmpeg  # Ubuntu
```

### メモリ不足

- Cloud Runのメモリを2Gi→4Giに増量
- ローカル環境でスワップ領域を確保

### レンダリングタイムアウト

- Cloud Runのタイムアウトを30分→60分に延長
- 動画の長さを45秒以内に制限

## ライセンス

MIT License

## 作成者

WF7 SNS動画化プロジェクト

