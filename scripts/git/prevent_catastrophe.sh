#!/usr/bin/env bash
# Aurora CloudBank - Catastrophe Prevention System
# Prevents accidental mass deletions in git operations

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛡️  Aurora CloudBank Catastrophe Prevention System${NC}"
echo "======================================================"
echo ""

# Function: Check for mass deletions in working directory
check_working_tree() {
    echo "🔍 Checking working tree for mass deletions..."
    
    DELETED=$(git status --short | grep -c "^ D" || true)
    TOTAL=$(git status --short | wc -l)
    
    if [ "$DELETED" -gt 100 ]; then
        echo -e "${RED}🚨 CATASTROPHE DETECTED!${NC}"
        echo -e "${RED}Working tree has $DELETED deleted files!${NC}"
        echo ""
        echo "This matches the pattern of the Nov 14, 2025 incident."
        echo ""
        echo "Recovery options:"
        echo "  1. git restore .           # Restore all deleted files"
        echo "  2. git checkout HEAD -- .  # Reset to last commit"
        echo "  3. git status              # Review what's deleted"
        echo ""
        return 1
    elif [ "$DELETED" -gt 10 ]; then
        echo -e "${YELLOW}⚠️  Warning: $DELETED files are deleted${NC}"
        echo ""
        git status --short | grep "^ D" | head -20
        echo ""
    else
        echo -e "${GREEN}✅ No mass deletions detected${NC}"
    fi
}

# Function: Validate git operations
validate_git_operation() {
    local operation=$1
    
    case "$operation" in
        "commit")
            echo "📝 Validating commit..."
            
            STAGED_DEL=$(git diff --cached --name-status | grep -c "^D" || true)
            
            if [ "$STAGED_DEL" -gt 100 ]; then
                echo -e "${RED}❌ BLOCKED: Attempting to commit $STAGED_DEL deletions${NC}"
                echo "Use --no-verify to override (NOT recommended)"
                return 1
            fi
            
            echo -e "${GREEN}✅ Commit validation passed${NC}"
            ;;
            
        "push")
            echo "📤 Validating push..."
            
            # Check if push would delete many files on remote
            LOCAL_FILES=$(git ls-tree -r HEAD --name-only | wc -l)
            
            if [ "$LOCAL_FILES" -lt 100 ]; then
                echo -e "${RED}⚠️  WARNING: Only $LOCAL_FILES files in repository${NC}"
                echo "This is suspiciously low. Normal count is ~2,000+ files."
                echo ""
                read -p "Are you ABSOLUTELY SURE you want to push? (type 'yes'): " confirm
                if [ "$confirm" != "yes" ]; then
                    echo -e "${RED}Push cancelled${NC}"
                    return 1
                fi
            fi
            
            echo -e "${GREEN}✅ Push validation passed${NC}"
            ;;
            
        *)
            echo "Unknown operation: $operation"
            return 1
            ;;
    esac
}

# Function: Create safety backup
create_safety_backup() {
    echo "💾 Creating safety backup..."
    
    BACKUP_DIR=".git/safety_backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/pre_operation_${TIMESTAMP}.bundle"
    
    git bundle create "$BACKUP_FILE" HEAD --all 2>/dev/null
    
    if [ -f "$BACKUP_FILE" ]; then
        echo -e "${GREEN}✅ Safety backup created: $BACKUP_FILE${NC}"
        
        # Keep only last 10 backups
        ls -t "$BACKUP_DIR"/*.bundle | tail -n +11 | xargs -r rm
    else
        echo -e "${YELLOW}⚠️  Could not create safety backup${NC}"
    fi
}

# Function: Install git command wrappers
install_wrappers() {
    echo "🔧 Installing git command safety wrappers..."
    
    # Create git alias for safe commit
    git config alias.safe-commit '!f() { 
        bash scripts/git/prevent_catastrophe.sh validate commit && git commit "$@"
    }; f'
    
    # Create git alias for safe push
    git config alias.safe-push '!f() {
        bash scripts/git/prevent_catastrophe.sh validate push && git push "$@"
    }; f'
    
    echo -e "${GREEN}✅ Git aliases installed:${NC}"
    echo "   git safe-commit   # Protected commit command"
    echo "   git safe-push     # Protected push command"
    echo ""
}

# Function: Check system health
health_check() {
    echo "🏥 Running system health check..."
    echo ""
    
    # File count
    TOTAL_FILES=$(find . -type f -not -path "./.git/*" -not -path "./node_modules/*" | wc -l)
    echo "📁 Total files: $TOTAL_FILES"
    
    if [ "$TOTAL_FILES" -lt 500 ]; then
        echo -e "${RED}⚠️  File count is suspiciously low!${NC}"
        echo "Expected: ~2,500 files. Found: $TOTAL_FILES"
    else
        echo -e "${GREEN}✅ File count healthy${NC}"
    fi
    
    # Git status
    echo ""
    echo "📊 Git status:"
    git status --short | head -20
    
    # Critical files
    echo ""
    echo "🔑 Critical files:"
    CRITICAL=("README.md" "package.json" "requirements.txt" "pyproject.toml" "Makefile")
    for file in "${CRITICAL[@]}"; do
        if [ -f "$file" ]; then
            echo -e "   ${GREEN}✓${NC} $file"
        else
            echo -e "   ${RED}✗${NC} $file (MISSING!)"
        fi
    done
    
    echo ""
}

# Main command router
case "${1:-check}" in
    "check")
        check_working_tree
        ;;
    "validate")
        validate_git_operation "$2"
        ;;
    "backup")
        create_safety_backup
        ;;
    "install")
        install_wrappers
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 {check|validate|backup|install|health}"
        echo ""
        echo "Commands:"
        echo "  check     - Check for mass deletions in working tree"
        echo "  validate  - Validate git operation (commit|push)"
        echo "  backup    - Create safety backup bundle"
        echo "  install   - Install git command wrappers"
        echo "  health    - Run system health check"
        exit 1
        ;;
esac
