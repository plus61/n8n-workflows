#!/bin/bash

# Phase4c NEW 10-node Workflow Test Script
# Tests the simplified Phase4c workflow (Exra8DkAfWsmOPiE)

echo "=== Phase4c NEW Workflow Test ==="
echo "Workflow ID: Exra8DkAfWsmOPiE"
echo "Nodes: 10 (simplified from 26)"
echo ""

# Step 1: Activate workflow
echo "[Step 1] Activating workflow..."
# Note: Must activate in n8n UI first as MCP doesn't support activation yet

# Step 2: Send test webhook
echo "[Step 2] Sending test webhook..."
WEBHOOK_URL="https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4c-video-concatenator"
PAYLOAD_FILE="data/test-phase4c-new-webhook-payload.json"

echo "URL: $WEBHOOK_URL"
echo "Payload: $PAYLOAD_FILE"
echo ""

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d @"$PAYLOAD_FILE" \
  -v \
  2>&1 | tee /tmp/phase4c-new-test-curl.log

echo ""
echo ""

# Step 3: Check result
if [ -f /tmp/phase4c-new-test-curl.log ]; then
  echo "[Step 3] Checking result..."

  # Extract HTTP status code
  STATUS_CODE=$(grep "< HTTP" /tmp/phase4c-new-test-curl.log | tail -1 | awk '{print $3}')
  echo "HTTP Status: $STATUS_CODE"

  # Extract response body
  echo ""
  echo "Response:"
  grep -A 100 "^{" /tmp/phase4c-new-test-curl.log | jq '.' 2>/dev/null || grep -A 100 "^{" /tmp/phase4c-new-test-curl.log
fi

echo ""
echo "=== Test Complete ==="
echo ""
echo "Next steps:"
echo "1. Check n8n UI for execution details"
echo "2. Verify FAL FFmpeg API was called"
echo "3. Check final_video_url in response"
echo "4. Compare with old 26-node workflow"
