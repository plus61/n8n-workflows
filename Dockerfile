# Railway n8n Dockerfile (n8n専用 - Creatomate統合版)
# Build timestamp: 2025-11-11 01:30 JST
# Note: Phase4はCreatomate外部レンダリングを使用（FastAPI不要）
# Version: 1.39.0+ required for PR #9157 (fixes "No Webhook node found" error with Respond to Webhook)
# Force rebuild to clear Railway cache - disable Metal Build if issues persist
FROM n8nio/n8n:1.68.3

# Verify n8n installation
RUN which n8n && n8n --version || echo "n8n not found in base image"

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

# n8n環境変数設定（Railwayの環境変数で上書き可能）
ENV N8N_PROTOCOL=https
ENV N8N_HOST=n8n-python-production-344b.up.railway.app
ENV WEBHOOK_URL=https://n8n-python-production-344b.up.railway.app/

# Railway healthcheck configuration
ENV RAILWAY_HEALTHCHECK_TIMEOUT_SEC=300

# n8n port (RailwayのPORT環境変数を使用)
EXPOSE 5678

# n8n標準起動（Railwayが自動的にPORTを注入）
# 完全パスを指定してENTRYPOINT問題を回避
ENTRYPOINT []
CMD ["/usr/local/bin/node", "/usr/local/bin/n8n", "start"]
