# Vercel Deployment Guide for Aurora CloudBank Symbolic

## ✅ Setup Complete

Your repository is now configured for Vercel deployment with the following files:

### 1. **`api/index.py`** - Vercel Entrypoint
   - Imports the main FastAPI app from `aurora_api.py`
   - Exports `app` for Vercel to discover

### 2. **`vercel.json`** - Vercel Configuration
   - Configured for Python 3.12
   - Routes all traffic to `api/index.py`
   - Set memory to 3008 MB and max duration to 60s

### 3. **`requirements.txt`** - Lightweight Dependencies for Vercel
   - **PRODUCTION DEPLOYMENT ONLY** - excludes heavy packages (qiskit, scipy, pandas, plotly, redis)
   - Optimized for Vercel's 50MB deployment size limit
   - All excluded packages gracefully degrade with mock implementations

### 4. **`requirements-full.txt`** - Complete Dependencies for Local Development
   - **LOCAL DEVELOPMENT** - includes ALL packages
   - Use this for local setup: `pip install -r requirements-full.txt`
   - Includes quantum computing (qiskit), scientific computing (scipy), data analysis (pandas)

## 🏗️ Dependency Strategy

**Two-Tier Approach:**
- **Vercel (Production):** Uses `requirements.txt` (lightweight, ~40MB)
- **Local Dev:** Uses `requirements-full.txt` (complete, ~150MB)

This allows full-featured local development while keeping deployments within Vercel limits.

## 🔧 Environment Variables Required

Before deploying, you **must** add these environment variables in your Vercel project settings:

```bash
AURORA_SECRET_KEY=<your-secret-key>
CSRF_SECRET_KEY=<your-csrf-key>
WS_AUTH_SECRET=<your-ws-secret>
AES_KEY_256_HEX=<your-aes-key>
AURORA_API_URL=https://your-vercel-deployment.vercel.app
ALLOWED_CORS_ORIGINS=https://your-vercel-deployment.vercel.app
COMMAND_NODE_PORT=3001
```

### How to Add Environment Variables in Vercel:

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add each variable from your local `.env` file
4. Make sure to add them for **Production**, **Preview**, and **Development** environments

⚠️ **CRITICAL**: Copy the values from your local `.env` file (generated on Nov 14, 2025) to Vercel's environment variables. These are the secure secrets needed for your app to run.

## 📦 Deployment Steps

1. **Commit these new files:**
   ```bash
   git add api/index.py vercel.json
   git commit -m "feat: Add Vercel deployment configuration"
   git push origin main
   ```

2. **Configure Environment Variables in Vercel:**
   - Copy all values from your local `.env` file
   - Paste them into Vercel's environment variable settings
   - Update `AURORA_API_URL` to your Vercel deployment URL

3. **Trigger Deployment:**
   - Vercel will auto-deploy after you push
   - Or manually trigger a redeploy from the Vercel dashboard

4. **Verify Deployment:**
   - Check the deployment logs for successful build
   - Visit `https://your-deployment.vercel.app/health` to verify the API is running
   - Visit `https://your-deployment.vercel.app/docs` to see the API documentation

## 🎯 What Was Fixed

**Problem:** Vercel couldn't find a FastAPI app instance named `app`

**Solution:**
- Created `api/index.py` that imports and exports your main `app` from `aurora_api.py`
- Created `vercel.json` to tell Vercel how to build and route your FastAPI app
- Configured proper Python version (3.12) and resource limits

## 🔍 Testing Locally

To test the Vercel entrypoint locally:

```bash
# Load environment variables
export $(cat .env | xargs)

# Test import
python -c "from api.index import app; print('✅ App loaded:', app.title)"

# Run with Uvicorn
uvicorn api.index:app --reload --port 8080
```

## 📚 Additional Resources

- [Vercel FastAPI Documentation](https://vercel.com/docs/frameworks/backend/fastapi)
- Your main app: `api/aurora_api.py` (2461 lines, 183+ routes)
- Health check: `/health` and `/api/health`

---

**Status:** Ready for Vercel deployment! 🚀
