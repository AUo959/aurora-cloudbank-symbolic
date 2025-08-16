# Consolidating GitHub Actions Approvals (T1)

## Purpose
Replace multiple per-job approvals with a single environment-gated approval per workflow run.

## How it works
1. New reusable workflow `.github/workflows/t1-approval-gate.yml` runs a single job that targets environment `ci-batch-approval`.
2. GitHub shows one approval dialog for that job. After approving once, all downstream jobs run without additional prompts.
3. Existing workflows declare a first job `approval-gate` using the reusable workflow, and set `needs: approval-gate` on the rest.

## Setup (one-time)
- Settings → Environments → New environment: `ci-batch-approval`
  - Protection rules → Required reviewers: add yourself/team.

## Security & DLP
- No secrets or sensitive values are logged by the gate.
- All logs include symbolic anchors: `T1`, `SRB_BATCH_APPROVAL_V1`.

## Audit
- The gate prints a deterministic SHA256 seal derived from repo/workflow/run/sha.
- Manifests are stored under `manifests/ci-approval-consolidation.manifest.json`.

## Notes
- If PRs from forks still show an "Approve and run" banner, that's a separate GitHub security control for forks. This change ensures each workflow only needs one approval, not many.