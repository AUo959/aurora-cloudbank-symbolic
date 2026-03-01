#!/bin/bash

# Aurora CloudBank - Robust Commit Manager
# Handles consistent commit and push operations with error handling

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAX_RETRIES=3
RETRY_DELAY=2
COMMIT_BATCH_SIZE=10

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Check git status
check_git_status() {
    log "Checking git repository status..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
        exit 1
    fi
    
    # Check if there are uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        warning "There are uncommitted changes"
        return 1
    fi
    
    # Check if we're ahead of remote
    local ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
    if [ "$ahead" -gt 0 ]; then
        warning "Branch is $ahead commits ahead of remote"
        return 2
    fi
    
    return 0
}

# Commit staged changes
commit_changes() {
    local message="$1"
    log "Committing changes with message: $message"
    
    # Check if there are staged changes
    if git diff --cached --quiet; then
        warning "No staged changes to commit"
        return 0
    fi
    
    # Commit with signed commit
    if git commit -S -m "$message"; then
        success "Changes committed successfully"
        return 0
    else
        error "Failed to commit changes"
        return 1
    fi
}

# Push changes with retry mechanism
push_changes() {
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log "Attempting to push changes (attempt $((retry_count + 1))/$MAX_RETRIES)..."
        
        # Check network connectivity
        if ! ping -c 1 github.com > /dev/null 2>&1; then
            warning "Network connectivity issues detected"
            sleep $RETRY_DELAY
            ((retry_count++))
            continue
        fi
        
        # Try to push
        if git push origin main; then
            success "Changes pushed successfully"
            return 0
        else
            error "Push failed (attempt $((retry_count + 1)))"
            
            # Check if we need to pull first
            if git fetch origin main 2>/dev/null; then
                local behind=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo "0")
                if [ "$behind" -gt 0 ]; then
                    warning "Remote has $behind new commits, attempting rebase..."
                    if git rebase origin/main; then
                        log "Rebase successful, retrying push..."
                        continue
                    else
                        error "Rebase failed, manual intervention required"
                        return 1
                    fi
                fi
            fi
            
            sleep $RETRY_DELAY
            ((retry_count++))
        fi
    done
    
    error "Failed to push after $MAX_RETRIES attempts"
    return 1
}

# Batch push for large number of commits
batch_push() {
    local ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
    
    if [ "$ahead" -gt "$COMMIT_BATCH_SIZE" ]; then
        log "Large number of commits ($ahead) detected, using batch push strategy"
        
        # Create a temporary branch for batch pushing
        local temp_branch="temp-batch-$(date +%s)"
        git checkout -b "$temp_branch"
        
        # Push in batches
        local commits_pushed=0
        while [ $commits_pushed -lt $ahead ]; do
            local batch_end=$((commits_pushed + COMMIT_BATCH_SIZE))
            if [ $batch_end -gt $ahead ]; then
                batch_end=$ahead
            fi
            
            log "Pushing batch $((commits_pushed + 1))-$batch_end of $ahead commits..."
            
            # Reset to specific commit range
            git reset --hard "HEAD~$((ahead - batch_end))"
            
            if push_changes; then
                commits_pushed=$batch_end
                success "Batch push completed: $commits_pushed/$ahead commits"
            else
                error "Batch push failed"
                git checkout main
                git branch -D "$temp_branch"
                return 1
            fi
        done
        
        # Clean up
        git checkout main
        git branch -D "$temp_branch"
        success "All batches pushed successfully"
        return 0
    else
        return 1  # Use regular push
    fi
}

# Main execution
main() {
    log "Aurora CloudBank - Robust Commit Manager Starting..."
    
    # Check git status
    local status_code
    check_git_status
    status_code=$?
    
    case $status_code in
        0)
            success "Git repository is clean and up to date"
            ;;
        1)
            log "Uncommitted changes detected, staging all changes..."
            git add .
            if [ -n "${1:-}" ]; then
                commit_changes "$1"
            else
                commit_changes "🔧 Aurora CloudBank - Automated commit $(date '+%Y-%m-%d %H:%M:%S')"
            fi
            ;;
        2)
            log "Commits ahead of remote detected, attempting push..."
            ;;
    esac
    
    # Try batch push first for large commits
    if ! batch_push; then
        # Regular push
        if ! push_changes; then
            error "Push operation failed"
            exit 1
        fi
    fi
    
    success "Robust commit manager completed successfully"
    
    # Final status check
    log "Final repository status:"
    git status --porcelain
    local ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
    if [ "$ahead" -eq 0 ]; then
        success "Repository is now synchronized with remote"
    else
        warning "Repository is still $ahead commits ahead of remote"
    fi
}

# Run main function with all arguments
main "$@"
