#!/usr/bin/env python3
"""
WF7 FFmpeg Video Renderer FastAPI Server
Wraps render_video_ffmpeg.py CLI tool as an HTTP API for n8n integration
"""

import base64
import json
import tempfile
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import io
import textwrap
from PIL import Image, ImageDraw, ImageFont
import cloudinary
import cloudinary.uploader

app = FastAPI(title="WF7 FFmpeg Video Renderer")

# Cloudinary設定（Phase4a用）
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Phase4a スライド生成用の定数
# フォント設定（Railway環境 - fontconfigで自動解決）
FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"

# デフォルトブランドカラー
DEFAULT_BRAND_COLORS = {
    'background': '#1a1a2e',
    'primary_text': '#ffffff',
    'secondary_text': '#aaaaaa',
    'accent': '#00d4ff',
    'cta_bg': '#ff6b6b',
    'cta_text': '#ffffff'
}

# セクションラベル
SECTION_LABELS = {
    "hook": "フック",
    "intro": "導入",
    "point1": "ポイント①",
    "point2": "ポイント②",
    "point3": "ポイント③",
    "summary": "まとめ",
    "cta": "今すぐ行動"
}


# Phase4a ヘルパー関数
def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color (#RRGGBB) to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_slide(text: str, section_type: str, duration: int,
                 brand_colors: Dict[str, str], icon: Optional[str] = None) -> Image.Image:
    """
    Create a single slide image for Phase4a

    Args:
        text: Main text to display
        section_type: One of hook, intro, point1-3, summary, cta
        duration: Duration in seconds (for display label)
        brand_colors: Dict with background, primary_text, accent colors
        icon: Optional emoji icon to display

    Returns:
        PIL Image object (1080x1920)
    """
    bg_color = hex_to_rgb(brand_colors.get('background', '#1a1a2e'))
    img = Image.new('RGB', (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Load fonts - fontconfig will resolve these paths
    try:
        if section_type in ["hook", "cta"]:
            font_main = ImageFont.truetype(FONT_BOLD_PATH, 90)
        else:
            font_main = ImageFont.truetype(FONT_PATH, 70)
        font_label = ImageFont.truetype(FONT_PATH, 40)
        font_icon = ImageFont.truetype(FONT_PATH, 120)
    except Exception as e:
        # Explicit error - do not fall back silently
        error_msg = f"Font loading failed: {e}\n"
        error_msg += f"FONT_PATH={FONT_PATH}\n"
        error_msg += f"FONT_BOLD_PATH={FONT_BOLD_PATH}\n"
        error_msg += "Please verify fonts are installed in Railway environment"
        raise RuntimeError(error_msg)

    # Draw icon if provided
    if icon:
        accent_color = hex_to_rgb(brand_colors.get('accent', '#00d4ff'))
        draw.text((540, 400), icon, fill=accent_color, font=font_icon, anchor="mm")

    # Wrap text based on section type
    if section_type == "hook":
        wrapped = textwrap.fill(text, width=15)
        y_offset = 700
    elif section_type == "cta":
        wrapped = text
        y_offset = 900
    else:
        wrapped = textwrap.fill(text, width=18)
        y_offset = 600

    # Calculate text position
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font_main)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (1080 - text_width) // 2
    y = y_offset

    # Draw text with shadow
    draw.multiline_text((x+3, y+3), wrapped, fill="#000000", font=font_main, align="center")
    primary_text_color = hex_to_rgb(brand_colors.get('primary_text', '#ffffff'))
    draw.multiline_text((x, y), wrapped, fill=primary_text_color, font=font_main, align="center")

    # Draw duration label (bottom left)
    label_text = f"{duration}秒"
    secondary_text_color = hex_to_rgb(brand_colors.get('secondary_text', '#aaaaaa'))
    draw.text((50, 1850), label_text, fill=secondary_text_color, font=font_label)

    # Draw section label (top left)
    section_label = SECTION_LABELS.get(section_type, "")
    accent_color = hex_to_rgb(brand_colors.get('accent', '#00d4ff'))
    draw.text((50, 100), section_label, fill=accent_color, font=font_label)

    return img


def image_to_base64(img: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


def upload_image_to_cloudinary(img: Image.Image, section: str, script_id: str) -> str:
    """
    Upload PIL Image to Cloudinary and return public URL

    Args:
        img: PIL Image object to upload
        section: Section name (hook, intro, point1, etc.)
        script_id: Notion script ID for folder organization

    Returns:
        str: Cloudinary public URL (https://res.cloudinary.com/...)

    Raises:
        RuntimeError: If Cloudinary credentials are not configured
        Exception: If upload fails
    """
    # Validate Cloudinary configuration
    if not all([
        os.getenv("CLOUDINARY_CLOUD_NAME"),
        os.getenv("CLOUDINARY_API_KEY"),
        os.getenv("CLOUDINARY_API_SECRET")
    ]):
        raise RuntimeError(
            "Cloudinary credentials not configured. Set CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET environment variables."
        )

    # Convert PIL Image to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Upload to Cloudinary
    # Folder structure: wf7-slides/{script_id}/{section}
    folder = f"wf7-slides/{script_id}"
    public_id = f"{section}"

    try:
        upload_result = cloudinary.uploader.upload(
            buffer,
            folder=folder,
            public_id=public_id,
            resource_type="image",
            overwrite=True,  # Overwrite if already exists
            format="png"
        )

        # Return secure URL
        image_url = upload_result.get("secure_url")
        print(f"✅ Uploaded to Cloudinary: {image_url}")
        return image_url

    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")


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


class GenerateSingleVideoRequest(BaseModel):
    """Single video generation request model for Phase4b"""
    section: str                # "hook", "intro", "point1", etc.
    duration: int               # Video duration in seconds (3-20)
    image_url: str              # Cloudinary image URL
    motion_prompt: str          # Motion description (currently unused)
    text: str                   # Subtitle text
    script_id: str              # Notion script ID


class ConcatVideoRequest(BaseModel):
    """Video concatenation request model for Phase 4c"""
    script_id: str
    videos_metadata: List[Dict[str, Any]]


class GenerateSlideRequest(BaseModel):
    """Slide generation request model for Phase 4a"""
    section: str                            # "hook", "intro", "point1", "point2", "point3", "summary", "cta"
    text: str                               # Main text to display on slide
    duration: int                           # Slide duration in seconds (3-20)
    brand_colors: Optional[Dict[str, str]] = None  # Optional brand colors (uses DEFAULT_BRAND_COLORS if not provided)
    icon: Optional[str] = None              # Optional emoji icon
    script_id: str                          # Notion script ID


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


@app.post("/generate-single-video")
async def generate_single_video_endpoint(request: GenerateSingleVideoRequest):
    """
    Phase 4b: Generate single video from static image

    Expects:
    {
        "section": "hook",
        "duration": 3,
        "image_url": "https://res.cloudinary.com/...",
        "motion_prompt": "...",
        "text": "...",
        "script_id": "..."
    }

    Returns:
    {
        "success": true,
        "section": "hook",
        "duration": 3,
        "videoData": "base64...",
        "video_size_bytes": 150000,
        "script_id": "...",
        "motion_prompt": "...",
        "text": "...",
        "filename": "video_hook.mp4",
        "mimeType": "video/mp4"
    }
    """
    import requests
    import time

    # Validate duration
    if not (1 <= request.duration <= 20):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid duration: {request.duration}. Must be 1-20 seconds."
        )

    # Validate image_url (Cloudinary only)
    if not request.image_url.startswith("https://res.cloudinary.com/"):
        raise HTTPException(
            status_code=400,
            detail="Only Cloudinary URLs are allowed"
        )

    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Define paths
        timestamp = int(time.time() * 1000)
        input_path = tmp_path / f"slide_{request.section}_{timestamp}.png"
        output_path = tmp_path / f"video_{request.section}_{timestamp}.mp4"

        try:
            # 1. Download image
            print(f"Downloading image: {request.image_url}")
            img_response = requests.get(request.image_url, timeout=30)
            img_response.raise_for_status()

            input_path.write_bytes(img_response.content)
            print(f"Image downloaded: {input_path.stat().st_size} bytes")

            # 2. Generate video with ffmpeg
            ffmpeg_cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", str(input_path),
                "-t", str(request.duration),
                "-c:v", "libx264",
                "-preset", "fast",       # Encoding speed (fast, medium, slow)
                "-crf", "23",           # Quality parameter (18-28, lower=better quality)
                "-pix_fmt", "yuv420p",
                "-vf", "scale=1080:1920",
                "-r", "30",
                "-y",
                str(output_path)
            ]

            print(f"Executing ffmpeg: duration={request.duration}s, section={request.section}")
            result = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=request.duration * 2 + 10
            )

            if result.returncode != 0:
                stderr_lines = result.stderr.strip().split('\n')
                stderr_tail = '\n'.join(stderr_lines[-20:])
                raise HTTPException(
                    status_code=500,
                    detail=f"FFmpeg execution failed: {stderr_tail}"
                )

            print(f"FFmpeg stdout: {result.stdout[-200:]}")

            # 3. Check output file
            if not output_path.exists():
                raise HTTPException(
                    status_code=500,
                    detail=f"Output video not found: {output_path}"
                )

            video_size = output_path.stat().st_size
            print(f"Video generated: {video_size} bytes, duration={request.duration}s")

            # 4. Read and encode video
            video_data = output_path.read_bytes()
            video_b64 = base64.b64encode(video_data).decode('utf-8')

            # 5. Return response
            return {
                "success": True,
                "section": request.section,
                "duration": request.duration,
                "videoData": video_b64,
                "video_size_bytes": video_size,
                "script_id": request.script_id,
                "motion_prompt": request.motion_prompt,
                "text": request.text,
                "filename": f"video_{request.section}.mp4",
                "mimeType": "video/mp4"
            }

        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image download failed: {str(e)}"
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=504,
                detail=f"FFmpeg timeout (duration={request.duration}s)"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {str(e)}"
            )


