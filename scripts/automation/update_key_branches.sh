#!/bin/bash

# Simple branch update script for key Aurora branches
echo "Updating key Aurora branches with main..."

cd /workspaces/aurora-cloudbank-symbolic

# List of important branches to update
key_branches=(
    "codex/address-security,-privacy,-and-enhancement-issues"
    "codex/perform-repository-health-check"
    "dependabot/pip/uvicorn-0.35.0"
    "codex/design-and-implement-aurora-interlink-fabric"
    "codex/fix-dev-container-and-dockerfile-issues"
)

# Ensure main is current
git checkout main
git pull origin main

echo "Main branch updated. Latest commit:"
git log --oneline -1

echo ""
echo "Updating key branches..."

for branch in "${key_branches[@]}"; do
    echo "Processing: $branch"
    
    # Create safe local branch name
    local_branch=$(echo "$branch" | sed 's/[^a-zA-Z0-9]/-/g')
    
    # Check if remote branch exists
    if git ls-remote --heads origin "$branch" | grep -q "$branch"; then
        # Create or update local branch
        if git show-ref --verify --quiet "refs/heads/$local_branch"; then
            git branch -D "$local_branch"
        fi
        
        git checkout -b "$local_branch" "origin/$branch"
        
        # Check if merge is needed
        commits_behind=$(git rev-list --count "HEAD..main")
        if [ "$commits_behind" -eq 0 ]; then
            echo "  ✅ $branch is up to date"
        else
            echo "  🔄 $branch is $commits_behind commits behind, merging..."
            git merge main --no-edit
            echo "  ✅ Merged main into $branch"
        fi
    else
        echo "  ⚠️  Remote branch $branch not found"
    fi
    echo ""
done

# Return to main
git checkout main
echo "Branch update process completed!"
