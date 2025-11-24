# Intelligent Integration Plan – Command `#932//.`

**Version:** 2.1.0  
**Purpose:** Generate mission-focused, phased integration plans with quality gates, issue context, and selective integration logic to ensure optimal merge order and prevent code regression.

---
## 🔧 Command Summary
`#932//.` executes the Intelligent Integration Planner v2.1 – **Mission-Focused Edition**

**What's New in v2.1 (Mission-Focused):**
- 🎯 **Mission Scoring:** PRs prioritized by repository improvement value
  - Critical/high-priority issue resolution: +3/+2 mission score
  - Code quality improvements: added to mission score
  - Mission-focused ordering prevents merging inferior code
- 🔍 **Quality Assessment:** Automated code quality scoring
  - Positive indicators: code reduction (+2), test coverage (+1), documentation (+1)
  - Negative indicators: large untested changes (-2), huge single files (-1)
  - Quality recommendations: merge/verify_tests/review_carefully
- 📋 **Issue Integration:** Full open issue context with PR mapping
  - Issues grouped by priority (critical/high/medium/low)
  - Shows which PRs address each issue
  - Identifies orphaned issues (no PRs addressing them)
  - Issue priority influences merge order
- ⚡ **Selective Integration Logic:** Quality gates prevent mistakes
  - Each PR validated for code improvement before merge
  - Mission score ensures critical issues addressed first
  - Older PRs (lower number) prioritized when mission score equal

**What's Still in v2:**
- **Specific execution strategies** per PR (not generic task lists)
- **Context-aware commands** based on actual PR state
- **Phased integration sequence** with checkpoint gates
- **Decision tree logic** for 6 PR states: immediate, quick_win, rebase_required, fix_required, wait, complex

**Process:**
1. Scans all open & draft pull requests with detailed state analysis
2. Evaluates each PR through decision tree:
   - ✅ **Immediate:** Ready to merge (all checks passed, no blockers)
   - ⚡ **Quick Win:** Clean draft (just needs "mark ready")
   - 🔄 **Rebase Required:** Has merge conflicts
   - 🔧 **Fix Required:** Failing CI checks
   - ⏳ **Wait:** CI checks pending
   - 🎯 **Complex:** Needs manual triage
3. Generates **phased integration sequence** with specific commands:
   - Phase 1: Immediate Merge Batch
   - Phase 2: Quick Win Activation
   - Phase 3: Batch Rebase & Conflict Resolution
   - Phase 4: CI Failure Remediation
   - Phase 5: Pending CI Checks
   - Phase 6: Complex Case Triage
4. Provides **checkpoint gates** between phases
5. Outputs both Markdown (human-readable) and JSON (machine-parseable)

---
## 🧠 Evaluation Dimensions
Each PR is scored across dimensions:
- **Mission Alignment:**
  - Linked to critical issues (+3 mission score)
  - Linked to high-priority issues (+2 mission score)
  - Code quality improvements (adds to mission score)
- **Quality Assessment:**
  - Code reduction (fewer lines = +2)
  - Test coverage (test files = +1)
  - Documentation (docs = +1)
  - Large untested changes (-2)
  - Huge single files >500 lines (-1)
- **Issue Context:**
  - Which issues the PR addresses
  - Issue priority level (critical/high/medium/low)
  - Age of unaddressed issues (escalates priority)
- **Technical State:**
  - Draft status
  - Mergeability (`mergeStateStatus`, conflicts)
  - Status checks rollup (passing/failing/pending)
  - Review decision & required approvals
- **Dependencies & Risk:**
  - Linked issues (direct closing references or body mentions)
  - Task density (derived readiness tasks)
  - Dependency hints (mentions of other PR numbers)
  - **Risk scoring** (files changed, code churn)
  - **Dependency graph** (which PRs block others)
  - **Time estimates** (based on size and complexity)

---
## 🎯 Mission-Focused Ordering

**Philosophy:** The integration planner prioritizes work that advances repository function, not just executes tasks.

**Ordering Algorithm (Applied to All Phases):**
1. **Mission Score (Descending):** Higher mission scores first
   - PRs addressing critical issues (score 3+) have priority
   - PRs addressing high-priority issues (score 2+) next
   - Quality improvements add to mission score
