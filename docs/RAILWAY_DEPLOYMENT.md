# Railway n8n + Python環境 デプロイガイド

## 概要

このDockerfileは、n8n公式イメージにPython 3 + MoviePy + FFmpegを統合したカスタムイメージです。

**Debian版**: Alpine互換性問題を解決し、安定性と互換性を優先。

## 統合内容

- **ベースイメージ**: `n8nio/n8n:latest-debian` (Debian Linux)
- **Python**: 3.x (Debian標準)
- **FFmpeg**: 動画エンコーダー
- **MoviePy**: 1.0.3 (動画編集ライブラリ)
- **Pillow**: 10.1.0 (画像処理)
- **numpy**: 1.24.3 (数値計算)
- **WF7 レンダラー**: `/app/render_video.py`
- **利点**: 高い互換性、安定したパッケージビルド

## Railway デプロイ手順

### 1. Railwayプロジェクト設定

1. Railway Dashboard → プロジェクト選択
2. n8nサービスを選択
3. Settings → Deploy タブ

### 2. Dockerfile指定

**Custom Dockerfile Path**:
```
Dockerfile.n8n-python
```

### 3. Build Context設定

**Root Directory**:
```
/
```

**Watch Paths** (オプション):
```
Dockerfile.n8n-python
workflows/wf7-video-renderer/**
```

### 4. 環境変数確認

以下の環境変数が設定されていることを確認：

```bash
# n8n基本設定
N8N_HOST=https://n8n-python-production-344b.up.railway.app
N8N_PORT=5678
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app

# Python環境
PYTHONUNBUFFERED=1

# Google Drive OAuth2 (既存)
# Notion API Token (既存)
```

### 5. デプロイ実行

```bash
# Railwayが自動的に以下を実行:
# 1. Dockerfile.n8n-python をビルド
# 2. n8n + Python + FFmpeg統合イメージ作成
# 3. コンテナ起動
# 4. ヘルスチェック (port 5678)
```

### 6. 検証

#### Python環境確認
```bash
# Railway CLIまたはDashboard Console経由
python --version
# → Python 3.11.x

ffmpeg -version
# → ffmpeg version X.X.X

pip list | grep moviepy
# → moviepy 1.0.3
```

#### render_video.py確認
```bash
ls -la /app/render_video.py
# → -rwxr-xr-x 1 node node ... /app/render_video.py

python /app/render_video.py --help
# → WF7 動画レンダリング CLI ヘルプ表示
```

## WF7 Phase4での利用

Phase4ワークフロー内で以下のコマンドを実行：

```python
python /app/render_video.py \
  --script /tmp/script_${articleId}.json \
  --assets /tmp/assets_${articleId}.json \
  --template default \
  --out /tmp/video_${articleId}.mp4
```

### 入力ファイル
- `/tmp/script_${articleId}.json`: Notionから読み取った台本データ
- `/tmp/assets_${articleId}.json`: Notionから読み取ったアセットメタデータ
- `/tmp/asset_${articleId}_${index}.jpg`: Google Driveからダウンロードした画像

### 出力ファイル
- `/tmp/video_${articleId}.mp4`: レンダリングされた動画 (1080x1920)
- `/tmp/video_${articleId}_thumb.jpg`: サムネイル画像

## トラブルシューティング

### Alpine版でのビルドエラー（Python 3.12互換性問題）

**原因**: Alpine Linux + Python 3.12 + 古いパッケージの互換性問題
- `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'`
- Python 3.12で削除されたAPIを古いパッケージが使用
- numpy 1.24.3 のビルドに失敗

**解決策（本Dockerfileに適用済み）**:
```dockerfile
# Debian版のn8nイメージを使用
FROM n8nio/n8n:latest-debian

# Debianの安定したPython環境
RUN apt-get update && apt-get install -y \
    python3 python3-pip ffmpeg
```
→ **互換性問題を根本解決、ビルド時間5-7分**

### ビルドエラー: "requirements.txt not found"

**原因**: Docker Build Contextがプロジェクトルートではない

**解決策**:
```bash
# Railway Settings → Build & Deploy
# Root Directory: "/" (プロジェクトルート)
# Dockerfile Path: "Dockerfile.n8n-python"
```

### Python実行エラー: "python: not found"

**原因**: Pythonシンボリックリンクが作成されていない

**解決策**: Dockerfile内で以下を確認
```dockerfile
RUN ln -sf /usr/bin/python3 /usr/bin/python
```

### FFmpegエラー: "ffmpeg: not found"

**原因**: FFmpegがインストールされていない

**解決策**: Dockerfile内で`apt-get install ffmpeg`を確認

### MoviePyエラー: "No module named 'moviepy'"

**原因**: requirements.txtのインストールに失敗

**解決策**: ビルドログで`pip3 install`の成功を確認

### Debian版のメリット

- **互換性**: Pythonパッケージのビルドが安定
- **パッケージ**: apt経由で多くのプリビルドパッケージが利用可能
- **安定性**: 本番環境で実績のあるDebian環境
- **デメリット**: イメージサイズがAlpine版より大きい（約+200MB）

## 注意事項

### メモリ使用量

- 動画レンダリングは**メモリ集約的**
- Railway Free Plan: 512MB (不十分の可能性)
- **推奨**: Hobby Plan以上 (8GB RAM)

### ビルド時間

- **Debian版ビルド時間**:
  - 初回ビルド: 約**5-7分**
  - Python + FFmpeg + MoviePy/Pillow/numpyのインストール
  - キャッシュ有効後: 約1-2分
- **Alpine版との比較**: 互換性問題を解決し、安定したビルド

### ストレージ

- `/tmp/`ディレクトリは**エフェメラル**
- コンテナ再起動で消去
- 動画ファイルは即座にFile Serverまたはクラウドストレージへ転送

## 次のステップ

1. ✅ Dockerfileデプロイ
2. ✅ Python環境検証
3. ⏳ Phase4 E2Eテスト実行
4. ⏳ 動画出力確認

---

**作成日**: 2025-11-01
**対象環境**: Railway n8n Production
# Force redeploy 2025年 11月 6日 木曜日 01時07分20秒 JST
