#!/bin/bash

# Aurora CloudBank Environment Setup Script
# Prevents dependency conflicts and ensures clean builds

set -euo pipefail

echo "🌟 Aurora CloudBank Environment Setup"
echo "===================================="

# Configuration
PYTHON_VERSION="3.12"
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
BACKUP_DIR=".backup"

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

# Function to check Python version
check_python_version() {
    log_info "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        return 1
    fi
    
    CURRENT_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ "$CURRENT_VERSION" != "$PYTHON_VERSION" ]]; then
        log_warning "Expected Python $PYTHON_VERSION, found $CURRENT_VERSION"
    fi
    
    log_success "Python version: $(python3 --version)"
}

# Function to create clean virtual environment
setup_venv() {
    log_info "Setting up virtual environment..."
    
    # Remove existing venv if it exists and is corrupted
    if [[ -d "$VENV_DIR" ]]; then
        if ! source "$VENV_DIR/bin/activate" 2>/dev/null; then
            log_warning "Removing corrupted virtual environment"
            rm -rf "$VENV_DIR"
        else
            log_info "Virtual environment already exists and is functional"
            deactivate 2>/dev/null || true
            return 0
        fi
    fi
    
    # Create new virtual environment
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip to latest version
    pip install --upgrade pip
    
    log_success "Virtual environment created and activated"
}

# Function to backup current state
backup_state() {
    log_info "Backing up current state..."
    
    mkdir -p "$BACKUP_DIR/requirements"
    mkdir -p "$BACKUP_DIR/venv"
    
    # Backup requirements files
    for file in requirements.txt requirements-dev.txt requirements-optional.txt pyproject.toml; do
        if [[ -f "$file" ]]; then
            cp "$file" "$BACKUP_DIR/requirements/$file.$(date +%Y%m%d_%H%M%S)"
            log_success "Backed up $file"
        fi
    done
    
    # Create freeze of current environment if it exists
    if [[ -d "$VENV_DIR" ]] && source "$VENV_DIR/bin/activate" 2>/dev/null; then
        pip freeze > "$BACKUP_DIR/requirements/pip_freeze.$(date +%Y%m%d_%H%M%S).txt"
        deactivate
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
    
    source "$VENV_DIR/bin/activate"
    
    if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
        log_error "Required dependency file $REQUIREMENTS_FILE not found"
        return 1
    fi
    
    # Test dependency resolution first
    if pip install -r "$REQUIREMENTS_FILE" --dry-run; then
        log_success "Dependency resolution test passed"
    else
        log_error "Dependency resolution failed - check for conflicts"
        return 1
    fi
    
    # Install dependencies
    pip install -r "$REQUIREMENTS_FILE"
    
    # Optionally install development/testing dependencies
    if [[ -f "requirements-dev.txt" ]]; then
        log_info "Installing development dependencies from requirements-dev.txt..."
        pip install -r requirements-dev.txt || log_warning "Development dependency installation encountered issues"
    fi
    
    # Verify installation
    pip check
    
    log_success "Dependencies installed successfully"
}

# Function to verify Aurora functionality
verify_aurora() {
    log_info "Verifying Aurora CloudBank functionality..."
    
    source "$VENV_DIR/bin/activate"
    
    # Test critical imports
    python3 -c "
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
    source "$VENV_DIR/bin/activate"
    cat > ".env_status.json" << EOF
{
    "setup_date": "$(date -Iseconds)",
    "python_version": "$(python --version)",
    "pip_version": "$(pip --version)",
    "requirements_file": "$REQUIREMENTS_FILE",
    "venv_path": "$VENV_DIR",
    "status": "ready",
    "validation_passed": true
}
EOF
    deactivate 2>/dev/null || true
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
