#!/bin/bash
# Phase4c Manual Test Script
# Created: 2025-11-14 23:09:20 JST
# Purpose: Test Phase4c video concatenation with Phase4b outputs

echo "========================================="
echo "Phase4c Manual Test - Video Concatenation"
echo "Created: 2025-11-14 23:09:20 JST"
echo "========================================="
echo ""
echo "Testing Phase4c with 7 videos from Phase4b executions 2198-2204"
echo "Total duration: 80 seconds (3+10+13+13+14+20+7)"
echo ""

curl -X POST 'https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4c-video-concatenator' \
  -H 'Content-Type: application/json' \
  --data '{
    "script_id": "2aa68d5c-2986-815c-aba4-da72d9830bf3",
    "videos_metadata": [
      {
        "section": "hook",
        "duration": 3,
        "video_url": "https://res.cloudinary.com/drzmodro8/video/upload/v1763128709/n8n_meo_wf7_slide/v2p0yalcxevxpizmss8q.mp4",
        "cloudinary_public_id": "n8n_meo_wf7_slide/v2p0yalcxevxpizmss8q"
      },
      {
        "section": "intro",
        "duration": 10,
        "video_url": "https://res.cloudinary.com/drzmodro8/video/upload/v1763128724/n8n_meo_wf7_slide/bd8msz7htv3sslomcf9z.mp4",
        "cloudinary_public_id": "n8n_meo_wf7_slide/bd8msz7htv3sslomcf9z"
      },
      {
        "section": "point1",
        "duration": 13,
        "video_url": "https://res.cloudinary.com/drzmodro8/video/upload/v1763128740/n8n_meo_wf7_slide/flf278tnfnvdseuqhpxa.mp4",
        "cloudinary_public_id": "n8n_meo_wf7_slide/flf278tnfnvdseuqhpxa"
      },
      {
        "section": "point2",
        "duration": 13,
        "video_url": "https://res.cloudinary.com/drzmodro8/video/upload/v1763128756/n8n_meo_wf7_slide/u0hifxkzygy8nat7wxw8.mp4",
        "cloudinary_public_id": "n8n_meo_wf7_slide/u0hifxkzygy8nat7wxw8"
      },
      {
        "section": "point3",
        "duration": 14,
        "video_url": "https://res.cloudinary.com/drzmodro8/video/upload/v1763128764/n8n_meo_wf7_slide/ksjhmo6bmyqftjuo7vwo.mp4",
        "cloudinary_public_id": "n8n_meo_wf7_slide/ksjhmo6bmyqftjuo7vwo"
      },
      {
        "section": "summary",
        "duration": 20,
        "video_url": "https://res.cloudinary.com/drzmodro8/video/upload/v1763128783/n8n_meo_wf7_slide/cp9r16ucftizufnftnr9.mp4",
        "cloudinary_public_id": "n8n_meo_wf7_slide/cp9r16ucftizufnftnr9"
      },
      {
        "section": "cta",
        "duration": 7,
        "video_url": "https://res.cloudinary.com/drzmodro8/video/upload/v1763128791/n8n_meo_wf7_slide/jpjnxilosasdeod8u5ys.mp4",
        "cloudinary_public_id": "n8n_meo_wf7_slide/jpjnxilosasdeod8u5ys"
      }
    ]
  }' \
  -v

echo ""
echo "========================================="
echo "Test completed at $(date +'%Y-%m-%d %H:%M:%S %Z')"
echo "========================================="
