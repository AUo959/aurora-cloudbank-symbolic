#!/bin/bash
# Aurora Admin Helper - Bypass branch protection with proper workflows
# Thread: T1→T8→T9→INFINITE
# DLP: context_tag=admin_helper, symbolic_hash=BRANCH_PROTECTION_BYPASS_v1

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Aurora Admin Helper${NC}"
echo "================================"
echo ""

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}📍 Current branch: ${YELLOW}${CURRENT_BRANCH}${NC}"

# Function to auto-merge current PR
auto_merge_pr() {
    echo ""
    echo -e "${YELLOW}🔄 Auto-merge PR workflow${NC}"
    echo "================================"
    
    # Check if there's an open PR for current branch
    PR_NUMBER=$(gh pr view --json number -q .number 2>/dev/null || echo "")
    
    if [ -z "$PR_NUMBER" ]; then
        echo -e "${RED}❌ No open PR found for branch ${CURRENT_BRANCH}${NC}"
        echo -e "${YELLOW}💡 Create a PR first with: gh pr create${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Found PR #${PR_NUMBER}${NC}"
    
    # Add auto-merge label
    echo "📌 Adding auto-merge label..."
    gh pr edit $PR_NUMBER --add-label "auto-merge,admin-approved"
    
    echo ""
    echo -e "${GREEN}✅ Auto-merge triggered!${NC}"
    echo -e "${BLUE}📊 Monitor progress: gh pr view ${PR_NUMBER} --web${NC}"
}

# Function to direct push via workflow
direct_push() {
    echo ""
    echo -e "${YELLOW}⚡ Direct push to main workflow${NC}"
    echo "================================"
    
    if [ "$CURRENT_BRANCH" == "main" ]; then
        echo -e "${RED}❌ Already on main branch${NC}"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo -e "${RED}❌ You have uncommitted changes${NC}"
        echo -e "${YELLOW}💡 Commit your changes first${NC}"
        exit 1
    fi
    
    # Push current branch to remote
    echo "📤 Pushing current branch to remote..."
    git push -u origin $CURRENT_BRANCH
    
    # Get commit message
    LAST_COMMIT_MSG=$(git log -1 --pretty=%B)
    
    echo ""
    echo -e "${YELLOW}📝 Last commit message:${NC}"
    echo "$LAST_COMMIT_MSG"
    echo ""
    read -p "Use this commit message for merge? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter merge commit message: " MERGE_MSG
        LAST_COMMIT_MSG=$MERGE_MSG
    fi
    
    # Trigger workflow
    echo "🚀 Triggering admin push workflow..."
    gh workflow run admin-quick-push.yml \
        -f commit_message="$LAST_COMMIT_MSG" \
        -f branch="$CURRENT_BRANCH"
    
    echo ""
    echo -e "${GREEN}✅ Workflow triggered!${NC}"
    echo -e "${BLUE}📊 Monitor progress: gh run list --workflow=admin-quick-push.yml${NC}"
}

# Function to create and auto-merge PR
create_and_merge() {
    echo ""
    echo -e "${YELLOW}🎯 Create PR and auto-merge${NC}"
    echo "================================"
    
    if [ "$CURRENT_BRANCH" == "main" ]; then
        echo -e "${RED}❌ Already on main branch${NC}"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo -e "${RED}❌ You have uncommitted changes${NC}"
        echo -e "${YELLOW}💡 Commit your changes first${NC}"
        exit 1
    fi
    
    # Push current branch
    echo "📤 Pushing current branch..."
    git push -u origin $CURRENT_BRANCH
    
    # Get last commit message for PR title
    LAST_COMMIT=$(git log -1 --pretty=%B | head -1)
    
    echo ""
    echo -e "${YELLOW}📝 PR Title: ${NC}${LAST_COMMIT}"
    
    # Create PR with auto-merge label
    echo "🔧 Creating PR with auto-merge label..."
    gh pr create \
        --title "$LAST_COMMIT" \
        --body "Auto-merge requested by admin workflow.

**Changes:**
$(git log main..HEAD --oneline | head -10)

**Status:** Ready for auto-merge
**Thread:** T1→T8→T9→INFINITE" \
        --label "auto-merge,admin-approved" \
        --base main
    
    echo ""
    echo -e "${GREEN}✅ PR created and auto-merge triggered!${NC}"
    echo -e "${BLUE}📊 View PR: gh pr view --web${NC}"
}

# Function to list pending PRs
list_prs() {
    echo ""
    echo -e "${YELLOW}📋 Open Pull Requests${NC}"
    echo "================================"
    gh pr list --state open
}

# Function to merge specific PR
merge_pr() {
    echo ""
    read -p "Enter PR number to merge: " PR_NUM
    
    if [ -z "$PR_NUM" ]; then
        echo -e "${RED}❌ No PR number provided${NC}"
        exit 1
    fi
    
    echo "📌 Adding auto-merge label to PR #${PR_NUM}..."
    gh pr edit $PR_NUM --add-label "auto-merge,admin-approved"
    
    echo ""
    echo -e "${GREEN}✅ Auto-merge triggered for PR #${PR_NUM}${NC}"
    echo -e "${BLUE}📊 Monitor: gh pr view ${PR_NUM} --web${NC}"
}

# Main menu
echo ""
echo "Select an option:"
echo "1) Auto-merge current PR"
echo "2) Direct push to main (via workflow)"
echo "3) Create PR and auto-merge"
echo "4) List open PRs"
echo "5) Merge specific PR"
echo "6) Exit"
echo ""
read -p "Choice (1-6): " -n 1 -r
echo
echo ""

case $REPLY in
    1)
        auto_merge_pr
        ;;
    2)
        direct_push
        ;;
    3)
        create_and_merge
        ;;
    4)
        list_prs
        ;;
    5)
        merge_pr
        ;;
    6)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✨ Done!${NC}"