2. **Quality Score (Descending):** Higher quality code first when mission score equal
   - Code reduction preferred over additions
   - Test coverage and docs increase score
3. **PR Number (Ascending):** Older PRs first when mission/quality equal
   - Lower PR numbers = older work likely more foundational

**Quality Gates:**
- ⚠️ PRs with negative quality scores get "verify_tests" recommendation
- 🔴 PRs with score -2 or lower get "review_carefully" recommendation
- ✅ PRs with score 0+ get "merge" recommendation

**Selective Integration Logic:**
- Each PR's quality assessed before merge recommendation
- Mission scoring prevents inferior code from overwriting existing work
- Critical/high-priority issues always float to top of their phase
- Quality warnings signal need for careful review

**Example Ordering:**
```
Phase: Immediate Merge
  1. ⭐ PR #404 (mission: 3, quality: 0) - Addresses CRITICAL issue #384
  2. 🎯 PR #403 (mission: 2, quality: 1) - Addresses HIGH issue #383, has tests
  3. PR #402 (mission: 0, quality: 2) - Code reduction, good quality
  4. PR #401 (mission: 0, quality: -1) - Needs review, large untested change
```

---
## 📊 Output Structure (JSON)
```jsonc
{
  "generated_at": "2025-11-19T14:25:00Z",
  "repository": "owner/repo",
  "summary": {
    "total_open_prs": 12,
    "phase_counts": {"phase_1": 4, "phase_2": 5, "phase_3": 3},
    "estimated_phase_1_time": "45min",
    "high_risk_count": 2,
    "draft_count": 3
  },
  "phases": {
    "phase_1": [ 
      {"number": 123, "title": "Ready PR", "tasks": [], "issues": [456], 
       "risk": "low", "files_changed": 3, "time_estimate": "5-15min"} 
    ],
    "phase_2": [ 
      {"number": 124, "title": "Minor fixes", "tasks": ["Fix failing check"], 
       "risk": "medium", "files_changed": 15, "time_estimate": "30-60min"} 
    ],
    "phase_3": [ 
      {"number": 125, "title": "Complex refactor", "tasks": ["Resolve conflicts"], 
       "risk": "high", "files_changed": 47, "time_estimate": "60-120min"} 
    ]
  },
  "recommendations": [
    "3 PRs in draft - marking ready could accelerate Phase 2",
    "PR #125 blocks 2 others - prioritize merge"
  ],
  "bottlenecks": [
    {"pr": 125, "blocks": 2},
    {"pr": 130, "blocks": 1}
  ],
  "critical_path": [125, 130, 131],
  "checkpoints": [
    {"name": "Batch Merge – Ready Set", "prs": [123, 130, 131]},
    {"name": "Rebase Complex Group", "prs": [125, 128]}
  ],
  "ordering": [123,130,131,124,126,125]
}
```

---
## ✅ Phase Definitions

| Phase | Criteria | Action |
|-------|----------|--------|
| 1 – Ready | No tasks, mergeable, not draft | Merge immediately (respect CI sequence) |
| 2 – Near-Ready | ≤ 2 tasks, no structural blockers | Triage tasks, re-run checks, merge next |
| 3 – Complex | > 2 tasks OR conflicts OR missing review gating | Assign owners, schedule sequentially |

---
## 🛠 Readiness Task Heuristics

| Condition | Generated Task |
|-----------|----------------|
| `isDraft == true` | "Mark ready for review" |
| `mergeStateStatus != CLEAN` | "Resolve merge conflicts" |
| Failing status check | "Fix failing status checks" |
| Pending status check | "Wait for or rerun checks" |
| No linked issues | "Link or create issue reference" |
| Review required | "Obtain required approvals" |
| Mentions another PR in body | "Verify dependency PR sequencing" |
| No tests changed (heuristic) | "Add or confirm test coverage" |

---
## 🚀 Execution

**Full Plan (Markdown + JSON):**
```bash
python scripts/integration_plan_932.py
```

**Phases Only (Quick Summary):**
```bash
python scripts/integration_plan_932.py --phases
```

**JSON Only (For Automation):**
```bash
python scripts/integration_plan_932.py --json-only
```

**Interactive Execution:**
```bash
python scripts/integration_plan_932.py --execute  # Future: step-through mode
```

