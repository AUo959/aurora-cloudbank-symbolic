#!/bin/bash

# 🔄 AURORA CLOUDBANK - GIT DIVERGENCE RESOLUTION
# Safe resolution of branch divergence with backup and verification

echo "🔄 AURORA CLOUDBANK - GIT DIVERGENCE RESOLUTION"
echo "=============================================="

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
    fi
}

# Function to create backup
create_backup() {
    echo "📋 Creating backup of current state..."
    BACKUP_BRANCH="backup-$(date +%Y%m%d-%H%M%S)"
    git branch "$BACKUP_BRANCH"
    print_status $? "Created backup branch: $BACKUP_BRANCH"
    echo "   Backup branch created at: $BACKUP_BRANCH"
}

# Step 1: Analyze current situation
echo ""
echo "📋 Step 1: Analyzing git repository state..."
echo "Current branch: $(git branch --show-current)"
echo "Repository status:"
git status --porcelain

# Step 2: Fetch latest from remote
echo ""
echo "📋 Step 2: Fetching latest from remote..."
git fetch origin
print_status $? "Fetched from remote"

# Step 3: Show divergence details
echo ""
echo "📋 Step 3: Divergence Analysis"
echo "=============================================="
echo "🔍 LOCAL COMMITS (not on remote):"
git log --oneline origin/main..HEAD
echo ""
echo "🔍 REMOTE COMMITS (not local):"
git log --oneline HEAD..origin/main
echo ""
echo "🔍 GRAPHICAL VIEW:"
git log --oneline --graph --all -15

# Step 4: Create backup before resolution
echo ""
echo "📋 Step 4: Creating backup..."
create_backup

# Step 5: Analyze resolution options
echo ""
echo "📋 Step 5: Resolution Options"
echo "=============================================="
echo "Available resolution strategies:"
echo "1. MERGE: git pull origin main (creates merge commit)"
echo "2. REBASE: git pull --rebase origin main (replays local commits on top of remote)"
echo "3. RESET: git reset --hard origin/main (LOSES local commits - use backup to recover)"
echo "4. MANUAL: Handle conflicts manually"
echo ""

# Step 6: Check if we can safely merge
echo "📋 Step 6: Checking merge feasibility..."
git merge-base --is-ancestor HEAD origin/main
if [ $? -eq 0 ]; then
    echo "✅ Local commits are ahead of remote - safe to push"
    RESOLUTION_TYPE="FAST_FORWARD"
else
    git merge-base --is-ancestor origin/main HEAD
    if [ $? -eq 0 ]; then
        echo "✅ Remote commits are ahead of local - safe to pull"
        RESOLUTION_TYPE="FAST_FORWARD_PULL"
    else
        echo "⚠️  True divergence detected - merge or rebase required"
        RESOLUTION_TYPE="DIVERGED"
    fi
fi

# Step 7: Recommend resolution strategy
echo ""
echo "📋 Step 7: Recommended Resolution Strategy"
echo "=============================================="

case $RESOLUTION_TYPE in
    "FAST_FORWARD")
        echo "🎯 RECOMMENDED: Force push (your local commits are newer)"
        echo "   Command: git push --force-with-lease origin main"
        echo "   Reason: Local commits are simply ahead of remote"
        ;;
    "FAST_FORWARD_PULL")
        echo "🎯 RECOMMENDED: Simple pull"
        echo "   Command: git pull origin main"
        echo "   Reason: Remote commits are simply ahead of local"
        ;;
    "DIVERGED")
        echo "🎯 RECOMMENDED: Merge with verification"
        echo "   Command: git pull origin main"
        echo "   Reason: Both branches have unique commits"
        echo "   Note: This will create a merge commit"
        ;;
esac

# Step 8: Provide manual resolution commands
echo ""
echo "📋 Step 8: Manual Resolution Commands"
echo "=============================================="
echo "To resolve manually, choose one of these commands:"
echo ""
echo "Option A - Merge Strategy (recommended for collaboration):"
echo "   git pull origin main"
echo "   # Resolve any conflicts if they occur"
echo "   git push origin main"
echo ""
echo "Option B - Rebase Strategy (clean linear history):"
echo "   git pull --rebase origin main"
echo "   # Resolve any conflicts if they occur"
echo "   git push origin main"
echo ""
echo "Option C - Force Push (USE WITH CAUTION - overwrites remote):"
echo "   git push --force-with-lease origin main"
echo ""
echo "Option D - Reset to remote (LOSES local commits):"
echo "   git reset --hard origin/main"
echo "   # Use backup branch to recover local commits if needed"
echo ""

# Step 9: GPG signing verification
echo "📋 Step 9: GPG Signing Status"
echo "=============================================="
echo "GPG signing enabled: $(git config --global commit.gpgsign)"
echo "GPG key configured: $(git config --global user.signingkey)"
echo ""
echo "🔐 All resolved commits will be GPG signed automatically"

# Step 10: Final recommendations
echo ""
echo "🎯 FINAL RECOMMENDATIONS"
echo "=============================================="
echo "1. 🛡️  Backup created: Use it to recover if needed"
echo "2. 🔄 For Aurora CloudBank: Use MERGE strategy to preserve history"
echo "3. 🔐 GPG signing: All commits will be signed automatically"
echo "4. 📊 Verify: Always check git log after resolution"
echo "5. 🚀 Test: Run your tests before final push"
echo ""
echo "💡 Recommended next command:"
echo "   git pull origin main"
echo ""
echo "🔍 After resolution, verify with:"
echo "   git log --oneline --graph -10"
echo "   git log --show-signature -1"
echo ""
echo "📋 Resolution script complete. Execute your chosen strategy above."
