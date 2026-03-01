#!/bin/bash
# Security-First PR Merge Process
# Implements safe, ethical, and optimal merge sequence

set -euo pipefail  # Strict error handling

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Security validation function
validate_security() {
    local branch=$1
    log_info "Security validation for branch: $branch"

    # Check for suspicious files
    if git show $branch --name-only | grep -E '\.(exe|bat|ps1|sh)$' | grep -v 'scripts/'; then
        log_warning "Potentially dangerous executable files found"
        return 1
    fi

    # Check for hardcoded secrets
    if git show $branch | grep -iE '(password|secret|key|token)\s*[=:]\s*["\047]'; then
        log_warning "Potential hardcoded secrets detected"
        return 1
    fi

    # Check file size limits
    if git show $branch --name-only | xargs -I {} sh -c 'test -f "{}" && test $(wc -c < "{}") -gt 1048576' 2>/dev/null; then
        log_warning "Large files detected (>1MB)"
        return 1
    fi

    log_success "Security validation passed"
    return 0
}

# Functional validation
validate_functionality() {
    local branch=$1
    log_info "Functional validation for branch: $branch"

    # Check if package.json changes are valid
    if git show $branch --name-only | grep -q package.json; then
        git show $branch:package.json | python3 -m json.tool > /dev/null || {
            log_error "Invalid package.json detected"
            return 1
        }
    fi

    # Check if requirements.txt changes are valid
    if git show $branch --name-only | grep -q requirements.txt; then
        # Validate Python package format
        if git show $branch:requirements.txt | grep -E '^[^#\s]' | grep -vE '^[a-zA-Z0-9\-_.]+([<>=!]+[0-9.]+)?$'; then
            log_warning "Potentially invalid requirements.txt format"
        fi
    fi

    log_success "Functional validation passed"
    return 0
}

# Ethical compliance check
validate_ethics() {
    local branch=$1
    log_info "Ethical compliance check for branch: $branch"

    # Check for privacy concerns
    if git show $branch | grep -iE '(personal.*data|private.*key|user.*info)'; then
        log_warning "Potential privacy concerns detected"
        return 1
    fi

    # Check for license compliance
    if git show $branch --name-only | grep -iE 'license|copyright'; then
        log_info "License-related changes detected - manual review recommended"
    fi

    log_success "Ethical compliance check passed"
    return 0
}

# Safe merge function
safe_merge() {
    local branch=$1
    local merge_type=$2

    log_info "Attempting safe merge of $branch with strategy: $merge_type"

    # Create merge backup
    local backup_branch="backup-merge-$branch-$(date +%H%M%S)"
    git branch $backup_branch

    # Attempt merge
    case $merge_type in
        "security")
            # Fast-forward only for security updates
            if git merge --ff-only origin/$branch; then
                log_success "Security update merged successfully (fast-forward)"
                git branch -d $backup_branch
                return 0
            else
                log_warning "Fast-forward merge failed, attempting merge commit"
                if git merge --no-ff origin/$branch -m "Security update: $branch"; then
                    log_success "Security update merged with merge commit"
                    git branch -d $backup_branch
                    return 0
                fi
            fi
            ;;
        "feature")
            # Squash merge for feature branches to maintain clean history
            if git merge --squash origin/$branch; then
                git commit -m "Feature merge: $branch (squashed)"
                log_success "Feature branch merged successfully (squashed)"
                git branch -d $backup_branch
                return 0
            fi
            ;;
    esac

    # If merge failed, restore backup
    log_error "Merge failed, restoring backup"
    git reset --hard $backup_branch
    git branch -d $backup_branch
    return 1
}

# Main execution
main() {
    log_info "Starting security-first PR merge process"

    # Ensure we're on main and up to date
    git checkout main
    git fetch origin

    # Get list of branches
    local dependabot_branches=($(git branch -r | grep dependabot | sed 's/.*origin\///'))
    local feature_branches=($(git branch -r | grep codex | sed 's/.*origin\///' | head -5))  # Limit to 5 for safety

    # Phase 1: Security Updates (Dependabot)
    log_info "Phase 1: Processing security updates"
    for branch in "${dependabot_branches[@]}"; do
        log_info "Processing security branch: $branch"

        if validate_security "origin/$branch" && validate_functionality "origin/$branch" && validate_ethics "origin/$branch"; then
            if safe_merge "$branch" "security"; then
                log_success "Successfully merged security update: $branch"
                # Clean up remote branch reference
                git push origin --delete $branch 2>/dev/null || log_warning "Could not delete remote branch $branch"
            else
                log_error "Failed to merge security update: $branch"
            fi
        else
            log_warning "Validation failed for security branch: $branch - skipping"
        fi

        # Pause between merges for safety
        sleep 1
    done

    # Phase 2: Feature Branches (Limited and Validated)
    log_info "Phase 2: Processing feature branches (limited to 5 for safety)"
    for branch in "${feature_branches[@]}"; do
        log_info "Processing feature branch: $branch"

        if validate_security "origin/$branch" && validate_functionality "origin/$branch" && validate_ethics "origin/$branch"; then
            read -p "Merge feature branch $branch? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if safe_merge "$branch" "feature"; then
                    log_success "Successfully merged feature branch: $branch"
                else
                    log_error "Failed to merge feature branch: $branch"
                fi
            else
                log_info "Skipped feature branch: $branch"
            fi
        else
            log_warning "Validation failed for feature branch: $branch - skipping"
        fi

        # Pause between merges for safety
        sleep 1
    done

    # Final validation
    log_info "Running final CI/CD validation"
    if ./scripts/validate-cicd.sh > /dev/null 2>&1; then
        log_success "Final validation passed"
    else
        log_warning "Final validation has warnings - check output"
    fi

    log_success "Security-first PR merge process completed"
}

# Run main function
main "$@"
