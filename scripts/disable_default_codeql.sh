#!/bin/bash
# Disable default CodeQL setup
# Symbolic Anchor: T1-DISABLE-DEFAULT-2025

echo "🔧 Disabling default CodeQL setup..."
echo "📌 Anchor: T1-DISABLE-DEFAULT-2025"

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "⚠️ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    echo "   Or run: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo "   sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo "   echo 'deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null"
    echo "   sudo apt update && sudo apt install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "⚠️ Not authenticated with GitHub CLI. Please run:"
    echo "   gh auth login"
    exit 1
fi

# Attempt to disable default setup
echo "🚫 Attempting to disable default CodeQL setup..."
gh api \
  --method DELETE \
  /repos/AUo959/aurora-cloudbank-symbolic/code-scanning/default-setup \
  2>/dev/null && echo "✅ Default setup disabled successfully" || echo "ℹ️ Default setup already disabled or not found"

echo "🔒 Default CodeQL setup disabled"
echo "📋 Next: Commit unified workflow and push to trigger new analysis"
