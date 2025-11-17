# Vercel Ignored Build Step Configuration

## Overview
This configuration prevents Vercel from building when only backend/infrastructure files change, reducing CI noise and deployment costs.

## Implementation

### Option 1: Vercel Project Settings (Recommended)
1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Git**
3. Scroll to **Ignored Build Step**
4. Set the command to:
   ```bash
   bash scripts/vercel-should-build.sh
   ```

### Option 2: Via Vercel CLI
```bash
vercel project settings update --ignore-command "bash scripts/vercel-should-build.sh"
```

## How It Works

The `scripts/vercel-should-build.sh` script checks if any frontend-related files changed:

**Triggers Build (exit 1):**
- Changes in `static/` directory
- Changes in `tests/web/` directory  
- Changes to `vercel.json`
- Changes to `.vercelignore`

**Skips Build (exit 0):**
- Changes only in `api/`, `src/`, `tools/`, `tests/` (non-web)
- Documentation updates (`*.md`, `docs/`)
- Configuration files (`*.yml`, `*.yaml`, `.github/`)
- Python code changes without frontend impact

## Testing Locally

```bash
# Simulate check for current commit
bash scripts/vercel-should-build.sh
echo "Exit code: $?"

# Exit code 1 = Build will run
# Exit code 0 = Build will be skipped
```

## Benefits
- ✅ Reduces unnecessary Vercel builds on backend-only PRs
- ✅ Saves deployment time and Vercel bandwidth quota
- ✅ Cleaner PR status checks (no false failures)
- ✅ Faster CI feedback loop

## Example Scenarios

### Scenario 1: Backend API Change
```
Changed files:
  api/aurora_api.py
  src/core/native_dlp_export.py

Result: BUILD SKIPPED ⏭️
```

### Scenario 2: Frontend Update
```
Changed files:
  static/css/dashboard.css
  static/js/aurora.js

Result: BUILD REQUIRED ✅
```

### Scenario 3: Mixed Changes
```
Changed files:
  api/routes.py
  static/index.html
  vercel.json

Result: BUILD REQUIRED ✅
```

## Troubleshooting

### Build skipped when it shouldn't be
- Check if frontend path is missing from `FRONTEND_PATHS` pattern in script
- Add the path pattern to the regex: `^(static/|tests/web/|your-path/|vercel\.json)`

### Build runs when it should skip
- Verify `vercel.json` or `.vercelignore` isn't being changed
- Check git diff output: `git diff HEAD^ HEAD --name-only`

## References
- [Vercel Ignored Build Step Docs](https://vercel.com/docs/concepts/projects/overview#ignored-build-step)
- Script location: `scripts/vercel-should-build.sh`
- Frontend paths: `static/`, `tests/web/`
