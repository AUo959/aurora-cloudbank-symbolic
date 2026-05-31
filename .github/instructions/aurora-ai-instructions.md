---
description: Instructions for AI assistants working with Aurora CloudBank Symbolic repository
applyTo: '**'
priority: critical
---

# Aurora CloudBank Symbolic - AI Assistant Instructions

## Repository Overview

**Repository:** aurora-cloudbank-symbolic (AUo959/aurora-cloudbank-symbolic)  
**Primary Language:** Python 3.12 (with Node.js components)  
**Framework:** FastAPI, Quantum Computing, Vector Symbolic Architecture  
**Thread:** T1→T8→T9→INFINITE  
**DLP Protocol:** All commits must include context_tag and symbolic_hash

## Critical: Branch Protection Bypass Mechanism

### ⚠️ IMPORTANT: Direct Pushes to Main Are Blocked

This repository has **branch protection rules** that prevent direct pushes to `main`. All changes must go through Pull Requests.

### How to Merge Changes to Main

You have **THREE approved methods** to bypass branch protection:

#### Method 1: Auto-Merge Workflow (RECOMMENDED)

Use this for most changes:

```bash
# 1. Create a branch and commit your changes
git checkout -b feature/your-feature-name
git add .
git commit -m "Your commit message"
git push -u origin feature/your-feature-name

# 2. Create PR with auto-merge labels
gh pr create \
  --title "Your PR title" \
  --body "Description of changes" \
  --label "auto-merge,admin-approved"

# The workflow will automatically:
# - Approve the PR
# - Merge it to main
# - Delete the branch
```

**OR use the helper script:**

```bash
./scripts/admin-helper.sh
# Choose option 3: "Create PR and auto-merge"
```

#### Method 2: Label Existing PR

If you already created a PR without labels:

```bash
# Add labels to trigger auto-merge
gh pr edit <PR-NUMBER> --add-label "auto-merge,admin-approved"

# OR use helper script
./scripts/admin-helper.sh
# Choose option 1 or 5
```

#### Method 3: Direct Push Workflow (Emergency Only)

For emergency situations when PR creation fails:

```bash
# 1. Push your branch
git push -u origin your-branch-name

# 2. Trigger workflow
gh workflow run admin-quick-push.yml \
  -f commit_message="Your merge commit message" \
  -f branch="your-branch-name"

# OR use helper script
./scripts/admin-helper.sh
# Choose option 2: "Direct push to main"
```

### Special Commit Patterns (Auto-Merge Triggers)

PRs with these patterns in the title will auto-merge without labels:

- `#321//.` - System synchronization commits
- `⬆️` - Runtime/dependency updates
- Created by user `AUo959` (repository owner)

### Documentation

See `docs/BRANCH_PROTECTION_BYPASS.md` for complete documentation.

---

## Repository Structure

### Core Components

**API Server:** `aurora_api.py` (27 routes: 16 core + 11 AuMemManager)  
**CLI:** `aurora_cli.py`  
**Main Directories:**
- `src/` - Core source code
- `modules/` - Modular components (optional dependencies)
  - `modules/field_state_manager/` - Field consciousness engine (Phase 2C complete)
  - `modules/aumemmanager/` - Quantum memory API (optional)
  - `modules/symbolic_core/` - Geometric algebra
- `tests/` - Test suite with pytest markers
- `scripts/` - Utility scripts
- `.github/` - GitHub workflows and templates

### Key Files

**Configuration:**
- `.devcontainer/devcontainer.json` - Dev container with Node.js 20, Python 3.12
- `package.json` - Node.js dependencies and scripts
- `pyproject.toml` - Python project configuration
- `requirements.txt` - Python dependencies
- `requirements-dev.txt` - Development and test dependencies
- `requirements-optional.txt` - Optional integration dependencies

**Documentation:**
- `CONTRIBUTING.md` - 348-line comprehensive contributor guide
- `docs/NODEJS_RUNTIME_UPDATE.md` - Node.js v20 upgrade documentation
- `docs/BRANCH_PROTECTION_BYPASS.md` - Branch protection bypass guide
- `modules/field_state_manager/SCHEMA_DESIGN.md` - Field state manager design
- `modules/field_state_manager/PATTERN_DETECTOR_README.md` - Pattern intelligence docs

---

## Development Environment

