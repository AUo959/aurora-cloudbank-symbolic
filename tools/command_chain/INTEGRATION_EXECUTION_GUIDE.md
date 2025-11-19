# Integration Execution Guide for #932//.

**Command:** `python scripts/integration_plan_932.py`  
**Version:** 2.0.0  
**Purpose:** Step-by-step guide for executing phased integration plans

---

## Quick Start

### 1. Generate Current Plan
```bash
python scripts/integration_plan_932.py --phases
```

This shows the current integration sequence with checkpoint gates.

### 2. View Full Details
```bash
python scripts/integration_plan_932.py > integration_plan.md
```

This generates a comprehensive plan with:
- Specific commands for each PR
- Risk assessments
- Time estimates
- Checkpoint requirements

### 3. Execute Phase-by-Phase

#### Phase 1: Immediate Merge Batch
For PRs marked **immediate** (✅ ready, all checks passed):
```bash
# Review and merge
gh pr view <PR_NUMBER>
gh pr merge <PR_NUMBER> --squash --auto
```

#### Phase 2: Quick Win Activation
For PRs marked **quick_win** (⚡ clean drafts):
```bash
# Mark ready and merge
gh pr ready <PR_NUMBER>
# Wait ~2min for CI
gh pr checks <PR_NUMBER> --watch
gh pr merge <PR_NUMBER> --squash --auto
```

#### Phase 3: Batch Rebase & Conflict Resolution
For PRs marked **rebase_required** (🔄 conflicts):
```bash
# Rebase workflow
gh pr checkout <PR_NUMBER>
git fetch origin main
git rebase origin/main

# Resolve conflicts in editor, then:
git add .
git rebase --continue
git push --force-with-lease

# Wait for CI
gh pr checks <PR_NUMBER> --watch

# ⚠️ CHECKPOINT: Test locally before proceeding to next PR
```

#### Phase 4: CI Failure Remediation
For PRs marked **fix_required** (🔧 failing checks):
```bash
# Investigate and fix
gh pr checks <PR_NUMBER>  # View full failure details
gh pr checkout <PR_NUMBER>

# Fix issues locally, then:
git commit -am 'fix: Address CI failures'
git push

# Wait for CI re-run
gh pr checks <PR_NUMBER> --watch
```

#### Phase 5: Pending CI Checks
For PRs marked **wait** (⏳ CI running):
```bash
# Monitor progress
gh pr checks <PR_NUMBER> --watch

# Re-run plan after completion
python scripts/integration_plan_932.py --phases
```

#### Phase 6: Complex Case Triage
For PRs marked **complex** (🎯 manual coordination):
```bash
# Full inspection
gh pr view <PR_NUMBER>
gh pr diff <PR_NUMBER>

# Coordinate with PR author
# Assign owners for manual review
```

---

## Checkpoint Protocol

**After Each Phase:**
1. Verify all PRs in phase completed successfully
2. Re-run plan to confirm phase cleared:
   ```bash
   python scripts/integration_plan_932.py --phases
   ```
3. If new PRs moved to immediate/quick_win, execute those first
4. Proceed to next phase only after checkpoint verification

**Checkpoint Failure Handling:**
- If rebase fails: Document conflicts, coordinate with author
- If CI fails: Investigate root cause, may need to postpone PR
- If manual review needed: Escalate to team leads

---

## Automation Patterns

### Continuous Integration Loop
```bash
#!/bin/bash
# Auto-execute immediate merges in loop

while true; do
  python scripts/integration_plan_932.py --json-only > plan.json
  
  # Extract immediate PRs
  IMMEDIATE=$(jq -r '.integration_sequence[] | 
    select(.name | contains("Immediate")) | 
    .prs[]' plan.json)
  
  if [ -z "$IMMEDIATE" ]; then
    echo "No immediate PRs. Waiting..."
    sleep 300  # 5min
    continue
  fi
  
  # Merge immediate PRs
  for PR in $IMMEDIATE; do
    gh pr merge $PR --squash --auto
    echo "Merged PR #$PR"
  done
  
  sleep 60  # Wait 1min before re-scan
done
```

### Batch Rebase Helper
```bash
#!/bin/bash
# Rebase all conflicting PRs

python scripts/integration_plan_932.py --json-only > plan.json

jq -r '.strategies[] | 
  select(.phase == "rebase_required") | 
  .pr' plan.json | while read PR; do
  
  echo "Rebasing PR #$PR..."
  gh pr checkout $PR
  git fetch origin main
  
  if git rebase origin/main; then
    git push --force-with-lease
    echo "✅ PR #$PR rebased successfully"
  else
    echo "❌ PR #$PR has conflicts - manual intervention required"
    git rebase --abort
  fi
done
```

---

## Best Practices

1. **Always checkpoint between phases** - Don't rush ahead
2. **Test rebased PRs locally** - Conflicts can break tests
3. **Monitor CI closely** - Catch failures early
4. **Re-scan frequently** - Repo state changes as PRs merge
5. **Coordinate with authors** - Complex PRs need collaboration

---

## Troubleshooting

**Q: Plan shows 0 phases with work**  
A: All PRs are in complex/wait state. Review manually.

**Q: Rebase created new conflicts**  
A: Abort with `git rebase --abort`, coordinate with author.

**Q: CI passed locally but failing in GitHub**  
A: Check for environment differences (env vars, dependencies).

**Q: Too many PRs in rebase phase**  
A: Consider merging main into PR branches instead of rebasing.

---

**Thread:** T1→T8→T9→INFINITE  
**DLP:** context_tag=integration_execution_guide, symbolic_hash=EXEC_v1
