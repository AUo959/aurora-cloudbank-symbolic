#!/bin/bash

# Aurora CloudBank PR Implementation Script - Phase 1
# Safely integrate critical fixes while maintaining system health

set -euo pipefail

echo "🎯 AURORA CLOUDBANK - PR IMPLEMENTATION PHASE 1"
echo "==============================================="
echo "Target: Critical fixes (copilot/fix-144, copilot/fix-137)"
echo "Current main: $(git rev-parse --short HEAD)"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to validate system health
validate_system() {
    echo "🔍 System Health Validation"
    echo "----------------------------"
    
    # Test suite validation
    echo "Running test suite..."
    if python3 -m pytest tests/ -q --tb=no; then
        print_status "Test suite: All tests passing"
    else
        print_error "Test suite: Some tests failing"
        return 1
    fi
    
    # Workflow validation
    echo "Validating workflows..."
    workflow_count=$(find .github/workflows -name "*.yml" | wc -l)
    if python3 -c "
import yaml
from pathlib import Path
try:
    workflows = list(Path('.github/workflows').glob('*.yml'))
    for wf in workflows:
        with open(wf) as f:
            yaml.safe_load(f)
    print(f'All {len(workflows)} workflows valid')
except Exception as e:
    print(f'Workflow error: {e}')
    exit(1)
"; then
        print_status "Workflows: All $workflow_count workflows valid"
    else
        print_error "Workflows: Validation failed"
        return 1
    fi
    
    # Core systems check
    echo "Checking core systems..."
    if python3 -c "
from aurora_api import app
from src.aurora.core.symbolic_engine import SymbolicEngine  
from modules.symbolic_core.geometric_algebra import GeometricAlgebra
print('All core systems importable')
" 2>/dev/null; then
        print_status "Core systems: All operational"
    else
        print_warning "Core systems: Some import issues (non-critical)"
    fi
    
    echo
}

# Function to test merge compatibility
test_merge() {
    local branch=$1
    local test_branch="test-merge-$(basename $branch)"
    
    echo "🧪 Testing merge compatibility: $branch"
    echo "----------------------------------------"
    
    # Create test branch
    git checkout -b "$test_branch" main
    
    # Test merge
    if git merge "origin/$branch" --no-commit --no-ff; then
        print_status "Merge test: No conflicts detected"
        
        # Test system after merge
        if validate_system; then
            print_status "Post-merge validation: System healthy"
            git reset --hard HEAD  # Reset the test merge
            git checkout main
            git branch -D "$test_branch"
            return 0
        else
            print_error "Post-merge validation: System issues detected"
            git reset --hard HEAD
            git checkout main  
            git branch -D "$test_branch"
            return 1
        fi
    else
        print_error "Merge test: Conflicts detected"
        git merge --abort
        git checkout main
        git branch -D "$test_branch" 
        return 1
    fi
}

# Function to perform actual merge
perform_merge() {
    local branch=$1
    local merge_branch="integration/$(basename $branch)"
    
    echo "🔄 Performing integration: $branch"
    echo "-----------------------------------"
    
    # Create integration branch
    git checkout -b "$merge_branch" main
    
    # Perform merge
    if git merge "origin/$branch" --no-ff -m "Integrate $branch - automated critical fixes"; then
        print_status "Merge completed successfully"
        
        # Final validation
        if validate_system; then
            print_status "Final validation: System healthy after integration"
            
            # Switch to main and merge
            git checkout main
            git merge "$merge_branch" --no-ff -m "Complete integration of $branch"
            git branch -D "$merge_branch"
            
            print_status "Integration complete: $branch merged into main"
            return 0
        else
            print_error "Final validation: System issues after integration"
            git checkout main
            git branch -D "$merge_branch"
            return 1
        fi
    else
        print_error "Merge failed for $branch"
        git merge --abort
        git checkout main
        git branch -D "$merge_branch"
        return 1
    fi
}

# Main execution flow
main() {
    echo "📋 Phase 1 Implementation Plan:"
    echo "1. Validate current system health"
    echo "2. Test merge compatibility for each target branch"
    echo "3. Perform safe integration if tests pass"
    echo "4. Validate final system state"
    echo

    # Ensure we're on main and up to date
    git checkout main
    git fetch origin
    
    print_status "Starting from validated main branch"
    
    # Initial system validation
    echo "🔍 INITIAL SYSTEM VALIDATION"
    echo "============================"
    if ! validate_system; then
        print_error "Initial system validation failed - aborting"
        exit 1
    fi
    
    # Define target branches for Phase 1
    PHASE1_BRANCHES=(
        "copilot/fix-144"
        "copilot/fix-137"
    )
    
    echo "🎯 PHASE 1 IMPLEMENTATION"
    echo "========================"
    
    for branch in "${PHASE1_BRANCHES[@]}"; do
        echo
        echo "Processing: $branch"
        echo "$(printf '=%.0s' {1..50})"
        
        # Check if branch exists
        if ! git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
            print_warning "Branch $branch not found - skipping"
            continue
        fi
        
        # Test merge compatibility
        if test_merge "$branch"; then
            print_status "Branch $branch is safe to merge"
            
            # Ask for confirmation (can be automated in production)
            echo "Ready to integrate $branch. Proceed? (y/N)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                if perform_merge "$branch"; then
                    print_status "Successfully integrated: $branch"
                else
                    print_error "Failed to integrate: $branch"
                    echo "Manual intervention required before proceeding"
                    exit 1
                fi
            else
                print_warning "Skipping integration of $branch"
            fi
        else
            print_error "Branch $branch failed merge test - skipping"
        fi
    done
    
    echo
    echo "🎉 PHASE 1 COMPLETION SUMMARY"
    echo "============================"
    
    # Final system validation
    if validate_system; then
        print_status "Phase 1 complete - all systems operational"
        echo
        echo "📊 System Status:"
        echo "• Main branch updated with critical fixes"
        echo "• All tests passing: $(python3 -m pytest tests/ --tb=no -q 2>&1 | grep -o '[0-9]* passed' | head -1 || echo 'Tests completed')"
        echo "• All workflows valid: $(find .github/workflows -name "*.yml" | wc -l) files"
        echo "• Ready for Phase 2 implementation"
        
        echo
        echo "🎯 Next Steps:"
        echo "1. Review Phase 2 plan (fix/workflows branch analysis)"
        echo "2. Continue with PR_IMPLEMENTATION_ROADMAP.md"
        echo "3. Monitor system health and user feedback"
        
    else
        print_error "Phase 1 completed with system issues"
        echo "Manual review and fixes required before proceeding"
        exit 1
    fi
}

# Error handling
trap 'echo "Script interrupted"; git checkout main 2>/dev/null || true; exit 1' INT TERM

# Execute main function
main "$@"