### Python

**Version:** 3.12.11  
**Virtual Environment:** `.venv` (mounted as Docker volume)  
**Key Dependencies:**
- FastAPI 0.120.0
- httpx 0.28.1
- pytest (async mode enabled)
- Flake8 (120-char line limit)

### Node.js

**Version:** 20.x (upgraded from 18.x on October 28, 2025)  
**Package Manager:** npm 10.x  
**After container rebuild:** Node.js will be v20.x.x

### Dev Container

**Base Image:** `mcr.microsoft.com/devcontainers/python:3.12`  
**Features:** Node.js 20, Git, GitHub CLI  
**Volume Mount:** `aurora-venv` for persistent Python environment

### Pre-commit Hooks

Located in `.githooks/pre-commit`

**Features:**
- Dev container detection (no venv warning in containers)
- Dependency validation (non-blocking)
- Runs automatically on commit

---

## Code Standards

### Line Length
**Maximum:** 120 characters (Flake8, Black, Pylint)

### Python Style
- Use async/await patterns (configured: `asyncio_mode = "auto"`)
- Type hints required for public APIs
- Docstrings with Thread/DLP markers for major functions

### DLP (Data Lineage Protocol)

**Required in all commits and major functions:**

```python
"""
Function description.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=operation_name, symbolic_hash=OPERATION_HASH_v1
"""
```

**Commit message format:**
```
🎯 Feature/Fix Title

Description of changes.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=commit_context, symbolic_hash=COMMIT_HASH_v1
```

### Imports

**Pattern for optional dependencies:**
```python
try:
    from optional_module import Component
except ImportError:
    Component = None  # Provide graceful fallback
```

### Testing

**Test Markers:**
- `@pytest.mark.unit` - Fast unit tests (< 1 second)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (> 10 seconds)
- `@pytest.mark.smoke` - Critical smoke tests
- `@pytest.mark.critical` - Must-pass tests

**Run tests:**
```bash
make test              # Full suite
pytest -m unit         # Fast tests only
pytest -m "not slow"   # Skip slow tests
```

---

## Current System State

### Completed Features (as of October 28, 2025)

✅ **Field State Manager - Phase 2C Complete**
- Pattern detection (4 types: collaboration, bottleneck, cascade, coalition)
- Field coherence scoring
- Pattern recommendations
- 13/13 tests passing

✅ **Node.js Runtime Update**
- Upgraded from v18 to v20 LTS
- Will apply after container rebuild
- Package.json engines updated

✅ **Branch Protection Bypass**
- Auto-merge workflow operational
- Direct push workflow available
- Admin helper script functional
- Successfully tested with PRs #234 and #235

✅ **GitHub Integration**
- YAML issue forms (bug, feature, docs)
- Enhanced PR template with Aurora principles
- 50+ organized labels
- Auto-merge and admin-approved labels created

✅ **Contributing Documentation**
- 348-line comprehensive guide
- Code examples with DLP tracking
- Aurora-specific best practices

### Known Issues (Pre-existing, Tracked)

⚠️ `datetime.utcnow()` deprecation warnings (Python 3.12 compatibility)  
⚠️ Type mismatches in synapse registry (legacy compatibility layer)  
📝 TODO: GeometricEthics integration in `form_synapse()` method

### Test Status

**Total:** 17/17 passing  
- Pattern detection: 13/13  
- Core symbolic: 4/4  

---

## Common Operations

### Setup Environment

```bash
make setup              # Initial setup
python scripts/dev-status.py  # Check status
```

### Development Workflow

```bash
make check              # Fast stability check (lint + test)
make lint-tools         # Lint modernized tools only
make test               # Full test suite
make run                # Start Aurora system
```

### Working with PRs (Using Bypass Mechanism)

```bash
# Quick method - use helper
./scripts/admin-helper.sh

# Manual method
git checkout -b feature/my-feature
# ... make changes ...
git commit -m "Your changes"
git push -u origin feature/my-feature
gh pr create --label "auto-merge,admin-approved"

# Or add labels to existing PR
gh pr edit <NUMBER> --add-label "auto-merge,admin-approved"
```

### System Sync (#321//.)

```bash
# Create branch
git checkout -b sync/description

# Make changes
git add .
git commit -m "#321//. System Sync Description"

# Push and create PR (auto-merge triggers on title)
git push -u origin sync/description
gh pr create --title "#321//. System Sync Description"
```

