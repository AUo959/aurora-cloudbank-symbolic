# Aurora CloudBank – Developer Deployment Guide

> Issue Reference: #387 (Critical, Orphan) – Provide a Developer Deployment Guide
> Context Tag: DLP:deployment_guide_v1

## 1. Purpose & Scope
This guide enables contributors to stand up a reproducible local and (future) Kubernetes-based deployment of Aurora CloudBank Symbolic, adhering to project invariants:
- Use `make setup` (never raw `pip install`) – enforces lockfile and conflict resolution
- Preserve DLP lineage, T1/SRB anchors, and memory seals integrity
- Maintain security posture (no plaintext secrets; parameterized logging; verify dependency health)

## 2. Prerequisites
| Component | Version / Note |
|-----------|----------------|
| Python | 3.11+ (verified via `make status`) |
| GitHub CLI | Authenticated (`gh auth status`) |
| Docker | Latest stable; for containerized runs |
| Make | GNU Make 4.x |
| kubectl (optional) | For Kubernetes deployment previews |
| Helm (planned) | For future chart release |

## 3. First-Time Environment Setup
```bash
# Clone repository
git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic

# Initialize environment (creates venv, installs pinned deps)
make setup

# Verify environment & dependency health
make status
python scripts/dev-status.py

# Run fast quality gate (lint + tests)
make check
```
**Do Not:** Run `pip install -r requirements.txt` directly (bypasses lock + conflict safeguards).

## 4. Everyday Developer Workflow
```bash
# Activate venv (if not auto-activated)
source .venv/bin/activate

# Pull latest changes
git pull --rebase origin main

# Run integration planner (#932//.) to prioritize work
python scripts/integration_plan_932.py --phases

# Execute quick win PR actions or rebase tasks as surfaced
# (See Intelligent Integration Plan spec for sequencing)

# Run focused tests
pytest -m unit -q

# Full suite before large merges
make test
```

## 5. Running the FastAPI Server
Primary entrypoint: `api/aurora_api.py` (NOT the legacy root file).
```bash
# Start server
make run
# or
python api/aurora_api.py

# Health checks
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```
Routers auto-injected: Memory Manager, Monitoring Dashboard, Resilience Sentinel, HR System, Quantum Simulator, Ethics (GUMAS).

## 6. Security & Quality Gates
| Gate | Command | Purpose |
|------|---------|---------|
| Lint (scoped) | `make lint-tools` | Fast lint of modern toolsets |
| Lint (full) | `make lint-all` | Broad lint (may surface legacy issues) |
| Tests | `make test` | Complete pytest suite |
| Security | `make security` | Bandit & safety scans |
| Maintenance | `make maintenance-scan` | Automated maintenance pipeline |

### Pre-Commit Checklist
- Flake8 line limit respected (120 chars)
- Added/updated tests for new functionality
- No blocking CI failures
- DLP tags included for export operations
- Optional dependency imports wrapped in try/except

## 7. Rebase & Merge Workflow (From #932//. Plan)
**Batch Rebase Phase:**
```bash
gh pr checkout <PR_NUMBER>
git fetch origin main
git rebase origin/main
# Resolve conflicts
git add .
git rebase --continue
git push --force-with-lease
```
Repeat per PR in the rebase batch. Use mission scoring to prioritize PRs addressing critical issues.

## 8. Handling CI Failures
- Use `gh pr checks <PR_NUMBER>` to inspect
- For failing lint/tests: reproduce locally
```bash
pytest -k <affected_test>
make lint-tools
```
- For dependency or security alerts: run `make security` then patch

## 9. Adding New Features
1. Create feature branch: `git switch -c feature/<short-descriptor>`
2. Implement scoped changes (respect optional dependency patterns)
3. Add tests (`tests/` with appropriate markers)
4. Run `make check`
5. Open PR; ensure issue reference in description (`Closes #<issue>`)
6. Re-run `#932//.` to see integration position

## 10. Kubernetes Deployment (Preview)
A skeleton manifest is provided in `k8s/deployment/aurora-cloudbank.yml` (Issue #385). **Status:** Draft.
```bash
# Apply (experimental)
kubectl apply -f k8s/deployment/aurora-cloudbank.yml
# Check resources
kubectl get pods -l app=aurora-cloudbank
```
Future: Helm chart, environment overlays (dev/stage/prod), secrets via sealed-secrets.

## 11. Troubleshooting
| Symptom | Resolution |
|---------|------------|
| `ImportError` for optional module | Verify graceful degradation path; mock if needed |
| Server wont start | Confirm using `api/aurora_api.py`; check dependency validation script |
| Tests hanging | Use `pytest -m unit -vv --maxfail=1` to narrow scope |
| PR not prioritized | Ensure issue reference + quality indicators present |

## 12. DLP & Anchor Integrity
All exports must include:
- `context_tag` (operation context)
- Symbolic hash validation
- Manifest creation via `NativeDLPTracker.create_export_manifest`
Advances T1/SRB anchors per chain execution.

## 13. Next Improvements (Follow-up to Issue #387)
- Add deployment troubleshooting matrix
- Expand Kubernetes section (resource requests, autoscaling)
- Include CI workflow diagrams
- Add secret management policy section

---
**Maintainer:** R-2 Mode (Integration & Validation)
**Last Updated:** 2025-11-19
**Version:** 1.0.0
