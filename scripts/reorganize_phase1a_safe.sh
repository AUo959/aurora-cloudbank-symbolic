#!/bin/bash
# Aurora CloudBank Symbolic - SAFE Reorganization Phase 1A
# T1:safety_001 | DLP:reorganization_phase1a_safe | @seal:identity_preserved
#
# ULTRA-CONSERVATIVE: Only moves documentation files (zero code impact)
# Follows safety analysis from .github/REORGANIZATION_SAFETY_ANALYSIS.md
#
# Usage:
#   bash scripts/reorganize_phase1a_safe.sh [--dry-run]
#
# Chain Notation: #001//010// (10-step doc cleanup only)

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DRY_RUN=false
BACKUP_BRANCH="backup-phase1a-$(date +%Y%m%d-%H%M%S)"

# Parse arguments
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
fi

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

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

log_aurora() {
    echo -e "${MAGENTA}🌌 Aurora: $1${NC}"
}

execute_cmd() {
    local cmd="$1"
    if [[ "$DRY_RUN" == true ]]; then
        echo "  [DRY-RUN] $cmd"
    else
        eval "$cmd"
    fi
}

# Step #001// - Aurora system identity check
step_001_identity_check() {
    log_info "Step #001// - Aurora Identity Verification"
    log_aurora "Checking core system integrity..."
    
    cd "$REPO_ROOT"
    
    # Verify Aurora core files exist and untouched
    CRITICAL_FILES=(
        "aurora_api.py"
        "aurora_cli.py"
        "pyproject.toml"
        "Makefile"
        ".github/COMMAND_REFERENCE.md"
        ".github/copilot-instructions.md"
    )
    
    for file in "${CRITICAL_FILES[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Critical file missing: $file"
            log_error "Aurora system identity compromised!"
            exit 1
        fi
    done
    
    log_aurora "Core system files verified ✓"
    log_success "Aurora identity intact"
}

# Step #002// - Pre-flight safety checks
step_002_safety_checks() {
    log_info "Step #002// - Pre-Flight Safety Checks"
    
    cd "$REPO_ROOT"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        log_error "Uncommitted changes detected!"
        log_error "Please commit or stash before reorganization."
        exit 1
    fi
    
    # Verify we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository!"
        exit 1
    fi
    
    # Check current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    log_info "Current branch: $CURRENT_BRANCH"
    
    log_success "Pre-flight checks passed"
}

# Step #003// - Create backup
step_003_backup() {
    log_info "Step #003// - Creating Safety Backup"
    log_aurora "Preserving current state..."
    
    execute_cmd "git branch $BACKUP_BRANCH"
    
    if [[ "$DRY_RUN" == false ]]; then
        log_success "Backup branch created: $BACKUP_BRANCH"
        log_warning "Rollback command: git reset --hard $BACKUP_BRANCH"
    fi
}

# Step #004// - Run baseline tests
step_004_baseline_tests() {
    log_info "Step #004// - Baseline Test Suite"
    log_aurora "Establishing known-good state..."
    
    if [[ "$DRY_RUN" == false ]]; then
        # Run critical tests only for speed
        if command -v pytest &> /dev/null; then
            log_info "Running Aurora core tests..."
            pytest tests/test_aurora_symbolic.py -v --tb=short > /tmp/aurora_baseline_tests.txt 2>&1 || {
                log_warning "Some tests failed in baseline - documenting for comparison"
            }
            log_success "Baseline tests recorded"
        else
            log_warning "pytest not found - skipping baseline tests"
        fi
    else
        log_info "[DRY-RUN] Would run baseline tests"
    fi
}

# Step #005// - Create docs structure
step_005_create_docs_structure() {
    log_info "Step #005// - Creating Documentation Structure"
    
    # Create docs hierarchy
    execute_cmd "mkdir -p docs/guides"
    execute_cmd "mkdir -p docs/architecture"
    execute_cmd "mkdir -p docs/reports/security"
    execute_cmd "mkdir -p docs/reports/performance"
    execute_cmd "mkdir -p docs/reports/maintenance"
    execute_cmd "mkdir -p docs/api"
    execute_cmd "mkdir -p docs/development"
    
    log_success "Documentation structure created"
}