**Example Output:**
```
# 🎯 Phased Integration Plan

## 📊 Summary
- Total PRs: 15
- Estimated Total Time: 300min
- High Risk PRs: 8
- Phases with Work: 3

## 🚀 Integration Sequence

### Phase 1: 🚀 Immediate Merge Batch
PRs ready to merge with zero blockers
- PRs: #123, #456
- Estimated Time: 6min
- Checkpoint: ✅ Verify all merged successfully

Commands:
gh pr view 123  # Final review
gh pr merge 123 --squash --auto
gh pr view 456
gh pr merge 456 --squash --auto

### Phase 2: 🔄 Batch Rebase & Conflict Resolution
Rebase conflicting PRs on updated main
- PRs: #407, #400, #401
- Estimated Time: 60min
- Checkpoint: ⚠️ Test each rebased PR locally

Commands:
gh pr checkout 407
git fetch origin main
git rebase origin/main
# Resolve conflicts, then:
git push --force-with-lease
```

**Command Chain Flow:**
```
#932//. → Plan → Execute Phase 1 → #932//. (re-scan) → Execute Phase 2 → Repeat
```

If integrated into higher command chain automation, `#932//.` will invoke the script and surface output.

---
## 🧪 Checkpoints Strategy
The planner suggests checkpoints:
- **Batch Merge (Ready Set):** Merge all Phase 1 PRs back-to-back (guarded by CI green). 
- **Rebase Pivot:** After Phase 1, rebase Phase 2 PRs to minimize churn.
- **Complex Integration Gate:** Schedule Phase 3 merges individually with targeted validation.

---
## 🔒 Safety & DLP
All output may embed a lineage manifest:
- `context_tag`: `integration_plan_932`
- Hash of ordered PR list for reproducibility

---
## 📥 Dependencies
Requires:
- GitHub CLI (`gh`) authenticated
- Network access to repo metadata

Graceful degradation: If `gh` is unavailable, script will emit a structured error with mitigation guidance.

---
## 🧩 Extensibility
Future enhancements:
- Detect cross-repo dependencies
- Auto-generate `gh workflow run` triggers for blocked CI
- Integrate semantic diff complexity scoring
- Add risk weighting (files touched, churn, test delta)

---
## 🧾 Example Markdown Snippet (v2.1)
```markdown
# 🎯 Phased Integration Plan
Generated: 2025-11-19T14:25:00Z
Repository: owner/repo

## 📊 Summary
- **Total PRs:** 15
- **Estimated Total Time:** 300min
- **High Risk PRs:** 15
- **Phases with Work:** 3

### Phase Breakdown
- **quick_win:** 3 PR(s)
- **rebase_required:** 10 PR(s)
- **wait:** 2 PR(s)

## 🎯 Open Issues Overview

### 🚨 CRITICAL Priority (5 issues)
- **Issue #384:** Activate Telemetry and Observability → Addressed by PR(s): #404
- **Issue #383:** Add RBAC and OAuth2 Authentication → Addressed by PR(s): #403
- **Issue #387:** Provide Developer Deployment Guide ⚠️ No PRs addressing this issue
- **Issue #385:** Implement Kubernetes CI Pipeline ⚠️ No PRs addressing this issue
- **Issue #382:** Consolidate MCP Bridge Logic → Addressed by PR(s): #389

### ⚠️ Orphaned Issues (No PRs)
- 🚨 Issue #387: Provide Developer Deployment Guide (critical)
- 🚨 Issue #385: Implement Kubernetes CI Pipeline (critical)

## 🚀 Integration Sequence

### Phase 1: ⚡ Quick Win Activation
**Mark clean drafts as ready for review**
- **PRs:** #404, #408, #410
- **Count:** 3
- **Estimated Time:** 24min
- **Checkpoint:** 📋 Review each before marking ready

## 📋 Detailed PR Strategies

### 🔴 ⭐ PR #404: Activate telemetry and observability infrastructure
**Phase:** quick_win | **Mission Score:** 3
**Estimated Time:** 8min

**Addresses Issues:**
- 🚨 Issue #384: Activate Telemetry and Observability (critical priority)

**Code Quality:** ✅ Score: 2 | Recommendation: merge
  - Positive: Code reduction, Test coverage

**Risk Factors:**
- ⭐ Addresses CRITICAL issue
- High complexity: 4 files, 706 lines

### 🔴 PR #409: chore(deps): bump glob dependency
**Phase:** rebase_required | **Mission Score:** 0
**Estimated Time:** 15-30min

**Code Quality:** 🔴 Score: -1 | Recommendation: verify_tests
  - Warnings: Large single-file change: package-lock.json

**Risk Factors:**
- ⚠️ Quality concerns - review carefully
- High complexity: 2 files, 1338 lines

## Phase 2 – Near-Ready (5)
- PR #124: Fix tests (15-30min) – Fix failing status checks
- PR #126: Update docs (5-15min) – Link or create issue reference

## Phase 3 – Complex (3)
- 🔴 PR #125: Complex refactor (60-120min) – Resolve conflicts; Verify dependency PR sequencing

### Checkpoints
1. Batch merge Phase 1 (123,130,...)
2. Rebase Phase 2 after Phase 1
3. Sequential merge Phase 3 with focused validation
```

