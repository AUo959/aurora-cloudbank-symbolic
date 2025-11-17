# Command Chain Reference

**Complete guide to all implemented command chain commands**

## 🎯 Available Commands

### #321//. - Comprehensive Sync & Validate
**Full 6-phase workflow for complete working tree cleanup**

```bash
python tools/command_chain/cmd_321.py
python tools/command_chain/dispatcher.py 321
```

**Phases:**
1. Check for pending changes
2. Intelligent staging (by priority)
3. Generate semantic commit
4. Sync to remote (with rebase)
5. Context-aware validation
6. Performance verification

**Use when:** You want a complete, reliable cleanup with validation  
**Time:** ~17 seconds (typical)

---

### #STATUS//. - Quick Status Check
**Phase 1 only - fast status overview**

```bash
python tools/command_chain/cmd_status.py
python tools/command_chain/dispatcher.py STATUS
```

**What it does:**
- Detects all pending changes
- Categorizes files (source, tests, docs, config, workflows, other)
- Identifies docs-only or config-only changes
- Shows summary of changes by category

**Use when:** You just want to see what's changed without committing  
**Time:** ~0.02 seconds

---

### #COMMIT//. - Stage and Commit Only
**Phases 1-3 - commit locally without syncing**

```bash
python tools/command_chain/cmd_commit.py
python tools/command_chain/dispatcher.py COMMIT
```

**What it does:**
1. Check for pending changes
2. Stage files intelligently (by priority)
3. Generate semantic commit message
4. Commit to local repository

**Use when:** You want to commit but not push yet (maybe reviewing changes first)  
**Time:** ~0.5 seconds

**Note:** After this, use #SYNC//. to push to remote

---

### #SYNC//. - Sync to Remote Only
**Phase 4 only - push local commits**

```bash
python tools/command_chain/cmd_sync.py
python tools/command_chain/dispatcher.py SYNC
```

**What it does:**
1. Pull from remote (with rebase if configured)
2. Detect conflicts with enhanced resolution guidance
3. Push local commits to remote

**Use when:** You have local commits ready to push  
**Time:** ~1 second

**Conflict Handling:** Provides step-by-step resolution guidance

---

## 🔧 Configuration

All commands use the same configuration file: `.aurora/sync_config.json`

### Key Settings

```json
{
  "commit_message_template": "{type}({scope}): {summary}",
  "validation_level": "fast",
  "use_rebase": true,
  "auto_push": true,
  "conflict_resolution_strategy": "prompt",
  "skip_validation_on_docs_only": true,
  "skip_tests_on_config_only": true
}
```

### Conflict Resolution Strategies

- **`"prompt"`** (default) - Provides detailed guidance for manual resolution
- **`"abort"`** - Aborts rebase/merge to preserve work, requires manual intervention

---

## 📊 Command Comparison

| Command | Phases | Time | Commits | Syncs | Validates |
|---------|--------|------|---------|-------|-----------|
| #321//. | 1-6 | ~17s | ✅ | ✅ | ✅ |
| #STATUS//. | 1 | ~0.02s | ❌ | ❌ | ❌ |
| #COMMIT//. | 1-3 | ~0.5s | ✅ | ❌ | ❌ |
| #SYNC//. | 4 | ~1s | ❌ | ✅ | ❌ |

---

## 🎯 Common Workflows

### Quick Check Before Break
```bash
python tools/command_chain/cmd_status.py
# See what's changed, decide if you need to commit
```

### Save Work in Progress
```bash
python tools/command_chain/cmd_commit.py
# Commit locally, sync later
```

### Push Previously Committed Work
```bash
python tools/command_chain/cmd_sync.py
# Just push what's already committed
```

### Complete Checkpoint with Validation
```bash
python tools/command_chain/cmd_321.py
# Full workflow - commit, sync, validate
```

### Development Cycle
```bash
# 1. Check status frequently
python tools/command_chain/cmd_status.py

# 2. Commit when ready
python tools/command_chain/cmd_commit.py

# 3. Continue coding...

# 4. Full sync and validate before break
python tools/command_chain/cmd_321.py
```

---

## 🚀 Using the Dispatcher

The dispatcher provides a unified interface:

```bash
# List available commands
python tools/command_chain/dispatcher.py --list

# Execute any command by code
python tools/command_chain/dispatcher.py 321
python tools/command_chain/dispatcher.py STATUS
python tools/command_chain/dispatcher.py COMMIT
python tools/command_chain/dispatcher.py SYNC

# Use custom configuration
python tools/command_chain/dispatcher.py 321 --config my_config.json

# Specify workspace
python tools/command_chain/dispatcher.py STATUS --workspace /path/to/repo
```

---

## 🛡️ Enhanced Conflict Resolution

**New in Phase 4:** Intelligent conflict detection and resolution guidance

### When Conflicts Occur

**Strategy: `"prompt"` (default)**
```
❌ Merge conflicts detected in 2 file(s)
⚠️  Manual resolution required:
  1. Edit conflicted files to resolve markers
  2. Run: git add <resolved-files>
  3. Run: git rebase --continue
  4. Retry sync with #SYNC//. or #321//.
```

**Strategy: `"abort"`**
```
❌ Conflicts detected - aborted to preserve work
⚠️  Rebase aborted to protect local changes
  To resolve manually:
  1. Run: git pull origin main
  2. Resolve conflicts in affected files
  3. Commit resolved changes
  4. Retry #321//. or #SYNC//.
```

### Configuring Strategy

Edit `.aurora/sync_config.json`:
```json
{
  "conflict_resolution_strategy": "prompt"  // or "abort"
}
```

---

## 📝 Implementation Notes

### File Categorization

All commands use intelligent file categorization:
- **Source:** `src/`, `api/`, `modules/*.py`
- **Tests:** `tests/*.py`
- **Docs:** `*.md`, `docs/`
- **Workflows:** `.github/workflows/`
- **Config:** `*.json`, `*.yaml`, `*.toml`
- **Other:** Everything else

### Staging Priority

When staging files, priority order:
1. Source code files
2. Test files
3. Workflow files
4. Documentation files
5. Configuration files
6. Other files

### Semantic Commits

Auto-detection of commit type:
- **feat:** New source files
- **refactor:** Modified source files
- **test:** Test changes
- **docs:** Documentation changes
- **ci:** Workflow changes
- **chore:** Config/other changes

---

## 🔗 Integration

### Parser Integration

Commands are registered in `parser.py`:
```python
SUPPORTED_COMMANDS = {
    '321',  # Full sync
    # ... other commands
}
```

### Dispatcher Integration

Add new commands to dispatcher:
```python
from tools.command_chain.dispatcher import register_command

def my_command(config_path=None, workspace_path=None):
    # Implementation
    pass

register_command('MYCOMMAND', my_command)
```

---

## 📚 Related Documentation

- **[COMPREHENSIVE_SYNC_321.md](COMPREHENSIVE_SYNC_321.md)** - Full #321//. specification
- **[USAGE_321.md](USAGE_321.md)** - Detailed usage guide for #321//.
- **[COMMAND_REFERENCE.md](../../.github/COMMAND_REFERENCE.md)** - Aurora command syntax reference

---

## ✅ Validation Results

All commands tested and validated:
- ✅ #321//. - 3 successful executions, 100% success rate
- ✅ #STATUS//. - Fast status checks working
- ✅ #COMMIT//. - Local commits working
- ✅ #SYNC//. - Remote sync working
- ✅ Dispatcher - All command routing working
- ✅ Enhanced conflict resolution - Guidance tested

---

**Last Updated:** November 16, 2025  
**Version:** 1.0.0
