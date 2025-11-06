# WF7 Phase4 FastAPI Integration Guide

## Current Status
- FastAPI renderer service deployed as separate Railway service
- Service URL: `https://fastapi-renderer-production.up.railway.app`
- Deployment initiated but may still be building

## Service Endpoints

### Health Check
```
GET https://fastapi-renderer-production.up.railway.app/health
```

### Video Rendering
```
POST https://fastapi-renderer-production.up.railway.app/render
```

Request body:
```json
{
  "title": "Video title",
  "quote": "Quote text",
  "author": "Author name"
}
```

## n8n Workflow Update Instructions

### Step 1: Update the HTTP Request Node

1. Open the Phase4 workflow in n8n
2. Find the "Phase4 FFmpegレンダラー" HTTP Request node
3. Update the URL from `http://localhost:8000/render` to:
   ```
   https://fastapi-renderer-production.up.railway.app/render
   ```

### Step 2: Configure the Request

Ensure the HTTP Request node has:
- **Method**: POST
- **URL**: `https://fastapi-renderer-production.up.railway.app/render`
- **Body Parameters Format**: JSON
- **Specify Body**: "Using JSON"
- **JSON Body**:
  ```json
  {
    "title": "{{ $json.title }}",
    "quote": "{{ $json.quote }}",
    "author": "{{ $json.author }}"
  }
  ```

### Step 3: Test the Workflow

1. Run a test execution with sample data:
   ```json
   {
     "title": "Test Video",
     "quote": "This is a test quote",
     "author": "Test Author"
   }
   ```

2. Check that the response contains:
   - `video_url`: URL to the rendered video
   - `duration`: Render time
   - `metadata`: Video information

## Troubleshooting

### If the service returns 404
- Check deployment status: `railway logs`
- Verify service is running: `curl https://fastapi-renderer-production.up.railway.app/health`
- May need to wait for deployment to complete

### If rendering fails
- Check n8n execution logs for error details
- Verify FFmpeg is working in the FastAPI container
- Check Railway logs: `railway logs 2>&1 | grep -i error`

### Common Issues
1. **Connection refused**: Service not yet deployed
2. **404 Not Found**: Service still deploying or wrong URL
3. **500 Internal Server Error**: FFmpeg issue in container
4. **Timeout**: Video rendering exceeds 600s timeout

## Architecture Overview

```
n8n Workflow
    ↓
HTTP Request Node (Phase4 FFmpegレンダラー)
    ↓
FastAPI Service (https://fastapi-renderer-production.up.railway.app)
    ↓
FFmpeg Process (render_video_ffmpeg.py)
    ↓
Video Output (MP4)
```

## Service Configuration

### Railway Services
- **n8n-python**: Main n8n service
- **fastapi-renderer**: Dedicated FFmpeg rendering service

### Dockerfile Configuration
- Uses `Dockerfile.fastapi` for the renderer service
- Python 3.11 Alpine base image
- Includes FFmpeg and Japanese fonts
- FastAPI server on port 8000

## Next Steps

1. Verify FastAPI service deployment is complete
2. Update n8n workflow with new service URL
3. Test end-to-end video rendering
4. Monitor performance and logs
5. Consider adding error handling and retry logic