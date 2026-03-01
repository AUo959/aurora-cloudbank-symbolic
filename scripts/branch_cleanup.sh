#!/bin/bash

# Aurora CloudBank Repository Branch Cleanup Script
# Systematically removes stale branches to achieve optimized structure
# Created: July 2, 2025

echo "🧹 AURORA CLOUDBANK BRANCH CLEANUP"
echo "=================================="
echo "🎯 Objective: Remove stale branches and achieve optimized repository structure"
echo ""

# Set working directory
WORKSPACE_ROOT="/workspaces/aurora-cloudbank-symbolic"
cd "$WORKSPACE_ROOT"

# Safety check - ensure we're on main
echo "📍 Ensuring we're on main branch..."
git checkout main
echo ""

# Create backup before cleanup
BACKUP_BRANCH="backup-before-cleanup-$(date +%Y%m%d-%H%M%S)"
echo "💾 Creating safety backup: $BACKUP_BRANCH"
git branch "$BACKUP_BRANCH"
echo ""

# Function to safely delete local branch
delete_local_branch() {
    local branch="$1"
    echo "   🗑️  Deleting local branch: $branch"
    if git branch -d "$branch" 2>/dev/null; then
        echo "       ✅ Successfully deleted"
    elif git branch -D "$branch" 2>/dev/null; then
        echo "       ✅ Force deleted (had unmerged changes)"
    else
        echo "       ❌ Failed to delete"
    fi
}

# Function to check if branch is stale (0 commits ahead of main)
is_stale_branch() {
    local branch="$1"
    local ahead_behind=$(git for-each-ref --format='%(ahead-behind:HEAD)' "refs/remotes/$branch" 2>/dev/null)
    local ahead=$(echo "$ahead_behind" | cut -d' ' -f1)
    [ "$ahead" = "0" ]
}

echo "🔍 PHASE 1: Analyzing branch status..."
echo ""

# Get list of all remote branches (excluding main and HEAD)
remote_branches=$(git for-each-ref --format='%(refname:short)' refs/remotes | grep -v "origin/main" | grep -v "origin/HEAD")

stale_branches=()
active_branches=()

for branch in $remote_branches; do
    if is_stale_branch "$branch"; then
        stale_branches+=("$branch")
    else
        active_branches+=("$branch")
    fi
done

echo "📊 Branch Analysis Results:"
echo "   🟢 Active branches (have commits ahead): ${#active_branches[@]}"
echo "   🔴 Stale branches (0 commits ahead): ${#stale_branches[@]}"
echo ""

if [ ${#active_branches[@]} -gt 0 ]; then
    echo "🟢 Active branches to keep:"
    for branch in "${active_branches[@]}"; do
        ahead_behind=$(git for-each-ref --format='%(ahead-behind:HEAD)' "refs/remotes/$branch")
        echo "   - $branch ($ahead_behind)"
    done
    echo ""
fi

echo "🔴 Stale branches to clean up:"
echo ""

# Categorize stale branches
echo "📂 DEPENDABOT BRANCHES (outdated dependency updates):"
for branch in "${stale_branches[@]}"; do
    if [[ $branch == *"dependabot"* ]]; then
        echo "   - $branch"
    fi
done
echo ""

echo "📂 CODEX DEVELOPMENT BRANCHES (completed features):"
for branch in "${stale_branches[@]}"; do
    if [[ $branch == *"codex"* ]]; then
        echo "   - $branch"
    fi
done
echo ""

echo "📂 ALERT-AUTOFIX BRANCHES (security fixes applied):"
for branch in "${stale_branches[@]}"; do
    if [[ $branch == *"alert-autofix"* ]]; then
        echo "   - $branch"
    fi
done
echo ""

echo "📂 INTEGRATION BRANCHES (already merged):"
for branch in "${stale_branches[@]}"; do
    if [[ $branch == *"integration"* ]] || [[ $branch == *"graphics-card"* ]]; then
        echo "   - $branch"
    fi
done
echo ""

echo "📂 OTHER STALE BRANCHES:"
for branch in "${stale_branches[@]}"; do
    if [[ $branch != *"dependabot"* ]] && [[ $branch != *"codex"* ]] && [[ $branch != *"alert-autofix"* ]] && [[ $branch != *"integration"* ]] && [[ $branch != *"graphics-card"* ]]; then
        echo "   - $branch"
    fi
done
echo ""

echo "⚠️  WARNING: This will delete ${#stale_branches[@]} stale branches."
echo "💾 Backup created as: $BACKUP_BRANCH"
echo ""

read -p "🤔 Do you want to proceed with cleanup? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "❌ Cleanup cancelled by user"
    exit 0
fi

echo ""
echo "🗑️  PHASE 2: Cleaning up local branches..."
echo ""

# Clean up local branches that correspond to stale remotes
local_branches=$(git branch | grep -v "main" | grep -v "backup-" | sed 's/^[* ] //')

for local_branch in $local_branches; do
    # Check if corresponding remote is stale
    remote_equivalent="origin/$local_branch"
    if [[ " ${stale_branches[@]} " =~ " $remote_equivalent " ]]; then
        delete_local_branch "$local_branch"
    fi
done

echo ""
echo "📊 PHASE 3: Repository optimization summary..."
echo ""

# Show final branch count
remaining_local=$(git branch | grep -v "main" | grep -v "backup-" | wc -l)
remaining_remote=$(git branch -r | grep -v "origin/main" | grep -v "origin/HEAD" | wc -l)

echo "✅ Cleanup completed!"
echo ""
echo "📈 Optimization Results:"
echo "   🏠 Local branches remaining: $remaining_local (+ backups)"
echo "   🌐 Remote branches: $remaining_remote (cleanup pending remote)"
echo ""

echo "🎯 RECOMMENDATIONS:"
echo ""
echo "1. 🚀 To delete remote branches (after verification):"
echo "   Run: git push origin --delete <branch-name>"
echo ""
echo "2. 🔄 To sync and prune tracking references:"
echo "   Run: git remote prune origin"
echo ""
echo "3. 📊 To verify cleanup:"
echo "   Run: python3 scripts/gitwiz.py branch list"
echo ""

echo "💾 Remember: Backup branch '$BACKUP_BRANCH' contains the state before cleanup"
echo ""
echo "🎉 Repository structure optimization complete!"