---
## 🔁 Invocation Pattern
Use command syntax anywhere the parser is active:
```
Please generate the integration roadmap #932//.
```
Parser recognizes `932` as supported numeric alias and dispatches the workflow.

---
## 🧪 Testing Notes
A minimal test ensures:
- Script runs without exception
- JSON block contains `phases.phase_1`, `phases.phase_2`, `phases.phase_3`
- Markdown includes `Phase 1` heading

---
## 📣 Ownership
Maintainer: Integration & Release Engineering (R-2 Mode)
Escalation: Open issue tagged `integration-plan` if heuristics need tuning.

---
*End of specification for `#932//.`*

---
## 🛰 Current Integration Readiness Snapshot (UTC & Lifespan Modernization)
Generated: 2025-11-24T00:00:00Z (planner context)

### ✅ Recently Completed Modernization Steps
- Centralized UTC time utilities (`utc_now`, `utc_iso`, `utc_z`) adopted across core runtime (monitoring dashboard, symbolic engine, coordination models, audit logging, relay agents, Nexus core modules: entity manager, multi-agent coordinator, reality fork manager, memory weaver, entropy monitor, quantum bridge).
- Added shutdown manifest helper in `api/aurora_api.py` (Phase 1 implementation) capturing telemetry snapshot, HALO/PAS state, crew agent inventory with deterministic SHA-256 hash.
- Lifespan context confirmed and extended: startup initializes telemetry + drift controller, shutdown now persists manifest (`shutdown_manifest.json`).
- Initial targeted UTC sweep applied to high-impact script (`scripts/nexus_drift_detector.py`) migrating from `datetime.utcnow()` → `utc_iso()` and removing bare `except` blocks.
- Crew agent merge conflict artifacts resolved; related API tests passing (4/4 in `tests/test_crew_agents_api.py`).

### 📌 Remaining Temporal Debt (UTC Migration)
Occurrences of legacy `datetime.utcnow` persist in multiple scripts (examples):
- `scripts/nexus_phase*` verification & roadmap scripts (phase1, phase2, phase5, post_sync).
- `scripts/gitwiz_*` workflow orchestrators and dependency updaters (time deltas, execution windows).
- `scripts/gumas_*` status / scanner utilities (glyphcard, codebase scanner, status implementation summary).
- `scripts/aurora_codeql_diagnostics.py`, `scripts/consolidate_codeql.py` (diagnostic stamping).
Prioritization heuristic:
1. Drift / verification pipelines (phase & post-sync scripts) – high integration impact.
2. GitWiz orchestration scripts – affect automation timing and audit accuracy.
3. Security / diagnostics stamping – ensure consistent ordering in audit chains.

### 🔄 Next Temporal Migration Wave (Proposed Sequence)
Phase A (High Impact):
1. `scripts/nexus_phase1_verify.py`
2. `scripts/nexus_post_sync_verification.py`
3. `scripts/nexus_phase5_verification_manifest.py`
Phase B (Automation Core):
4. `scripts/gitwiz_workflow_orchestrator.py`
5. `scripts/gitwiz_integrated_command.py`
6. `scripts/gitwiz_dependency_updater.py`
Phase C (Diagnostics / Compliance):
7. `scripts/aurora_codeql_diagnostics.py`
8. `scripts/gumas_codebase_scanner.py`
9. `scripts/consolidate_codeql.py`

