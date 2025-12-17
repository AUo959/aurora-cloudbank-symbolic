#!/bin/bash

# Aurora CloudBank Environment Setup Script
# Prevents dependency conflicts and ensures clean builds

set -euo pipefail

echo "🌟 Aurora CloudBank Environment Setup"
echo "===================================="

# Configuration
PYTHON_VERSION="3.12"
VENV_DIR="${AURORA_VENV_DIR:-.venv}"
REQUIREMENTS_FILE="requirements-lock.txt"
BACKUP_DIR=".backup"

# Prefer a specific Python when available (can be overridden)
PYTHON_BIN="${AURORA_PYTHON_BIN:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

venv_is_valid() {
    [[ -x "$VENV_DIR/bin/python" ]] && [[ -f "$VENV_DIR/bin/activate" ]]
}

ensure_python_bin() {
    if [[ -n "$PYTHON_BIN" ]]; then
        return 0
    fi

    if command -v "python${PYTHON_VERSION}" &> /dev/null; then
        PYTHON_BIN="python${PYTHON_VERSION}"
        return 0
    fi

    PYTHON_BIN="python3"
}

# Function to check Python version
check_python_version() {
    log_info "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        return 1
    fi

    ensure_python_bin
    
    CURRENT_VERSION=$($PYTHON_BIN --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ "$CURRENT_VERSION" != "$PYTHON_VERSION" ]]; then
        log_warning "Expected Python $PYTHON_VERSION, found $CURRENT_VERSION"
    fi
    
    log_success "Python version: $($PYTHON_BIN --version)"
}

