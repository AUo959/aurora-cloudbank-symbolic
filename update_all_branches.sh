#!/bin/bash

# Aurora CloudBank - Branch Update Script
# Updates all remote feature branches with latest main branch changes

set -e  # Exit on any error

echo "🔄 Aurora CloudBank Branch Update Utility"
echo "========================================="

# Ensure we're in the right directory
cd /workspaces/aurora-cloudbank-symbolic

# Fetch latest from all remotes
echo "📡 Fetching latest changes from all remotes..."
git fetch --all --prune

# Ensure main is up to date
echo "🔄 Updating main branch..."
git checkout main
git pull origin main

# Get list of all remote branches (excluding main and HEAD)
echo "📋 Collecting remote branches to update..."
remote_branches=$(git branch -r | grep -v 'HEAD\|main$' | sed 's/origin\///' | sort -u)

# Count total branches
total_branches=$(echo "$remote_branches" | wc -l)
current=0

echo "📊 Found $total_branches remote branches to update"
echo ""

# Track success/failure
success_count=0
failure_count=0
failed_branches=()

# Update each branch
for branch in $remote_branches; do
    current=$((current + 1))
    echo "[$current/$total_branches] Processing branch: $branch"
    
    # Skip if branch doesn't exist remotely anymore
    if ! git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
        echo "  ⚠️  Remote branch origin/$branch not found, skipping..."
        continue
    fi
    
    # Create/checkout local tracking branch
    if git show-ref --verify --quiet "refs/heads/$branch"; then
        echo "  🔄 Checking out existing local branch: $branch"
        git checkout "$branch"
        git pull origin "$branch" || {
            echo "  ⚠️  Failed to pull $branch, trying to reset..."
            git reset --hard "origin/$branch"
        }
    else
        echo "  🆕 Creating new local tracking branch: $branch"
        git checkout -b "$branch" "origin/$branch"
    fi
    
    # Check if branch is behind main
    commits_behind=$(git rev-list --count "HEAD..main")
    if [ "$commits_behind" -eq 0 ]; then
        echo "  ✅ Branch $branch is already up to date with main"
        success_count=$((success_count + 1))
        continue
    fi
    
    echo "  📈 Branch $branch is $commits_behind commits behind main"
    
    # Attempt to merge main into the branch
    echo "  🔀 Merging main into $branch..."
    if git merge main --no-edit; then
        echo "  ✅ Successfully merged main into $branch"
        
        # Push the updated branch
        echo "  📤 Pushing updated $branch to remote..."
        if git push origin "$branch"; then
            echo "  ✅ Successfully pushed $branch"
            success_count=$((success_count + 1))
        else
            echo "  ❌ Failed to push $branch"
            failure_count=$((failure_count + 1))
            failed_branches+=("$branch (push failed)")
        fi
    else
        echo "  ❌ Merge conflict detected in $branch"
        echo "  🔄 Aborting merge and skipping this branch..."
        git merge --abort
        failure_count=$((failure_count + 1))
        failed_branches+=("$branch (merge conflict)")
    fi
    
    echo ""
done

# Return to main branch
echo "🔄 Returning to main branch..."
git checkout main

# Summary
echo ""
echo "📊 BRANCH UPDATE SUMMARY"
echo "========================"
echo "✅ Successfully updated: $success_count branches"
echo "❌ Failed to update: $failure_count branches"

if [ $failure_count -gt 0 ]; then
    echo ""
    echo "❌ Failed branches:"
    for failed_branch in "${failed_branches[@]}"; do
        echo "  - $failed_branch"
    done
    echo ""
    echo "💡 Failed branches may require manual intervention due to:"
    echo "   - Merge conflicts"
    echo "   - Protected branch policies"
    echo "   - Permission issues"
fi

echo ""
echo "🎯 Branch update process complete!"
echo "📝 All successfully updated branches now include the latest security fixes from main."

exit 0
