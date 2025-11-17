# #321//. - Comprehensive Sync & Validate

**Status:** ✅ Fully Implemented  
**Version:** 1.0.0  
**Created:** 2025-11-16

## 🎯 Quick Start

```bash
# Execute with defaults (uses .aurora/sync_config.json if exists)
python tools/command_chain/cmd_321.py

# Preview what it will do (dry-run)
python tools/command_chain/cmd_321.py --dry-run

# Use custom configuration
python tools/command_chain/cmd_321.py --config custom_config.json

# Create a configuration file
python tools/command_chain/cmd_321.py --init-config ~/.aurora/sync.json

# View current configuration
python tools/command_chain/cmd_321.py --show-config
```

## Philosophy

**Reliable, fast, elegant** - clean your working tree anytime with consistent high quality and minimal cognitive overhead.

- ✅ **Context-aware** - Understands what types of files changed
- ✅ **Intelligent staging** - Groups files by category and priority
- ✅ **Semantic commits** - Generates meaningful commit messages
- ✅ **Safe sync** - Pull with rebase, conflict detection
- ✅ **Smart validation** - Skips unnecessary checks
- ✅ **Performance tracking** - Reports timing for each phase

## The 6 Phases

### Phase 1: Check for Pending Changes
- Detects all file changes with `git status --porcelain`
- Categorizes files: source, tests, docs, config, workflows, other
- Identifies if changes are docs-only or config-only
- Early exit if working tree already clean

### Phase 2: Intelligent Staging
Stages files in priority order:
1. **Source code** - `src/`, `api/`, `modules/` (Python files)
2. **Tests** - `tests/` (Python files)
3. **Workflows** - `.github/workflows/`
4. **Documentation** - `.md` files, `docs/`
5. **Configuration** - `.json`, `.yaml`, `.toml`
6. **Other** - Everything else

### Phase 3: Generate & Commit
- Analyzes changes to determine semantic commit type:
  - `feat:` - Mostly new source files
  - `refactor:` - Mostly modified source
  - `test:` - Mostly test changes
  - `docs:` - Documentation updates
  - `ci:` - Workflow changes
  - `chore:` - Config/other changes
- Generates commit message from template
- Adds DLP tag for traceability

### Phase 4: Sync to Main
- Pulls from remote with rebase (configurable)
- Detects conflicts before push
- Pushes to remote (configurable)
- Verifies sync success

### Phase 5: Quick Validation
- **Smart skipping:**
  - Docs-only changes skip validation
  - Config-only changes skip tests
- **Runs checks based on validation level:**
  - `fast` - Lint critical files + unit tests
  - `thorough` - Lint all + unit/integration tests
  - `complete` - Full lint + all tests
- Non-blocking - warnings don't fail execution

### Phase 6: Performance Verification
- Measures total execution time
- Compares against performance target
- Verifies working tree is clean
- Reports warnings if issues detected

## Configuration

### Default Configuration

The `.aurora/sync_config.json` file contains smart defaults:

```json
{
  "commit_message_template": "{type}({scope}): {summary}",
  "default_commit_type": "chore",
  "validation_level": "fast",
  "skip_validation_on_docs_only": true,
  "skip_tests_on_config_only": true,
  "performance_target_seconds": 45,
  "use_rebase": true,
  "auto_push": true,
  "lint_command": "flake8 src/ api/ modules/ --max-line-length=120 --select=E,F --statistics",
  "test_command": "pytest -m unit -x --tb=short -q"
}
```

### Customization Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `commit_message_template` | string | `"{type}({scope}): {summary}"` | Commit message format |
| `default_commit_type` | string | `"chore"` | Fallback commit type |
| `validation_level` | string | `"fast"` | Validation thoroughness: `fast`, `thorough`, `complete` |
| `skip_validation_on_docs_only` | bool | `true` | Skip checks for doc-only changes |
| `skip_tests_on_config_only` | bool | `true` | Skip tests for config-only changes |
| `performance_target_seconds` | int | `45` | Target execution time |
| `timeout_seconds` | int | `300` | Max execution time |
| `use_rebase` | bool | `true` | Use rebase vs merge |
| `auto_push` | bool | `true` | Automatically push to remote |
| `lint_command` | string | (see config) | Linting command to run |
| `test_command` | string | (see config) | Test command for fast validation |
| `fast_test_markers` | string | `"unit"` | Pytest markers for fast tests |
| `thorough_test_markers` | string | `"unit or integration"` | Pytest markers for thorough tests |

### Creating Custom Configurations

```bash
# Initialize config with defaults
python tools/command_chain/cmd_321.py --init-config my_config.json

# Edit the file to customize
nano my_config.json

# Use your custom config
python tools/command_chain/cmd_321.py --config my_config.json
```

### Per-Project Configurations

Place `.aurora/sync_config.json` in your project root - it will be auto-detected:

```bash
mkdir -p .aurora
python tools/command_chain/cmd_321.py --init-config .aurora/sync_config.json
# Edit as needed
python tools/command_chain/cmd_321.py  # Auto-uses .aurora/sync_config.json
```

## Use Cases

### 1. Regular Development Checkpoints
```bash
# Every 30-60 minutes during development
python tools/command_chain/cmd_321.py
```
**Result:** Progress saved, working tree clean, ready to continue coding

### 2. Before Context Switch
```bash
# Switching to different task
python tools/command_chain/cmd_321.py
```
**Result:** Current work saved safely, can switch focus without losing progress

