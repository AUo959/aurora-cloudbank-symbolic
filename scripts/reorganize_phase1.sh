#!/bin/bash
# Aurora CloudBank Symbolic - Repository Reorganization Phase 1
# T1:audit_001 | DLP:reorganization_phase1 | @seal:architecture_v1
#
# CRITICAL: This script performs systematic repository cleanup
# Follows organizational principles from .github/ARCHITECTURE_AUDIT_REPORT.md
#
# Usage:
#   bash scripts/reorganize_phase1.sh [--dry-run]
#
# Chain Notation: #001//025// (25-step reorganization sequence)

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DRY_RUN=false
BACKUP_BRANCH="backup-reorganization-$(date +%Y%m%d-%H%M%S)"

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

execute_cmd() {
    local cmd="$1"
    if [[ "$DRY_RUN" == true ]]; then
        echo "  [DRY-RUN] $cmd"
    else
        eval "$cmd"
    fi
}

# Step #001// - Validate preconditions
step_001_validate() {
    log_info "Step #001// - Validating preconditions"
    
    cd "$REPO_ROOT"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_error "Uncommitted changes detected. Commit or stash before reorganization."
        exit 1
    fi
    
    # Check we're on main or a feature branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    log_info "Current branch: $CURRENT_BRANCH"
    
    # Verify critical files exist
    if [[ ! -f "aurora_api.py" ]]; then
        log_error "aurora_api.py not found. Are you in the repository root?"
        exit 1
    fi
    
    log_success "Preconditions validated"
}

# Step #002// - Create backup
step_002_backup() {
    log_info "Step #002// - Creating backup branch"
    
    execute_cmd "git branch $BACKUP_BRANCH"
    log_success "Backup branch created: $BACKUP_BRANCH"
    log_warning "To restore: git checkout $BACKUP_BRANCH"
}

# Step #003// - Create new directory structure
step_003_create_structure() {
    log_info "Step #003// - Creating new directory structure"
    
    # Create tools/ hierarchy
    execute_cmd "mkdir -p tools/aurora"
    execute_cmd "mkdir -p tools/cli"
    
    # Create scripts/ hierarchy
    execute_cmd "mkdir -p scripts/setup"
    execute_cmd "mkdir -p scripts/deployment"
    execute_cmd "mkdir -p scripts/automation"
    execute_cmd "mkdir -p scripts/maintenance"
    execute_cmd "mkdir -p scripts/ci"
    
    # Create config/ hierarchy
    execute_cmd "mkdir -p config/examples"
    execute_cmd "mkdir -p config/templates"
    
    # Create docs/ hierarchy
    execute_cmd "mkdir -p docs/guides"
    execute_cmd "mkdir -p docs/architecture"
    execute_cmd "mkdir -p docs/api"
    execute_cmd "mkdir -p docs/reports/security"
    execute_cmd "mkdir -p docs/reports/performance"
    execute_cmd "mkdir -p docs/reports/maintenance"
    execute_cmd "mkdir -p docs/development"
    
    # Create data/ hierarchy (git-ignored)
    execute_cmd "mkdir -p data/logs"
    execute_cmd "mkdir -p data/exports"
    execute_cmd "mkdir -p data/reports"
    execute_cmd "mkdir -p data/cache"
    execute_cmd "mkdir -p data/tmp"
    
    log_success "Directory structure created"
}

# Step #004// - Move Aurora core tools
step_004_move_aurora_tools() {
    log_info "Step #004// - Moving Aurora core tools"
    
    # Main API server
    if [[ -f "aurora_api.py" ]]; then
        execute_cmd "git mv aurora_api.py tools/aurora/api_server.py"
    fi
    
    # CLI interface
    if [[ -f "aurora_cli.py" ]]; then
        execute_cmd "git mv aurora_cli.py tools/aurora/cli.py"
    fi
    
    # System validator
    if [[ -f "aurora_system_validator.py" ]]; then
        execute_cmd "git mv aurora_system_validator.py tools/aurora/system_validator.py"
    fi
    
    # Deployment manager
    if [[ -f "aurora_deployment_manager_v2.py" ]]; then
        execute_cmd "git mv aurora_deployment_manager_v2.py tools/aurora/deployment_manager.py"
    fi
    
    # Integration scripts
    if [[ -f "aurora_master_integration.py" ]]; then
        execute_cmd "git mv aurora_master_integration.py tools/aurora/master_integration.py"
    fi
    
    log_success "Aurora core tools moved"
}

