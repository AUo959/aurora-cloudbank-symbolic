# Phase 1 – CI Stabilization & Deployment Unblock

> Objective: Get all targeted PRs (#372, #375, #376, #378) green by propagating workflow + Vercel fixes, then collect fresh gate outputs to inform Phase 2.

## Scope
- Workflow integrity: `.github/workflows/collab-sync.yml` (pinned actions, allowlist fallback)
- Deployment config: `vercel.json` (modern functions runtime)
- PR Branch Sync: Rebase/merge main into target branches
- Check Categories: Minimal CI, Code Quality Analysis, PR Evaluation, Selective Integration, Vercel, SonarCloud, Codacy Quality Gate

## PR Status Matrix (Pre-Rebase Snapshot – PLACEHOLDERS)
| PR | Branch | Minimal CI | Vercel | Quality Gate | PR Eval | Selective Integration | Codacy | SonarCloud | Action Required |
|----|--------|-----------|--------|--------------|---------|-----------------------|--------|-----------|----------------|
| #372 | chore/coverage-syntax-fixes | FAIL | FAIL | PENDING | FAIL | FAIL | WARN | FAIL | Yes |
| #375 | AUo959-pbpaste-|-patch | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | Yes |
| #376 | claude/claude-md-mi195x335e1nhkdy-01EnfSEMdXZ1wBghSvejx2oR | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL | Yes |
| #378 | copilot/sub-pr-376 | FAIL | FAIL | CANCELLED | FAIL | FAIL | WARN | FAIL | Yes |

Replace placeholders after reruns with actual statuses.

## Rebase & Rerun Checklist
1. Fetch latest main.
2. Checkout PR branch.
3. Rebase onto `origin/main` (or merge if preferred, rebase recommended for linear history).
4. Force push with lease.
5. Trigger CI rerun (GitHub UI if CLI lacks permission).
6. Capture new statuses and update matrix.

### Rebase Commands (Template)
```bash
# Replace <branch-name> with actual branch from PR metadata
git fetch origin
git checkout <branch-name>
git rebase origin/main
# Resolve conflicts if any, then:
git push --force-with-lease origin <branch-name>
```

## Post-Rerun Data Collection
Capture for each PR:
- Vercel build ID / link
- Failing job names & logs summary (first error line)
- Codacy gate result (pass/fail) & top 3 issue types
- SonarCloud quality gate status (overall + key metric breaches)

## Success Criteria
- All 4 target PRs: Green or only non-blocking warnings.
- Vercel deployments: SUCCESS for each branch.
- No unpinned action warnings in workflows.
- Codacy & SonarCloud: Pass or reduced failures with actionable list.

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Rebase conflicts | Delay | Resolve iteratively; prioritize workflow & config file correctness |
| Permission to rerun checks | Blocks automation | Use UI; escalate token scope if persistent |
| Hidden dependency failures | Unexpected CI breaks | Run `make check` locally before push |
| Vercel environment mismatch | Continued deploy failure | Verify runtime logs; ensure `api/index.py` reachable |

## Next After Success
Proceed to Phase 2 – Quality & Modernization:
- Address residual lint/security findings
- Increment targeted test coverage
- Consolidate workflow duplication (common composite)

## Data Capture Template (Update After Reruns)
```yaml
phase1_results:
  collected_at: <timestamp>
  prs:
    - number: 372
      branch: <branch>
      checks:
        minimal_ci: PASS
        vercel: PASS
        pr_evaluation: PASS
        selective_integration: PASS
        codacy_quality_gate: PASS
        sonarcloud: PASS
      notes: ""
    - number: 375
      branch: <branch>
      checks: { ... }
    - number: 376
      branch: <branch>
      checks: { ... }
    - number: 378
      branch: <branch>
      checks: { ... }
summary:
  blockers_remaining: []
  transition_ready: true
```

## Operator Actions Pending
- Fill branch names from PR metadata.
- Execute rebase sequence for each branch.
- Trigger UI reruns.
- Update matrix + YAML template.

---
Anchor: PHASE-1-CI-STABILIZATION
Created: 2025-11-17

## Status Snapshot (2025-11-17)
- PR #372 (chore/coverage-syntax-fixes): CI Check: FAILURE; Code Quality Analysis: FAILURE; evaluate: FAILURE; evaluate-and-integrate: FAILURE; SonarCloud Code Analysis: FAILURE. Many other analyzers/tests green.
- PR #375 (AUo959-pbpaste-|-patch): Checks pending/neutral; infra checks green (content-labeling, security-scan, dashboards).
- PR #376 (claude/claude-md-mi195x335e1nhkdy-01EnfSEMdXZ1wBghSvejx2oR): Checks pending/neutral; infra checks green.
- PR #378 (copilot/sub-pr-376): Checks pending/neutral; infra checks green.
- PR #390 (Phase 1): CI Check: FAILURE; Code Quality Analysis: FAILURE; evaluate: FAILURE; evaluate-and-integrate: FAILURE; Codacy Static Code Analysis: ACTION_REQUIRED; most other analyzers/tests green.

````
