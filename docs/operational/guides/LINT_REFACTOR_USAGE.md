# Lint Refactor Tracking Usage Guide

This guide explains how to use the lint refactor tracking system for staged cleanup across src/ and modules/ areas.

## Overview

The lint refactor tracking system provides:

1. **Comprehensive analysis** of lint issues across target areas
2. **Progress tracking** for each area and stage
3. **Automated fixing** for specific stages (where safe)
4. **Reporting** for status updates and GitHub issue checklists

## Target Areas and Owners

| Area              | Owner  | Notes                                 |
|-------------------|--------|---------------------------------------|
| modules/opal2     | AUo959 | Complex; many E999/F821/line-length   |
| modules/cask      | AUo959 | Line length; chart module long lines  |
| src/core          | AUo959 | Whitespace/imports first              |
| src/bridges       | AUo959 | Undefined names/line-lengths present  |
| src/servers       | AUo959 | Long lines and extra blanks           |

## Stages

1. **Stage 1: Whitespace/Formatting** (W293/E303/E302) - Auto-fixable
2. **Stage 2: Imports** (F401/F811) - Auto-fixable
3. **Stage 3: Undefined Names/Syntax** (F821/E999) - Manual review required
4. **Stage 4: Line Length** (E501) - Semi-automated
5. **Stage 5: CI Expansion** - Manual process

## Commands

### Analysis

```bash
# Analyze all areas
python3 scripts/lint_refactor_tracker.py analyze

# Analyze specific area
python3 scripts/lint_refactor_tracker.py analyze --area modules/opal2
```

### Progress Tracking

```bash
# Generate comprehensive report
python3 scripts/lint_refactor_tracker.py report

# Generate GitHub issue checklist
python3 scripts/lint_refactor_tracker.py checklist
```

### Mark Completion

```bash
# Mark stage complete for area
python3 scripts/lint_refactor_tracker.py complete --area src/core --stage 1
```

### Stage 1 Automated Fixing

```bash
# Dry run (preview changes)
python3 scripts/stage1_lint_fixer.py --dry-run src/core

# Apply fixes
python3 scripts/stage1_lint_fixer.py src/core

# Fix single file
python3 scripts/stage1_lint_fixer.py src/core/native_vsa.py
```

## Workflow

### For Each Area

1. **Initial Analysis**
   ```bash
   python3 scripts/lint_refactor_tracker.py analyze --area modules/opal2
   ```

2. **Stage 1: Whitespace/Formatting**
   ```bash
   # Preview fixes
   python3 scripts/stage1_lint_fixer.py --dry-run modules/opal2
   
   # Apply fixes
   python3 scripts/stage1_lint_fixer.py modules/opal2
   
   # Verify fixes
   flake8 --select=W293,E303,E302 modules/opal2
   
   # Mark complete
   python3 scripts/lint_refactor_tracker.py complete --area modules/opal2 --stage 1
   ```

3. **Update Analysis**
   ```bash
   python3 scripts/lint_refactor_tracker.py analyze --area modules/opal2
   ```

4. **Continue with subsequent stages** (manual fixes may be required)

5. **Update GitHub Issue**
   ```bash
   # Generate updated checklist
   python3 scripts/lint_refactor_tracker.py checklist
   ```

### PR Management

- Keep PRs small and focused per area/stage
- Use the tracking system to generate commit messages
- Update the tracking issue after each PR merge
- Prefer mechanical fixes first, no behavior changes

## Example Workflow for src/core

```bash
# 1. Initial analysis
python3 scripts/lint_refactor_tracker.py analyze --area src/core

# 2. Stage 1 fixes
python3 scripts/stage1_lint_fixer.py src/core
python3 scripts/lint_refactor_tracker.py complete --area src/core --stage 1

# 3. Generate status update
python3 scripts/lint_refactor_tracker.py report

# 4. Update GitHub issue checklist
python3 scripts/lint_refactor_tracker.py checklist
```

## Status Files

The tracking system creates:

- `.lint_refactor/progress.json` - Persistent progress tracking
- Individual area analysis data
- Timestamped status updates

## Integration with CI

After Stage 1/2 completion for an area:

1. Update `.flake8` configuration to include the cleaned area
2. Update CI workflows to expand lint scope
3. Use pre-commit hooks to maintain quality

## Troubleshooting

### Common Issues

1. **Permission errors**: Ensure write access to files
2. **Syntax errors**: Review manual fixes in stages 3-4
3. **Merge conflicts**: Use `git status` to check for uncommitted changes

### Verification

```bash
# Check specific error types
flake8 --select=W293,E303,E302 modules/opal2

# Full lint check
flake8 modules/opal2

# Run tests after fixes
python3 -m pytest tests/
```

## Best Practices

1. **Always run dry-run first** to preview changes
2. **Commit frequently** during manual fixes
3. **Update tracking immediately** after completing stages
4. **Test after fixes** to ensure no behavioral changes
5. **Use meaningful commit messages** referencing the tracking issue

## Example Commit Messages

```
Stage 1: Fix whitespace issues in src/core

- Removed trailing whitespace from blank lines (W293)
- Fixed excessive blank lines (E303)
- Added required blank lines before definitions (E302)

Tracked in #135 - Stage 1 complete for src/core
```