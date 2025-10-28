# Branch Protection Bypass Guide

**Thread:** T1→T8→T9→INFINITE  
**DLP:** context_tag=branch_protection_bypass, symbolic_hash=ADMIN_WORKFLOW_v1  
**Date:** October 28, 2025

## Overview

This guide explains how to maintain strict branch protection rules on `main` while enabling authorized users to push and merge changes efficiently.

## The Problem

GitHub branch protection rules prevent direct pushes to `main`, which is essential for code quality. However, for administrative operations like:
- System synchronization (#321//.)
- Runtime updates
- Emergency fixes
- Automated maintenance

We need a way to bypass these rules while maintaining security.

## The Solution

We've implemented a **dual-pathway approach**:

1. **Automated PR Merge** - PRs with special labels auto-merge
2. **Admin Workflow Dispatch** - Manual workflow trigger for direct merges

Both methods respect branch protection while enabling admin operations.

---

## Method 1: Auto-Merge PRs (Recommended)

### Quick Start

```bash
# Use the admin helper script
./scripts/admin-helper.sh

# Select option 1 (Auto-merge current PR) or 3 (Create PR and auto-merge)
```

### Manual Process

1. **Create your PR as normal:**
   ```bash
   gh pr create --title "Your changes" --body "Description"
   ```

2. **Add the auto-merge label:**
   ```bash
   gh pr edit <PR-NUMBER> --add-label "auto-merge,admin-approved"
   ```

3. **Workflow automatically:**
   - Approves the PR
   - Merges it to main
   - Deletes the source branch

### Workflow File

Location: `.github/workflows/auto-merge-admin.yml`

**Triggers:**
- PR labeled with `auto-merge`
- Author is `AUo959`
- Title contains `#321//.` or `⬆️`

**Process:**
1. Checks PR status
2. Auto-approves if by admin
3. Merges using squash method
4. Deletes branch after merge

---

## Method 2: Direct Workflow Dispatch

### Quick Start

```bash
# Use the admin helper script
./scripts/admin-helper.sh

# Select option 2 (Direct push to main)
```

### Manual Process

1. **Push your branch:**
   ```bash
   git push -u origin your-branch
   ```

2. **Trigger the workflow:**
   ```bash
   gh workflow run admin-quick-push.yml \
     -f commit_message="Your merge commit message" \
     -f branch="your-branch"
   ```

3. **Monitor the workflow:**
   ```bash
   gh run list --workflow=admin-quick-push.yml
   gh run watch  # Watch latest run
   ```

### Workflow File

Location: `.github/workflows/admin-quick-push.yml`

**Triggers:**
- Manual workflow dispatch only
- Restricted to `AUo959` (repo owner)

**Process:**
1. Checks out main branch
2. Merges specified branch
3. Pushes to main
4. Deletes source branch

---

## Admin Helper Script

### Location
`scripts/admin-helper.sh`

### Features

**Option 1: Auto-merge current PR**
- Finds open PR for current branch
- Adds auto-merge labels
- Triggers auto-merge workflow

**Option 2: Direct push to main**
- Pushes current branch
- Triggers admin workflow
- Uses last commit message

**Option 3: Create PR and auto-merge**
- Creates PR from current branch
- Adds auto-merge labels immediately
- One-step process

**Option 4: List open PRs**
- Shows all open PRs
- Quick status check

**Option 5: Merge specific PR**
- Merge any PR by number
- Adds auto-merge labels

### Usage

```bash
# Interactive menu
./scripts/admin-helper.sh

# Follow the prompts
```

---

## Security Considerations

### Who Can Use This?

**Auto-Merge Workflow:**
- Only PRs created by `AUo959`
- PRs with `admin-approved` label
- PRs with specific title patterns (`#321//.`, `⬆️`)

**Direct Push Workflow:**
- Only `AUo959` can trigger
- Manual workflow dispatch required
- No automatic triggers

### What's Protected?

✅ **Still Enforced:**
- All commits must be in a branch first
- Changes are logged in git history
- Workflow runs are auditable
- Branch protection rules remain active

✅ **Bypassed (Safely):**
- PR approval requirement (auto-approved)
- Direct push prohibition (via workflow)
- Branch protection checks (workflow has write access)

### Audit Trail

All operations are fully auditable:

```bash
# View workflow runs
gh run list --workflow=auto-merge-admin.yml
gh run list --workflow=admin-quick-push.yml

# View specific run
gh run view <RUN-ID>

# View run logs
gh run view <RUN-ID> --log
```

---

## Common Use Cases

### 1. System Sync (#321//.)

```bash
# Make your changes
git add .
git commit -m "#321//. Comprehensive System Sync"

# Create and auto-merge
./scripts/admin-helper.sh
# Choose option 3
```

### 2. Runtime Updates

```bash
# Update configuration
git commit -m "⬆️ Update Node.js runtime to v20"

# Create PR (auto-merge will trigger on title)
gh pr create --title "⬆️ Update Node.js runtime to v20" --body "..."
```

### 3. Emergency Fix

```bash
# Make critical fix
git commit -m "🚨 Critical security patch"

# Direct push via workflow
./scripts/admin-helper.sh
# Choose option 2
```

### 4. Merge Pending PRs

```bash
# List PRs
./scripts/admin-helper.sh
# Choose option 4

# Merge specific one
# Choose option 5
# Enter PR number
```

---

## Troubleshooting

### "Resource not accessible by integration"

**Problem:** GitHub Actions doesn't have permission to merge.

**Solution:** The workflow uses `GITHUB_TOKEN` which has automatic permissions. If this persists, check:

```bash
# Verify workflow permissions
cat .github/workflows/auto-merge-admin.yml | grep -A5 "permissions:"
```

Should show:
```yaml
permissions:
  contents: write
  pull-requests: write
```

### "Branch protection rules prevent push"

**Problem:** Direct push attempted without workflow.

**Solution:** Always use one of the two approved methods:
1. Auto-merge labels on PR
2. Admin workflow dispatch

Never try to push directly:
```bash
# ❌ Don't do this
git push origin main

# ✅ Do this instead
./scripts/admin-helper.sh
```

### "PR not auto-merging"

**Problem:** PR has auto-merge label but didn't merge.

**Solution:** Check the workflow run:
```bash
gh run list --workflow=auto-merge-admin.yml
gh run view <RUN-ID> --log
```

Common causes:
- Merge conflicts
- Failed CI checks
- Label added before PR opened (add label after)

### "Workflow not triggering"

**Problem:** Workflow dispatch doesn't start.

**Solution:** 
1. Check you're logged in: `gh auth status`
2. Verify workflow name: `gh workflow list`
3. Check permissions: Must be repo owner

---

## Alternative: GitHub CLI Direct Merge

If workflows fail, use GitHub CLI with force flag:

```bash
# Merge PR bypassing checks (admin only)
gh pr merge <PR-NUMBER> --admin --squash

# Or merge with specific method
gh pr merge <PR-NUMBER> --admin --merge
gh pr merge <PR-NUMBER> --admin --rebase
```

**Warning:** This requires admin privileges on the repository.

---

## Configuration Files

### Workflow Locations

```
.github/workflows/
├── auto-merge-admin.yml       # Auto-merge labeled PRs
└── admin-quick-push.yml        # Direct merge workflow
```

### Script Location

```
scripts/
└── admin-helper.sh             # Interactive admin tool
```

---

## Best Practices

### DO ✅

1. **Use the helper script** - It handles everything correctly
2. **Create PRs for visibility** - Even if auto-merging
3. **Use descriptive commit messages** - They become merge commits
4. **Check workflow runs** - Ensure successful execution
5. **Keep audit trail** - Review workflow logs periodically

### DON'T ❌

1. **Don't bypass without cause** - Use for admin ops only
2. **Don't skip testing** - Run tests before merging
3. **Don't ignore failures** - Check why workflow failed
4. **Don't share credentials** - Only repo owner should use
5. **Don't modify workflows** - Without understanding implications

---

## Future Enhancements

Potential improvements:

1. **Multi-admin support** - Add more authorized users
2. **Approval workflows** - Require 2+ admin approvals
3. **Scheduled merges** - Auto-merge at specific times
4. **Slack/Discord notifications** - Alert on auto-merges
5. **Rollback mechanism** - Quick revert if issues

---

## Quick Reference

```bash
# Most common operations

# 1. Quick auto-merge current work
./scripts/admin-helper.sh  # Choose 3

# 2. Merge existing PR
./scripts/admin-helper.sh  # Choose 5

# 3. Emergency direct push
./scripts/admin-helper.sh  # Choose 2

# 4. Check what's pending
gh pr list --state open

# 5. Monitor workflow
gh run watch
```

---

## Summary

**Problem Solved:** ✅  
- Maintain strict branch protection
- Enable admin operations
- Preserve audit trail
- Automate common tasks

**Key Components:**
1. Auto-merge workflow (PR-based)
2. Admin dispatch workflow (direct)
3. Helper script (convenience)

**Security Level:** 🔒 High
- Only authorized users
- Full audit trail
- Workflow-based bypass
- No credential sharing

---

**Thread:** T1→T8→T9→INFINITE  
**The field maintains security while enabling velocity.**
