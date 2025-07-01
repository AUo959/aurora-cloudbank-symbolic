#!/bin/bash
# Merge Dependabot Security Updates
# Automatically merges Dependabot pull requests that update dependencies

set -e

echo "🔐 Merging Dependabot Security Updates"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    case $status in
        "success") echo -e "${GREEN}✅ $message${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "error") echo -e "${RED}❌ $message${NC}" ;;
        *) echo "$message" ;;
    esac
}

# Ensure we're on main and up to date
print_status "info" "Ensuring main branch is current..."
git checkout main
git pull origin main

# List of dependabot branches that are ahead of main
dependabot_branches=(
    "dependabot/pip/httpx-0.28.1"
    "dependabot/pip/pytest-8.4.1"
    "dependabot/pip/uvicorn-0.34.3"
)

echo ""
echo "📦 Dependencies to Update:"
echo "========================="

for branch in "${dependabot_branches[@]}"; do
    echo "  🔸 $branch"
done

echo ""
read -p "Proceed with merging these security updates? (y/N): " confirm

if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    print_status "warning" "Merge cancelled by user"
    exit 0
fi

echo ""
echo "🚀 Merging Security Updates..."
echo "=============================="

for branch in "${dependabot_branches[@]}"; do
    echo ""
    print_status "info" "Processing: $branch"

    # Check if branch exists
    if git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
        # Create a temporary branch for testing
        temp_branch="temp-merge-$(echo $branch | sed 's/\//-/g')"
        git checkout -b "$temp_branch" main

        # Attempt to merge
        if git merge "origin/$branch" --no-edit; then
            print_status "success" "Successfully merged $branch"

            # Switch back to main and merge the temp branch
            git checkout main
            git merge "$temp_branch" --no-edit

            # Clean up temp branch
            git branch -d "$temp_branch"

            print_status "success" "✨ $branch merged into main"
        else
            print_status "error" "Merge conflict in $branch - manual resolution required"
            git merge --abort
            git checkout main
            git branch -d "$temp_branch" 2>/dev/null || true
            echo "  👉 Please resolve conflicts manually for: $branch"
        fi
    else
        print_status "warning" "Branch $branch not found"
    fi
done

echo ""
echo "📊 Final Status:"
echo "==============="

# Check if we have changes to push
if [ "$(git rev-list --count origin/main..main)" -gt 0 ]; then
    print_status "success" "Ready to push $(git rev-list --count origin/main..main) new commits"
    echo ""
    read -p "Push changes to remote? (y/N): " push_confirm

    if [[ $push_confirm == [yY] || $push_confirm == [yY][eE][sS] ]]; then
        git push origin main
        print_status "success" "🎉 Security updates successfully pushed to main!"
    else
        print_status "warning" "Changes staged locally but not pushed"
    fi
else
    print_status "info" "No changes to push"
fi

echo ""
print_status "success" "Dependabot merge process complete!"
