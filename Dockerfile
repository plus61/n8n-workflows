# Railway n8n Dockerfile (n8n専用 - Creatomate統合版)
# Build timestamp: 2025-11-06 02:30 JST
# Note: Phase4はCreatomate外部レンダリングを使用（FastAPI不要）
FROM n8nio/n8n:latest

# rootユーザーで追加パッケージをインストール
USER root

# FFmpeg + 日本語フォントのインストール（Code node用）
RUN apk add --no-cache \
    ffmpeg \
    font-noto-cjk \
    fontconfig \
    bash

# フォントキャッシュ更新
RUN fc-cache -fv

# nodeユーザーに戻す（n8nの標準ユーザー）
USER node

# Railway healthcheck configuration
ENV RAILWAY_HEALTHCHECK_TIMEOUT_SEC=300

# n8n port
EXPOSE 5678

# n8n標準のentrypointとコマンドを使用
# Railway's PORT env var will be mapped to 5678
CMD ["n8n"]