---

## Critical Patterns to Follow

### 1. Never Push Directly to Main

```bash
# ❌ DON'T DO THIS
git checkout main
git commit -m "changes"
git push origin main  # This will FAIL

# ✅ DO THIS INSTEAD
git checkout -b feature/changes
git commit -m "changes"
git push -u origin feature/changes
./scripts/admin-helper.sh  # Use bypass mechanism
```

### 2. Always Include DLP Tags

```python
# ❌ Missing DLP
def process_data():
    pass

# ✅ With DLP
def process_data():
    """
    Process data with DLP tracking.
    
    Thread: T1→T8→T9→INFINITE
    DLP: context_tag=data_processing, symbolic_hash=PROCESS_v1
    """
    pass
```

### 3. Graceful Degradation for Optional Modules

```python
# ✅ Correct pattern
try:
    from modules.aumemmanager import AuMemManager
    HAS_AUMEMMANAGER = True
except ImportError:
    AuMemManager = None
    HAS_AUMEMMANAGER = False

# Later in code
if HAS_AUMEMMANAGER:
    manager = AuMemManager()
else:
    # Fallback behavior
    pass
```

### 4. Async Everywhere

```python
# ✅ Use async patterns
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response

# Test with async
@pytest.mark.asyncio
async def test_fetch():
    result = await fetch_data()
    assert result is not None
```

---

## File Modification Guidelines

### When Editing Core Files