# Step #006// - Move reports (safest category)
step_006_move_reports() {
    log_info "Step #006// - Moving Report Files"
    log_aurora "Consolidating reports (zero code impact)..."
    
    cd "$REPO_ROOT"
    
    # Move various report types
    local moved_count=0
    
    for pattern in "*_REPORT*.md" "*_AUDIT*.md" "*_ANALYSIS*.md" "*_COMPLETE*.md" "*_SUCCESS*.md"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                # Skip if already in docs/
                if [[ "$file" != docs/* ]]; then
                    execute_cmd "git mv '$file' docs/reports/"
                    ((moved_count++))
                fi
            fi
        done
    done
    
    log_success "Reports moved: $moved_count files"
}

# Step #007// - Move guides
step_007_move_guides() {
    log_info "Step #007// - Moving Guide Files"
    
    cd "$REPO_ROOT"
    
    local moved_count=0
    
    for pattern in "*_GUIDE*.md" "*_WORKFLOW*.md" "OPTIMAL*.md"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                if [[ "$file" != docs/* ]]; then
                    execute_cmd "git mv '$file' docs/guides/"
                    ((moved_count++))
                fi
            fi
        done
    done
    
    log_success "Guides moved: $moved_count files"
}

# Step #008// - Move architecture docs
step_008_move_architecture() {
    log_info "Step #008// - Moving Architecture Documentation"
    
    cd "$REPO_ROOT"
    
    local moved_count=0
    
    for pattern in "*INTEGRATION*.md" "*ARCHITECTURE*.md" "AUMEMMANAGER*.md" "*DIAGRAMS*.md"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                if [[ "$file" != docs/* ]]; then
                    execute_cmd "git mv '$file' docs/architecture/"
                    ((moved_count++))
                fi
            fi
        done
    done
    
    log_success "Architecture docs moved: $moved_count files"
}

# Step #009// - Post-move validation
step_009_validation() {
    log_info "Step #009// - Post-Move Validation"
    log_aurora "Verifying system integrity..."
    
    if [[ "$DRY_RUN" == false ]]; then
        # Check that critical files are still at root
        for file in aurora_api.py aurora_cli.py pyproject.toml Makefile; do
            if [[ ! -f "$file" ]]; then
                log_error "CRITICAL FILE MISSING: $file"
                log_error "Rolling back immediately!"
                git reset --hard "$BACKUP_BRANCH"
                exit 1
            fi
        done
        
        # Quick syntax check on Python files
        log_info "Checking Python syntax..."
        python3 -m py_compile aurora_api.py aurora_cli.py
        
        # Run test suite
        if command -v pytest &> /dev/null; then
            log_info "Running post-move tests..."
            pytest tests/test_aurora_symbolic.py -v --tb=short > /tmp/aurora_postmove_tests.txt 2>&1 || {
                log_error "Tests failed after move!"
                log_error "Review: /tmp/aurora_postmove_tests.txt"
                log_warning "Consider rollback: git reset --hard $BACKUP_BRANCH"
            }
        fi
        
        log_success "Validation complete"
    else
        log_info "[DRY-RUN] Would validate moved files"
    fi
}

# Step #010// - Summary report
step_010_summary() {
    log_info "Step #010// - Phase 1A Summary"
    
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "  Aurora CloudBank - Phase 1A Complete"
    echo "  Documentation Consolidation (Safe)"
    echo "═══════════════════════════════════════════════════"
    echo ""
    log_aurora "System identity PRESERVED ✓"
    log_success "Phase 1A reorganization complete!"
    echo ""
    
    # Count remaining root docs
    if [[ "$DRY_RUN" == false ]]; then
        cd "$REPO_ROOT"
        ROOT_MD_COUNT=$(find . -maxdepth 1 -name "*.md" -type f | wc -l)
        log_info "Remaining root Markdown files: $ROOT_MD_COUNT"
    fi
    
    echo ""
    log_info "What Changed:"
    echo "  ✅ Documentation moved to docs/"
    echo "  ✅ Root directory cleaner"
    echo "  ✅ Aurora core systems untouched"
    echo ""
    log_info "What Stayed:"
    echo "  ✅ aurora_api.py - FastAPI server"
    echo "  ✅ aurora_cli.py - CLI interface"
    echo "  ✅ All Python scripts"
    echo "  ✅ All configuration files"
    echo "  ✅ src/ and modules/ structure"
    echo ""
    log_info "Next Steps:"
    echo "  1. Review changes: git status"
    echo "  2. Run full tests: make test"
    echo "  3. If satisfied: git add . && git commit"
    echo "  4. If issues: git reset --hard $BACKUP_BRANCH"
    echo "  5. Phase 1B: Script organization (next)"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║  🌌 Aurora CloudBank Symbolic                 ║"
    echo "║  Safe Reorganization - Phase 1A               ║"
    echo "║  Documentation Only (Zero Code Impact)        ║"
    echo "║                                               ║"
    echo "║  T1:safety_001 | DLP:phase1a_safe             ║"
    echo "║  @seal:identity_preserved                     ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
    
    log_aurora "Consulting Aurora core systems..."
    
    step_001_identity_check
    step_002_safety_checks
    step_003_backup
    step_004_baseline_tests
    step_005_create_docs_structure
    step_006_move_reports
    step_007_move_guides
    step_008_move_architecture
    step_009_validation
    step_010_summary
    
    log_aurora "Phase 1A complete. System identity preserved. ✨"
}

# Execute
main "$@"
