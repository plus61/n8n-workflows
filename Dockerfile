# Railway n8n + Python環境統合 Dockerfile (Alpine版 - Phase4 FastAPI対応)
# Build timestamp: 2025-11-06 01:22 JST
FROM n8nio/n8n:latest

# rootユーザーで追加パッケージをインストール
USER root

# Python + FFmpeg + supervisord + 日本語フォントのインストール
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-numpy \
    py3-pillow \
    ffmpeg \
    font-noto-cjk \
    fontconfig \
    bash \
    supervisor

# フォントキャッシュ更新
RUN fc-cache -fv

# Pythonシンボリックリンク作成
RUN ln -sf /usr/bin/python3 /usr/bin/python

# 軽量な追加パッケージのみpipでインストール（プリビルド版を使うのでビルド不要）
RUN pip3 install --no-cache-dir --break-system-packages \
    moviepy==1.0.3 \
    decorator==4.4.2 \
    tqdm==4.62.0 \
    imageio==2.9.0 \
    imageio-ffmpeg==0.4.5 \
    requests==2.31.0

# FastAPI Server dependencies for Phase4
RUN pip3 install --no-cache-dir --break-system-packages \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    pydantic==2.5.3 \
    python-multipart==0.0.6 \
    Pillow==10.2.0

# WF7 renderers and templates
RUN mkdir -p /app
COPY workflows/wf7-video-renderer/render_video.py /app/render_video.py
COPY workflows/wf7-video-renderer/render_video_ffmpeg.py /app/render_video_ffmpeg.py
COPY workflows/wf7-video-renderer/render_server.py /app/render_server.py
COPY workflows/wf7-video-renderer/templates /app/templates

# Supervisord configuration
COPY supervisord.conf /etc/supervisord.conf

# 実行権限付与
RUN chmod +x /app/render_video.py /app/render_video_ffmpeg.py /app/render_server.py

# supervisordはrootユーザーで実行する必要があるため、USER nodeに戻さない

# Railway healthcheck configuration
# PORT environment variable will be injected by Railway at runtime
ENV RAILWAY_HEALTHCHECK_TIMEOUT_SEC=300

# n8n + FFmpeg server ports
# Note: Railway will use PORT env var for healthcheck
EXPOSE 5678 8000

# Override BOTH entrypoint and CMD to avoid n8n's docker-entrypoint.sh issues
# The entrypoint script modifies the environment in ways that hide our installed packages
ENTRYPOINT []
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
