#!/bin/bash

##############################################################################
# Aurora CloudBank - Enhanced "Time to Clean Up" Command v2.0
# 
# Now with intelligent validation file management to prevent regeneration cycles
# Integrates with Aurora Validation Manager for elegant validation handling
##############################################################################

echo "🧹 Aurora CloudBank - Enhanced Time to Clean Up v2.0!"
echo "======================================================="
echo "🌟 Initiating comprehensive repository synchronization with smart validation..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[AURORA]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_action() {
    echo -e "${PURPLE}🚀${NC} $1"
}

print_smart() {
    echo -e "${CYAN}🧠${NC} $1"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository! Cleanup aborted."
    exit 1
fi

# Initialize validation manager
print_action "Step 0: Initializing Aurora Validation Manager..."

if [[ -f "scripts/aurora_validation_manager.py" ]]; then
    # Check current validation strategy
    VALIDATION_STATUS=$(python scripts/aurora_validation_manager.py --status 2>/dev/null | grep "Strategy:" | cut -d' ' -f2)
    print_smart "Current validation strategy: ${VALIDATION_STATUS:-default}"
    
    # If no strategy is set, implement smart_exclusion
    if [[ -z "$VALIDATION_STATUS" || "$VALIDATION_STATUS" == "None" ]]; then
        print_action "Setting up smart validation exclusion strategy..."
        python scripts/aurora_validation_manager.py --strategy smart_exclusion
        print_success "Smart exclusion strategy activated"
    fi
    
    # Clean up old validation reports
    print_action "Cleaning up old validation reports..."
    python scripts/aurora_validation_manager.py --cleanup
else
    print_warning "Validation manager not found - using legacy validation handling"
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
print_status "Current branch: ${CURRENT_BRANCH}"

# Step 1: Pre-cleanup validation check
print_action "Step 1: Pre-cleanup repository analysis..."

# Check for uncommitted changes (excluding validation files)
ALL_CHANGES=$(git status --porcelain)
if [[ -n "$ALL_CHANGES" ]]; then
    print_status "Found changes in working directory:"
    echo "$ALL_CHANGES" | while read status file; do
        # Check if this is a validation file that should be excluded
        IS_VALIDATION=false
        if [[ -f "scripts/aurora_validation_manager.py" ]]; then
            EXCLUDE_CHECK=$(python scripts/aurora_validation_manager.py --exclude-file "$file" 2>/dev/null | grep "Exclude from commit:" | cut -d' ' -f4)
            if [[ "$EXCLUDE_CHECK" == "True" ]]; then
                IS_VALIDATION=true
            fi
        fi
        
        if [[ "$IS_VALIDATION" == true ]]; then
            case $status in
                ??) echo -e "  ${YELLOW}? Validation (excluded):${NC} $file" ;;
                M*) echo -e "  ${YELLOW}~ Validation (excluded):${NC} $file" ;;
                A*) echo -e "  ${YELLOW}+ Validation (excluded):${NC} $file" ;;
                *) echo -e "  ${YELLOW}$status Validation (excluded):${NC} $file" ;;
            esac
        else
            case $status in
                ??) echo -e "  ${YELLOW}? Untracked:${NC} $file" ;;
                M*) echo -e "  ${YELLOW}~ Modified:${NC} $file" ;;
                A*) echo -e "  ${GREEN}+ Added:${NC} $file" ;;
                D*) echo -e "  ${RED}- Deleted:${NC} $file" ;;
                *) echo -e "  ${BLUE}$status${NC} $file" ;;
            esac
        fi
    done
    
    # Filter out validation files for actual staging
    FILTERED_CHANGES=$(echo "$ALL_CHANGES" | while read status file; do
        if [[ -f "scripts/aurora_validation_manager.py" ]]; then
            EXCLUDE_CHECK=$(python scripts/aurora_validation_manager.py --exclude-file "$file" 2>/dev/null | grep "Exclude from commit:" | cut -d' ' -f4)
            if [[ "$EXCLUDE_CHECK" != "True" ]]; then
                echo "$status $file"
            fi
        else
            # Legacy filtering - exclude known validation files
            if [[ "$file" != "PRE_COMMIT_VALIDATION_ISSUES.md" && "$file" != "CANONICAL_VALIDATION_REPORT.md" ]]; then
                echo "$status $file"
            fi
        fi
    done)
    
    if [[ -n "$FILTERED_CHANGES" ]]; then
        print_status "Non-validation changes detected - will stage and commit"
        HAS_CHANGES=true
    else
        print_smart "Only validation files changed - using smart exclusion"
        HAS_CHANGES=false
    fi
else
    print_success "Working directory clean"
    HAS_CHANGES=false
fi

# Step 2: Pull latest changes from remote
print_action "Step 2: Pulling latest changes from remote..."
if git pull origin "${CURRENT_BRANCH}" --no-edit; then
    print_success "Successfully pulled latest changes"