@app.post("/generate-slide")
async def generate_slide_endpoint(request: GenerateSlideRequest):
    """
    Phase 4a: Generate single slide image with text overlay

    Expects:
    {
        "section": "hook",
        "text": "フックテキスト",
        "duration": 3,
        "brand_colors": {
            "background": "#1a1a2e",
            "primary_text": "#ffffff",
            "accent": "#00d4ff"
        },
        "icon": "⚠️",
        "script_id": "notion-id"
    }

    Returns:
    {
        "success": true,
        "section": "hook",
        "duration": 3,
        "imageData": "base64...",
        "image_size_bytes": 50000,
        "filename": "slide_hook.png",
        "mimeType": "image/png"
    }
    """
    # 1. Validate section
    valid_sections = ["hook", "intro", "point1", "point2", "point3", "summary", "cta"]
    if request.section not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid section: {request.section}. Must be one of {valid_sections}"
        )

    # 2. Validate duration
    if not (1 <= request.duration <= 20):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid duration: {request.duration}. Must be 1-20 seconds."
        )

    # 3. Set default brand colors if not provided
    brand_colors = request.brand_colors if request.brand_colors else DEFAULT_BRAND_COLORS

    try:
        # 4. Generate slide image
        print(f"Generating slide: section={request.section}, duration={request.duration}s")
        slide_img = create_slide(
            text=request.text,
            section_type=request.section,
            duration=request.duration,
            brand_colors=brand_colors,
            icon=request.icon
        )

        # 5. Upload to Cloudinary (primary)
        try:
            image_url = upload_image_to_cloudinary(slide_img, request.section, request.script_id)
        except Exception as cloudinary_error:
            print(f"⚠️ Cloudinary upload failed: {cloudinary_error}")
            # Fallback: Continue with base64-only response
            image_url = None

        # 6. Convert to base64 (backward compatibility)
        image_b64 = image_to_base64(slide_img)

        # Calculate approximate size (base64 is ~1.33x original)
        image_size = len(image_b64.encode('utf-8'))
        print(f"Slide generated: {image_size} bytes (base64), section={request.section}")

        # 7. Return response with image_url (Phase4b compatible)
        return {
            "success": True,
            "section": request.section,
            "duration": request.duration,
            "image_url": image_url,  # ✅ NEW: Cloudinary URL for Phase4b
            "imageData": image_b64,  # Backward compatibility
            "image_size_bytes": image_size,
            "script_id": request.script_id,
            "filename": f"slide_{request.section}.png",
            "mimeType": "image/png"
        }

    except RuntimeError as e:
        # Font loading error - explicit failure
        raise HTTPException(
            status_code=500,
            detail=f"Font loading failed: {str(e)}"
        )
    except Exception as e:
        # General error
        raise HTTPException(
            status_code=500,
            detail=f"Slide generation failed: {str(e)}"
        )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "wf7-ffmpeg-renderer"}