Each file: replace `datetime.utcnow()` with `utc_iso()` (string contexts) or `utc_now()` (delta / arithmetic), remove ad-hoc formatting, ensure no bare `except:` usages.

### 🧪 Lifespan & Manifest Enhancement Roadmap
 
| Phase | Enhancement | Outcome |
|-------|-------------|---------|
| 1 (done) | Basic shutdown manifest with telemetry + controller state | Deterministic snapshot |
| 2 | Add memory seals & Nexus state digests (entropy, fork counts) | Broader integrity coverage |
| 3 | Include pending task queue & active agent collaboration metrics | Operational traceability |
| 4 | DLP lineage embedding (chain notation + symbolic anchors) | Full provenance chain |
| 5 | Configurable export channel (S3 / artifact uploader) | External retention |

### 🧪 Recommended Validation Additions
Tests to add (before Phase 2 lifespan enhancements):
- `test_lifespan_shutdown_manifest_creation` (assert file exists, required keys: generated_at, components.telemetry.performance_metrics, hash length = 64).
- `test_utc_consistency_in_manifest` (regex ensure timestamps end with 'Z' or use ISO without naive forms).
- `test_drift_detector_utc_migration` (assert no `datetime.utcnow` substring remains; ensure timestamp field present and formatted).

### 🎯 Mission Alignment Impact (PR #418 – Crew Agents Completion)
- Enhances operational surface: crew agent inventory now captured in manifest → improves integration sequencing for subsequent multi-agent coordination PRs.
- Reduces future merge friction by resolving latent merge conflict markers and normalizing time handling before broad integration targeting (#932 workflow).
- Suggested mission scoring bump criteria: +1 quality (conflict resolution), +1 reliability (UTC standardization proximity when follow-up sweep completes).

### 🔐 Risk & Gate Summary
 
| Risk | Mitigation | Gate Condition |
|------|------------|----------------|
| Partial UTC migration may yield mixed timestamp formats | Execute Phase A & B sweeps | All NEXUS verification scripts free of `datetime.utcnow` |
| Manifest lacks memory/quantum state | Implement Phase 2 helper augmentation | Presence of `components.memory_seals` key |
| Untracked automation drift in GitWiz scripts | Migrate timestamps + add delta assertions | Execution time calculations use `utc_now()` |
| Inconsistent diagnostics stamping | Standardize to UTC utilities | All diagnostic JSON emits ISO 8601 with 'Z' suffix |

### 🧩 Immediate Action Commands (Manual Execution)
```bash
# Phase A UTC sweep (example single-file patch loop)
sed -i "s/datetime.utcnow().isoformat()/utc_iso()/g" scripts/nexus_phase1_verify.py
sed -i "s/datetime.utcnow().isoformat()/utc_iso()/g" scripts/nexus_post_sync_verification.py
sed -i "s/datetime.utcnow().isoformat()/utc_iso()/g" scripts/nexus_phase5_verification_manifest.py

# Verify no legacy usage remains in Phase A targets
grep -n "datetime.utcnow" scripts/nexus_phase1_verify.py scripts/nexus_post_sync_verification.py scripts/nexus_phase5_verification_manifest.py || echo "Phase A clean"

# Run focused tests (placeholder names; add when tests created)
pytest -k shutdown_manifest -v || true
```

### 🧪 Integration Checkpoint Injection for `#932//.`
Add after Phase 1 scanning:
```
Checkpoint: UTC Temporal Consistency – verify no mixed naive timestamps in readiness-critical scripts.
If inconsistent: auto-insert tasks → "Migrate remaining datetime.utcnow occurrences".
```

### 📓 Lineage & Provenance Extension (Planned)
- Add `context_tag": "shutdown_manifest_v2"` and embed anchor exports (`T1`, `SRB`).
- Include chain notation for integration wave: e.g., `"integration_chain": "001//932//"` when invoked within command chain.

### 🏁 Summary
System is in strong position for mission-focused integration sequencing: core runtime stabilized, manifest groundwork laid, remaining temporal debt scoped and ordered. Proceed with Phase A UTC sweep before expanding planner heuristics to enforce temporal consistency gates.

---