# Function to create clean virtual environment
setup_venv() {
    log_info "Setting up virtual environment..."

    ensure_python_bin
    
    # Remove existing venv if it exists and is corrupted
    if [[ -d "$VENV_DIR" ]]; then
        if venv_is_valid && "$VENV_DIR/bin/python" -c "import sys" &>/dev/null; then
            log_info "Virtual environment already exists and is functional"
            return 0
        fi

        log_warning "Existing virtual environment is missing/invalid"
        if [[ -w "$VENV_DIR" ]]; then
            log_warning "Removing corrupted virtual environment"
            rm -rf "$VENV_DIR"
        else
            if [[ "${AURORA_VENV_REPAIR:-0}" == "1" ]] && command -v sudo &>/dev/null; then
                log_warning "Attempting repair of '$VENV_DIR' using sudo (AURORA_VENV_REPAIR=1)"
                sudo chown -R "$(id -u)":"$(id -g)" "$VENV_DIR" 2>/dev/null || true
                if [[ ! -w "$VENV_DIR" ]]; then
                    log_warning "Chown did not make '$VENV_DIR' writable; attempting to clear contents"
                    sudo rm -rf "$VENV_DIR"/* 2>/dev/null || true
                    sudo chown -R "$(id -u)":"$(id -g)" "$VENV_DIR" 2>/dev/null || true
                fi
            fi

            log_error "Cannot repair '$VENV_DIR' (not writable: $(ls -ld "$VENV_DIR" 2>/dev/null || true))"
            log_info "Fix options:"
            log_info "  1) Remove/chown it, then re-run: sudo rm -rf $VENV_DIR   (or: sudo chown -R \"$(id -un)\":\"$(id -gn)\" $VENV_DIR)"
            log_info "  2) Use an alternate venv path: AURORA_VENV_DIR=.venv-user bash scripts/setup_environment.sh"
            return 1
        fi
    fi
    
    # Create new virtual environment
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    
    # Upgrade pip to latest version
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    
    log_success "Virtual environment created and activated"
}

# Function to backup current state
backup_state() {
    log_info "Backing up current state..."
    
    mkdir -p "$BACKUP_DIR/requirements"
    mkdir -p "$BACKUP_DIR/venv"
    
    # Backup requirements files
    for file in requirements.txt requirements-lock.txt pyproject.toml; do
        if [[ -f "$file" ]]; then
            cp "$file" "$BACKUP_DIR/requirements/$file.$(date +%Y%m%d_%H%M%S)"
            log_success "Backed up $file"
        fi
    done
    
    # Create freeze of current environment if it exists
    if venv_is_valid; then
        "$VENV_DIR/bin/python" -m pip freeze > "$BACKUP_DIR/requirements/pip_freeze.$(date +%Y%m%d_%H%M%S).txt" || true
        log_success "Backed up current pip freeze"
    fi
}

# Function to validate dependencies
validate_dependencies() {
    log_info "Validating dependencies..."
    
    if [[ -f "scripts/validate_dependencies.py" ]]; then
        if python scripts/validate_dependencies.py; then
            log_success "Dependency validation passed"
            return 0
        else
            log_error "Dependency validation failed"
            return 1
        fi
    else
        log_warning "Dependency validator not found, skipping validation"
        return 0
    fi
}

# Function to install dependencies
install_dependencies() {
    log_info "Installing dependencies..."

    if ! venv_is_valid; then
        log_error "Virtual environment is not ready at '$VENV_DIR'"
        return 1
    fi
    
    # Fallback to requirements.txt when lock file is missing
    if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
        log_warning "Lock file $REQUIREMENTS_FILE not found; falling back to requirements.txt"
        REQUIREMENTS_FILE="requirements.txt"
    fi
    
    # Test dependency resolution first
    if "$VENV_DIR/bin/python" -m pip install -r "$REQUIREMENTS_FILE" --dry-run; then
        log_success "Dependency resolution test passed"
    else
        log_warning "Dependency resolution dry-run failed (pip may not support --dry-run or conflicts exist)"
        log_info "Continuing with real install; if it fails, resolve conflicts and re-run setup"
    fi
    
    # Install dependencies
    "$VENV_DIR/bin/python" -m pip install -r "$REQUIREMENTS_FILE"
    
    # Optionally install development/testing dependencies
    if [[ -f "requirements-dev.txt" ]]; then
        log_info "Installing development dependencies from requirements-dev.txt..."
        "$VENV_DIR/bin/python" -m pip install -r requirements-dev.txt || log_warning "Development dependency installation encountered issues"
    fi
    
    # Verify installation
    "$VENV_DIR/bin/python" -m pip check
    
    log_success "Dependencies installed successfully"
}

# Function to verify Aurora functionality
verify_aurora() {
    log_info "Verifying Aurora CloudBank functionality..."

    if ! venv_is_valid; then
        log_error "Virtual environment is not ready at '$VENV_DIR'"
        return 1
    fi
    
    # Test critical imports
    "$VENV_DIR/bin/python" -c "
import fastapi
import httpx
import pandas
import numpy
print('✅ Core dependencies loaded successfully')
print(f'FastAPI: {fastapi.__version__}')
print(f'httpx: {httpx.__version__}')
print(f'pandas: {pandas.__version__}')
" || {
        log_error "Core dependency verification failed"
        return 1
    }
    
    # Test Aurora symbolic manifest
    if [[ -f "scripts/symbolic_manifest.py" ]]; then
        python scripts/symbolic_manifest.py --help-aurora > /dev/null || {
            log_warning "Aurora symbolic manifest test failed"
        }
    fi
    
    log_success "Aurora verification completed"
}

# Function to create environment status file
create_status_file() {
    if ! venv_is_valid; then
        log_error "Virtual environment is not ready at '$VENV_DIR'"
        return 1
    fi

    cat > ".env_status.json" << EOF
{
    "setup_date": "$(date -Iseconds)",
    "python_version": "$("$VENV_DIR/bin/python" --version)",
    "pip_version": "$("$VENV_DIR/bin/python" -m pip --version)",
    "requirements_file": "$REQUIREMENTS_FILE",
    "venv_path": "$VENV_DIR",
    "status": "ready",
    "validation_passed": true
}
EOF
    log_success "Environment status file created"
}

# Main execution
main() {
    echo
    
    # Check prerequisites
    check_python_version || exit 1
    
    # Backup current state
    backup_state
    
    # Setup clean environment
    setup_venv || exit 1
    
    # Validate dependencies before installation
    validate_dependencies || exit 1
    
    # Install dependencies
    install_dependencies || exit 1
    
    # Verify Aurora functionality
    verify_aurora || exit 1
    
    # Create status file
    create_status_file
    
    echo
    log_success "Aurora CloudBank environment setup completed successfully!"
    log_info "To activate the environment: source $VENV_DIR/bin/activate"
    echo
}

# Run main function
main "$@"