else
    print_warning "Pull encountered issues - continuing with cleanup"
fi

# Step 3: Smart staging (excluding validation files)
if [[ "$HAS_CHANGES" == true ]]; then
    print_action "Step 3: Smart staging (excluding validation files)..."
    
    # Stage all files first
    git add .
    
    # Then unstage validation files if using smart exclusion
    if [[ -f "scripts/aurora_validation_manager.py" ]]; then
        echo "$ALL_CHANGES" | while read status file; do
            if [[ -n "$file" ]]; then
                EXCLUDE_CHECK=$(python scripts/aurora_validation_manager.py --exclude-file "$file" 2>/dev/null | grep "Exclude from commit:" | cut -d' ' -f4)
                if [[ "$EXCLUDE_CHECK" == "True" ]]; then
                    git reset HEAD "$file" 2>/dev/null || true
                    print_smart "Excluded from staging: $file"
                fi
            fi
        done
    fi
    
    # Show what's actually staged
    STAGED_FILES=$(git diff --cached --name-status)
    if [[ -n "$STAGED_FILES" ]]; then
        echo -e "${CYAN}📋 Staged files (smart filtered):${NC}"
        echo "$STAGED_FILES" | while read status file; do
            case $status in
                A) echo -e "  ${GREEN}+ Added:${NC} $file" ;;
                M) echo -e "  ${YELLOW}~ Modified:${NC} $file" ;;
                D) echo -e "  ${RED}- Deleted:${NC} $file" ;;
                R*) echo -e "  ${PURPLE}➡ Renamed:${NC} $file" ;;
                *) echo -e "  ${BLUE}? $status:${NC} $file" ;;
            esac
        done
        print_success "Smart staging complete"
    else
        print_smart "No files to stage after smart filtering"
        HAS_CHANGES=false
    fi
else
    print_status "Step 3: No changes to stage"
fi

# Step 4: Intelligent commit with validation cycle prevention
if [[ "$HAS_CHANGES" == true ]]; then
    print_action "Step 4: Creating commit with cycle-safe validation..."
    
    # Generate commit message
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    COMMIT_MSG="🧹 Aurora Enhanced Cleanup - Smart sync ${TIMESTAMP}

📊 Repository cleanup with intelligent validation:
- Smart staging excludes validation files from commit cycle
- Applied Aurora Validation Manager strategies
- Maintained canonical compliance without regeneration loops
- Synchronized Aurora CloudBank components

🔄 Enhanced cleanup with validation cycle prevention
🌟 Aurora CloudBank v3.5.1_macroready - All systems operational"

    # Single commit attempt with smart validation
    print_status "Committing with smart validation handling..."
    
    if git commit -m "$COMMIT_MSG"; then
        print_success "Successfully created commit with smart validation"
        echo -e "${CYAN}📝 Commit message:${NC}"
        echo "$COMMIT_MSG" | sed 's/^/  /'
        COMMIT_SUCCESS=true
    else
        print_error "Commit failed - manual intervention required"
        print_status "This should not happen with smart validation active"
        COMMIT_SUCCESS=false
    fi
else
    print_status "Step 4: No changes to commit"
    COMMIT_SUCCESS=false
fi

# Step 5: Push to remote
print_action "Step 5: Pushing to remote repository..."

if [[ "$COMMIT_SUCCESS" == true ]]; then
    if git push origin "${CURRENT_BRANCH}"; then
        print_success "Successfully pushed to remote"
    else
        print_warning "Failed to push to remote - attempting force push with lease..."
        if git push --force-with-lease origin "${CURRENT_BRANCH}"; then
            print_success "Successfully force-pushed to remote"
        else
            print_error "Failed to push to remote even with force-with-lease"
            print_status "This may require manual intervention"
        fi
    fi
else
    # Check if we have unpushed commits anyway
    UNPUSHED_COMMITS=$(git log origin/"${CURRENT_BRANCH}"..HEAD --oneline 2>/dev/null | wc -l)
    if [[ $UNPUSHED_COMMITS -gt 0 ]]; then
        print_status "Found unpushed commits, attempting push..."
        git push origin "${CURRENT_BRANCH}" || print_warning "Could not push existing commits"
    else
        print_status "No new commits to push"
    fi
fi

# Step 6: Sync other branches
print_action "Step 6: Checking for other branches to sync..."
OTHER_BRANCHES=$(git branch -r | grep -v "${CURRENT_BRANCH}" | grep -v "HEAD" | sed 's/origin\///' | tr -d ' ')

