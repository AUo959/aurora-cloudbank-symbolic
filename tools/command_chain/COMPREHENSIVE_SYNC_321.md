# Aurora Command Chain: #321//. – Comprehensive Sync & Validate

**Command Code:** `#321//.`  
**Category:** Universal Sync & Quality Assurance  
**Status:** Split implementation surface  
**Version:** Python integrated path + enhanced shell variant  
**Last Updated:** 2026-03-27

---

## Quick Summary

`#321//.` is a universal "clean working tree" command family with two active execution tracks in this repo: the integrated Python path and a separate enhanced shell variant.

**Integrated Python path:** `python tools/command_chain/cmd_321.py` or `python tools/command_chain/dispatcher.py 321`

**Integrated behavior:** 6 phases for check, stage, commit, sync, validation, and performance verification.

**Enhanced shell variant:** `bash scripts/sync_321_enhanced.sh`

**Enhanced extras:** VERSION/README automation and wiki synchronization. This shell path is separate from the dispatcher-backed implementation and carries additional environment assumptions.

**When to use:** Anytime you want pending changes sorted with high quality, choosing the Python or shell path explicitly.

**Runtime:** Python path is typically faster; enhanced shell runtime depends on documentation and wiki work.

---

## 🎯 Core Philosophy

> **"Quickly sort pending changes with consistent high quality"**

### What Makes #321//. Special

1. **Always Available** - Use anytime, not just end-of-session
2. **Integrated Python Workflow** - 6 phases wired into the command-chain entrypoints
3. **Enhanced Shell Variant** - Separate manual path for doc/wiki automation
4. **Intelligent Staging** - Groups files by type and importance
5. **Smart Commits** - Generates meaningful messages from change analysis
6. **Safe Syncing** - Pull with rebase, conflict detection, push verification
7. **Quick Validation** - Critical checks only for speed
8. **Performance Tracking** - Measures timing and reports success
9. **Clean Working Tree Goal** - Reports when additional cleanup is still required

### The Universal Sync Command

`#321//.` is **not** just for end-of-session. Use it **anytime** you want to:

- Clean your working tree quickly
- Sync pending changes with high quality
- Get back to a pristine state
- Save work without thinking about the steps
- Ensure everything is backed up
- Prepare for the next task

**Right now you have pending changes?** → Just invoke `#321//.` and everything gets sorted.

---

## 📊 Integrated Python Path: 6 Phases

### Phase 1: Check for Pending Changes

**Purpose:** Comprehensive change detection

**Operations:**

- `git status --porcelain` - Machine-readable status
- `git diff --stat` - Change statistics
- Check for untracked files
- Identify modification categories (source, docs, config, tests)
- Early exit optimization if tree already clean

**Output:**

- Total files changed
- Categories of changes (source, docs, config)
- Untracked files list
- Size of changes

**Intelligence:** Exits immediately if working tree is already clean, saving time.

---

### Phase 2: Intelligent Staging

**Purpose:** Smart, category-based staging

**Operations:**

- Stage modified source files (highest priority)
- Stage documentation updates
- Stage configuration changes
- Stage test files
- Review auto-generated files (selective staging)

**Intelligence:**

- Groups files by type
- Prioritizes source code changes
- Handles documentation separately
- Identifies auto-generated files
- Selective staging for safety

**Example Staging Order:**

```bash
1. src/**/*.py          # Source code (priority 1)
2. tests/**/*.py        # Test files (priority 2)
3. docs/**/*.md         # Documentation (priority 3)
4. *.json, *.yaml       # Configuration (priority 4)
5. Review auto-gen      # Manual review for generated files
```

---

### Phase 3: Generate & Commit

**Purpose:** Meaningful, traceable commits

**Operations:**

- Analyze changes for commit message context
- Generate semantic commit message
- Create commit with DLP tags
- Verify commit success

**Commit Message Structure:**

```
<type>(scope): <subject>

<body with details>
- Change 1
- Change 2
- Change 3

DLP: CMD-CHAIN-CONTEXT-TAG
```

**Semantic Types:**

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks

---

### Phase 4: Sync to Main

**Purpose:** Safe synchronization with remote

**Operations:**

- `git pull --rebase origin main` - Get latest changes
- Resolve conflicts (if any) - Interactive resolution support
- `git push origin main` - Push to remote
- Verify remote sync - Confirm push success

