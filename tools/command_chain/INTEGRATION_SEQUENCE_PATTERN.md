# Integration Sequence Pattern (#932 → #933 → #934)

**Purpose:** Chain integration planning → execution → validation as a repeatable sequence.

---

## Command Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  #932//.    │──→───│   #933//.    │──→───│  #934//.    │
│   PLAN      │      │   EXECUTE    │      │   VALIDATE  │
└─────────────┘      └──────────────┘      └─────────────┘
     ↓                      ↓                     ↓
  Survey PRs          Merge Phase 1         Check status
  Generate plan       (with safeguards)     Re-scan state
  Output commands     Run next batch        Loop if needed
```

---

## Stage 1: Plan (#932//.)

**What it does:**
- Scans open PRs and issues
- Categorizes by readiness (Phase 1/2/3)
- Outputs merge order + next commands

**Usage:**
```bash
# Generate plan with actionable commands
python scripts/integration_plan_932.py --next-commands > plan.txt

# Machine-readable JSON for automation
python scripts/integration_plan_932.py --json-only > plan.json
```

**Output Example:**
```
Phase 1 – Ready (3)
- PR #123: Health endpoint ✅
- PR #124: Typo fix ✅

## Next Commands
gh pr merge 123 --auto --squash
gh pr merge 124 --auto --squash
```

---

## Stage 2: Execute (#933//.)

**What it does:**
- Takes plan JSON as input
- Merges Phase 1 PRs sequentially
- Respects CI gates and checks
- Stops on first failure

**Usage:**
```bash
# Interactive mode (with confirmation)
python scripts/integration_plan_932.py --execute

# Automated (CI-friendly)
cat plan.json | python scripts/integration_execute_933.py --batch
```

**Safety:**
- Confirmation prompt before merge
- Dry-run mode available
- Rollback on CI failure

---

## Stage 3: Validate (#934//.)

**What it does:**
- Re-scans repository state
- Compares to original plan
- Reports deltas (merged, blocked, new)
- Generates updated plan if needed

**Usage:**
```bash
# Check post-merge state
python scripts/integration_validate_934.py --original plan.json

# Continue to next phase
python scripts/integration_validate_934.py --continue-to-phase 2
```

**Output:**
```
✅ Phase 1: 3/3 merged
⚠️  Phase 2: 2 PRs now ready (moved from Phase 3)
🔄 Replan suggested: Yes
```

---

## Full Sequence (One-Liner)

```bash
# Plan → Execute Phase 1 → Validate → Loop
python scripts/integration_plan_932.py --next-commands | \
  tee plan.txt && \
  python scripts/integration_plan_932.py --execute && \
  python scripts/integration_plan_932.py --json-only > updated.json
```

---

## Future: Auto-Sequence (#935//.)

```bash
# Run full cycle until all PRs merged or blocked
python scripts/integration_auto_935.py \
  --max-iterations 5 \
  --pause-between-phases 60
```

**Stops when:**
- All PRs merged
- No Phase 1 candidates remain
- CI failure threshold exceeded
- Manual intervention required

---

## Extending the Chain

**Add custom stages:**
- `#936//.` - Rebase Phase 2 on updated main
- `#937//.` - Notify stakeholders of plan changes
- `#938//.` - Generate release notes from merged PRs

**Hook into existing commands:**
- `#321//.` (Comprehensive Sync) runs before #932
- `#808//.` (Optimizing Pulse) tunes sequence params

---

## Status Tracking

**View active sequence:**
```bash
ls -lt plan*.json | head -5  # Recent plans
cat .integration_sequence_state  # Current stage
```

**Resume interrupted sequence:**
```bash
python scripts/integration_resume.py --from-stage 2
```

---

*Sequence pattern enables hands-off integration with safety gates.*
