#!/bin/bash

# Final GPG-signed commit for Aurora CloudBank Orion Station
# This script will complete the deployment-ready state

echo "🚀 Aurora CloudBank Orion Station - Final GPG Commit"
echo "=================================================="

# Navigate to the repository
cd /workspaces/aurora-cloudbank-symbolic

# Check if we have GPG configured
echo "Checking GPG configuration..."
if ! git config --get user.signingkey; then
    echo "⚠️  No GPG signing key configured, setting up..."
    git config --global user.signingkey C99D828826F276C8
    git config --global commit.gpgsign true
    git config --global tag.gpgsign true
fi

# Check GPG key availability
echo "Verifying GPG key..."
if ! gpg --list-secret-keys C99D828826F276C8 >/dev/null 2>&1; then
    echo "❌ GPG key not found. Please run aurora_gpg_setup.sh first."
    exit 1
fi

# Show current git status
echo "📊 Current git status:"
git status --porcelain

# Add all files
echo "📝 Adding all files to staging..."
git add .

# Check for merge conflicts
echo "🔍 Checking for merge conflicts..."
if git status --porcelain | grep -q "^UU"; then
    echo "❌ Merge conflicts detected. Please resolve manually."
    git status
    exit 1
fi

# Count staged files
STAGED_COUNT=$(git diff --cached --name-only | wc -l)
echo "📁 Files staged for commit: $STAGED_COUNT"

if [ $STAGED_COUNT -eq 0 ]; then
    echo "✅ No changes to commit. Repository is clean."
    exit 0
fi

# Create comprehensive commit message
COMMIT_MSG="🔧 Aurora CloudBank Orion Station - Final Deployment Ready

✨ Comprehensive finalization of the Aurora CloudBank Symbolic project
🔐 GPG-signed commit for secure deployment
📚 Documentation, workflows, and scripts fully integrated
🛠️ All quality gates and deployment checks resolved
🌟 Repository now deployment-ready for production

Files updated:
- Documentation: Deployment guides, status reports, architecture docs
- Workflows: GitHub Actions with explicit permissions
- Scripts: Deployment, GPG setup, diagnostics, git operations
- Configuration: GPG keys, project settings, environment setup

GPG Key: C99D828826F276C8
Signed-off-by: Orion Station <orion-station@aurora-cloudbank.ai>"

# Attempt GPG-signed commit
echo "🔐 Creating GPG-signed commit..."
if git commit -S -m "$COMMIT_MSG"; then
    echo "✅ Commit successful!"
    
    # Push to main branch
    echo "🚀 Pushing to main branch..."
    if git push origin main; then
        echo "✅ Push successful!"
        echo "🎉 Aurora CloudBank Orion Station deployment complete!"
        
        # Show final status
        echo "📊 Final repository status:"
        git status
        git log --oneline -n 3
        
    else
        echo "❌ Push failed. Please check network connection and permissions."
        exit 1
    fi
else
    echo "❌ Commit failed. Checking GPG setup..."
    gpg --list-secret-keys
    git config --list | grep -i gpg
    exit 1
fi

echo "🎯 All operations completed successfully!"
echo "Repository is now deployment-ready and all changes are pushed."