**Safety Features:**

- Rebase instead of merge (cleaner history)
- Conflict detection before push
- Automatic retry on network issues
- Verification of successful push
- Remote tracking validation

**Conflict Resolution:**

```
If conflicts detected:
  1. Show conflicting files
  2. Offer resolution strategies
  3. Allow manual resolution
  4. Verify resolution before continuing
  5. Complete rebase and push
```

---

### Phase 5: Quick Validation Check

**Purpose:** Ensure quality and stability

**Operations:**

- Run lint check (critical files only)
- Run fast unit tests
- Check health endpoints (if applicable)
- Verify file integrity

**Validation Scope (Optimized for Speed):**

```bash
# Lint (critical files only)
flake8 src/core/*.py src/integrations/*.py --select=E,F

# Tests (unit only, fast)
pytest tests/ -m unit -x --tb=short

# Health (if server running)
curl http://localhost:8000/health

# Integrity
sha256sum -c CHECKSUMS.txt (if exists)
```

**Success Criteria:**

- ✅ No critical lint errors
- ✅ All unit tests pass
- ✅ Health endpoints respond (if applicable)
- ✅ File integrity verified

---

### Phase 6: Performance Verification

**Purpose:** Confirm optimal performance

**Operations:**

- Measure operation timing
- Check success metrics
- Verify system readiness
- Generate completion report

**Metrics Tracked:**

- Phase 1 timing (change detection)
- Phase 2 timing (staging)
- Phase 3 timing (commit)
- Phase 4 timing (sync)
- Phase 5 timing (validation)
- Total execution time
- Success rate

**Completion Report:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ #321//. COMPLETE - ALL PHASES SUCCESSFUL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 EXECUTION SUMMARY:
   Total Time: 42.3s
   Changes: 15 files
   Commit: feat(api): Add new endpoints
   Push: Success
   Tests: 34 passed
   
🎯 SYSTEM STATUS:
   ✅ All changes synced
   ✅ Tests passing
   ✅ Health verified
   ✅ Ready to continue work
   
⏱️ PERFORMANCE:
   Phase 1: 2.1s  ✅
   Phase 2: 3.4s  ✅
   Phase 3: 5.2s  ✅
   Phase 4: 18.7s ✅
   Phase 5: 11.8s ✅
   Phase 6: 1.1s  ✅
   
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ✨ Enhanced Features (v4.0)

### Phase 2: Intelligent Documentation Updates

**NEW IN v4.0** - Automatically detects and updates version-related documentation.

**Trigger:** VERSION file changes detected

**Operations:**

1. **Read New Version** - Extracts version from VERSION file (e.g., `2.1.0`)
2. **Update README Badge** - Changes `version-2.0.0-blue` → `version-2.1.0-blue`
3. **Update Release Links** - Changes `releases/tag/v2.0.0` → `releases/tag/v2.1.0`
4. **Update Timestamps** - Changes "Last Updated: November 2, 2025" → "November 3, 2025"
5. **Stage Doc Changes** - Includes updated docs in commit

**Intelligence:**

