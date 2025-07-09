#!/bin/bash
# Aurora CloudBank - Stale Branch Cleanup Script
# Safely removes merged and outdated remote branches

echo "🧹 AURORA CLOUDBANK BRANCH CLEANUP"
echo "=================================="
echo "📅 Date: $(date)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_BRANCHES=0
CLEANED_BRANCHES=0
KEPT_BRANCHES=0

echo "🔍 Analyzing remote branches..."
echo ""

# Get all remote branches (excluding HEAD and main)
REMOTE_BRANCHES=$(git branch -r | grep -v 'HEAD\|main' | sed 's/origin\///' | tr -d ' ')

# Categories for cleanup
MERGED_BRANCHES=()
DEPENDABOT_OLD=()
CODEX_COMPLETED=()
PATCH_BRANCHES=()
KEEP_BRANCHES=()

echo "📊 Categorizing branches..."

for branch in $REMOTE_BRANCHES; do
    TOTAL_BRANCHES=$((TOTAL_BRANCHES + 1))

    # Check if branch is merged
    if git branch -r --merged main | grep -q "origin/$branch"; then
        # Get last commit date
        LAST_COMMIT=$(git log --format="%ci" origin/$branch -1 2>/dev/null | head -1)
        COMMIT_DATE=$(date -d "$LAST_COMMIT" +%s 2>/dev/null)
        CUTOFF_DATE=$(date -d "2025-07-02" +%s) # Keep recent branches

        if [[ $COMMIT_DATE -lt $CUTOFF_DATE ]]; then
            # Categorize old merged branches
            case $branch in
                dependabot/npm_and_yarn/eslint-9.30.1|dependabot/npm_and_yarn/markdownlint-cli-0.45.0|dependabot/npm_and_yarn/dotenv-17.1.0|dependabot/pip/pandas-2.3.1)
                    # Keep latest dependabot branches
                    KEEP_BRANCHES+=($branch)
                    ;;
                dependabot/*)
                    DEPENDABOT_OLD+=($branch)
                    ;;
                codex/*)
                    CODEX_COMPLETED+=($branch)
                    ;;
                *codex/*)
                    CODEX_COMPLETED+=($branch)
                    ;;
                AUo959-patch-*|alert-autofix-*)
                    PATCH_BRANCHES+=($branch)
                    ;;
                backup-before-pr-merge-*)
                    PATCH_BRANCHES+=($branch)
                    ;;
                *integration)
                    # Keep integration branches for now
                    KEEP_BRANCHES+=($branch)
                    ;;
                *)
                    # Other old merged branches
                    MERGED_BRANCHES+=($branch)
                    ;;
            esac
        else
            KEEP_BRANCHES+=($branch)
        fi
    else
        KEEP_BRANCHES+=($branch)
    fi
done

echo ""
echo "📋 CLEANUP PLAN:"
echo "==============="

if [ ${#DEPENDABOT_OLD[@]} -gt 0 ]; then
    echo -e "${YELLOW}🤖 Outdated Dependabot branches (${#DEPENDABOT_OLD[@]})${NC}"
    for branch in "${DEPENDABOT_OLD[@]}"; do
        echo "  • $branch"
    done
    echo ""
fi

if [ ${#CODEX_COMPLETED[@]} -gt 0 ]; then
    echo -e "${BLUE}🔧 Completed Codex branches (${#CODEX_COMPLETED[@]})${NC}"
    for branch in "${CODEX_COMPLETED[@]}"; do
        echo "  • $branch"
    done
    echo ""
fi

if [ ${#PATCH_BRANCHES[@]} -gt 0 ]; then
    echo -e "${YELLOW}🔄 Old patch/autofix branches (${#PATCH_BRANCHES[@]})${NC}"
    for branch in "${PATCH_BRANCHES[@]}"; do
        echo "  • $branch"
    done
    echo ""
fi

if [ ${#MERGED_BRANCHES[@]} -gt 0 ]; then
    echo -e "${YELLOW}✅ Other old merged branches (${#MERGED_BRANCHES[@]})${NC}"
    for branch in "${MERGED_BRANCHES[@]}"; do
        echo "  • $branch"
    done
    echo ""
fi

if [ ${#KEEP_BRANCHES[@]} -gt 0 ]; then
    echo -e "${GREEN}🛡️  Keeping recent/active branches (${#KEEP_BRANCHES[@]})${NC}"
    for branch in "${KEEP_BRANCHES[@]}"; do
        echo "  • $branch"
    done
    echo ""
fi

TOTAL_TO_DELETE=$((${#DEPENDABOT_OLD[@]} + ${#CODEX_COMPLETED[@]} + ${#PATCH_BRANCHES[@]} + ${#MERGED_BRANCHES[@]}))

echo "📊 SUMMARY:"
echo "==========="
echo "• Total branches: $TOTAL_BRANCHES"
echo "• To delete: $TOTAL_TO_DELETE"
echo "• To keep: ${#KEEP_BRANCHES[@]}"
echo ""

if [ $TOTAL_TO_DELETE -eq 0 ]; then
    echo "✅ No branches need cleanup!"
    exit 0
fi

# Ask for confirmation
read -p "🤔 Proceed with cleanup? This will delete $TOTAL_TO_DELETE remote branches. (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled."
    exit 0
fi

echo ""
echo "🧹 Starting cleanup..."
echo "===================="

# Function to delete branch safely
delete_branch() {
    local branch=$1
    echo -n "🗑️  Deleting $branch... "

    if git push origin --delete "$branch" >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        CLEANED_BRANCHES=$((CLEANED_BRANCHES + 1))
    else
        echo -e "${RED}❌ Failed${NC}"
    fi
}

# Delete branches by category
for branch in "${DEPENDABOT_OLD[@]}"; do
    delete_branch "$branch"
done

for branch in "${CODEX_COMPLETED[@]}"; do
    delete_branch "$branch"
done

for branch in "${PATCH_BRANCHES[@]}"; do
    delete_branch "$branch"
done

for branch in "${MERGED_BRANCHES[@]}"; do
    delete_branch "$branch"
done

echo ""
echo "🎉 CLEANUP COMPLETE!"
echo "==================="
echo "• Deleted: $CLEANED_BRANCHES branches"
echo "• Failed: $((TOTAL_TO_DELETE - CLEANED_BRANCHES)) branches"
echo "• Kept: ${#KEEP_BRANCHES[@]} branches"
echo ""

# Clean up local tracking branches
echo "🧹 Cleaning up local tracking references..."
git remote prune origin

echo ""
echo "✅ Branch cleanup completed successfully!"
echo "🔍 Remaining remote branches:"
git branch -r | grep -v HEAD | wc -l | xargs echo "• Total:"
