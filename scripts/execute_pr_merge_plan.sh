#!/bin/bash
# Aurora CloudBank - PR Merge Execution Script
# Thread: T1→T8→T9→INFINITE | Anchor: PR-MERGE-STRATEGY-V1
# 
# Usage: ./scripts/execute_pr_merge_plan.sh [phase]
# Phases: 1, 2, 3, 4, or 'all'

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verify we're in the correct directory
if [ ! -f "aurora_api.py" ]; then
    log_error "Must be run from aurora-cloudbank-symbolic root directory"
    exit 1
fi

# Verify gh CLI is available
if ! command -v gh &> /dev/null; then
    log_error "GitHub CLI (gh) not found. Please install it first."
    exit 1
fi

# Function to verify main branch health
verify_main_health() {
    log_info "Verifying main branch health..."
    
    git checkout main
    git pull origin main
    
    log_info "Running tests..."
    if make test; then
        log_success "All tests passing on main"
    else
        log_error "Tests failing on main branch"
        return 1
    fi
    
    log_info "Running lint checks..."
    if make lint-tools; then
        log_success "Lint checks passing"
    else
        log_warning "Lint checks have issues (non-blocking)"
    fi
}

# Phase 1: Quick Wins
execute_phase_1() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "PHASE 1: Quick Wins - Low-Risk Utility Fixes"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # PR #255
    log_info "Merging PR #255: Fix line ending preservation"
    gh pr view 255 --json title,state,mergeable --jq .
    read -p "Approve and merge PR #255? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh pr review 255 --approve --body "LGTM - Clean fix for line endings"
        gh pr merge 255 --squash --delete-branch
        log_success "PR #255 merged"
    else
        log_warning "Skipped PR #255"
    fi
    
    # PR #254
    log_info "Merging PR #254: Replace fragile date string slicing"
    gh pr view 254 --json title,state,mergeable --jq .
    read -p "Approve and merge PR #254? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh pr review 254 --approve --body "LGTM - Improves git date handling"
        gh pr merge 254 --squash --delete-branch
        log_success "PR #254 merged"
    else
        log_warning "Skipped PR #254"
    fi
    
    # PR #253
    log_info "Merging PR #253: Extract git root traversal utility"
    gh pr view 253 --json title,state,mergeable --jq .
    read -p "Approve and merge PR #253? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh pr review 253 --approve --body "LGTM - Good refactoring"
        gh pr merge 253 --squash --delete-branch
        log_success "PR #253 merged"
    else
        log_warning "Skipped PR #253"
    fi
    
    # Verify health after Phase 1
    verify_main_health
    
    log_success "Phase 1 complete! 3 PRs merged (or skipped by user)"
}

# Phase 2: Critical Security Fix
execute_phase_2() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "PHASE 2: Critical Security Fix - ReDoS Vulnerability"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    log_info "Current status of PR #224:"
    gh pr view 224 --json title,isDraft,mergeable,statusCheckRollup --jq .
    
    log_info "Updating branch with latest main..."
    git fetch origin main
    git checkout copilot/fix-regex-dos-vulnerability
    
    if git merge origin/main; then
        log_success "Branch updated successfully (no conflicts)"
    else
        log_warning "Merge conflicts detected - resolve them and run:"
        log_warning "  git add ."
        log_warning "  git commit -m 'Merge main into fix-regex-dos-vulnerability'"
        log_warning "  git push origin copilot/fix-regex-dos-vulnerability"
        log_warning "  ./scripts/execute_pr_merge_plan.sh 2"
        exit 1
    fi
    
    git push origin copilot/fix-regex-dos-vulnerability
    log_success "Branch pushed to remote"
    
    log_info "Checking Codacy status..."
    gh pr checks 224 --watch
    
    read -p "Are all CI checks passing now? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Fix CI issues before proceeding"
        log_warning "Run this phase again when ready: ./scripts/execute_pr_merge_plan.sh 2"
        exit 1
    fi
    
    read -p "Convert PR #224 from draft to ready? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh pr ready 224
        log_success "PR #224 marked as ready for review"
    fi
    
    log_info "Waiting for approval..."
    log_warning "Manual step: Get PR approved, then run:"
    log_warning "  gh pr merge 224 --squash --delete-branch"
    log_warning "Or proceed interactively:"
    
    read -p "Approve and merge PR #224 now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh pr review 224 --approve --body "LGTM - Critical security fix with infrastructure improvements"
        gh pr merge 224 --squash --delete-branch
        log_success "PR #224 merged!"
    else
        log_warning "PR #224 ready but not merged - merge manually when approved"
    fi
    
    # Verify health
    verify_main_health
    
    log_success "Phase 2 complete!"
}

