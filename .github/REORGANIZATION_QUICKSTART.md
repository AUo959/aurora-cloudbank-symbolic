# Aurora Repository Reorganization - Quick Start Guide

**Status:** ✅ Ready for Execution  
**Phase:** 1 of 5 (Root Directory Cleanup)  
**Estimated Time:** 2-3 hours  
**Risk Level:** Low (full backup + rollback available)

---

## 📋 Pre-Flight Checklist

Before running the reorganization script:

- [ ] **Read the audit report:** `.github/ARCHITECTURE_AUDIT_REPORT.md`
- [ ] **Backup verification:** Ensure all work is committed
- [ ] **Team notification:** Alert team members of pending changes
- [ ] **CI/CD awareness:** Monitor pipeline status
- [ ] **Time allocation:** Schedule 2-3 hours for Phase 1

---

## 🚀 Quick Start (3 Commands)

### 1. Dry Run (Recommended First)
```bash
cd /workspaces/aurora-cloudbank-symbolic
bash scripts/reorganize_phase1.sh --dry-run
```

**This will:**
- ✅ Show all planned moves without executing
- ✅ Validate preconditions
- ✅ Preview directory structure
- ⚠️ Make NO actual changes

### 2. Execute Phase 1
```bash
cd /workspaces/aurora-cloudbank-symbolic
bash scripts/reorganize_phase1.sh
```

**This will:**
- Create backup branch automatically
- Move 300+ files to organized locations
- Update .gitignore for data isolation
- Create README files in new directories
- Validate completion

### 3. Verify & Test
```bash
# Check what changed
git status

# Run test suite
make test

# If everything works, commit
git add .
git commit -m "Phase 1: Repository reorganization - Root cleanup

- Moved 91 Python scripts to tools/ and scripts/
- Moved 66 shell scripts to scripts/ subdirectories
- Moved 71 configs to config/examples/
- Moved 150+ docs to docs/ hierarchy
- Updated .gitignore for data isolation
- Added README files to new directories

DLP:reorganization_phase1 | T1:audit_001
See: .github/ARCHITECTURE_AUDIT_REPORT.md"
```

---

## 📊 What Phase 1 Does

### File Movements

**Python Scripts (91 files):**
```
aurora_api.py               → tools/aurora/api_server.py
aurora_cli.py               → tools/aurora/cli.py
aurora_system_validator.py  → tools/aurora/system_validator.py
advanced_*.py               → scripts/automation/
aurora_*automation*.py      → scripts/automation/
```

**Shell Scripts (66 files):**
```
*setup*.sh                  → scripts/setup/
activate*.sh                → scripts/setup/
*deploy*.sh                 → scripts/deployment/
*launch*.sh                 → scripts/deployment/
*cleanup*.sh                → scripts/maintenance/
*ci*.sh                     → scripts/ci/
```

**Configuration Files (71 files):**
```
*.json (except package.json) → config/examples/
*.yaml, *.yml               → config/examples/
```

**Documentation (150+ files):**
```
*_REPORT*.md                → docs/reports/
*_AUDIT*.md                 → docs/reports/
*_GUIDE*.md                 → docs/guides/
*_INTEGRATION*.md           → docs/architecture/
AUMEMMANAGER*.md            → docs/architecture/
```

### New Directory Structure

```
aurora-cloudbank-symbolic/
├── tools/
│   └── aurora/              # Main Aurora tools
│       ├── api_server.py
│       ├── cli.py
│       └── README.md
├── scripts/
│   ├── setup/               # Environment setup
│   ├── deployment/          # Deployment scripts
│   ├── automation/          # Automation workflows
│   ├── maintenance/         # Cleanup & fixes
│   ├── ci/                  # CI/CD scripts
│   └── README.md
├── config/
│   └── examples/            # Sample configurations
├── docs/
│   ├── guides/              # User guides
│   ├── architecture/        # System design
│   ├── reports/             # Audit reports
│   └── development/         # Dev guides
└── data/                    # Runtime data (git-ignored)
    ├── logs/
    ├── exports/
    ├── reports/
    └── cache/
```