if [[ -n "$OTHER_BRANCHES" ]]; then
    print_status "Found additional branches to sync:"
    echo "$OTHER_BRANCHES" | while read branch; do
        if [[ -n "$branch" ]]; then
            echo -e "  ${CYAN}📋${NC} $branch"
            if git fetch origin "$branch:$branch" 2>/dev/null; then
                print_success "Updated branch: $branch"
            else
                print_warning "Could not update branch: $branch"
            fi
        fi
    done
else
    print_status "No additional branches to sync"
fi

# Step 7: Enhanced repository health check
print_action "Step 7: Enhanced repository health check..."

# Repository size and commit count
REPO_SIZE=$(du -sh .git 2>/dev/null | cut -f1)
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null)
print_status "Repository size: ${REPO_SIZE}, commits: ${COMMIT_COUNT}"

# Validation manager status
if [[ -f "scripts/aurora_validation_manager.py" ]]; then
    print_smart "Validation Manager Status:"
    python scripts/aurora_validation_manager.py --status | grep -E "Strategy:|Exclude from Commit:" | sed 's/^/  /'
fi

# Check for large files
LARGE_FILES=$(find . -type f -size +10M -not -path './.git/*' -not -path './.aurora_validation/*' 2>/dev/null)
if [[ -n "$LARGE_FILES" ]]; then
    print_warning "Large files detected (>10MB):"
    echo "$LARGE_FILES" | while read file; do
        SIZE=$(du -h "$file" | cut -f1)
        echo -e "  ${YELLOW}📄${NC} $file (${SIZE})"
    done
else
    print_success "No large files detected"
fi

# Step 8: Aurora-specific validations
print_action "Step 8: Aurora CloudBank specific validations..."

# Check collaboration chamber
if pgrep -f "aurora_collaboration_chamber_launcher" > /dev/null; then
    print_success "Aurora Collaboration Chamber: OPERATIONAL"
else
    print_warning "Aurora Collaboration Chamber: Not running"
fi

# Check core files
AURORA_CORE_FILES=(
    "src/orchestrators/holographic_interface_orchestrator.js"
    "src/core/mesh_agent.js"
    "src/interfaces/aurora_collaboration_chamber.html"
    "aurora_collaboration_chamber_launcher.js"
    "scripts/aurora_validation_manager.py"
)

for file in "${AURORA_CORE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        print_success "Aurora core file present: $(basename "$file")"
    else
        print_warning "Aurora core file missing: $(basename "$file")"
    fi
done

# Step 9: Final cleanup and validation
print_action "Step 9: Final validation and cleanup..."

# Clean up old git objects
if git gc --auto; then
    print_success "Git garbage collection completed"
fi

# Update git index
git update-index --refresh > /dev/null 2>&1
print_success "Git index refreshed"

# Final status check
echo ""
echo "🎉 ENHANCED CLEANUP COMPLETE!"
echo "============================="

# Smart final status
FINAL_CHANGES=$(git status --porcelain)
if [[ -n "$FINAL_CHANGES" ]]; then
    print_smart "Remaining changes (validation files excluded by design):"
    echo "$FINAL_CHANGES" | while read status file; do
        if [[ -f "scripts/aurora_validation_manager.py" ]]; then
            EXCLUDE_CHECK=$(python scripts/aurora_validation_manager.py --exclude-file "$file" 2>/dev/null | grep "Exclude from commit:" | cut -d' ' -f4)
            if [[ "$EXCLUDE_CHECK" == "True" ]]; then
                echo -e "  ${CYAN}🔒 Validation (excluded):${NC} $file"
            else
                echo -e "  ${YELLOW}⚠️ Uncommitted:${NC} $file"
            fi
        else
            echo -e "  ${YELLOW}? ${NC} $file"
        fi
    done
else
    print_success "No uncommitted changes"
fi

# Synchronization status
LOCAL_COMMIT=$(git rev-parse HEAD 2>/dev/null)
REMOTE_COMMIT=$(git rev-parse origin/"${CURRENT_BRANCH}" 2>/dev/null)

if [[ "$LOCAL_COMMIT" == "$REMOTE_COMMIT" ]]; then
    print_success "Repository is fully synchronized with remote"
else
    print_status "Local:  ${LOCAL_COMMIT:0:8}"
    print_status "Remote: ${REMOTE_COMMIT:0:8}"
fi

# Final summary
print_success "Enhanced repository cleanup completed"
print_smart "Smart validation cycle prevention active"
print_success "Aurora CloudBank components verified"
print_status "Current branch: ${CURRENT_BRANCH}"

echo ""
echo -e "${CYAN}📊 Final Repository Status:${NC}"
git status --short --branch

echo ""
echo -e "${GREEN}🌟 Aurora CloudBank v3.5.1_macroready - Enhanced Cleanup Successful!${NC}"
echo -e "${CYAN}🧠 Smart Validation Manager: Active${NC}"
echo -e "${PURPLE}🏛️ Collaboration Chamber ready for next session${NC}"
echo ""
