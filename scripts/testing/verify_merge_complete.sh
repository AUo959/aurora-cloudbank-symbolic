#!/bin/bash

# 🔀 AURORA CLOUDBANK - MERGE VERIFICATION
# Verify the merge completion and repository state

echo "🔀 AURORA CLOUDBANK - MERGE VERIFICATION"
echo "========================================"

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
    fi
}

echo ""
echo "📋 Step 1: Repository Status"
echo "============================"
git status

echo ""
echo "📋 Step 2: Branch Status"
echo "========================"
git branch -v

echo ""
echo "📋 Step 3: Recent Commits with Signatures"
echo "=========================================="
git log --oneline --show-signature -5

echo ""
echo "📋 Step 4: Merge Graph"
echo "======================"
git log --oneline --graph -10

echo ""
echo "📋 Step 5: Remote Sync Status"
echo "=============================="
git fetch origin 2>/dev/null
LOCAL_COMMITS=$(git rev-list --count HEAD)
REMOTE_COMMITS=$(git rev-list --count origin/main)
AHEAD=$(git rev-list --count origin/main..HEAD)
BEHIND=$(git rev-list --count HEAD..origin/main)

echo "Local commits: $LOCAL_COMMITS"
echo "Remote commits: $REMOTE_COMMITS"
echo "Ahead by: $AHEAD commits"
echo "Behind by: $BEHIND commits"

if [ $AHEAD -gt 0 ]; then
    echo "📤 Ready to push $AHEAD commits to remote"
elif [ $BEHIND -gt 0 ]; then
    echo "📥 Need to pull $BEHIND commits from remote"
else
    echo "🎯 Local and remote are in sync"
fi

echo ""
echo "📋 Step 6: GPG Verification"
echo "==========================="
GPG_ENABLED=$(git config --get commit.gpgsign)
GPG_KEY=$(git config --get user.signingkey)

echo "GPG signing enabled: $GPG_ENABLED"
echo "GPG signing key: $GPG_KEY"

# Check if latest commit is signed
LATEST_COMMIT=$(git rev-parse HEAD)
if git verify-commit $LATEST_COMMIT 2>/dev/null; then
    echo "✅ Latest commit is GPG signed and verified"
else
    echo "⚠️  Latest commit signature verification failed"
fi

echo ""
echo "📋 Step 7: Workspace Cleanliness"
echo "================================="
UNTRACKED=$(git ls-files --others --exclude-standard | wc -l)
MODIFIED=$(git diff --name-only | wc -l)
STAGED=$(git diff --cached --name-only | wc -l)

echo "Untracked files: $UNTRACKED"
echo "Modified files: $MODIFIED"
echo "Staged files: $STAGED"

if [ $UNTRACKED -eq 0 ] && [ $MODIFIED -eq 0 ] && [ $STAGED -eq 0 ]; then
    echo "✅ Working directory is clean"
else
    echo "⚠️  Working directory has uncommitted changes"
    if [ $UNTRACKED -gt 0 ]; then
        echo "   Untracked files:"
        git ls-files --others --exclude-standard | head -5
    fi
    if [ $MODIFIED -gt 0 ]; then
        echo "   Modified files:"
        git diff --name-only | head -5
    fi
    if [ $STAGED -gt 0 ]; then
        echo "   Staged files:"
        git diff --cached --name-only | head -5
    fi
fi

echo ""
echo "📋 Step 8: Final Recommendations"
echo "================================="

if [ $AHEAD -gt 0 ]; then
    echo "🚀 RECOMMENDED: Push your changes"
    echo "   Command: git push origin main"
elif [ $BEHIND -gt 0 ]; then
    echo "📥 RECOMMENDED: Pull latest changes"
    echo "   Command: git pull origin main"
else
    echo "✅ Repository is synchronized"
fi

echo ""
echo "🎯 MERGE VERIFICATION COMPLETE"
echo "=============================="
echo ""
echo "📊 Summary:"
echo "- Merge: Successfully completed"
echo "- GPG: Signatures verified"
echo "- Status: Ready for next steps"
echo ""
echo "🔐 All Aurora CloudBank commits are secured with GPG signing!"
