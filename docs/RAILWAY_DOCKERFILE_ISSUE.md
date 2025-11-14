# Railway Dockerfile Build Issue

## Problem Discovery

After successful Dockerfile fixes (Alpine + prebuilt packages), Python is still not found in the Railway container.

## Root Cause

Railway was **NOT building from our custom Dockerfile** at all. Despite having:
- ✅ Correct Dockerfile.n8n-python-alpine with Alpine + Python + packages
- ✅ railway.json configured with `"builder": "DOCKERFILE"`
- ✅ Successful git commits and pushes
- ✅ Multiple deployment attempts

Railway continued using the default `n8nio/n8n:latest` image without customization.

## Evidence

```bash
# Verification workflow execution (ID: 1286)
stdout: "/bin/sh: /usr/bin/python3: not found"
stdout: "/bin/sh: /usr/bin/pip3: not found"
```

## Railway Logs Analysis

- **Observed**: Only container startup logs (n8n initialization)
- **Missing**: Docker build logs (FROM, RUN, COPY steps)
- **Expected**: Build steps showing Alpine package installation

## Solution Attempts

### Attempt 1: railway.json + custom Dockerfile name
```json
{
  "dockerfilePath": "Dockerfile.n8n-python-alpine"
}
```
❌ Railway ignored this configuration

### Attempt 2: Force rebuild with timestamp comment
```dockerfile
# Build timestamp: 2025-11-02 01:39 JST
```
❌ Still used cached default image

### Attempt 3: Standard Dockerfile naming (CURRENT)
```bash
cp Dockerfile.n8n-python-alpine Dockerfile
```
```json
{
  "dockerfilePath": "Dockerfile"
}
```
✅ **Testing in progress** - Railway typically auto-detects root Dockerfile

## Hypothesis

Railway's web UI configuration may be overriding railway.json settings. Possible causes:
1. Service settings in Railway dashboard configured for different build method
2. Nixpacks auto-detection taking precedence
3. Docker layer caching with wrong cache key
4. railway.json not being read during deployment

## Next Steps

1. Wait for current deployment to complete (with standard Dockerfile)
2. Check build logs for Docker build steps
3. If still failing, manually configure build settings in Railway dashboard
4. Alternative: Use Railway CLI to explicitly set Dockerfile path

## Timeline

- **2025-11-02 00:45**: Created Dockerfile.n8n-python (Debian - abandoned)
- **2025-11-02 01:17**: Created Dockerfile.n8n-python-alpine (Alpine - working locally)
- **2025-11-02 01:30**: Multiple deployment attempts, Python still not found
- **2025-11-02 01:40**: Discovered Railway not building custom Dockerfile
- **2025-11-02 01:47**: Created standard "Dockerfile" for auto-detection

## Deployment URL
Build Logs: https://railway.com/project/f6dfa2f7-13fe-4114-b4c9-0e1417e0a7bd/service/30d84665-f6d2-4d52-b4ad-ab76b62c501e?id=2e75932c-6e85-4f38-ade9-2e3d9cd9cdaf&
