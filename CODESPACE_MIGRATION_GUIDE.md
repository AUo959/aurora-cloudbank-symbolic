# 🚨 Aurora CloudBank - Codespace Migration & Cleanup Strategy

**Date:** July 30, 2025
**Purpose:** Handle old codespaces with large uncommitted changes and different dev containers
**Status:** Comprehensive Migration Guide

## 🎯 Executive Summary

When managing multiple codespaces with different dev container configurations and uncommitted changes, Aurora CloudBank provides a systematic approach to safely migrate, backup, and consolidate your work.

## 🔍 Pre-Migration Assessment

### 1. **Inventory Your Codespaces**

Run this assessment in each codespace:

```bash
# Check current state
echo "=== CODESPACE ASSESSMENT ==="
echo "Codespace: $(hostname)"
echo "Repository: $(git remote get-url origin)"
echo "Branch: $(git branch --show-current)"
echo "Last Commit: $(git log -1 --oneline)"
echo "Uncommitted: $(git status --porcelain | wc -l) files"
echo "Container: $(cat .devcontainer/devcontainer.json | grep '"name"' || echo 'Custom config')"
echo "Node: $(node --version)"
echo "Python: $(python3 --version)"
```

### 2. **Categorize Your Codespaces**

- **Primary Codespace** - Your main development environment
- **Experimental Codespaces** - Feature branches, testing environments  
- **Legacy Codespaces** - Old configurations, outdated containers
- **Backup Codespaces** - Emergency or sync codespaces

## 🛡️ Safe Migration Strategy

### Phase 1: Emergency Backup (Critical First Step)

**For each codespace with uncommitted changes:**

```bash
# Run Aurora's emergency backup script
./emergency_backup.sh
```

This automatically:
- Creates timestamped backup branch
- Commits all uncommitted changes  
- Pushes backup to remote repository
- Provides rollback instructions

**Manual backup alternative:**

```bash
# Create emergency backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_BRANCH="codespace-backup-${TIMESTAMP}"

git checkout -b "$BACKUP_BRANCH"
git add -A
git commit -m "🚨 Codespace backup - $(hostname) - ${TIMESTAMP}"
git push origin "$BACKUP_BRANCH"
```

### Phase 2: Container Assessment & Standardization

**Check dev container differences:**

```bash
# Compare container configurations
echo "=== CONTAINER ANALYSIS ==="
if [ -f .devcontainer/devcontainer.json ]; then
    echo "Using .devcontainer/devcontainer.json:"
    cat .devcontainer/devcontainer.json | grep -E '"name"|"image"|"dockerfile"'
fi

if [ -f devcontainer.json ]; then
    echo "Using root devcontainer.json:"
    cat devcontainer.json | grep -E '"name"|"image"|"dockerfile"'
fi

# Check for conflicts
./fix_devcontainer_conflicts.sh
```

**Aurora's container standardization options:**

1. **Performance Optimized** (Recommended)
   ```bash
   # Use Aurora's optimized container
   cp .devcontainer/devcontainer.json.backup .devcontainer/devcontainer.json.old
   # Apply performance fixes
   ./fix_devcontainer_conflicts.sh
   ```

2. **Minimal Container**
   ```bash
   # Switch to minimal configuration
   mv .devcontainer .devcontainer.backup
   # Uses root devcontainer.json
   ```

### Phase 3: Dependency & Environment Sync

**Standardize development environment:**

```bash
# Sync codespace helper
./codespace_sync_helper.sh

# Install missing dependencies
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt
fi

if [ -f package.json ]; then
    npm install
fi

# Verify environment
python3 --version
node --version
git --version
```

### Phase 4: Work Consolidation

**Strategy A: Merge All Changes to Main**

```bash
# In primary codespace
git checkout main
git pull origin main

# Merge each backup branch
for branch in $(git branch -r | grep "codespace-backup"); do
    echo "Reviewing: $branch"
    git checkout ${branch#origin/}
    git log --oneline -10
    read -p "Merge this branch? (y/n): " merge_choice
    
    if [[ "$merge_choice" == "y" ]]; then
        git checkout main
        git merge ${branch#origin/} --no-ff -m "Merge codespace work from $branch"
    fi
done
```

**Strategy B: Cherry-Pick Important Changes**

```bash
# Review and cherry-pick specific commits
git log --graph --oneline --all
git cherry-pick <commit-hash>
```

## 🔧 Container Migration Workflows

### For Different Dev Container Types

