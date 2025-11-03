#!/bin/bash
# 🚨 Emergency Codespace Backup & Sync
# Run this in ANY codespace instance to backup uncommitted work

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_BRANCH="emergency-backup-${TIMESTAMP}"

echo "🚨 EMERGENCY CODESPACE BACKUP UTILITY"
echo "======================================"

echo ""
echo "📊 Analyzing current state..."

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  UNCOMMITTED CHANGES FOUND!"
    echo ""
    echo "🔄 Creating emergency backup branch: ${BACKUP_BRANCH}"
    
    # Create backup branch
    git checkout -b "$BACKUP_BRANCH"
    git add -A
    git commit -m "🚨 Emergency backup from codespace at ${TIMESTAMP}

Auto-generated backup containing:
$(git status --porcelain | wc -l | tr -d ' ') changed files

Codespace sync operation in progress.
Review and merge manually if needed."
    
    # Push backup branch
    if git push origin "$BACKUP_BRANCH"; then
        echo "✅ Backup branch pushed successfully!"
        echo "📍 Branch: ${BACKUP_BRANCH}"
        
        # Return to main and sync
        git checkout main
        git pull origin main
        
        echo ""
        echo "✅ BACKUP COMPLETE!"
        echo "🔍 Your changes are safely stored in branch: ${BACKUP_BRANCH}"
        echo "🔧 You can now safely work with a clean main branch"
        echo ""
        echo "To restore your changes later:"
        echo "  git checkout ${BACKUP_BRANCH}"
        echo "  # Review changes"
        echo "  git checkout main"
        echo "  git merge ${BACKUP_BRANCH}  # if changes are needed"
        
    else
        echo "❌ Failed to push backup branch"
        echo "🔧 Try: git push --set-upstream origin ${BACKUP_BRANCH}"
    fi
else
    echo "✅ No uncommitted changes found"
    echo "🔄 Syncing with main..."
    git pull origin main
    echo "✅ Codespace is clean and up to date!"
fi
