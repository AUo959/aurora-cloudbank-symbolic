#!/bin/bash

# Quick Git Authentication Fix
echo "🔧 Quick Git Fix - No Container Rebuild Needed"

# Basic git setup
git config --global user.name "Aurora CloudBank"
git config --global user.email "aurora@cloudbank.dev"
git config --global commit.gpgsign false

# Check current remote
echo "Current git remote:"
git remote -v

# If using SSH, switch to HTTPS
REMOTE=$(git remote get-url origin)
if [[ "$REMOTE" == git@github.com:* ]]; then
    echo "Switching from SSH to HTTPS..."
    REPO_PATH=$(echo "$REMOTE" | sed 's/git@github.com://' | sed 's/\.git$//')
    git remote set-url origin "https://github.com/$REPO_PATH.git"
    echo "New remote: $(git remote get-url origin)"
fi

# Test git status
echo "Git status:"
git status --short

echo ""
echo "✅ Git configured for HTTPS authentication"
echo "📋 To push, you'll need a GitHub Personal Access Token"
echo "🔗 Create one at: https://github.com/settings/tokens"
echo ""
echo "Then try: git push origin main"
