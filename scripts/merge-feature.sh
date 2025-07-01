#!/bin/bash
# Merge Feature Branches
# Helps review and merge feature branches with proper validation

set -e

echo "🚀 Aurora Feature Branch Merger"
echo "==============================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Function to display branch info
show_branch_info() {
    local branch=$1
    echo ""
    print_status "info" "Branch: $branch"
    echo "────────────────────────────────────────"

    # Show commits
    echo "📝 Recent commits:"
    git log --oneline -5 "origin/$branch" | sed 's/^/    /'

    # Show file changes
    echo ""
    echo "📁 Files changed:"
    git diff --name-only main "origin/$branch" | head -10 | sed 's/^/    /'

    local total_files=$(git diff --name-only main "origin/$branch" | wc -l)
    if [ "$total_files" -gt 10 ]; then
        echo "    ... and $((total_files - 10)) more files"
    fi

    echo ""
}

# If branch name provided as argument
if [ $# -eq 1 ]; then
    BRANCH_NAME="$1"

    # Validate branch exists
    if ! git show-ref --verify --quiet "refs/remotes/origin/$BRANCH_NAME"; then
        print_status "error" "Branch '$BRANCH_NAME' not found"
        exit 1
    fi

    show_branch_info "$BRANCH_NAME"

    echo "🎯 Actions available:"
    echo "1. 🔍 Review changes (git diff main origin/$BRANCH_NAME)"
    echo "2. ✅ Merge branch"
    echo "3. 🧪 Test merge (create test branch)"
    echo "4. ❌ Skip this branch"
    echo ""

    read -p "Choose action (1-4): " action

    case $action in
        1)
            echo ""
            print_status "info" "Showing diff for $BRANCH_NAME..."
            git diff --stat main "origin/$BRANCH_NAME"
            echo ""
            read -p "Press Enter to continue..."
            ;;
        2)
            echo ""
            print_status "info" "Merging $BRANCH_NAME..."

            # Ensure we're on main
            git checkout main
            git pull origin main

            # Create merge commit
            if git merge "origin/$BRANCH_NAME" --no-edit; then
                print_status "success" "Successfully merged $BRANCH_NAME"

                # Run validation
                if [ -f "scripts/validate-cicd.sh" ]; then
                    print_status "info" "Running CI/CD validation..."
                    ./scripts/validate-cicd.sh
                fi

                echo ""
                read -p "Push to remote? (y/N): " push_confirm
                if [[ $push_confirm == [yY] || $push_confirm == [yY][eE][sS] ]]; then
                    git push origin main
                    print_status "success" "🎉 Branch merged and pushed!"
                fi
            else
                print_status "error" "Merge conflict detected!"
                echo "Please resolve conflicts manually or abort with: git merge --abort"
            fi
            ;;
        3)
            echo ""
            test_branch="test-merge-$(date +%s)"
            git checkout -b "$test_branch" main

            if git merge "origin/$BRANCH_NAME" --no-edit; then
                print_status "success" "Test merge successful"

                # Run validation
                if [ -f "scripts/validate-cicd.sh" ]; then
                    ./scripts/validate-cicd.sh
                fi

                git checkout main
                git branch -d "$test_branch"

                echo ""
                read -p "Proceed with actual merge? (y/N): " merge_confirm
                if [[ $merge_confirm == [yY] || $merge_confirm == [yY][eE][sS] ]]; then
                    exec "$0" "$BRANCH_NAME"  # Re-run script for actual merge
                fi
            else
                print_status "error" "Test merge failed"
                git merge --abort
                git checkout main
                git branch -d "$test_branch"
            fi
            ;;
        4)
            print_status "warning" "Skipping $BRANCH_NAME"
            ;;
        *)
            print_status "error" "Invalid choice"
            ;;
    esac

    exit 0
fi

# Interactive mode - list branches
echo "📋 Available Feature Branches:"
echo "=============================="

# Get branches that are ahead of main
feature_branches=()
while IFS= read -r branch; do
    branch_name=$(echo "$branch" | sed 's/origin\///')
    if [[ ! "$branch_name" =~ ^(main|HEAD)$ ]] && [[ ! "$branch_name" =~ ^dependabot/ ]]; then
        ahead_count=$(git rev-list --count main.."$branch" 2>/dev/null || echo "0")
        if [ "$ahead_count" -gt 0 ]; then
            feature_branches+=("$branch_name")
            echo "  🌿 $branch_name ($ahead_count commits ahead)"
        fi
    fi
done < <(git branch -r | grep -v "dependabot/" | sed 's/^[ *]*//')

if [ ${#feature_branches[@]} -eq 0 ]; then
    print_status "info" "No feature branches with new commits found"
    exit 0
fi

echo ""
echo "🎯 Choose a branch to review/merge:"
for i in "${!feature_branches[@]}"; do
    echo "$((i+1)). ${feature_branches[i]}"
done

echo ""
read -p "Enter branch number (or 'q' to quit): " choice

if [[ "$choice" == "q" || "$choice" == "Q" ]]; then
    print_status "info" "Exiting"
    exit 0
fi

# Validate choice
if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#feature_branches[@]} ]; then
    selected_branch="${feature_branches[$((choice-1))]}"
    exec "$0" "$selected_branch"  # Re-run script with selected branch
else
    print_status "error" "Invalid selection"
    exit 1
fi