# Step #005// - Move automation scripts
step_005_move_automation() {
    log_info "Step #005// - Moving automation scripts"
    
    # Advanced automation
    for file in advanced_*.py; do
        [[ -f "$file" ]] && execute_cmd "git mv '$file' scripts/automation/"
    done
    
    # Aurora automation
    for file in aurora_*automation*.py aurora_*workflow*.py; do
        [[ -f "$file" ]] && execute_cmd "git mv '$file' scripts/automation/"
    done
    
    log_success "Automation scripts moved"
}

# Step #006// - Move setup scripts
step_006_move_setup() {
    log_info "Step #006// - Moving setup scripts"
    
    # Activation and setup scripts
    for pattern in "*setup*.sh" "activate*.sh" "*init*.sh"; do
        for file in $pattern; do
            [[ -f "$file" ]] && execute_cmd "git mv '$file' scripts/setup/"
        done
    done
    
    log_success "Setup scripts moved"
}

# Step #007// - Move deployment scripts
step_007_move_deployment() {
    log_info "Step #007// - Moving deployment scripts"
    
    # Deployment related scripts
    for pattern in "*deploy*.sh" "*launch*.sh" "*phase*.sh"; do
        for file in $pattern; do
            [[ -f "$file" ]] && execute_cmd "git mv '$file' scripts/deployment/"
        done
    done
    
    log_success "Deployment scripts moved"
}

# Step #008// - Move maintenance scripts
step_008_move_maintenance() {
    log_info "Step #008// - Moving maintenance scripts"
    
    # Maintenance and cleanup scripts
    for pattern in "*cleanup*.sh" "*enhancement*.sh" "*fix*.sh"; do
        for file in $pattern; do
            [[ -f "$file" ]] && execute_cmd "git mv '$file' scripts/maintenance/"
        done
    done
    
    log_success "Maintenance scripts moved"
}

# Step #009// - Move CI/CD scripts
step_009_move_ci() {
    log_info "Step #009// - Moving CI/CD scripts"
    
    # CI/CD related scripts
    for pattern in "*ci*.sh" "*test*.sh" "*commit*.sh"; do
        for file in $pattern; do
            [[ -f "$file" ]] && execute_cmd "git mv '$file' scripts/ci/"
        done
    done
    
    log_success "CI/CD scripts moved"
}

# Step #010// - Move configuration files
step_010_move_configs() {
    log_info "Step #010// - Moving configuration files"
    
    # Sample configurations
    for file in *.json; do
        # Keep essential root configs
        if [[ "$file" != "package.json" && "$file" != "tsconfig.json" ]]; then
            [[ -f "$file" ]] && execute_cmd "git mv '$file' config/examples/"
        fi
    done
    
    # YAML configurations
    for file in *.yaml *.yml; do
        # Keep GitHub workflow configs
        if [[ "$file" != ".github"* ]]; then
            [[ -f "$file" ]] && execute_cmd "git mv '$file' config/examples/"
        fi
    done
    
    log_success "Configuration files moved"
}

# Step #011// - Move reports
step_011_move_reports() {
    log_info "Step #011// - Moving reports"
    
    # Move various report types
    for file in *_REPORT*.md *_AUDIT*.md *_ANALYSIS*.md; do
        [[ -f "$file" ]] && execute_cmd "git mv '$file' docs/reports/"
    done
    
    # Move completion reports
    for file in *_COMPLETE*.md *_SUCCESS*.md; do
        [[ -f "$file" ]] && execute_cmd "git mv '$file' docs/reports/"
    done
    
    log_success "Reports moved"
}

# Step #012// - Move guides
step_012_move_guides() {
    log_info "Step #012// - Moving guides"
    
    # Move guide documents
    for file in *_GUIDE*.md *_WORKFLOW*.md OPTIMAL*.md; do
        [[ -f "$file" ]] && execute_cmd "git mv '$file' docs/guides/"
    done
    
    log_success "Guides moved"
}

# Step #013// - Move architecture docs
step_013_move_architecture() {
    log_info "Step #013// - Moving architecture docs"
    
    # Architecture and integration docs
    for file in *INTEGRATION*.md *ARCHITECTURE*.md AUMEMMANAGER*.md; do
        [[ -f "$file" ]] && execute_cmd "git mv '$file' docs/architecture/"
    done
    
    log_success "Architecture docs moved"
}

