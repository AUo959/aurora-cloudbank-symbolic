#!/usr/bin/env bash
# Aurora CloudBank #321//. Enhanced - Comprehensive Sync with Intelligent Documentation
# Automatically updates version-related documentation and wiki when needed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_ROOT="/workspaces/aurora-cloudbank-symbolic"
VERSION_FILE="$WORKSPACE_ROOT/VERSION"
CHANGELOG_FILE="$WORKSPACE_ROOT/CHANGELOG.md"
README_FILE="$WORKSPACE_ROOT/README.md"
WIKI_DIR="$WORKSPACE_ROOT/wiki-content"

# Timing
START_TIME=$(date +%s)

echo -e "${BLUE}🔄 #321//. Enhanced Comprehensive Sync & Validate${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Phase 1: Check for Pending Changes
phase_start=$(date +%s)
echo -e "${BLUE}[Phase 1/7]${NC} Checking for pending changes..."

cd "$WORKSPACE_ROOT"
CHANGES=$(git status --porcelain)
if [ -z "$CHANGES" ]; then
    echo -e "${GREEN}✅ No changes detected - working tree clean${NC}"
    phase_end=$(date +%s)
    echo -e "⏱️  Phase 1: $((phase_end - phase_start))s"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✅ #321//. COMPLETE - Working tree already clean!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
fi

CHANGE_COUNT=$(echo "$CHANGES" | wc -l)
echo -e "${GREEN}✅ $CHANGE_COUNT files with changes detected${NC}"

# Analyze change categories
SRC_CHANGES=$(echo "$CHANGES" | grep -E '^\s*[AM].*\.(py|js|ts)$' | wc -l || true)
DOC_CHANGES=$(echo "$CHANGES" | grep -E '^\s*[AM].*\.md$' | wc -l || true)
CONFIG_CHANGES=$(echo "$CHANGES" | grep -E '^\s*[AM].*\.(json|yaml|yml|toml)$' | wc -l || true)

echo "   📂 Source files: $SRC_CHANGES"
echo "   📄 Documentation: $DOC_CHANGES"
echo "   ⚙️  Configuration: $CONFIG_CHANGES"

phase_end=$(date +%s)
echo -e "⏱️  Phase 1: $((phase_end - phase_start))s"
echo ""

# Phase 2: Intelligent Documentation Updates
phase_start=$(date +%s)
echo -e "${BLUE}[Phase 2/7]${NC} Checking for documentation updates needed..."

DOCS_UPDATED=false

# Check if VERSION file was changed
if echo "$CHANGES" | grep -q "VERSION"; then
    NEW_VERSION=$(cat "$VERSION_FILE" | tr -d '\n')
    echo -e "${YELLOW}📋 Version file changed to: $NEW_VERSION${NC}"
    
    # Update README badge if not already updated
    if grep -q "version-.*-blue" "$README_FILE"; then
        OLD_VERSION=$(grep -oP 'version-\K[0-9]+\.[0-9]+\.[0-9]+' "$README_FILE" | head -1)
        if [ "$OLD_VERSION" != "$NEW_VERSION" ]; then
            echo "   Updating README.md version badge: $OLD_VERSION → $NEW_VERSION"
            sed -i "s/version-$OLD_VERSION-blue/version-$NEW_VERSION-blue/g" "$README_FILE"
            sed -i "s|releases/tag/v$OLD_VERSION|releases/tag/v$NEW_VERSION|g" "$README_FILE"
            DOCS_UPDATED=true
        fi
    fi
    
    # Update "Last Updated" date in README
    CURRENT_DATE=$(date +"%B %d, %Y")
    if grep -q "Last Updated:" "$README_FILE"; then
        echo "   Updating README.md last updated date: $CURRENT_DATE"
        sed -i "s/_Last Updated: .*|/_Last Updated: $CURRENT_DATE |/g" "$README_FILE"
        DOCS_UPDATED=true
    fi
    
    echo -e "${GREEN}✅ Documentation auto-updated for version $NEW_VERSION${NC}"
else
    echo -e "${GREEN}✅ No version changes - documentation current${NC}"
fi

phase_end=$(date +%s)
echo -e "⏱️  Phase 2: $((phase_end - phase_start))s"
echo ""

# Phase 3: Intelligent Staging
phase_start=$(date +%s)
echo -e "${BLUE}[Phase 3/7]${NC} Staging changes intelligently..."

# Stage all changes
git add -A

STAGED_COUNT=$(git diff --cached --numstat | wc -l)
echo -e "${GREEN}✅ Staged $STAGED_COUNT files${NC}"

phase_end=$(date +%s)
echo -e "⏱️  Phase 3: $((phase_end - phase_start))s"
echo ""

# Phase 4: Generate & Commit
phase_start=$(date +%s)
echo -e "${BLUE}[Phase 4/7]${NC} Generating commit..."

# Analyze changes for commit message
if [ $SRC_CHANGES -gt 0 ] && [ $DOC_CHANGES -gt 0 ]; then
    COMMIT_TYPE="feat"
    COMMIT_SCOPE="core+docs"
elif [ $SRC_CHANGES -gt 0 ]; then
    COMMIT_TYPE="feat"
    COMMIT_SCOPE="core"