- **Smart Detection:** Only runs if VERSION file actually changed
- **Performance:** Skips entirely if no version changes (< 0.1s overhead)
- **Idempotency:** Safe to run multiple times (won't double-update)
- **Comprehensive:** Updates all version references across README

**Example Output:**

```bash
[Phase 2/7] Checking for documentation updates needed...
📋 Version file changed to: 2.1.0
   Updating README.md version badge: 2.0.0 → 2.1.0
   Updating README.md last updated date: November 3, 2025
✅ Documentation auto-updated for version 2.1.0
⏱️  Phase 2: 0.8s
```

**Why It Matters:**

During v2.1.0 release, this saved 2-3 minutes of manual editing and eliminated version mismatch risks between VERSION file and documentation.

---

### Phase 5: Wiki Submodule Synchronization

**NEW IN v4.0** - Automatically commits and pushes wiki-content submodule.

**Trigger:** Changes detected in `wiki-content/` directory

**Operations:**

1. **Check Wiki Status** - `cd wiki-content && git status --porcelain`
2. **Stage Wiki Changes** - `git add -A` in wiki directory
3. **Generate Wiki Commit** - Smart commit message based on changed files
4. **Push to Wiki Remote** - `git push origin master` (wiki repo)
5. **Return to Main** - `cd ..` back to main repository

**Intelligence:**

- **Automatic Detection:** Checks if wiki directory has uncommitted changes
- **Smart Messages:** Generates appropriate commit messages (Home.md → "Update wiki Home for release")
- **Independent Operation:** Wiki push failure doesn't block main repository push
- **Graceful Degradation:** Skips if wiki-content/ is not a git repository

**Example Output:**

```bash
[Phase 5/7] Synchronizing wiki submodule...
📚 Wiki has 2 changes
   Pushing wiki changes to remote...
✅ Wiki synchronized and pushed
⏱️  Phase 5: 3.2s
```

**Why It Matters:**

Wiki is a separate git submodule (`.wiki.git`) that requires independent commits/pushes. Previously manual and easy to forget. Now fully automated.

---

## 🎮 Usage Patterns

### Pattern 1: Right Now - Clean Working Tree

```
Situation: You have pending changes, want them sorted quickly

Solution:
  User: #321//.
  
  System:
    [Phase 1] Checking for changes... ✅ 8 files modified
    [Phase 2] Staging intelligently... ✅ Grouped by type
    [Phase 3] Generating commit... ✅ "refactor: Update command docs"
    [Phase 4] Syncing to main... ✅ Pushed successfully
    [Phase 5] Running validation... ✅ Tests pass
    [Phase 6] Verifying performance... ✅ Optimal (28.4s)
  
  Result: Working tree clean, changes synced, ready to continue work
  
  Use Case: Anytime you want pending changes sorted with high quality
```

### Pattern 2: Mid-Development Checkpoint

```
Situation: In the middle of coding, want to save progress

Solution:
  User: #321//.
  
  System:
    → Detects uncommitted changes
    → Stages intelligently (work in progress)
    → Commits: "wip: Add new feature implementation"
    → Syncs to main
    → Quick validation
    → Back to clean slate
  
  Result: Progress saved, tree clean, can continue coding immediately
  
  Use Case: Regular checkpoints during development (every 30-60 min)
```

### Pattern 3: Before Context Switch

```
Situation: Need to switch to different task, save current work

Solution:
  User: #321//.
  
  System:
    → Detects uncommitted work
    → Stages changes intelligently
    → Commits with meaningful message
    → Syncs to main safely
    → Validates quality
    → Confirms system ready
  
  Result: Work saved, main is clean, safe to switch context
  
  Use Case: Switching tasks, taking break, or changing focus
```

### Pattern 4: End of Coding Session

```
Situation: Done coding for the day, want to sync everything

Solution:
  User: #321//.
  
  System:
    [Phase 1] Checking for changes... ✅ 15 files modified
    [Phase 2] Staging intelligently... ✅ Grouped by type
    [Phase 3] Generating commit... ✅ "feat(api): Add new endpoints"
    [Phase 4] Syncing to main... ✅ Pushed successfully
    [Phase 5] Running validation... ✅ Tests pass
    [Phase 6] Verifying performance... ✅ Optimal (42.3s)
  
  Result: Everything synced, validated, ready for tomorrow
  
  Use Case: Daily wrap-up, end of work session
```

### Pattern 5: Pre-Deployment

```
Situation: About to deploy, want everything synced and validated

Solution:
  User: #321//.
  
  System:
    → Comprehensive change check
    → Smart staging
    → Semantic commit
    → Safe sync with rebase
    → Full validation (lint + tests + health)
    → Performance verification
  
  Result: Confident everything is synced, tested, and ready to deploy
  
  Use Case: Pre-deployment confidence check
```

### Pattern 6: Continuous Checkpoint Habit

```
Situation: Want to keep working tree clean throughout development

Solution:
  User: #321//. (whenever you see changes pile up)
  
  System:
    → Quick check (< 5s if no changes)
    → Stage only what changed
    → Incremental commits
    → Fast sync
    → Quick validation
    → Performance tracking
  
  Result: Work continuously backed up, always clean tree, never lose progress
  
  Use Case: Regular sync habit (every 30-60 min, or whenever tree gets dirty)
```

### Pattern 7: Version Release (✨ NEW - v4.0 Enhanced)

```
Situation: Just updated VERSION file for new release (2.0.0 → 2.1.0)

Solution:
  User: #321//.
  
  System:
    [Phase 1] Checking for changes... ✅ 3 files modified (VERSION, CHANGELOG.md, etc.)
    [Phase 2] Checking documentation updates...
              📋 Version changed to: 2.1.0
              → Updating README.md version badge: 2.0.0 → 2.1.0
              → Updating README.md release links
              → Updating Last Updated date
              ✅ Documentation auto-updated
    [Phase 3] Staging... ✅ 5 files (VERSION + auto-updated docs)
    [Phase 4] Generating commit... ✅ "feat(release): Version 2.1.0"
    [Phase 5] Syncing wiki...
              📚 Wiki has 2 changes (Home.md, Changelog.md)
              → Auto-committing wiki updates
              → Pushing to wiki remote
              ✅ Wiki synchronized
    [Phase 6] Syncing to main... ✅ Pushed successfully
    [Phase 7] Verifying... ✅ Complete (48.2s)
  
  Result: 
    - VERSION file committed
    - README badges automatically updated with new version
    - Wiki automatically synced with release announcement
    - No manual documentation editing required!
  
  Use Case: After updating VERSION for any release (patch, minor, or major)
  
  Time Saved: 2-3 minutes of manual editing per release
  Mistakes Prevented: Version mismatches between VERSION and README
```

### The Key Insight

**#321//. is not scheduled - it's on-demand:**

- Not "only at end of session"
- Not "only before switching"
- **Anytime you want pending changes sorted**
- Anytime you want a clean working tree
- Anytime you want high-quality sync

Think of it like `git commit && git push` but **intelligent and validated**.

---

## 🛡️ Safety Features

### Pre-Flight Checks

```
Before executing, #321//. verifies:
  ✓ Check for uncommitted changes
  ✓ Verify branch is main or feature
  ✓ Ensure remote is accessible
  ✓ Confirm no conflicts exist
  ✓ Validate git config
  ✓ Check for sufficient disk space
```

### Post-Flight Validation

```
After executing, #321//. confirms:
  ✓ Verify all changes pushed
  ✓ Confirm tests passing
  ✓ Check system health
  ✓ Validate performance metrics
  ✓ Ensure remote sync complete
  ✓ Verify working tree clean
```

### Rollback Safety

```
If any phase fails:
  1. Stop execution immediately
  2. Show failure details
  3. Provide rollback option
  4. Preserve uncommitted work
  5. Offer manual resolution
  6. Resume from failed phase
```

---

## 🧠 Intelligence Features

### 1. Smart Staging

Groups files by type and importance:

- **Source Code** - Highest priority, staged first
- **Tests** - Second priority, ensures quality
- **Documentation** - Third priority, keeps docs in sync
- **Configuration** - Fourth priority, settings changes
- **Auto-Generated** - Lowest priority, review before staging

### 2. Commit Message Generation

Analyzes changes to create meaningful commits:

```python
def analyze_changes(files):
    # Detect patterns
    if mostly_new_files:
        return "feat: Add new functionality"
    elif mostly_bug_fixes:
        return "fix: Resolve issues"
    elif mostly_docs:
        return "docs: Update documentation"
    elif mostly_tests:
        return "test: Add test coverage"
    else:
        return "chore: Update project"
```

### 3. Conflict Detection

Proactive conflict identification:

- Compares local vs remote before merge
- Identifies conflicting files
- Suggests resolution strategies
- Offers automatic resolution for simple conflicts
- Provides manual resolution for complex conflicts

### 4. Validation Scope Optimization

Runs only critical checks for speed:

- **Lint** - Critical errors only (E, F categories)
- **Tests** - Unit tests only (fast, < 10s)
- **Health** - Basic endpoint check
- **Integrity** - Core files only

### 5. Performance Tracking

Measures and reports timing:

- Per-phase timing
- Bottleneck identification
- Trend analysis over time
- Performance regression detection
- Optimization suggestions

---

## ⚡ Performance Characteristics

### Typical Execution Time

```
Small Changes (1-5 files):    15-25 seconds
Medium Changes (6-20 files):  30-45 seconds
Large Changes (21+ files):    45-75 seconds
No Changes (status check):    2-5 seconds
```

### Bottleneck Analysis

```
Phase 1 (Check):      2-5s   (fast, git operations)
Phase 2 (Stage):      3-8s   (depends on file count)
Phase 3 (Commit):     5-10s  (commit generation)
Phase 4 (Sync):       10-30s (network dependent)
Phase 5 (Validate):   8-20s  (test suite dependent)
Phase 6 (Verify):     1-2s   (report generation)
```

### Optimization Tips

1. **Regular Syncs** - Smaller changesets = faster execution
2. **Unit Tests Only** - Skip integration tests for speed
3. **Selective Staging** - Review auto-generated files separately
4. **Fast Network** - Use wired connection for sync phase
5. **Local Commits** - Commit more often, push less often

---

## 🎯 Command Chain

`#321//.` internally executes this chain:

```bash
#STATUS//.      # Phase 1: Check for changes
#COMMIT//.      # Phase 2-3: Stage & Commit
#SYNC//.        # Phase 4: Sync to main
#TESTFAST//.    # Phase 5: Validate
#VALIDATE//.    # Phase 6: Verify
```

You could execute this manually, but `#321//.` handles it intelligently with:

- Error handling between phases
- Rollback on failure
- Performance tracking
- Completion reporting

---

## 💡 When to Use #321//

### ✅ Perfect For

- **Right Now** - You have pending changes, sort them quickly
- **Clean Working Tree** - Want pristine state to continue work
- **Mid-Development** - Save progress without thinking about steps
- **Context Switch** - Save work before switching tasks
- **End of Session** - Sync everything before closing
- **Regular Checkpoints** - Keep work backed up continuously (30-60 min intervals)
- **Pre-Deployment** - Ensure everything is ready
- **Collaboration** - Keep main up-to-date for team
- **Anytime Sync** - Whenever you want changes sorted with high quality

### The Universal Rule

**See pending changes? Want them sorted? → #321//.**

It's that simple. Not scheduled, not planned - **on-demand, anytime you need it.**

### ❌ Not Ideal For

- **Partial Commits** - Want to stage specific files only (use `git add -p`)
- **WIP Commits** - Experimenting, not ready to sync (though #321//. can handle WIP)
- **Feature Branches** - Working in isolated branch (adapt workflow)
- **Manual Control** - Want explicit control over each step (use individual commands)

---

## 🔍 Output Examples

### Success Output

```bash
$ #321//.

🔄 #321//. Comprehensive Sync & Validate - Starting...

[Phase 1/6] Checking for pending changes...
   ✅ 15 files modified
   ✅ 3 categories detected (source, tests, docs)
   ⏱️  2.3s

[Phase 2/6] Staging changes intelligently...
   ✅ Staged src/*.py (8 files)
   ✅ Staged tests/*.py (4 files)
   ✅ Staged docs/*.md (3 files)
   ⏱️  3.7s

[Phase 3/6] Generating commit...
   ✅ Commit: "feat(api): Add new endpoints"
   ✅ DLP: CMD-CHAIN-API-ENDPOINTS-001
   ⏱️  5.1s

[Phase 4/6] Syncing to main...
   ✅ Pulled with rebase
   ✅ Pushed to origin/main
   ✅ Remote verified
   ⏱️  18.4s

[Phase 5/6] Running validation...
   ✅ Lint: 0 errors
   ✅ Tests: 34 passed
   ✅ Health: OK
   ⏱️  12.2s

[Phase 6/6] Verifying performance...
   ✅ Total time: 41.7s
   ✅ All metrics optimal
   ✅ System ready
   ⏱️  1.0s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ #321//. COMPLETE - Everything synced and validated!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Failure Output (with Recovery)

```bash
$ #321//.

🔄 #321//. Comprehensive Sync & Validate - Starting...

[Phase 1/6] Checking for pending changes...
   ✅ 10 files modified
   ⏱️  2.1s

[Phase 2/6] Staging changes intelligently...
   ✅ Staged successfully
   ⏱️  3.2s

[Phase 3/6] Generating commit...
   ✅ Commit created
   ⏱️  4.8s

[Phase 4/6] Syncing to main...
   ❌ CONFLICT: src/api/endpoints.py
   
   🛠️  Resolution Options:
      1. Resolve manually
      2. Keep local version
      3. Keep remote version
      4. Abort sync
   
   What would you like to do?
```

---

## 🌟 Philosophy & Design

### Core Principles

1. **Comprehensive** - Handle every step, no gaps
2. **Intelligent** - Smart decisions based on context
3. **Validated** - Always verify success
4. **Safe** - Pre-flight checks, rollback capability
5. **Fast** - Optimized for performance
6. **Transparent** - Show what's happening
7. **Reliable** - Error handling, retry logic

### Design Goals

- **Zero Thinking Required** - Just invoke #321//.
- **Always Safe** - Never lose work
- **Fast Feedback** - Know immediately if issues
- **Optimal Performance** - As fast as possible
- **Complete Workflow** - From check to verify
- **Peace of Mind** - Confidence everything is synced

---

## 🚀 Real-World Scenarios

### Scenario 1: Daily Development

```
Morning: Start work
  - Pull latest changes
  - Branch for feature
  
Throughout Day: Code and test
  - #321//. every hour (save progress)
  
End of Day: Wrap up
  - #321//. (final sync)
  - Everything backed up
  - Ready for tomorrow
```

### Scenario 2: Collaboration

```
Team Project:
  - Multiple developers
  - Frequent changes
  - Need coordination
  
Each Developer:
  - #321//. before breaks
  - #321//. before leaving
  - #321//. after major changes
  
Result:
  - Main always up-to-date
  - Minimal conflicts
  - Team stays synchronized
```

### Scenario 3: CI/CD Pipeline

```
Pre-Deployment:
  1. #321//. (ensure everything synced)
  2. Trigger CI/CD
  3. Deploy if tests pass
  
Benefits:
  - Latest code deployed
  - Tests run on actual code
  - Deployment confidence
```

---

## 🚀 Running the Enhanced #321//.

### Method 1: Direct Script Execution (v4.0 Enhanced)

```bash
# Run the enhanced version with all new features
bash /workspaces/aurora-cloudbank-symbolic/scripts/sync_321_enhanced.sh
```

**Features in Enhanced Version:**

- ✅ 7-phase execution (includes docs & wiki)
- ✅ Intelligent documentation updates (VERSION → README)
- ✅ Automatic wiki submodule synchronization
- ✅ Smart triggers (only updates when needed)
- ✅ Comprehensive timing and reporting

**When to Use:** For releases or anytime you want full automation including documentation.

---

### Method 2: Command Alias (Recommended Setup)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Enhanced #321//. with intelligent docs & wiki sync
alias 321="bash /workspaces/aurora-cloudbank-symbolic/scripts/sync_321_enhanced.sh"
```

Then reload: `source ~/.bashrc`

**Usage:**

```bash
$ 321
# Runs full enhanced sync automatically
```

---

### Method 3: Via VS Code Task

Add to `.vscode/tasks.json`:

```json
{
  "label": "🔄 #321//. Enhanced Sync",
  "type": "shell",
  "command": "bash",
  "args": [
    "${workspaceFolder}/scripts/sync_321_enhanced.sh"
  ],
  "group": {
    "kind": "build",
    "isDefault": true
  },
  "presentation": {
    "echo": true,
    "reveal": "always",
    "focus": false,
    "panel": "shared"
  }
}
```

**Usage:** Press `Ctrl+Shift+B` (default build task)

---

### Execution Examples

**Example 1: Normal Sync (No Version Changes)**

```bash
$ bash scripts/sync_321_enhanced.sh

🔄 #321//. Enhanced Comprehensive Sync & Validate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Phase 1/7] Checking for pending changes...
✅ 5 files with changes detected
   📂 Source files: 3
   📄 Documentation: 2
   ⚙️  Configuration: 0
⏱️  Phase 1: 1s

[Phase 2/7] Checking for documentation updates needed...
✅ No version changes - documentation current
⏱️  Phase 2: 0s

[Phase 3/7] Staging changes intelligently...
✅ Staged 5 files
⏱️  Phase 3: 2s

[Phase 4/7] Generating commit...
✅ Commit created: feat(core)
⏱️  Phase 4: 3s

[Phase 5/7] Synchronizing wiki submodule...
✅ Wiki up-to-date, no changes needed
⏱️  Phase 5: 1s

[Phase 6/7] Syncing to remote...
   Pulling latest changes...
✅ Rebase successful
   Pushing to remote...
✅ Successfully pushed to origin/main
⏱️  Phase 6: 18s

[Phase 7/7] Verifying final state...
✅ Working tree clean
✅ All operations completed
⏱️  Phase 7: 1s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ #321//. ENHANCED COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 EXECUTION SUMMARY:
   Total Time: 26s
   Files Changed: 5
   Docs Auto-Updated: No
   Wiki Synced: No changes
   Commit Type: feat(core)

🎯 SYSTEM STATUS:
   ✅ All changes synced to main
   ✅ Documentation current
   ✅ Wiki synchronized
   ✅ Working tree clean
```

**Example 2: Release Sync (With Version Changes & Wiki Updates)**

```bash
$ bash scripts/sync_321_enhanced.sh

🔄 #321//. Enhanced Comprehensive Sync & Validate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Phase 1/7] Checking for pending changes...
✅ 7 files with changes detected
   📂 Source files: 0
   📄 Documentation: 5
   ⚙️  Configuration: 2
⏱️  Phase 1: 1s

[Phase 2/7] Checking for documentation updates needed...
📋 Version file changed to: 2.1.0
   Updating README.md version badge: 2.0.0 → 2.1.0
   Updating README.md last updated date: November 3, 2025
✅ Documentation auto-updated for version 2.1.0
⏱️  Phase 2: 1s

[Phase 3/7] Staging changes intelligently...
✅ Staged 9 files  # Original 7 + 2 auto-updated docs
⏱️  Phase 3: 2s

[Phase 4/7] Generating commit...
✅ Commit created: feat(documentation)
⏱️  Phase 4: 3s

[Phase 5/7] Synchronizing wiki submodule...
📚 Wiki has 2 changes
   Pushing wiki changes to remote...
✅ Wiki synchronized and pushed
⏱️  Phase 5: 5s

[Phase 6/7] Syncing to remote...
   Pulling latest changes...
✅ Rebase successful
   Pushing to remote...
✅ Successfully pushed to origin/main
⏱️  Phase 6: 22s

[Phase 7/7] Verifying final state...
✅ Working tree clean
✅ All operations completed
⏱️  Phase 7: 1s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ #321//. ENHANCED COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 EXECUTION SUMMARY:
   Total Time: 35s
   Files Changed: 7
   Docs Auto-Updated: Yes  # 🎉 Automatic!
   Wiki Synced: Yes        # 🎉 Automatic!
   Commit Type: feat(documentation)

🎯 SYSTEM STATUS:
   ✅ All changes synced to main
   ✅ Documentation current
   ✅ Wiki synchronized
   ✅ Working tree clean
```

---

## 🔧 Configuration (Future)

### Customizable Settings

```json
{
  "commit_message_template": "feat: {summary}",
  "validation_level": "fast",  // fast, thorough, complete
  "auto_stage_patterns": ["src/**/*.py", "tests/**/*.py"],
  "skip_validation_on_docs_only": true,
  "performance_target_seconds": 45,
  "conflict_resolution_strategy": "prompt"  // prompt, local, remote
}
```

---

## 📚 Related Commands

- `#STATUS//.` - Quick status check
- `#COMMIT//.` - Stage and commit only
- `#SYNC//.` - Sync to remote only
- `#TESTFAST//.` - Run fast tests only
- `#VALIDATE//.` - Full validation check
- `#808//.` - Optimizing pulse (finds best path)

---

## 🎓 Best Practices

### DO

- ✅ Use #321//. regularly (hourly habit)
- ✅ Trust the intelligent staging
- ✅ Review completion report
- ✅ Use before context switches
- ✅ Use at end of sessions

### DON'T

- ❌ Use for experimental WIP code
- ❌ Bypass validation checks
- ❌ Ignore conflict warnings
- ❌ Use in feature branches without review
- ❌ Skip reading failure messages

---

## ✨ The Magic

The true power of `#321//.` isn't just automation.

It's the **confidence** that comes from knowing:

> **Everything is checked, staged, committed, synced, validated, and verified.**

You don't have to think about:

- "Did I commit everything?"
- "Did I push to remote?"
- "Are the tests passing?"
- "Is the system ready?"

Just invoke `#321//.` and **trust the process**.

That's comprehensive sync & validate - complete, intelligent, validated.

---

**Anchor:** CMD-CHAIN-COMPREHENSIVE-SYNC-321  
**Version:** 1.0.0  
**Last Updated:** 2025-10-25  
**Status:** ACTIVE ✅