@app.get("/test-fonts")
async def test_fonts():
    """
    Test font loading for WF7 Phase4a
    Validates that Noto Sans CJK fonts are properly installed and can be loaded
    """
    from PIL import ImageFont
    import os

    FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    FONT_BOLD_PATH = "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"

    results = {
        "service": "wf7-ffmpeg-renderer",
        "test_type": "font_loading",
        "tests": []
    }

    # Test 1: Font file existence
    font_files = [
        ("Regular", FONT_PATH),
        ("Bold", FONT_BOLD_PATH)
    ]

    for font_name, font_path in font_files:
        test_result = {
            "font": font_name,
            "path": font_path,
            "exists": os.path.exists(font_path)
        }

        if test_result["exists"]:
            test_result["size_mb"] = round(os.path.getsize(font_path) / (1024 * 1024), 2)

        results["tests"].append(test_result)

    # Test 2: Font loading
    loading_tests = [
        ("Regular 70pt", FONT_PATH, 70),
        ("Bold 90pt", FONT_BOLD_PATH, 90),
        ("Regular 40pt", FONT_PATH, 40),
    ]

    for test_name, font_path, font_size in loading_tests:
        test_result = {
            "test": test_name,
            "path": font_path,
            "size": font_size
        }

        try:
            font = ImageFont.truetype(font_path, font_size)
            test_result["status"] = "success"
            test_result["font_name"] = font.getname()
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)

        results["tests"].append(test_result)

    # Test 3: Japanese text rendering
    test_texts = [
        "CTAがありません",
        "フックテキストがありません",
        "導入テキストがありません",
    ]

    try:
        font = ImageFont.truetype(FONT_PATH, 70)

        for text in test_texts:
            bbox = font.getbbox(text)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]

            test_result = {
                "test": "japanese_rendering",
                "text": text,
                "width": width,
                "height": height,
                "status": "success" if width > 0 and height > 0 else "failed"
            }
            results["tests"].append(test_result)

    except Exception as e:
        results["tests"].append({
            "test": "japanese_rendering",
            "status": "failed",
            "error": str(e)
        })

    # Test 4: List installed fonts in common directories
    font_directories = [
        "/usr/share/fonts/truetype/noto/",
        "/usr/share/fonts/opentype/noto/",
        "/usr/share/fonts/truetype/",
        "/usr/share/fonts/",
    ]

    results["installed_fonts"] = {}

    for font_dir in font_directories:
        if os.path.exists(font_dir):
            try:
                files = os.listdir(font_dir)
                font_files = [f for f in files if f.endswith(('.ttf', '.ttc', '.otf'))]
                results["installed_fonts"][font_dir] = font_files[:20]  # Limit to 20 files
            except Exception as e:
                results["installed_fonts"][font_dir] = {"error": str(e)}
        else:
            results["installed_fonts"][font_dir] = "directory_not_found"

    # Overall status
    all_passed = all(
        test.get("status") == "success" or test.get("exists") == True
        for test in results["tests"]
    )
    results["overall_status"] = "pass" if all_passed else "fail"

    return results


