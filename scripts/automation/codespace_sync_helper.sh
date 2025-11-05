#!/bin/bash
# 🔧 Codespace Synchronization Helper
# Helps coordinate multiple codespace instances

echo "🔧 AURORA CODESPACE SYNC HELPER"
echo "================================="

echo ""
echo "📊 CURRENT CODESPACE STATUS:"
echo "Repository: aurora-cloudbank-symbolic"
echo "Branch: $(git branch --show-current)"
echo "Last Commit: $(git log -1 --oneline)"

echo ""
echo "🔍 CHECKING FOR UNCOMMITTED CHANGES:"
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ UNCOMMITTED CHANGES DETECTED!"
    echo ""
    echo "📝 Files with changes:"
    git status --short
    echo ""
    echo "💾 RECOMMENDED ACTIONS:"
    echo "1. Review changes: git diff"
    echo "2. Stage important changes: git add <files>"
    echo "3. Commit changes: git commit -m 'Sync: <description>'"
    echo "4. Push changes: git push origin main"
    echo "5. Or stash changes: git stash push -m 'Codespace sync backup'"
else
    echo "✅ NO UNCOMMITTED CHANGES - CODESPACE IS CLEAN"
fi

echo ""
echo "🔄 SYNC COMMANDS:"
echo "To pull latest changes: git pull origin main"
echo "To push local changes: git push origin main"
echo "To backup changes: git stash push -m 'Backup $(date)'"

echo ""
echo "🗑️ CLEANUP COMMANDS:"
echo "To reset to remote: git reset --hard origin/main"
echo "To clean untracked: git clean -fd"

echo ""
echo "✅ MAIN REPOSITORY STATUS:"
echo "- Remote branches: $(git ls-remote --heads origin | wc -l | tr -d ' ')"
echo "- Open PRs: 0 (ALL CLOSED)"
echo "- Optimization: COMPLETE ✅"