---

## 🔄 Rollback Procedure

If something goes wrong:

```bash
# Option 1: Hard reset to backup branch
git reset --hard backup-reorganization-TIMESTAMP

# Option 2: Revert specific commits
git revert HEAD

# Option 3: Restore from stash (if you stashed before)
git stash pop
```

**Backup branch name format:** `backup-reorganization-YYYYMMDD-HHMMSS`

---

## ⚠️ Known Issues & Solutions

### Issue 1: Import Errors After Move

**Symptom:** `ModuleNotFoundError: No module named 'aurora_api'`

**Solution:**
```bash
# Update import in files that reference moved modules
# Example: If code imports aurora_api
sed -i 's/import aurora_api/from tools.aurora import api_server as aurora_api/g' <file>

# Or add tools/ to Python path temporarily
export PYTHONPATH="${PYTHONPATH}:/workspaces/aurora-cloudbank-symbolic/tools"
```

### Issue 2: Shell Scripts Can't Find Paths

**Symptom:** Scripts fail with "file not found"

**Solution:**
```bash
# Update SCRIPT_DIR in moved scripts
# Most scripts already use:
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"  # Adjust .. to ../.. if needed
```

### Issue 3: CI/CD Pipeline Failures

**Symptom:** GitHub Actions can't find files

**Solution:**
```bash
# Update paths in .github/workflows/*.yml
# Example:
# OLD: python aurora_api.py
# NEW: python tools/aurora/api_server.py
```

---

## 🧪 Testing Strategy

### Minimal Test (Fast)
```bash
# Test critical functionality only
pytest tests/test_aurora_symbolic.py -v
pytest tests/test_chatgpt_agent_mode.py -v
```

### Standard Test (Recommended)
```bash
# Full test suite
make test
```

### Comprehensive Test (Thorough)
```bash
# All tests + linting
make check

# Security validation
make security
```

---

## 📈 Success Metrics

After Phase 1 completion, you should see:

```bash
# Count remaining root files
find . -maxdepth 1 -type f -name "*.py" | wc -l
# Target: <10 (down from 91)

find . -maxdepth 1 -type f -name "*.sh" | wc -l
# Target: <10 (down from 66)

find . -maxdepth 1 -type f -name "*.md" | wc -l
# Target: <10 (down from 150)
```

**Expected Reductions:**
- Python files: 91 → ~5 (95% reduction)
- Shell scripts: 66 → ~5 (92% reduction)
- Markdown docs: 150 → ~5 (97% reduction)
- **Total root files: 378 → ~20 (95% reduction)**

---

## 🎯 Next Steps After Phase 1

Once Phase 1 is complete and tested:

1. **Update Imports** - Run import path fixer (TBD in Phase 1.5)
2. **Update Documentation** - Reflect new paths in README files
3. **Update CI/CD** - Adjust GitHub Actions workflows
4. **Team Training** - Share new directory structure
5. **Proceed to Phase 2** - src/ reorganization (eliminate duplicates)

---

## 📞 Support

If you encounter issues:

1. **Check the audit report:** `.github/ARCHITECTURE_AUDIT_REPORT.md`
2. **Review backup branch:** `git branch -a | grep backup`
3. **Consult team** before proceeding if uncertain
4. **Document problems** for future reference

---

## 📝 Phase 1 Command Reference

**Dry run:**
```bash
bash scripts/reorganize_phase1.sh --dry-run
```

**Execute:**
```bash
bash scripts/reorganize_phase1.sh
```

**Check status:**
```bash
git status | head -50
```

**Validate cleanup:**
```bash
find . -maxdepth 1 -type f | wc -l
```

**Test functionality:**
```bash
make test
```

**Commit changes:**
```bash
git add .
git commit -m "Phase 1: Repository reorganization - Root cleanup"
```

---

**Report Status:** ✅ Ready for Execution  
**Last Updated:** 2025-01-03  
**Chain:** #001//017// (17-step cleanup sequence)  
**DLP:** reorganization_phase1  
**T1:** audit_001