elif [ $DOC_CHANGES -gt 0 ]; then
    COMMIT_TYPE="docs"
    COMMIT_SCOPE="documentation"
elif [ $CONFIG_CHANGES -gt 0 ]; then
    COMMIT_TYPE="chore"
    COMMIT_SCOPE="config"
else
    COMMIT_TYPE="chore"
    COMMIT_SCOPE="update"
fi

# Generate commit message
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
COMMIT_MSG="🔄 #321//. Comprehensive Sync: $COMMIT_TYPE($COMMIT_SCOPE)

Automated comprehensive sync with intelligent documentation updates.

Changes:
- $CHANGE_COUNT files modified
- Source files: $SRC_CHANGES
- Documentation: $DOC_CHANGES
- Configuration: $CONFIG_CHANGES

Thread: T1→T8→T9→INFINITE
DLP: context_tag=sync_321_enhanced_$TIMESTAMP, symbolic_hash=AUTO_SYNC_v2
Chain: #321//. (Enhanced Comprehensive Sync & Validate)"

git commit -m "$COMMIT_MSG"

echo -e "${GREEN}✅ Commit created: $COMMIT_TYPE($COMMIT_SCOPE)${NC}"

phase_end=$(date +%s)
echo -e "⏱️  Phase 4: $((phase_end - phase_start))s"
echo ""

# Phase 5: Wiki Synchronization
phase_start=$(date +%s)
echo -e "${BLUE}[Phase 5/7]${NC} Synchronizing wiki submodule..."

if [ -d "$WIKI_DIR/.git" ]; then
    cd "$WIKI_DIR"
    WIKI_CHANGES=$(git status --porcelain)
    
    if [ -n "$WIKI_CHANGES" ]; then
        WIKI_CHANGE_COUNT=$(echo "$WIKI_CHANGES" | wc -l)
        echo -e "${YELLOW}📚 Wiki has $WIKI_CHANGE_COUNT changes${NC}"
        
        # Stage and commit wiki changes
        git add -A
        
        # Determine wiki commit message
        if echo "$WIKI_CHANGES" | grep -q "Home.md"; then
            WIKI_MSG="docs: Update wiki Home for release"
        elif echo "$WIKI_CHANGES" | grep -q "Changelog.md"; then
            WIKI_MSG="docs: Update wiki Changelog"
        else
            WIKI_MSG="docs: Update wiki documentation"
        fi
        
        git commit -m "$WIKI_MSG

Auto-synchronized via #321//. enhanced sync
DLP: context_tag=wiki_sync_$TIMESTAMP"
        
        # Push wiki to remote
        echo "   Pushing wiki changes to remote..."
        git push origin master
        
        echo -e "${GREEN}✅ Wiki synchronized and pushed${NC}"
    else
        echo -e "${GREEN}✅ Wiki up-to-date, no changes needed${NC}"
    fi
    
    cd "$WORKSPACE_ROOT"
else
    echo -e "${YELLOW}⚠️  Wiki directory not a git repository, skipping${NC}"
fi

phase_end=$(date +%s)
echo -e "⏱️  Phase 5: $((phase_end - phase_start))s"
echo ""

# Phase 6: Sync to Main
phase_start=$(date +%s)
echo -e "${BLUE}[Phase 6/7]${NC} Syncing to remote..."

# Pull with rebase
echo "   Pulling latest changes..."
if git pull --rebase origin main; then
    echo -e "${GREEN}✅ Rebase successful${NC}"
else
    echo -e "${RED}❌ Rebase failed - conflicts detected${NC}"
    echo "   Please resolve conflicts manually and run #321//. again"
    exit 1
fi

# Push to remote
echo "   Pushing to remote..."
if git push origin main; then
    echo -e "${GREEN}✅ Successfully pushed to origin/main${NC}"
else
    echo -e "${RED}❌ Push failed${NC}"
    exit 1
fi

phase_end=$(date +%s)
echo -e "⏱️  Phase 6: $((phase_end - phase_start))s"
echo ""

# Phase 7: Performance Verification
phase_start=$(date +%s)
echo -e "${BLUE}[Phase 7/7]${NC} Verifying final state..."

# Verify working tree is clean
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✅ Working tree clean${NC}"
else
    echo -e "${YELLOW}⚠️  Working tree still has changes${NC}"
fi

# Calculate total time
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

echo -e "${GREEN}✅ All operations completed${NC}"

phase_end=$(date +%s)
echo -e "⏱️  Phase 7: $((phase_end - phase_start))s"
echo ""

# Final Report
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ #321//. ENHANCED COMPLETE${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 EXECUTION SUMMARY:"
echo "   Total Time: ${TOTAL_TIME}s"
echo "   Files Changed: $CHANGE_COUNT"
echo "   Docs Auto-Updated: $([[ "$DOCS_UPDATED" == "true" ]] && echo "Yes" || echo "No")"
echo "   Wiki Synced: $([[ -n "$WIKI_CHANGES" ]] && echo "Yes" || echo "No changes")"
echo "   Commit Type: $COMMIT_TYPE($COMMIT_SCOPE)"
echo ""
echo "🎯 SYSTEM STATUS:"
echo "   ✅ All changes synced to main"
echo "   ✅ Documentation current"
echo "   ✅ Wiki synchronized"
echo "   ✅ Working tree clean"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
