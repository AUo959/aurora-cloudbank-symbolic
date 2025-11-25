#!/usr/bin/env bash
# Batch Rebase Script for Phase 1 PRs
# Generated: 2025-11-25
# Purpose: Rebase 8 PRs from integration plan Phase 1

set -e  # Exit on error

# Phase 1 PR numbers (from integration plan #932)
PRS=(413 424 426 423 412 414 419 421)

echo "🔄 Phase 1: Batch Rebase & Conflict Resolution"
echo "================================================"
echo "PRs to rebase: ${PRS[@]}"
echo ""

# Function to rebase a single PR
rebase_pr() {
    local pr_number=$1
    echo "📌 Processing PR #$pr_number..."
    
    # Fetch PR branch
    gh pr checkout "$pr_number"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to checkout PR #$pr_number"
        return 1
    fi
    
    # Get branch name
    local branch_name=$(git branch --show-current)
    echo "   Branch: $branch_name"
    
    # Fetch latest main
    git fetch origin main
    
    # Attempt rebase
    echo "   Rebasing onto origin/main..."
    if git rebase origin/main; then
        echo "   ✅ Rebase successful!"
        
        # Force push (rebase changes history)
        echo "   Pushing rebased branch..."
        git push --force-with-lease origin "$branch_name"
        
        if [ $? -eq 0 ]; then
            echo "   ✅ PR #$pr_number rebased and pushed"
            return 0
        else
            echo "   ❌ Failed to push PR #$pr_number"
            git rebase --abort
            return 1
        fi
    else
        echo "   ⚠️  Rebase has conflicts - needs manual resolution"
        echo "   Aborting rebase for now..."
        git rebase --abort
        return 2  # Special code for conflicts
    fi
}

# Track results
SUCCESSFUL=()
FAILED=()
CONFLICTS=()

# Return to main before starting
git checkout main
git pull origin main

# Process each PR
for pr in "${PRS[@]}"; do
    echo ""
    rebase_pr "$pr"
    result=$?
    
    if [ $result -eq 0 ]; then
        SUCCESSFUL+=("$pr")
    elif [ $result -eq 2 ]; then
        CONFLICTS+=("$pr")
    else
        FAILED+=("$pr")
    fi
    
    # Return to main for next iteration
    git checkout main
done

# Summary
echo ""
echo "========================================"
echo "📊 Phase 1 Rebase Summary"
echo "========================================"
echo "✅ Successful: ${#SUCCESSFUL[@]} PRs"
[ ${#SUCCESSFUL[@]} -gt 0 ] && echo "   ${SUCCESSFUL[@]}"

echo "⚠️  Conflicts: ${#CONFLICTS[@]} PRs (need manual resolution)"
[ ${#CONFLICTS[@]} -gt 0 ] && echo "   ${CONFLICTS[@]}"

echo "❌ Failed: ${#FAILED[@]} PRs"
[ ${#FAILED[@]} -gt 0 ] && echo "   ${FAILED[@]}"

echo ""
if [ ${#CONFLICTS[@]} -gt 0 ]; then
    echo "⚠️  Next Step: Manually resolve conflicts for PRs: ${CONFLICTS[@]}"
    exit 1
elif [ ${#FAILED[@]} -gt 0 ]; then
    echo "❌ Some PRs failed to process - investigate errors above"
    exit 1
else
    echo "✅ Phase 1 complete! All PRs successfully rebased."
    echo "📋 Checkpoint: Test each rebased PR locally before merging"
    exit 0
fi
