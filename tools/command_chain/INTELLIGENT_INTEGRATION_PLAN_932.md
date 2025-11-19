# Intelligent Integration Plan – Command `#932//.`

**Version:** 1.0.0  
**Purpose:** Automatically survey repository issues & pull requests, derive readiness tasks, and synthesize a phased, checkpointed merge strategy optimized for stability and throughput.

---
## 🔧 Command Summary
`#932//.` executes the Intelligent Integration Planner.

It:
1. Scans all open issues
2. Scans all open & draft pull requests
3. Maps PR ↔ Issue relationships (closing references & inline `#<issue>` mentions)
4. Evaluates each PR for readiness (draft state, failing checks, missing reviews, missing issue linkage, merge conflicts, incomplete metadata)
5. Generates a **phased integration plan**:
   - **Phase 1 (Ready)**: Zero blocking tasks – safe to merge immediately
   - **Phase 2 (Near-Ready)**: ≤ 2 minor tasks – quick wins to unblock
   - **Phase 3 (Complex)**: Requires multiple or structural tasks – schedule carefully
6. Emits both human-readable Markdown and machine-friendly JSON
7. Provides **checkpoint suggestions** (review gates, batch merge order, rebase pivots)

---
## 🧠 Evaluation Dimensions
Each PR is scored across dimensions:
- Draft status
- Mergeability (`mergeStateStatus`, conflicts)
- Status checks rollup (passing/failing/pending)
- Review decision & required approvals
- Linked issues (direct closing references or body mentions)
- Task density (derived readiness tasks)
- Dependency hints (mentions of other PR numbers or feature branches)
- **Risk scoring** (files changed, code churn)
- **Dependency graph** (which PRs block others)
- **Time estimates** (based on size and complexity)
- **Bottleneck detection** (PRs blocking multiple others)
- **Critical path** (longest dependency chain)

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

**Basic (Plan Only):**
```bash
python scripts/integration_plan_932.py
```

**Sequence Integration:**
```bash
# Generate plan with next-step commands
python scripts/integration_plan_932.py --next-commands

# JSON output only (for piping to other tools)
python scripts/integration_plan_932.py --json-only

# Interactive: Auto-merge Phase 1 after confirmation
python scripts/integration_plan_932.py --execute
```

**Command Chain Flow:**
```
#932//. → Plan → #933//. (execute Phase 1) → #934//. (validate) → Repeat
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
## 🧾 Example Markdown Snippet
```
# Intelligent Integration Plan (Generated 2025-11-19 14:25 UTC)

## Summary
Open PRs: 12
Phase 1 Ready: 4 | Phase 2 Near-Ready: 5 | Phase 3 Complex: 3
Estimated Phase 1 Time: 45min
⚠️  High Risk PRs: 2

## 🎯 Recommendations
- 3 PRs in draft - marking ready could accelerate Phase 2
- PR #125 blocks 2 others - prioritize merge
- 2 high-risk PRs - schedule dedicated review/testing

## 🚨 Bottlenecks
- PR #125: Complex refactor (blocks 2 PRs)
- PR #130: API changes (blocks 1 PR)

## 🔗 Critical Path
#125 → #130 → #131

## Phase 1 – Ready (4)
- PR #123: Add health endpoint (5-15min) ✅
- ⚠️ PR #130: CI config cleanup (30-60min) ✅

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