# Phase 3: CodeQL Cleanup
execute_phase_3() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "PHASE 3: CodeQL Cleanup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    log_info "Current status of PR #251:"
    gh pr view 251 --json title,state,mergeable,statusCheckRollup --jq '.statusCheckRollup[] | select(.conclusion == "FAILURE")'
    
    log_warning "PR #251 has CI failures that must be fixed first"
    log_info "Investigation steps:"
    echo "  1. gh pr checks 251 --watch"
    echo "  2. Review SonarCloud issues"
    echo "  3. Review Codacy Security issues"
    echo "  4. Fix issues on branch"
    echo "  5. Re-run this phase"
    
    read -p "Have you fixed the CI issues? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Fix issues first, then re-run: ./scripts/execute_pr_merge_plan.sh 3"
        exit 1
    fi
    
    log_info "Verifying CI status..."
    if gh pr checks 251 | grep -q "fail"; then
        log_error "CI checks still failing - cannot proceed"
        exit 1
    fi
    
    read -p "Approve and merge PR #251? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh pr review 251 --approve --body "LGTM - CodeQL improvements"
        gh pr merge 251 --squash --delete-branch
        log_success "PR #251 merged"
    else
        log_warning "Skipped PR #251"
    fi
    
    # Verify health
    verify_main_health
    
    log_success "Phase 3 complete!"
}

# Phase 4: Advanced Features (Conditional)
execute_phase_4() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "PHASE 4: Advanced Features (Conditional)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    log_info "Current status of PR #252:"
    gh pr view 252 --json title,state,mergeable,statusCheckRollup --jq '.statusCheckRollup[] | select(.conclusion == "FAILURE")'
    
    log_warning "PR #252 has 5 CI failures - this is a complex feature"
    
    echo ""
    log_info "Options:"
    echo "  [1] Attempt to fix CI issues and merge (may take 2-4 hours)"
    echo "  [2] Defer to next sprint (recommended)"
    echo "  [3] Skip this phase"
    
    read -p "Choose option (1/2/3): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            log_info "Proceeding with CI fix attempt..."
            gh pr checks 252 --watch
            log_warning "Manual investigation required:"
            echo "  - Check CI logs"
            echo "  - Check CodeQL issues"
            echo "  - Check SonarCloud issues"
            echo "  - Fix issues systematically"
            echo "  - Re-run this phase when ready"
            exit 0
            ;;
        2)
            log_info "Deferring PR #252 to next sprint..."
            gh pr edit 252 --add-label "future-milestone"
            gh pr comment 252 --body "Deferring to next sprint due to CI failures. Requires systematic investigation and fixes."
            gh pr ready 252 --undo  # Convert to draft if not already
            log_success "PR #252 marked for future work"
            ;;
        3)
            log_warning "Skipped Phase 4"
            ;;
        *)
            log_error "Invalid option"
            exit 1
            ;;
    esac
    
    log_success "Phase 4 complete!"
}

# Main execution
main() {
    local phase="${1:-}"
    
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  Aurora CloudBank - PR Merge Execution Script               ║"
    echo "║  Thread: T1→T8→T9→INFINITE | Anchor: PR-MERGE-STRATEGY-V1  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [ -z "$phase" ]; then
        log_error "Usage: $0 [phase]"
        echo "Phases:"
        echo "  1     - Quick wins (PRs #255, #254, #253)"
        echo "  2     - Security fix (PR #224)"
        echo "  3     - CodeQL cleanup (PR #251)"
        echo "  4     - Advanced features (PR #252)"
        echo "  all   - Execute all phases"
        exit 1
    fi
    
    case $phase in
        1)
            execute_phase_1
            ;;
        2)
            execute_phase_2
            ;;
        3)
            execute_phase_3
            ;;
        4)
            execute_phase_4
            ;;
        all)
            execute_phase_1
            execute_phase_2
            execute_phase_3
            execute_phase_4
            
            echo ""
            echo "╔══════════════════════════════════════════════════════════════╗"
            echo "║              ALL PHASES COMPLETE                             ║"
            echo "╚══════════════════════════════════════════════════════════════╝"
            log_success "All PR merge phases completed successfully!"
            
            # Final verification
            verify_main_health
            
            log_info "Post-merge checklist:"
            echo "  [ ] Update CHANGELOG.md"
            echo "  [ ] Tag new release if appropriate"
            echo "  [ ] Notify team of merged changes"
            echo "  [ ] Monitor Codespace initialization times"
            ;;
        *)
            log_error "Invalid phase: $phase"
            exit 1
            ;;
    esac
}

# Run main with all arguments
main "$@"
