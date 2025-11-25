#!/bin/bash
# Phase4b Fix Verification Test
# Created: 2025-01-14 23:48 JST
# Purpose: Test if Phase4b FFmpeg fix (-crf 23, -preset fast) is deployed

echo "========================================="
echo "Phase4b Fix Verification Test"
echo "Testing /generate-single-video endpoint"
echo "========================================="
echo ""
echo "Expected result: Video size 500KB-1MB (was 10KB before fix)"
echo ""

# Test with a simple 3-second video
curl -X POST 'https://n8n-python-production-344b.up.railway.app/generate-single-video' \
  -H 'Content-Type: application/json' \
  --data '{
    "section": "test-fix",
    "duration": 3,
    "image_url": "https://res.cloudinary.com/drzmodro8/image/upload/v1763128692/n8n_meo_wf7_slide/a30kefxj6akbgseu1byh.png",
    "motion_prompt": "test fix",
    "text": "test",
    "script_id": "fix-verification"
  }' \
  -w '\n\n=== HTTP Response ===\nStatus Code: %{http_code}\nTotal Time: %{time_total}s\n' \
  -o /tmp/phase4b-response.json

echo ""
echo "========================================="
echo "Response Details:"
echo "========================================="

# Parse response and extract video size
if [ -f /tmp/phase4b-response.json ]; then
    cat /tmp/phase4b-response.json | python3 -m json.tool 2>/dev/null || cat /tmp/phase4b-response.json

    # Extract video size if present
    VIDEO_SIZE=$(cat /tmp/phase4b-response.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('video_size_bytes', 'N/A'))" 2>/dev/null)

    if [ "$VIDEO_SIZE" != "N/A" ]; then
        echo ""
        echo "========================================="
        echo "Video Size Analysis:"
        echo "========================================="
        echo "Raw bytes: $VIDEO_SIZE"

        # Convert to KB
        VIDEO_SIZE_KB=$(echo "scale=2; $VIDEO_SIZE / 1024" | bc)
        echo "Size (KB): $VIDEO_SIZE_KB"

        # Check if fix is applied
        if (( $(echo "$VIDEO_SIZE > 100000" | bc -l) )); then
            echo "✅ FIX APPLIED: Video size is >100KB (expected 500KB-1MB)"
        else
            echo "❌ FIX NOT APPLIED: Video size is still <100KB (expected >500KB)"
            echo "   Current deployment is still using old code"
        fi
    fi
fi

echo ""
echo "========================================="
echo "Test completed at $(date +'%Y-%m-%d %H:%M:%S %Z')"
echo "========================================="
