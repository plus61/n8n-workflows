FROM python:3.11-slim

# ffmpegインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係（FastAPIサーバー用）
COPY requirements-server.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements-server.txt

# アプリケーションコピー
COPY render_server.py /app/
COPY render_video_ffmpeg.py /app/
COPY phase4c_ffmpeg_concat.py /app/
COPY templates/ /app/templates/

# 実行権限
RUN chmod +x /app/render_server.py /app/render_video_ffmpeg.py

# ポート公開
EXPOSE 8000

# FastAPIサーバー起動
ENTRYPOINT ["python3", "/app/render_server.py"]

