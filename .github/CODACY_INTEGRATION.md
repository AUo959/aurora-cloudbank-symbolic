# Codacy Integration Guide

## ✅ Completed Setup

### 1. Workflow Configuration
- **File:** `.github/workflows/codacy-analysis.yml`
- **Triggers:** Push to main/develop/refactor/**, PRs to main/develop
- **Jobs:**
  - Codacy Security Scan (SARIF upload)
  - Codacy Coverage Report (pytest-cov)
  - Quality Gate Check (Flake8)

### 2. Repository Secret
- **Secret Name:** `CODACY_PROJECT_TOKEN`
- **Status:** ✅ Configured
- **Location:** GitHub → Repository Settings → Secrets and variables → Actions

## 🔒 Branch Protection (Manual Setup Required)

**Why:** Enforce quality gates before merging to main.

**Steps:**
1. Navigate to: https://github.com/AUo959/aurora-cloudbank-symbolic/settings/branches
2. Click "Add rule" or edit existing rule for `main`
3. Configure:
   - ✅ Branch name pattern: `main`
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select these status checks:
     - `Codacy Security Scan`
     - `Codacy Coverage Report`
     - `Quality Gate Check`
   - ✅ Do not allow bypassing the above settings

**Alternative (CLI - requires admin token):**
```bash
gh api repos/AUo959/aurora-cloudbank-symbolic/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=Codacy Security Scan \
  --field required_status_checks[contexts][]=Codacy Coverage Report \
  --field required_status_checks[contexts][]=Quality Gate Check \
  --field enforce_admins=true \
  --field required_pull_request_reviews[required_approving_review_count]=1
```

## 📊 Monitoring & Badges

### Current Workflow Status
```bash
# View latest run
gh run list -R AUo959/aurora-cloudbank-symbolic --workflow "Codacy Analysis" --limit 1

# Watch live
gh run watch <RUN_ID> -R AUo959/aurora-cloudbank-symbolic

# Get detailed job status
gh run view <RUN_ID> -R AUo959/aurora-cloudbank-symbolic
```

### Add Badges to README (After First Successful Run)
```markdown
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/{PROJECT_ID})](https://app.codacy.com/gh/AUo959/aurora-cloudbank-symbolic/dashboard)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/{PROJECT_ID})](https://app.codacy.com/gh/AUo959/aurora-cloudbank-symbolic/dashboard)
```

**Get PROJECT_ID:**
1. Visit: https://app.codacy.com/gh/AUo959/aurora-cloudbank-symbolic
2. URL contains project ID or copy from Settings → Integrations → Badge

## 🔍 Local Analysis (Pre-Commit)

### Run Codacy Analysis Locally
```bash
# Analyze specific file
codacy analyze --file tools/command_chain/artifact_manager.py

# Analyze entire project
codacy analyze

# Get pattern definitions
codacy patterns --tool Pylint
```

### Pre-commit Hook (Optional)
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
echo "🔍 Running Codacy analysis on changed files..."
git diff --cached --name-only --diff-filter=ACMR | grep '\.py$' | while read file; do
    if [ -f "$file" ]; then
        codacy analyze --file "$file" || exit 1
    fi
done
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

## 📈 Quality Metrics

### Current Analysis Results (Local)
- **artifact_manager.py:**
  - ⚠️ Cyclomatic complexity: 10 (limit 8) in `detect_generated_artifacts`
  - ✅ No security vulnerabilities
  - ✅ No Pylint issues

- **executor.py:**
  - ⚠️ File size: 1353 lines (limit 500)
  - ⚠️ Method size: `_handle_comprehensive_sync` (112 lines, limit 50)
  - ⚠️ Unnecessary lambda on line 478
  - ✅ No security vulnerabilities

- **test_automation_fixes.py:**
  - ⚠️ `shell=True` in subprocess (controlled context, acceptable for tests)
  - ⚠️ Unused variable `stderr` on line 91
  - ✅ No other issues

- **test_artifact_manager.py:**
  - ✅ Clean (no issues)

### Recommended Refactoring (Phase 2+)
1. Split `executor.py` into smaller modules (< 500 lines each)
2. Extract `_register_default_handlers` into separate file
3. Simplify `detect_generated_artifacts` (reduce cyclomatic complexity)
4. Remove unnecessary lambda in `executor.py:478`
5. Clean up unused `stderr` variable in tests

## 🚀 Workflow Optimization

### Parallel Job Execution
Current workflow runs jobs sequentially with `needs:` dependencies. For faster CI:

```yaml
jobs:
  codacy-security-scan:
    # Runs independently
  
  codacy-coverage-reporter:
    # Can run in parallel with security scan
    # Remove: needs: codacy-security-scan
  
  quality-gate:
    # Still needs both to complete
    needs: [codacy-security-scan, codacy-coverage-reporter]
```

### Caching Dependencies
Add to workflow for faster Python setup:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
    cache-dependency-path: requirements-lock.txt
```

## 📝 Next Steps

1. ✅ Workflow running (monitor: https://github.com/AUo959/aurora-cloudbank-symbolic/actions)
2. ⏳ Wait for first successful run (SARIF upload + coverage report)
3. 🔒 Configure branch protection (manual web UI step)
4. 📊 Add badges to README
5. 🔧 Address quality warnings (Phase 2 refactoring)

## 🆘 Troubleshooting

### SARIF Upload Failed
- Check: Code scanning is enabled (Settings → Security → Code security and analysis)
- Verify: SARIF file generated in workflow logs
- Ensure: Using `github/codeql-action/upload-sarif@v3`

### Coverage Not Uploading
- Confirm: `coverage.xml` generated in test step
- Check: CODACY_PROJECT_TOKEN secret is set correctly
- Verify: Codacy project linked to GitHub repo

### Quality Gate Failing
- Review: Flake8 output in workflow logs
- Fix: All violations (max line length, whitespace, etc.)
- Run locally: `flake8 <files> --max-line-length=120 --statistics`

### Workflow Not Triggering
- Check: Workflow file syntax with `gh workflow view "Codacy Analysis"`
- Verify: Push to correct branches (main, develop, refactor/**)
- Confirm: No workflow is disabled

---

**Last Updated:** 2025-11-16  
**Status:** Workflow running (Run #19397785999)  
**Next Check:** Monitor https://github.com/AUo959/aurora-cloudbank-symbolic/actions/runs/19397785999