**1. Legacy Custom Dockerfile → Modern Base Image**

```bash
# Backup current container
cp .devcontainer/devcontainer.json .devcontainer/legacy-backup.json

# Switch to modern base
cat > .devcontainer/devcontainer.json << 'EOF'
{
  "name": "Aurora CloudBank Modern",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:20",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {"version": "3.11"}
  }
}
EOF

# Rebuild container
# Ctrl+Shift+P → "Dev Containers: Rebuild Container"
```

**2. Heavy Extensions → Performance Optimized**

```bash
# Apply Aurora's performance optimizations
./diagnostics_summary.sh
./optimize_performance.sh

# Rebuild with optimized settings
# Memory usage: 8GB → 3GB
# CPU usage: 60% → 30%
```

**3. Different Python/Node Versions**

```bash
# Standardize to Aurora's preferred versions
# Node.js 20 LTS + Python 3.11
./fix_devcontainer_conflicts.sh
```

## 🔄 Large Uncommitted Changes Management

### For Massive Changesets (100+ files)

**1. Categorize Changes**

```bash
# Analyze change types
git status --porcelain | cut -c1-2 | sort | uniq -c
git diff --stat
git diff --name-only | head -20
```

**2. Stage Changes Selectively**

```bash
# Use Aurora's smart staging
git add -p  # Interactive staging
git add *.py  # Stage by file type
git add src/  # Stage by directory
```

**3. Create Logical Commits**

```bash
# Multiple focused commits instead of one massive commit
git commit -m "feat: Add symbolic processing engine"
git add docs/
git commit -m "docs: Update API documentation"
git add tests/
git commit -m "test: Add comprehensive test suite"
```

### For Complex Merge Conflicts

**Aurora's conflict resolution:**

```bash
# Use Aurora's merge tools
./scripts/aurora_enhanced_cleanup_command.sh
./scripts/aurora_validation_manager.py --resolve-conflicts
```

## 🧹 Cleanup & Optimization

### After Migration

**1. Clean Up Old Codespaces**

```bash
# In each old codespace, verify backup succeeded
git ls-remote --heads origin | grep "codespace-backup"

# If backups confirmed, delete old codespace
# (GitHub Codespaces → Delete codespace)
```

**2. Optimize Repository**

```bash
# Clean up backup branches (after verification)
git branch -r | grep "codespace-backup" | head -5  # Review first
# Delete old backups if no longer needed
git push origin --delete codespace-backup-old-timestamp
```

**3. Standardize Primary Codespace**

```bash
# Apply all Aurora optimizations
./scripts/aurora_optimal_workflow.sh
./verify_reload_readiness.sh
```

## 🚨 Emergency Procedures

### If Codespace Won't Start

```bash
# Emergency sync commands
git stash push -m "Emergency stash before codespace issues"
git push origin main --force-with-lease
```

### If Container Build Fails

```bash
# Fallback to minimal container
mv .devcontainer .devcontainer.broken
echo '{"image": "node:20"}' > devcontainer.json
# Rebuild container
```

### If Large Changes Lost

```bash
# Check reflog for lost commits
git reflog --all
git fsck --lost-found
# Restore from backup branches
git branch -r | grep backup
```

## 📊 Success Metrics

After migration, verify:

- ✅ **All important work preserved** in main branch or backup branches
- ✅ **Consistent dev container** across all active codespaces  
- ✅ **Performance optimized** (memory usage < 4GB)
- ✅ **Dependencies synchronized** (same Node/Python versions)
- ✅ **Clean git history** with logical commit messages
- ✅ **Backup branches** available for rollback if needed

## 🎯 Aurora-Specific Benefits

**Symbolic Continuity:** All migrations maintain T1/SRB anchor integrity
**DLP Tracking:** Full audit trail of all file movements and changes
**Memory Sealing:** Cryptographic verification of important state transitions
**Ethics Protocol:** Picard_Delta_3 compliance throughout migration process

## 🔗 Related Aurora Tools

- `emergency_backup.sh` - Automated backup creation
- `codespace_sync_helper.sh` - Multi-codespace coordination
- `fix_devcontainer_conflicts.sh` - Container standardization
- `aurora_optimal_workflow.sh` - Post-migration optimization
- `scripts/orion_backup_sync.py` - Advanced backup management

---

**Remember:** Aurora CloudBank's philosophy is "backup first, optimize second." Always ensure your work is safely preserved before making container or environment changes.