if __name__ == "__main__":
    import os

    # === フォント診断情報をログ出力 ===
    print("\n" + "=" * 60)
    print("フォントインストール状況診断")
    print("=" * 60)

    # 1. インストール済みパッケージ確認
    print("\n[1] fonts-noto関連パッケージ確認:")
    try:
        result = subprocess.run(
            ["dpkg", "-l"],
            capture_output=True,
            text=True,
            timeout=5
        )
        noto_packages = [line for line in result.stdout.split('\n') if 'fonts-noto' in line]
        if noto_packages:
            for pkg in noto_packages:
                print(f"  {pkg}")
        else:
            print("  ❌ fonts-notoパッケージが見つかりません")
    except Exception as e:
        print(f"  ❌ dpkgコマンド実行失敗: {e}")

    # 2. フォントディレクトリの確認
    print("\n[2] フォントディレクトリ確認:")
    font_dirs = [
        "/usr/share/fonts/",
        "/usr/share/fonts/truetype/",
        "/usr/share/fonts/truetype/noto/",
        "/usr/share/fonts/opentype/noto/"
    ]
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            try:
                files = os.listdir(font_dir)
                font_files = [f for f in files if f.endswith(('.ttf', '.ttc', '.otf'))]
                print(f"  ✅ {font_dir}: {len(files)}個のファイル ({len(font_files)}個のフォント)")
                if font_files:
                    for f in font_files[:5]:  # 最初の5個のみ表示
                        print(f"     - {f}")
            except Exception as e:
                print(f"  ⚠️ {font_dir}: エラー - {e}")
        else:
            print(f"  ❌ {font_dir}: ディレクトリが存在しません")

    # 3. fc-listでフォント確認
    print("\n[3] fontconfig (fc-list) 確認:")
    try:
        result = subprocess.run(
            ["fc-list", ":", "family"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            fonts = result.stdout.strip().split('\n')
            noto_fonts = [f for f in fonts if 'Noto' in f]
            print(f"  ✅ 合計 {len(fonts)} フォントファミリー検出")
            if noto_fonts:
                print(f"  ✅ Notoフォント: {len(noto_fonts)}個")
                for f in noto_fonts[:10]:  # 最初の10個のみ表示
                    print(f"     - {f}")
            else:
                print(f"  ❌ Notoフォントが見つかりません")
        else:
            print(f"  ❌ fc-list実行失敗: {result.stderr}")
    except Exception as e:
        print(f"  ❌ fc-listコマンド実行失敗: {e}")

    print("=" * 60 + "\n")

    # Railway injects PORT environment variable - use it for healthcheck compatibility
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting WF7 FFmpeg Video Renderer Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
