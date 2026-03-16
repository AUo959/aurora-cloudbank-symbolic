# 🧹 Branch Cleanup Analysis — Orion Station Operations

**Date:** 2026-03-09  
**Previous Analysis:** 2025-11-12  
**Mission:** Safe branch consolidation and cleanup

---

## 📊 Current State Assessment

**Total Remote Branches:** 24  
**Open PRs:** 4 (including this cleanup PR)  
**Safe to Delete:** 12 branches  
**Needs Review:** 7 branches  

Previous cleanup efforts (Nov 2025) reduced branches from 58 → 24.
This analysis targets the remaining stale branches.

---

## 🎯 Branch Categories

### 🔒 **KEEP — Protected / Active** (5 branches)

| Branch | Status | Notes |
|--------|--------|-------|
| `main` | Default branch | Protected |
| `copilot/consolidate-and-cleanup-branches` | PR #478 open | This cleanup PR |
| `staging/wave1-2026-03-08` | PR #475 open | Active staging wave |
| `staging/wave2-deps-2026-03-08` | PR #476 open | Active dependency batch |
| `staging/wave3-pr462-clean-2026-03-08` | PR #477 open | Active markdownlint bump |

---

### ✅ **SAFE TO DELETE — Closed PRs (never merged)** (8 branches)

These branches had PRs that were closed without merging. Work was either
superseded, abandoned, or consolidated into other PRs.

| Branch | PR | Age (days) | Ahead | Behind | Reason |
|--------|----|-----------|-------|--------|--------|
| `chore/fix-vercel-deploy-config` | #469 closed | ~73 | 1 | 10 | Superseded by staging waves |
| `chore/venv-consistent-tooling` | #468 closed | ~73 | 1 | 10 | Superseded by staging waves |
| `claude/claude-md-mi195x335e1nhkdy-01EnfSEMdXZ1wBghSvejx2oR` | #376 closed | ~109 | 5 | 158 | CLAUDE.md written via other path |
| `claude/orion-crew-search-01HqwbewEu9C964Fo4MRG6aq` | #415 closed | ~107 | 15 | 140 | Superseded by PRs #416–418 (merged) |
| `copilot/add-constellink-symbolic-module` | #414 closed | ~103 | 3 | 123 | Superseded by merged forecast engine |
| `copilot/fix-quality-gate-issue` | #452 closed | ~94 | 2 | 41 | Quality gate issue resolved elsewhere |
| `copilot/start-work-on-pr-412` | #420 closed | ~103 | 2 | 114 | Work completed in parent PR #412 |
| `copilot/sub-pr-445` | #449 closed | ~94 | 13 | 41 | Sub-PR not merged; parent #445 merged |

---

### ✅ **SAFE TO DELETE — Stale, No PR** (3 branches)

These feature branches have no associated PR and are significantly behind main.

| Branch | Age (days) | Ahead | Behind | Notes |
|--------|-----------|-------|--------|-------|
| `feature/drift-aware-agents` | ~115 | 1 | 366 | Nov 2025, placeholder branch |
| `feature/ethical-checkpointing` | ~115 | 1 | 366 | Nov 2025, placeholder branch |
| `feature/symbolic-forecast-engine` | ~115 | 1 | 366 | Nov 2025, work merged via `copilot/implement-symbolic-forecast-engine` PR #419 |

---

### ✅ **SAFE TO DELETE — Very Old Patch** (1 branch)

| Branch | Age (days) | Ahead | Behind | Notes |
|--------|-----------|-------|--------|-------|
| `AUo959-patch-quantum-forge-vector-gen` | ~117 | 1 | 407 | Nov 2025, no open PR |

---

### ⚠️ **NEEDS REVIEW** (4 branches)

These branches are relatively recent or have unique content worth checking.

| Branch | Age (days) | Ahead | Behind | Notes |
|--------|-----------|-------|--------|-------|
| `chore/recover-local-main-commits-2026-03-08` | ~1 | 2 | 0 | Very recent, 2 commits not on main |
| `claude/fix-cl-checks-WoZGv` | ~4 | 3 | 0 | Recent, 3 commits not on main |
| `claude/code-quality-review-0173PBr3e4Gd8be4ikMhrKvx` | ~109 | 2 | 171 | No PR, stale but has unique content |
| `claude/developer-friendly-brainstorm-011CUwVb3PEhKevELRWLvtbB` | ~113 | 3 | 572 | Very old, deeply diverged |

