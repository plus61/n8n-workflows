# Railway Dockerfile Build Issue - Status Update (2025-11-03)

## Current Situation

### ✅ What We've Confirmed:
1. **Dockerfile exists** in repository root with correct Python + FFmpeg setup
2. **railway.json correctly configured** with `"builder": "DOCKERFILE"`
3. **Railway Dashboard shows** "Builder: Dockerfile" setting
4. **New deployment triggered** via `railway up` command at 05:45 JST
5. **Service responding** - HTTP 200, last modified 05:45:35

### ❌ Critical Problem:
**Railway is NOT building from Dockerfile despite all configurations being correct**

### Evidence:
```bash
# Railway logs show ONLY:
- Container startup (n8n initialization)
- NO Docker build steps (no FROM, RUN, COPY commands)
- NO Python installation logs
- NO Alpine package installation

# Expected to see:
Step 1/N : FROM n8nio/n8n:latest
Step 2/N : USER root
Step 3/N : RUN apk add python3 py3-pip...
```

### Verification Results:
- All previous test executions (1285-1330) show: `python: not found`
- No change after `railway up` deployment
- Webhook "verify-python-env" not registered (workflow needs manual UI activation)

## Root Cause Hypothesis

Railway's **build detection may be overriding railway.json configuration**. Possible causes:

1. **Nixpacks Auto-Detection**: Railway may be detecting the repository as a Node.js project (due to n8n being Node-based) and using Nixpacks instead of Dockerfile
2. **Service Settings Override**: Railway Dashboard service settings may have a builder configuration that overrides railway.json
3. **Build Cache Issue**: Railway may be using a cached build that predates the Dockerfile configuration
4. **Branch/Environment Mismatch**: The deployment may be pulling from a different branch or environment

## Recommended Next Steps

### Option A: Force Dockerfile via Dashboard (RECOMMENDED)
1. Open Railway Dashboard: https://railway.com/project/75226584-188f-4dc9-8032-1bc2a3e7260b/service/8c490f9c-0344-4987-8617-1bf8af020951
2. Go to **Settings** tab
3. Find **Builder** section
4. Explicitly set to **Dockerfile** (even if it shows as already set)
5. Click **Deploy** to trigger new build
6. Monitor build logs for Docker steps

### Option B: Alternative Deployment Method
Create a separate Railway service specifically for Python rendering:
1. New service with Dockerfile builder
2. Expose HTTP endpoint for render_video.py
3. WF7 Phase4 calls this dedicated service
4. Simpler architecture, cleaner separation

### Option C: Local Docker Test (Verification)
Build Dockerfile locally to confirm it works:
```bash
docker build -t n8n-python-test -f Dockerfile .
docker run --rm n8n-python-test python3 --version
docker run --rm n8n-python-test pip3 list | grep moviepy
```

## Timeline
- **2025-11-01**: Initial Dockerfile creation attempts (18 commits)
- **2025-11-02**: Discovered Railway not building from Dockerfile
- **2025-11-03 05:45**: Deployed via `railway up` - still no Docker build logs
- **2025-11-03 05:48**: Created diagnosis document

## Required User Action

**Please check Railway Dashboard service settings** and explicitly set Builder to Dockerfile, then redeploy. The CLI commands and railway.json configuration may not be taking effect due to dashboard settings override.
