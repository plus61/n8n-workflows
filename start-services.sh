#!/bin/bash
# WF7 Phase4: Start both n8n and FFmpeg renderer server

set -e

echo "================== WF7 Phase4 Multi-Service Startup =================="
echo "🔧 Starting multi-service container..."

# Start n8n in background
echo "🚀 Starting n8n on port 5678 (background)..."
n8n > /tmp/n8n.log 2>&1 &
N8N_PID=$!

# Wait for n8n to be ready
echo "⏳ Waiting for n8n to start..."
sleep 10

# Check if n8n started successfully
if ps -p $N8N_PID > /dev/null; then
    echo "✅ n8n started successfully (PID: $N8N_PID)"
else
    echo "❌ n8n failed to start"
    cat /tmp/n8n.log
    exit 1
fi

echo "🚀 Starting FFmpeg HTTP renderer server on port 8000 (foreground)..."
echo "================================================================"
# Run FastAPI in foreground
exec python3 /app/render_server.py
