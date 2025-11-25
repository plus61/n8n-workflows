# WF7 ffmpegワークロード運用ドキュメント

**対象**: Railway上のFastAPIレンダラー（Phase4b `/generate-single-video`, Phase4c concat）  
**共有リポジトリ**: `plus61/n8n-workflows`（branch: `project`）

---

## 1. アーキテクチャ概要

- `Dockerfile.fastapi`（lines 1-34）で `python:3.11-slim` をベースに `apt-get install ffmpeg libmagic1 curl`。  
- `render_server.py` を `/app` 配下にコピーし、ENTRYPOINTで `python3 /app/render_server.py` を起動。  
- `railway.toml`（lines 4-13）で `builder = "dockerfile"`, `dockerfilePath = "Dockerfile.fastapi"`, `startCommand = "python3 /app/render_server.py"`, `healthcheckPath = "/health"` を設定。  
- Railwayサービス `fastapi-server` が `/health` でヘルスチェックを行い、n8n Phase4b HTTPリクエストノードから `/generate-single-video` を呼ぶ構成。

---

## 2. デプロイ手順

1. GitHub `project` ブランチにDockerfile/コードをコミット。  
2. Railway UI → `fastapi-server` →「Connect Repo」で `plus61/n8n-workflows` を接続（未接続だとDockerfileが反映されない）。  
3. デプロイ完了後 `curl https://fastapi-server-production-xxxx.up.railway.app/health` が `{"status":"healthy"}` を返すことを確認。  
4. Phase4bワークフロー（ID `hfhZijyKIt1DjI1V`）のNode2をHTTP Requestで上記URLに向ける（`CURRENT_STATE.md`記載）。

---

## 3. ffmpegワークロードの現在課題

### 3.1 フォント未インストール問題（発生中）

- Railway上の `python:3.11-slim` にはフォントが含まれず、`drawtext` などテキスト系フィルタでエラーが発生。  
- 例: Phase4bで字幕やCTAテキストを焼き込む際に `Fontconfig error: Cannot load default config file` となる。  
- **対処案**: Dockerfileに `fonts-noto-cjk fonts-noto-color-emoji fonts-noto-core` 等を追加し、`fc-cache -fv` を実行。  

### 3.2 エラーが出た場合の確認ポイント

1. `railway logs -s fastapi-server` で ffmpeg の stderr を確認。  
2. `/tmp` など一時ファイルはコンテナ再起動で消えるため、必要ならS3等へ退避。  
3. `drawtext` 利用時は `fontfile=/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc` のようにフルパス指定を推奨。

---

## 4. 今後のタスク

1. Dockerfileにフォントパッケージを追加し再デプロイ。  
2. Phase4bテストペイロード（`now/2025-01-14_11-45_Phase4b-FastAPI-Endpoint-Design.md`）で字幕付きレンダリングが通るか確認。  
3. 成功したら `CURRENT_STATE.md` と `DECISIONS.md` に更新内容を記録。  
4. Phase4a→Phase4b→Phase4c E2Eを再実行し、最終動画にテキスト要素が正しく埋め込まれているか検証。

---

**メモ**: Railway環境では`/usr/share/fonts`配下のフォントのみが利用可能。追加フォントはDockerイメージに含めるか、起動時スクリプトでダウンロードする。
