# Vercel Ignored Build Step Configuration

## Overview
This configuration prevents Vercel from building when only backend/infrastructure files change, reducing CI noise and deployment costs.

It also supports a full disable mode for projects where Vercel preview checks are known-bad and should stop reporting on PRs until deployment is fixed.

## Disable Vercel Completely

If Vercel is not a legitimate merge gate for this repository, set the Vercel project to skip every preview build:

1. Go to Vercel Project Settings → Git
2. Open Ignored Build Step
3. Set the command to:

```bash
AURORA_DISABLE_VERCEL_BUILDS=1 bash scripts/vercel-should-build.sh
```

Effect:
- Vercel will skip preview builds for all PRs
- The GitHub `Vercel` check stops failing on unrelated backend or dependency PRs
- GitHub branch protection remains controlled by the actual required checks, not Vercel

If you want to leave the project linked but permanently disable previews, this is the least invasive option.

## Admin Runbook

Use this order when Vercel is creating persistent PR noise and is not considered a legitimate merge gate.

### Step 1: Disable Preview Builds

In Vercel Project Settings → Git → Ignored Build Step, set:

```bash
AURORA_DISABLE_VERCEL_BUILDS=1 bash scripts/vercel-should-build.sh
```

Expected result:
- New PR updates should stop triggering preview deployments
- The Vercel integration remains linked, so it can be restored later
- Repository deployment config is preserved

### Step 2: Verify GitHub Branch Protection

Confirm that GitHub branch protection does not require the `Vercel` status check.

For this repository, the tracked branch protection manifest is:
- [.github/branch-protection.json](../.github/branch-protection.json)

The intended required checks are the repository-owned checks such as:
- `continuous-integration`
- `health-check`
- `security-scan`

### Step 3: Disconnect Vercel if PR Noise Continues

If the Vercel GitHub App still posts failing checks after preview builds are disabled, disconnect the repository from the Vercel project:

1. Open Vercel Project Settings → Git
2. Disconnect the linked Git repository

Use this only when you want zero Vercel PR signal. It is a stronger action than the ignored build step.

### Step 4: Re-enable Later if Needed

To restore Vercel previews later:

1. Reconnect the Git repository in Vercel
2. Remove the global disable command from Ignored Build Step
3. Revert to:

```bash
bash scripts/vercel-should-build.sh
```

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

To disable all preview builds instead of selectively skipping backend-only changes:

```bash
vercel project settings update --ignore-command "AURORA_DISABLE_VERCEL_BUILDS=1 bash scripts/vercel-should-build.sh"
```

## How It Works

The `scripts/vercel-should-build.sh` script checks if any frontend-related files changed.

It also skips immediately when either of these kill switches is present:
- Environment variable `AURORA_DISABLE_VERCEL_BUILDS=1`
- Repository marker file `.vercel-disabled`

**Triggers Build (exit 1):**
- Changes in `frontend/` directory
- Changes in `static/` directory
- Changes in `tests/web/` directory  
- Changes to `vercel.json`
- Changes to `.vercelignore`
- Changes to `package.json` or web build entry files

**Skips Build (exit 0):**
- Changes only in `api/`, `src/`, `tools/`, `tests/` (non-web)
- Documentation updates (`*.md`, `docs/`)
- Configuration files (`*.yml`, `*.yaml`, `.github/`)
- Python code changes without frontend impact
- Any PR when Vercel is globally disabled with `AURORA_DISABLE_VERCEL_BUILDS=1`

## Testing Locally

```bash
# Simulate check for current commit
bash scripts/vercel-should-build.sh
echo "Exit code: $?"

# Exit code 1 = Build will run
# Exit code 0 = Build will be skipped

# Simulate repository-wide disable mode
AURORA_DISABLE_VERCEL_BUILDS=1 bash scripts/vercel-should-build.sh
```

## Benefits
- ✅ Reduces unnecessary Vercel builds on backend-only PRs
- ✅ Saves deployment time and Vercel bandwidth quota
- ✅ Cleaner PR status checks (no false failures)
- ✅ Faster CI feedback loop
- ✅ Provides a clean emergency stop for broken Vercel integrations

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

### Vercel should stop running entirely
- Set the ignored build step to `AURORA_DISABLE_VERCEL_BUILDS=1 bash scripts/vercel-should-build.sh`
- Confirm the Vercel project is still linked to the correct repository
- If the `Vercel` GitHub check still appears as failing after that, disconnect the Git repository in Vercel Project Settings → Git

### Build skipped when it shouldn't be
- Check if frontend path is missing from `FRONTEND_PATHS` pattern in script
- Add the path pattern to the regex: `^(frontend/|static/|tests/web/|your-path/|vercel\.json)`

### Build runs when it should skip
- Verify `vercel.json` or `.vercelignore` isn't being changed
- Check git diff output: `git diff $(git merge-base HEAD origin/main) HEAD --name-only`

## References
- [Vercel Ignored Build Step Docs](https://vercel.com/docs/concepts/projects/overview#ignored-build-step)
- Script location: `scripts/vercel-should-build.sh`
- Frontend paths: `static/`, `tests/web/`
