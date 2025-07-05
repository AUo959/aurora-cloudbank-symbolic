#!/bin/bash

# Aurora CloudBank Branch Cleanup Script
# Systematically removes stale branches to optimize repository structure

echo "🧹 AURORA CLOUDBANK BRANCH CLEANUP"
echo "=================================="
echo ""

# Set working directory
WORKSPACE_ROOT="/workspaces/aurora-cloudbank-symbolic"
cd "$WORKSPACE_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to safely delete local branch
delete_local_branch() {
    local branch="$1"
    echo -e "${YELLOW}🗑️  Deleting local branch: $branch${NC}"
    git branch -D "$branch" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   ✅ Successfully deleted: $branch${NC}"
        return 0
    else
        echo -e "${RED}   ❌ Failed to delete: $branch${NC}"
        return 1
    fi
}

# Function to check if branch is fully merged
is_fully_merged() {
    local branch="$1"
    # Check if branch has 0 commits ahead of main
    ahead_behind=$(git for-each-ref --format='%(ahead-behind:HEAD)' "refs/heads/$branch" 2>/dev/null)
    if [[ "$ahead_behind" =~ ^0[[:space:]] ]]; then
        return 0  # Fully merged
    else
        return 1  # Has commits ahead
    fi
}

echo "📊 Analyzing branches for cleanup..."
echo ""

# Get list of local branches except main and current backup
local_branches=$(git branch --format='%(refname:short)' | grep -v '^main$' | grep -v '^backup-before-comprehensive-integration')

# Counters
deleted_count=0
skipped_count=0
failed_count=0

echo "🔍 BRANCH ANALYSIS:"
echo ""

# Categorize branches for cleanup
stale_branches=()
integration_branches=()
dependabot_branches=()
backup_branches=()
feature_branches=()

for branch in $local_branches; do
    if is_fully_merged "$branch"; then
        if [[ "$branch" =~ ^dependabot/ ]]; then
            dependabot_branches+=("$branch")
        elif [[ "$branch" =~ backup ]]; then
            backup_branches+=("$branch")
        elif [[ "$branch" =~ integration$ ]]; then
            integration_branches+=("$branch")
        elif [[ "$branch" =~ alert-autofix ]]; then
            stale_branches+=("$branch")
        elif [[ "$branch" =~ ^codex/ ]] || [[ "$branch" =~ codex- ]]; then
            feature_branches+=("$branch")
        else
            stale_branches+=("$branch")
        fi
    else
        echo -e "${BLUE}ℹ️  Keeping active branch: $branch (has commits ahead)${NC}"
        ((skipped_count++))
    fi
done

echo ""
echo "📋 CLEANUP PLAN:"
echo ""

# Show cleanup plan
echo -e "${RED}🗑️  STALE BRANCHES TO DELETE (${#stale_branches[@]}):"
for branch in "${stale_branches[@]}"; do
    echo "   - $branch"
done
echo ""

echo -e "${RED}🤖 DEPENDABOT BRANCHES TO DELETE (${#dependabot_branches[@]}):"
for branch in "${dependabot_branches[@]}"; do
    echo "   - $branch"
done
echo ""

echo -e "${RED}📦 INTEGRATION BRANCHES TO DELETE (${#integration_branches[@]}):"
for branch in "${integration_branches[@]}"; do
    echo "   - $branch"
done
echo ""

echo -e "${RED}💾 OLD BACKUP BRANCHES TO DELETE (${#backup_branches[@]}):"
for branch in "${backup_branches[@]}"; do
    echo "   - $branch"
done
echo ""

echo -e "${RED}🔧 FEATURE BRANCHES TO DELETE (${#feature_branches[@]}):"
for branch in "${feature_branches[@]}"; do
    echo "   - $branch"
done
echo ""

# Calculate totals
total_to_delete=$((${#stale_branches[@]} + ${#dependabot_branches[@]} + ${#integration_branches[@]} + ${#backup_branches[@]} + ${#feature_branches[@]}))

echo -e "${YELLOW}📊 SUMMARY:"
echo "   • Total branches to delete: $total_to_delete"
echo "   • Branches to keep: $skipped_count"
echo -e "${NC}"

# Confirmation prompt
echo "⚠️  This will permanently delete $total_to_delete local branches."
echo "Remote branches will be unaffected."
echo ""
read -p "Do you want to proceed? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting cleanup process..."
    echo ""
    
    # Delete stale branches
    if [ ${#stale_branches[@]} -gt 0 ]; then
        echo -e "${RED}🗑️  Deleting stale branches...${NC}"
        for branch in "${stale_branches[@]}"; do
            if delete_local_branch "$branch"; then
                ((deleted_count++))
            else
                ((failed_count++))
            fi
        done
        echo ""
    fi
    
    # Delete dependabot branches
    if [ ${#dependabot_branches[@]} -gt 0 ]; then
        echo -e "${RED}🤖 Deleting dependabot branches...${NC}"
        for branch in "${dependabot_branches[@]}"; do
            if delete_local_branch "$branch"; then
                ((deleted_count++))
            else
                ((failed_count++))
            fi
        done
        echo ""
    fi
    
    # Delete integration branches
    if [ ${#integration_branches[@]} -gt 0 ]; then
        echo -e "${RED}📦 Deleting integration branches...${NC}"
        for branch in "${integration_branches[@]}"; do
            if delete_local_branch "$branch"; then
                ((deleted_count++))
            else
                ((failed_count++))
            fi
        done
        echo ""
    fi
    
    # Delete old backup branches (but keep recent one)
    if [ ${#backup_branches[@]} -gt 0 ]; then
        echo -e "${RED}💾 Deleting old backup branches...${NC}"
        for branch in "${backup_branches[@]}"; do
            if delete_local_branch "$branch"; then
                ((deleted_count++))
            else
                ((failed_count++))
            fi
        done
        echo ""
    fi
    
    # Delete feature branches
    if [ ${#feature_branches[@]} -gt 0 ]; then
        echo -e "${RED}🔧 Deleting feature branches...${NC}"
        for branch in "${feature_branches[@]}"; do
            if delete_local_branch "$branch"; then
                ((deleted_count++))
            else
                ((failed_count++))
            fi
        done
        echo ""
    fi
    
    # Final summary
    echo "🎉 CLEANUP COMPLETE!"
    echo ""
    echo "📊 RESULTS:"
    echo -e "${GREEN}   ✅ Branches deleted: $deleted_count${NC}"
    echo -e "${BLUE}   ℹ️  Branches kept: $skipped_count${NC}"
    if [ $failed_count -gt 0 ]; then
        echo -e "${RED}   ❌ Failed deletions: $failed_count${NC}"
    fi
    echo ""
    
    # Show remaining branches
    echo "📋 REMAINING BRANCHES:"
    git branch
    echo ""
    
    echo "✨ Repository structure optimized!"
    echo "🚀 Ready for continued development with clean branch structure."
    
else
    echo ""
    echo "❌ Cleanup cancelled by user."
    echo "Repository remains unchanged."
fi

echo ""
echo "🔚 Branch cleanup script completed."
