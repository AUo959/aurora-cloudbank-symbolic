#!/bin/bash
# Pull Request Management Script for Aurora CloudBank
# Helps review and merge pending pull requests

set -e

echo "🔄 Aurora CloudBank - Pull Request Management"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    local status=$1
    local message=$2
    case $status in
        "success") echo -e "${GREEN}✅ $message${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "error") echo -e "${RED}❌ $message${NC}" ;;
        "info") echo -e "${BLUE}ℹ️  $message${NC}" ;;
        *) echo "$message" ;;
    esac
}

# Fetch latest changes
print_status "info" "Fetching latest changes from remote..."
git fetch origin

echo ""
echo "📋 Current Remote Branches (Potential PRs):"
echo "==========================================="

# List remote branches that aren't main
git branch -r | grep -v "origin/main" | grep -v "origin/HEAD" | while read branch; do
    branch_name=$(echo $branch | sed 's/origin\///')
    echo "  📍 $branch_name"

    # Check if branch has commits ahead of main
    ahead_count=$(git rev-list --count main..$branch 2>/dev/null || echo "0")
    behind_count=$(git rev-list --count $branch..main 2>/dev/null || echo "0")

    if [ "$ahead_count" -gt 0 ]; then
        echo "    📈 $ahead_count commits ahead of main"
    fi
    if [ "$behind_count" -gt 0 ]; then
        echo "    📉 $behind_count commits behind main"
    fi

    # Show latest commit
    latest_commit=$(git log --oneline -1 $branch 2>/dev/null | head -1)
    if [ -n "$latest_commit" ]; then
        echo "    🎯 Latest: $latest_commit"
    fi
    echo ""
done

echo ""
echo "🔍 Analysis Summary:"
echo "==================="

# Count different types of branches
dependabot_count=$(git branch -r | grep -c "dependabot" || echo "0")
codex_count=$(git branch -r | grep -c "codex" || echo "0")
other_count=$(git branch -r | grep -v "origin/main" | grep -v "origin/HEAD" | grep -v "dependabot" | grep -v "codex" | wc -l)

print_status "info" "Dependabot branches (security updates): $dependabot_count"
print_status "info" "Codex branches (feature development): $codex_count"
print_status "info" "Other branches: $other_count"

echo ""
echo "🎯 Recommendations:"
echo "=================="

if [ "$dependabot_count" -gt 0 ]; then
    print_status "warning" "Security updates available - should be reviewed and merged"
fi

if [ "$codex_count" -gt 0 ]; then
    print_status "info" "Feature branches available - review for integration"
fi

echo ""
echo "⚡ Quick Actions Available:"
echo "=========================="
echo "1. Review specific branch: git checkout origin/<branch-name>"
echo "2. Merge dependabot updates: ./scripts/merge-dependabot.sh"
echo "3. Create feature branch merge: ./scripts/merge-feature.sh <branch-name>"
echo "4. Clean up merged branches: git remote prune origin"
echo ""

print_status "success" "Pull request analysis complete!"
echo "Use the suggestions above or let me know which branches you'd like to merge."
