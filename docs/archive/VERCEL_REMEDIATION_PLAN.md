# Vercel Remediation Plan (System-Wide)

**Status:** Draft
**Owner:** Integration & Release Engineering (R-2 Mode)
**Context Tag:** integration_vercel_remediation_001

## Problem Summary
- Vercel deployments fail across multiple PRs; issues exceed scope of individual changes.
- Likely systemic: framework detection, build config, env vars, or routing between frontend and FastAPI backend.
- Decision: defer per-PR fixes and deliver a single, comprehensive remediation PR.

## Goals
- Restore reliable Vercel deployments for the web frontend(s).
- Standardize build and routing config; isolate backend from Vercel deploy surface.
- Provide clear guidance and guardrails to avoid future misconfigurations.

## Scope
- Frontend builds (Next.js/Static): framework config, build command, output directory.
- `vercel.json`: routes/rewrites, headers, caching, output mode.
- Env vars and secrets: ensure required values exist (preview/prod).
- CI integration: GitHub checks mapping and branch protection requirements.
- Backend (FastAPI) is NOT deployed on Vercel; use API URL rewrites/proxy if needed.

## Root Causes To Investigate
- Missing/incorrect `vercel.json` or project settings.
- No framework detected (missing `package.json`, incorrect build command).
- Build-time env vars not set (e.g., `NEXT_PUBLIC_*`, API endpoints).
- Misconfigured rewrites to backend causing 404/500 in preview.
- Large functions or unsupported runtimes for server-side paths.

## Actions
1. Add `vercel.json` with explicit configuration:
   - `buildCommand` (npm ci && npm run build) or framework auto-detect.
   - `outputDirectory` (e.g., `.vercel/output` or `out` for static export).
   - `routes`/`rewrites` to FastAPI base URL.
   - `headers` for CORS/cache control if needed.
2. Frontend build readiness:
   - Confirm `package.json` scripts (`build`, `start`, `dev`).
   - Ensure entry (`pages/` or `app/` for Next.js) is valid.
   - Static export path configured when applicable.
3. Env/Secrets hygiene:
   - Define preview/prod env vars in Vercel project.
   - Document required keys; add `.env.example`.
4. CI/Checks alignment:
   - Map Vercel preview status to PR checks intentionally.
   - Update branch protection: limit required Vercel checks to frontend PRs.
5. Docs & Guardrails:
   - Add deployment README with troubleshooting.
   - Add lint rule or CI step validating presence of minimal config.

## Rollout
- Create branch `feature/vercel-remediation-umbrella`.
- Commit `vercel.json`, docs, minimal frontend config alignment.
- Open PR with clear scope, test preview URL, and acceptance criteria.

## Risks & Mitigations
- Backend coupling: avoid deploying FastAPI on Vercel; use external URL.
- Preview failures due to missing env vars: gate with validation pre-checks.
- Route conflicts: test rewrites locally and on preview.

## Acceptance Criteria
- PR preview succeeds on Vercel for the frontend.
- `vercel.json` present and routes verified.
- Branch protection updated to avoid blocking backend-only PRs on Vercel.
- Documentation added: deployment steps + troubleshooting.

## Follow-Ups
- Add CI job to validate `vercel.json` presence and basic schema.
- Weekly check on Vercel deploy health and error rates.