# Step #014// - Update .gitignore
step_014_update_gitignore() {
    log_info "Step #014// - Updating .gitignore"
    
    if [[ "$DRY_RUN" == false ]]; then
        cat >> .gitignore << 'EOF'

# === Phase 1 Reorganization - Data Isolation ===
# Added: $(date +%Y-%m-%d)

# Runtime data (never commit)
data/
*.log
*.cache
*.pid
*.sock

# Build artifacts
__pycache__/
*.pyc
*.pyo
*.pyd
*.so
*.egg-info/
dist/
build/
.eggs/

# Environment
.env
.env.local
.venv/
venv/
ENV/

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db
*.swp
*.swo

# Temporary files
*.tmp
*.bak
*.backup
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# === End Phase 1 Reorganization ===
EOF
        log_success ".gitignore updated"
    else
        echo "  [DRY-RUN] Would append data isolation rules to .gitignore"
    fi
}

# Step #015// - Create README files
step_015_create_readmes() {
    log_info "Step #015// - Creating README files"
    
    # tools/aurora/README.md
    if [[ "$DRY_RUN" == false ]]; then
        cat > tools/aurora/README.md << 'EOF'
# Aurora Core Tools

This directory contains the main Aurora CloudBank Symbolic tools and entry points.

## Files

- `api_server.py` - FastAPI server (formerly `aurora_api.py`)
- `cli.py` - Command-line interface (formerly `aurora_cli.py`)
- `system_validator.py` - System validation utilities
- `deployment_manager.py` - Deployment orchestration

## Usage

**Start API server:**
```bash
python tools/aurora/api_server.py
```

**CLI interface:**
```bash
python tools/aurora/cli.py --help
```

## Migration Notice

These files were moved from repository root during Phase 1 reorganization.
See `.github/ARCHITECTURE_AUDIT_REPORT.md` for details.
EOF
    fi
    
    # scripts/README.md
    if [[ "$DRY_RUN" == false ]]; then
        cat > scripts/README.md << 'EOF'
# Aurora Scripts

Organized scripts for various operational tasks.

## Directory Structure

- `setup/` - Environment setup and initialization scripts
- `deployment/` - Deployment and launch scripts
- `automation/` - Workflow automation and orchestration
- `maintenance/` - Cleanup, enhancement, and fix scripts
- `ci/` - CI/CD integration scripts

## Migration Notice

Scripts were consolidated from repository root during Phase 1 reorganization.
See `.github/ARCHITECTURE_AUDIT_REPORT.md` for details.
EOF
    fi
    
    log_success "README files created"
}

# Step #016// - Validate moves
step_016_validate() {
    log_info "Step #016// - Validating reorganization"
    
    # Count remaining root files
    ROOT_PY=$(find . -maxdepth 1 -name "*.py" -type f | wc -l)
    ROOT_SH=$(find . -maxdepth 1 -name "*.sh" -type f | wc -l)
    ROOT_MD=$(find . -maxdepth 1 -name "*.md" -type f | wc -l)
    
    log_info "Remaining root files:"
    log_info "  Python: $ROOT_PY (target: <5)"
    log_info "  Shell: $ROOT_SH (target: <5)"
    log_info "  Markdown: $ROOT_MD (target: <10)"
    
    if [[ $ROOT_PY -lt 10 && $ROOT_SH -lt 10 ]]; then
        log_success "Root directory significantly cleaner"
    else
        log_warning "Additional cleanup may be needed"
    fi
}

# Step #017// - Summary report
step_017_summary() {
    log_info "Step #017// - Reorganization Summary"
    
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "  Aurora Repository Reorganization - Phase 1"
    echo "═══════════════════════════════════════════════════"
    echo ""
    log_success "Phase 1 reorganization complete!"
    echo ""
    log_info "Next Steps:"
    echo "  1. Review changes: git status"
    echo "  2. Test functionality: make test"
    echo "  3. Update import paths (see migration guide)"
    echo "  4. Commit changes: git commit -m 'Phase 1: Root directory cleanup'"
    echo "  5. Proceed to Phase 2 (src/ reorganization)"
    echo ""
    log_warning "Backup branch: $BACKUP_BRANCH"
    log_warning "To rollback: git reset --hard $BACKUP_BRANCH"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║  Aurora CloudBank Symbolic                    ║"
    echo "║  Repository Reorganization - Phase 1          ║"
    echo "║  T1:audit_001 | DLP:reorganization_phase1     ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
    
    step_001_validate
    step_002_backup
    step_003_create_structure
    step_004_move_aurora_tools
    step_005_move_automation
    step_006_move_setup
    step_007_move_deployment
    step_008_move_maintenance
    step_009_move_ci
    step_010_move_configs
    step_011_move_reports
    step_012_move_guides
    step_013_move_architecture
    step_014_update_gitignore
    step_015_create_readmes
    step_016_validate
    step_017_summary
}

# Execute
main "$@"