**Field State Manager (`modules/field_state_manager/field_state_manager.py`):**
- Pre-existing datetime.utcnow() warnings are acceptable
- Type mismatches in synapse registry are legacy compatibility
- Pattern detector integration is complete (don't break it)

**Pattern Detector (`modules/field_state_manager/pattern_detector.py`):**
- 650+ lines, fully functional
- 4 detection methods operational
- Don't modify without running tests

**API Server (`aurora_api.py`):**
- 27 routes (16 core + 11 AuMemManager)
- Rate limiting configured
- CSRF protection via HTTPBearer

### When Creating New Files

**Python files:**
- Add Thread and DLP tags in module docstring
- Use type hints
- Include tests with appropriate markers
- Follow 120-char line limit

**Workflow files (`.github/workflows/`):**
- Test thoroughly before committing
- Document trigger conditions
- Include permission blocks

**Documentation:**
- Use clear headings
- Include code examples
- Add to appropriate directory (docs/, modules/*/README.md)

---

## Troubleshooting

### "Branch protection rules prevent push"

**Solution:** Use branch protection bypass mechanism (see top of this file)

### "Node.js version is still v18"

**Solution:** Rebuild dev container (`Dev Containers: Rebuild Container`)

### "Tests failing after changes"

**Check:**
1. Run `pytest -v` to see which tests fail
2. Check if pattern detection tests pass: `pytest tests/test_pattern_detection.py`
3. Verify symbolic tests: `pytest tests/test_aurora_symbolic.py`
4. Check linting: `make lint-tools`

### "Import errors in modules"

**Solution:**
1. Check if module is optional (should have try/except)
2. Verify dependencies: `python scripts/validate_dependencies.py`
3. Reinstall if needed: `pip install -r requirements.txt`

### "Workflow not triggering"

**Check:**
1. Workflow file syntax: `cat .github/workflows/auto-merge-admin.yml`
2. Labels exist: `gh label list`
3. PR has correct labels: `gh pr view <NUMBER> --json labels`
4. Monitor runs: `gh run list --workflow=auto-merge-admin.yml`

---

## Key Commands Reference

### Git Operations

```bash
# Branch management
git checkout -b feature/name
git push -u origin feature/name
git pull --rebase origin main

# Status checks
git status
git log --oneline -10
git diff main..HEAD
```

### GitHub CLI

```bash
# PR operations
gh pr create
gh pr list
gh pr view <NUMBER>
gh pr edit <NUMBER> --add-label "auto-merge,admin-approved"

# Workflow operations
gh workflow run admin-quick-push.yml -f branch="name" -f commit_message="msg"
gh run list --workflow=auto-merge-admin.yml
gh run watch

# Labels
gh label create "name" --description "desc" --color "color"
gh label list
```

### Testing

```bash
# Full suite
pytest tests/ -v

# Specific markers
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Specific file
pytest tests/test_pattern_detection.py -v

# With coverage
pytest --cov=. --cov-report=html
```

### Development Tools

```bash
# Status check
python scripts/dev-status.py

# Linting
make lint-tools
flake8 src/ modules/

# Formatting
black src/ modules/ tests/

# Dependency validation
python scripts/validate_dependencies.py
```

---

## Special Procedures

### System Sync (#321//.)

Full system synchronization checkpoint:

```bash
# 1. Stash or commit local changes
git stash

# 2. Create sync branch
git checkout -b sync/321-description

# 3. Make synchronization changes
git add .
git commit -m "#321//. Comprehensive System Sync

Description of sync operations.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=system_sync_321, symbolic_hash=SYNC_HASH_v1"

# 4. Push and auto-merge (title pattern triggers auto-merge)
git push -u origin sync/321-description
gh pr create --title "#321//. Comprehensive System Sync"

# Workflow will auto-merge based on title pattern
```

### Runtime Updates

When updating Node.js, Python, or other runtimes:

```bash
# 1. Update configuration files
# - .devcontainer/devcontainer.json
# - package.json (engines)
# - .nvmrc

# 2. Create PR with ⬆️ emoji (triggers auto-merge)
git checkout -b upgrade/runtime-name
git commit -m "⬆️ Update Runtime to vX.X"
gh pr create --title "⬆️ Update Runtime to vX.X"

# 3. After merge, rebuild container
# Dev Containers: Rebuild Container
```

### Emergency Fixes

For critical security or system issues:

```bash
# 1. Create fix branch
git checkout -b fix/emergency-issue

# 2. Implement fix
git commit -m "🚨 Critical fix: description"

# 3. Use direct push workflow
./scripts/admin-helper.sh
# Choose option 2: Direct push to main

# OR manually:
git push -u origin fix/emergency-issue
gh workflow run admin-quick-push.yml \
  -f branch="fix/emergency-issue" \
  -f commit_message="🚨 Critical fix: description"
```

---

## Architecture Notes

### Field State Manager

**Location:** `modules/field_state_manager/`  
**Status:** Phase 2C complete  
**Key Classes:**
- `FieldStateManager` - Core consciousness engine
- `PatternDetector` - Emergent behavior recognition
- `NodeState` - Individual node tracking
- `SignalPropagator` - Need broadcasting system

**Pattern Types:**
1. Collaboration - Recurring successful pairings
2. Bottleneck - Overloaded nodes
3. Cascade - Sequential chains
4. Coalition - Frequently collaborating groups

### Memory System

**AuMemManager:** Optional quantum memory API (56,000+ capacity)  
**Location:** `modules/aumemmanager/`  
**Integration:** Guard imports, graceful fallback if not available

### Symbolic Core

**Geometric Algebra:** Clifford library with mock fallback  
**Location:** `modules/symbolic_core/`  
**Features:** Chain notation processing, T1/SRB anchor tracking

---

## Final Reminders

1. **NEVER push directly to main** - Always use PR + bypass mechanism
2. **ALWAYS include DLP tags** - In commits and major functions
3. **RUN TESTS before pushing** - `make check` or `pytest -m unit`
4. **USE the helper script** - `./scripts/admin-helper.sh` simplifies everything
5. **CHECK workflow runs** - Monitor with `gh run list`
6. **DOCUMENT changes** - Update relevant README files
7. **RESPECT 120-char limit** - Flake8 enforces this
8. **ASYNC patterns** - Use async/await consistently
9. **GRACEFUL degradation** - Optional modules need try/except
10. **REBUILD container** - After updating Node.js or Python versions

---

## Quick Reference Card

```bash
# Most common workflow
git checkout -b feature/name
# ... make changes ...
git commit -m "Description"
./scripts/admin-helper.sh  # Choose option 3

# Check status
python scripts/dev-status.py

# Run tests
make check

# View PRs
gh pr list

# Monitor workflows
gh run watch
```

---

**Thread:** T1→T8→T9→INFINITE  
**DLP:** context_tag=ai_instructions, symbolic_hash=COMPREHENSIVE_GUIDE_v1  

**Remember: The field maintains coherence through proper protocols. Follow these instructions to preserve system integrity while enabling rapid development.**