**Substatus for review branches:**
- `chore/recover-local-main-commits-2026-03-08` — Created same day as staging waves; may contain commits intended for main. **Check if these commits are in the staging branches.**
- `claude/fix-cl-checks-WoZGv` — Recent CI fix work. **Check if fixes landed on main.**
- `claude/code-quality-review-*` and `claude/developer-friendly-brainstorm-*` — Old Claude session branches. Likely safe to delete but verify no unique docs.

---

### 🔍 **Staging Branches (not in scope)** (2 integration branches)

These staging branches are not associated with open PRs but were used for
integration work alongside the active wave PRs.

| Branch | Age (days) | Ahead | Behind | Notes |
|--------|-----------|-------|--------|-------|
| `staging/integration-2026-03-06` | ~3 | 8 | 0 | Integration staging |
| `staging/integration-deps-2026-03-06` | ~1 | 17 | 0 | Deps integration staging |

**Recommendation:** Keep until wave PRs (#475–477) are resolved.

---

### 🔍 **Claude Review Branch** (1 branch)

| Branch | Age (days) | Ahead | Behind | Notes |
|--------|-----------|-------|--------|-------|
| `claude/review-recent-agents-01JLVAkok774R7ERR7XjN6hS` | ~105 | 5 | 129 | Agent review session, no PR |

**Recommendation:** Safe to delete after verifying no unique review docs.

---

## 🚀 Cleanup Commands

### Phase 1: Closed PR branches (zero risk)

```bash
git push origin --delete \
  chore/fix-vercel-deploy-config \
  chore/venv-consistent-tooling \
  claude/claude-md-mi195x335e1nhkdy-01EnfSEMdXZ1wBghSvejx2oR \
  claude/orion-crew-search-01HqwbewEu9C964Fo4MRG6aq \
  copilot/add-constellink-symbolic-module \
  copilot/fix-quality-gate-issue \
  copilot/start-work-on-pr-412 \
  copilot/sub-pr-445
```

### Phase 2: Stale feature branches (zero risk)

```bash
git push origin --delete \
  feature/drift-aware-agents \
  feature/ethical-checkpointing \
  feature/symbolic-forecast-engine \
  AUo959-patch-quantum-forge-vector-gen
```

### Phase 3: After review of "Needs Review" branches

```bash
# Only after confirming content is not needed:
git push origin --delete \
  claude/code-quality-review-0173PBr3e4Gd8be4ikMhrKvx \
  claude/developer-friendly-brainstorm-011CUwVb3PEhKevELRWLvtbB \
  claude/review-recent-agents-01JLVAkok774R7ERR7XjN6hS
# Recent branches — delete only after verifying content:
# git push origin --delete chore/recover-local-main-commits-2026-03-08
# git push origin --delete claude/fix-cl-checks-WoZGv
```

### Phase 4: After staging wave PRs are resolved

```bash
git push origin --delete \
  staging/integration-2026-03-06 \
  staging/integration-deps-2026-03-06
```

---

## 📊 Expected Impact

| Phase | Branches Removed | Remaining |
|-------|-----------------|-----------|
| Before | — | 24 |
| Phase 1 (closed PRs) | 8 | 16 |
| Phase 2 (stale features) | 4 | 12 |
| Phase 3 (after review) | 3–5 | 7–9 |
| Phase 4 (after staging) | 2 | 5–7 |

**Target state:** 5–7 branches (main + active work only)

---

## 🔧 Automated Cleanup Tool

For future cleanups, use the safe branch cleanup script:

```bash
# Dry-run analysis (safe — no changes)
python scripts/safe_branch_cleanup.py

# Generate report to file
python scripts/safe_branch_cleanup.py --save-report BRANCH_CLEANUP_PLAN.md --report-only

# Execute cleanup (deletes safe-to-remove branches)
python scripts/safe_branch_cleanup.py --execute

# Custom staleness threshold
python scripts/safe_branch_cleanup.py --stale-days 60
```

Or via Makefile:
```bash
make branch-cleanup-dry     # Preview deletions
make branch-cleanup-safe    # Run safe_branch_cleanup.py in dry-run mode
```

---

**Report Generated:** 2026-03-09  
**Next Review:** After Phase 1+2 execution  
**Tool:** `scripts/safe_branch_cleanup.py`