### 3. End of Coding Session
```bash
# Done for the day
python tools/command_chain/cmd_321.py
```
**Result:** Everything synced, validated, ready for tomorrow

### 4. Pre-Deployment Confidence
```bash
# Before deploying to production
python tools/command_chain/cmd_321.py --config thorough_validation.json
```
**Result:** All changes synced, thoroughly tested, confident to deploy

### 5. Documentation Updates
```bash
# Made doc-only changes
python tools/command_chain/cmd_321.py
```
**Result:** Docs committed, validation skipped (per config), fast execution

## Output Example

```
📄 Using config: .aurora/sync_config.json
🚀 Executing #321//. - Comprehensive Sync & Validate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ #321//. COMPLETE - ALL PHASES SUCCESSFUL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 EXECUTION SUMMARY:
   Total Time: 17.3s
   Changes: 3 files
   Commit: c1b562d5
   Message: chore(config): Update 3 files (1 config, 2 other)

DLP: CMD-CHAIN-SYNC-321-20251116_023145

🎯 PHASE STATUS:
   Phase 1: Check Changes               0.0s ✅
   Phase 2: Intelligent Staging         0.0s ✅
   Phase 3: Generate & Commit           0.5s ✅
   Phase 4: Sync to Main                1.4s ✅
   Phase 5: Quick Validation           15.3s ✅
   Phase 6: Performance Verification    0.0s ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Programmatic Usage

```python
from tools.command_chain.comprehensive_sync_321 import execute_321

# Execute with defaults
result = execute_321()

# Execute with custom config
result = execute_321(config_path=".aurora/sync_config.json")

# Check result
if result.success:
    print(f"✅ Success! Cleaned working tree in {result.total_duration:.1f}s")
    print(f"Committed {result.files_changed} files with SHA: {result.commit_sha}")
else:
    print("❌ Failed - check phase results")
    for phase in result.phases:
        if not phase.success:
            print(f"  Failed at Phase {phase.phase_number}: {phase.message}")

# Print full report
print(result.format_report())
```

## Key Features

### 🎯 Context-Aware Intelligence

- **Detects file categories** - Source, tests, docs, config, workflows
- **Smart validation** - Skips unnecessary checks based on change type
- **Semantic commits** - Generates meaningful messages from context
- **Priority staging** - Orders files by importance

### 🛡️ Safety & Reliability

- **Rebase by default** - Cleaner history than merge commits
- **Conflict detection** - Identifies issues before push
- **Non-blocking validation** - Warnings don't stop execution
- **DLP tracking** - Every commit tagged for traceability

### ⚡ Performance Optimized

- **Fast validation** - Unit tests only by default
- **Smart skipping** - Docs-only changes skip tests
- **Timeout protection** - Won't hang indefinitely
- **Performance tracking** - Reports actual vs target timing

### 🔧 Highly Customizable

- **JSON configuration** - Easy to customize without code changes
- **Validation levels** - Choose speed vs thoroughness
- **Template commits** - Define your own message format
- **Selective validation** - Configure what runs when

## Best Practices

### DO ✅

- Use regularly (every 30-60 min) during development
- Trust the intelligent staging - it groups files correctly
- Review the completion report to understand what happened
- Customize `.aurora/sync_config.json` for project-specific needs
- Use `--dry-run` to preview behavior before executing

### DON'T ❌

- Use for experimental WIP code (commit manually instead)
- Ignore warnings - they indicate issues to investigate
- Skip reading failure messages - they guide resolution
- Disable validation without good reason
- Use in feature branches without reviewing staged files

## Troubleshooting

### "Failed to pull from remote"
**Cause:** Network issues or conflicts  
**Fix:** Check network, resolve conflicts manually with `git status`

### "Failed to push to remote"
**Cause:** Remote has changes or push rejected  
**Fix:** Pull first, resolve conflicts, retry

### "Lint check found issues"
**Cause:** Code quality violations detected  
**Result:** Non-blocking warning - commit still succeeded  
**Action:** Review violations and fix in next commit

### "Some tests failed"
**Cause:** Test failures detected during validation  
**Result:** Non-blocking warning - commit still succeeded  
**Action:** Review test failures and fix issues

### Execution takes too long
**Solution:** Adjust `validation_level` from `thorough` to `fast` in config

### Want to skip tests for config changes
**Solution:** Set `skip_tests_on_config_only: true` in config

## Implementation Details

- **Language:** Python 3.12+
- **Dependencies:** git, pytest, flake8 (for validation)
- **Configuration format:** JSON
- **Exit codes:** 0 = success, 1 = failure, 130 = interrupted

## Integration with Command Chain

The `#321//.` command is integrated into the Aurora command chain system:

```bash
# Using numeric code (once wired into parser)
#321//.

# Using CLI directly (available now)
python tools/command_chain/cmd_321.py
```

## Files

- `tools/command_chain/comprehensive_sync_321.py` - Core implementation
- `tools/command_chain/cmd_321.py` - CLI wrapper
- `.aurora/sync_config.json` - Default configuration
- `tools/command_chain/COMPREHENSIVE_SYNC_321.md` - Detailed documentation

## Version History

- **1.0.0** (2025-11-16) - Initial implementation
  - All 6 phases operational
  - JSON configuration support
  - Context-aware intelligence
  - CLI with dry-run and config management
