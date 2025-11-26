# Vercel Deployment Guide

## Overview
Aurora CloudBank frontend is deployed on Vercel; backend (FastAPI) runs separately and is proxied via rewrites.

## Prerequisites
- Node.js 18+ and npm installed
- Vercel CLI: `npm i -g vercel`
- Vercel account with project linked

## Configuration

### `vercel.json`
- **Build Command:** `npm ci && npm run build`
- **Output Directory:** `out` (static export)
- **Rewrites:** `/api/*` routes to backend URL (set in env vars)
- **Headers:** Security headers (X-Content-Type-Options, X-Frame-Options, XSS-Protection)

### Environment Variables
**Required (Vercel Dashboard):**
- `NEXT_PUBLIC_API_BASE_URL`: Backend API base URL (e.g., `https://aurora-api.example.com`)
- `@aurora_backend_url`: Secret env var for backend URL (for server-side rewrites)

**Optional:**
- `NODE_ENV`: Set to `production` for builds

### Frontend Build Scripts
Ensure `package.json` includes:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build && next export",
    "start": "next start"
  }
}
```

## Local Testing
```bash
# Install dependencies
npm ci

# Run development server
npm run dev

# Build for production
npm run build

# Preview build locally
npx serve out
```

## Deployment

### Preview (PR)
- Push to PR branch
- Vercel automatically deploys preview
- Check logs: `vercel logs <deployment-url>`

### Production
```bash
# Deploy to production
vercel --prod

# Or via GitHub: merge to main
```

## Troubleshooting

### Build Fails: "No framework detected"
- Ensure `package.json` exists in repo root
- Verify `build` script is defined
- Check Vercel project settings: Framework preset should be `Next.js` or `Other`

### 404 on API Routes
- Verify `@aurora_backend_url` env var is set in Vercel dashboard
- Check rewrite rules in `vercel.json`
- Test backend URL directly (CORS should allow Vercel domain)

### Environment Variables Not Applied
- Set env vars in Vercel Dashboard > Project > Settings > Environment Variables
- Redeploy after adding/updating env vars
- Preview and Production environments need separate values

### Deployment Timeout
- Reduce build time: use npm cache
- Check function memory and maxDuration in `vercel.json`
- Backend functions >10s should run externally, not on Vercel

## CI/CD Integration

### GitHub Branch Protection
- Vercel check is **optional** for backend-only PRs
- Required for frontend changes
- Adjust in: Repo Settings > Branches > main > Require status checks

### Vercel CLI Commands
```bash
# Link project
vercel link

# Deploy preview
vercel

# Deploy production
vercel --prod

# View logs
vercel logs <deployment-url>

# List deployments
vercel ls
```

## Support
- **Vercel Docs:** https://vercel.com/docs
- **Next.js Docs:** https://nextjs.org/docs
- **Repo Issues:** Tag with `vercel-deployment`
