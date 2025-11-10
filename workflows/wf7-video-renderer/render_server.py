#!/usr/bin/env python3
"""
WF7 FFmpeg Video Renderer FastAPI Server
Wraps render_video_ffmpeg.py CLI tool as an HTTP API for n8n integration
"""

import base64
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="WF7 FFmpeg Video Renderer")


class Asset(BaseModel):
    """Asset data model"""
    assetIndex: int
    assetTag: str
    imageData: str  # Base64-encoded image data


class RenderRequest(BaseModel):
    """Render request model"""
    articleId: str
    script: Dict[str, Any]
    assets: List[Asset]
    bgm: str | None = None
    narration: str | None = None


@app.post("/render")
async def render_video(request: RenderRequest):
    """
    Render video from script and assets

    Expects:
    {
        "articleId": "article-123",
        "script": { "video_script": { "segments": [...] } },
        "assets": [
            {"assetIndex": 0, "assetTag": "scene1", "imageData": "base64..."},
            {"assetIndex": 1, "assetTag": "scene2", "imageData": "base64..."}
        ]
    }

    Returns:
    {
        "articleId": "article-123",
        "videoData": "base64...",
        "thumbData": "base64...",
        "duration": 15.5,
        "mimeType": "video/mp4"
    }
    """

    # Create temp directory for processing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # 1. Write script.json
        script_path = tmp_path / "script.json"
        script_data = {
            "articleId": request.articleId,
            "version": "1.0",
            "createdAt": "2025-11-05",
            "video_script": request.script
        }
        script_path.write_text(json.dumps(script_data, ensure_ascii=False, indent=2))

        # 2. Write assets.json and decode images
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir(exist_ok=True)

        assets_data = {
            "articleId": request.articleId,
            "assets": []
        }

        for asset in request.assets:
            # Decode base64 image data
            image_data = base64.b64decode(asset.imageData)

            # Determine file extension from data (simple JPEG check)
            ext = "jpg" if image_data.startswith(b'\xff\xd8\xff') else "png"

            # Write image file
            image_path = assets_dir / f"{asset.assetTag}.{ext}"
            image_path.write_bytes(image_data)

            assets_data["assets"].append({
                "assetIndex": asset.assetIndex,
                "assetTag": asset.assetTag,
                "imagePath": str(image_path)
            })

        assets_path = tmp_path / "assets.json"
        assets_path.write_text(json.dumps(assets_data, ensure_ascii=False, indent=2))

        # 3. Set output paths
        output_video = tmp_path / f"{request.articleId}.mp4"

        # 4. Build command for render_video_ffmpeg.py
        cmd = [
            "python3",
            "/app/render_video_ffmpeg.py",
            "--script", str(script_path),
            "--assets", str(assets_path),
            "--out", str(output_video)
        ]

        # Add optional parameters
        if request.bgm:
            bgm_path = tmp_path / "bgm.mp3"
            bgm_path.write_bytes(base64.b64decode(request.bgm))
            cmd.extend(["--bgm", str(bgm_path)])

        if request.narration:
            narration_path = tmp_path / "narration.mp3"
            narration_path.write_bytes(base64.b64decode(request.narration))
            cmd.extend(["--narration", str(narration_path)])

        # 5. Execute rendering
        print(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=600
            )

            if result.returncode != 0:
                # Return last 50 lines of stderr on error
                stderr_lines = result.stderr.strip().split('\n')
                stderr_tail = '\n'.join(stderr_lines[-50:]) if len(stderr_lines) > 50 else result.stderr
                raise HTTPException(
                    status_code=500,
                    detail=f"FFmpeg rendering failed: {stderr_tail}"
                )

            print(result.stdout)

        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=504,
                detail="FFmpeg rendering timeout (600s limit exceeded)"
            )

        # 6. Read output files
        if not output_video.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Output video not found: {output_video}"
            )

        video_data = output_video.read_bytes()
        video_b64 = base64.b64encode(video_data).decode('utf-8')

        # Check for thumbnail
        thumb_path = tmp_path / f"{request.articleId}_thumb.jpg"
        thumb_b64 = None
        if thumb_path.exists():
            thumb_data = thumb_path.read_bytes()
            thumb_b64 = base64.b64encode(thumb_data).decode('utf-8')

        # Extract duration from ffprobe (simple approach)
        try:
            duration_cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(output_video)
            ]
            duration_result = subprocess.run(
                duration_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 0.0
        except Exception:
            duration = 0.0

        # 7. Return response with base64-encoded data
        return {
            "articleId": request.articleId,
            "videoData": video_b64,
            "thumbData": thumb_b64,
            "duration": duration,
            "mimeType": "video/mp4"
        }


class ConcatVideoRequest(BaseModel):
    """Video concatenation request model for Phase 4c"""
    script_id: str
    videos_metadata: List[Dict[str, Any]]


@app.post("/concat-videos")
async def concat_videos_endpoint(request: ConcatVideoRequest):
    """
    Phase 4c: Concatenate 7 videos into final MP4

    Expects:
    {
        "script_id": "29b68d5c-2986-817f-xxx",
        "videos_metadata": [
            {
                "section": "hook",
                "duration": 3,
                "video_url": "https://v3b.fal.media/files/...",
                "filename": "video_1_hook.mp4"
            },
            ... 7 videos total
        ]
    }

    Returns:
    {
        "success": true,
        "script_id": "...",
        "final_video_url": "...",  # or base64 data
        "total_duration": 80,
        "videos_count": 7
    }
    """
    import sys
    import os

    # Add current directory to Python path to import phase4c module
    sys.path.insert(0, os.path.dirname(__file__))

    try:
        from phase4c_ffmpeg_concat import concat_videos

        # Call the concat function
        input_data = {
            "script_id": request.script_id,
            "videos_metadata": request.videos_metadata
        }

        result = concat_videos(input_data)

        # Read the final video file and encode as base64
        output_path = result.get("output_video_path")
        if output_path and os.path.exists(output_path):
            with open(output_path, "rb") as f:
                video_data = f.read()
                video_b64 = base64.b64encode(video_data).decode('utf-8')

            # Cleanup temp files
            from phase4c_ffmpeg_concat import cleanup_temp_files
            cleanup_temp_files(result.get("temp_dir"))

            return {
                "success": True,
                "script_id": request.script_id,
                "videoData": video_b64,  # Base64-encoded final video
                "total_duration": result.get("total_duration"),
                "videos_count": result.get("videos_count"),
                "output_size_bytes": result.get("output_video_size"),
                "mimeType": "video/mp4"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Output video not found: {output_path}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video concatenation failed: {str(e)}"
        )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "wf7-ffmpeg-renderer"}


if __name__ == "__main__":
    import os
    # Railway injects PORT environment variable - use it for healthcheck compatibility
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting WF7 FFmpeg Video Renderer Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
