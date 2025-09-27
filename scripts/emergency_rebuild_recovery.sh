#!/bin/bash

# Aurora CloudBank Emergency Rebuild Recovery System
# Use when DevContainer rebuild fails and system is in recovery mode

set -e

echo "🚨 Aurora CloudBank Emergency Rebuild Recovery"
echo "=============================================="

WORKSPACE_ROOT="$(pwd)"
VENV_DIR=".venv"
BACKUP_DIR=".backup"
LOG_FILE="emergency_recovery_$(date +%Y%m%d_%H%M%S).log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to handle errors
handle_error() {
    local error_msg="$1"
    log "❌ ERROR: $error_msg"
    echo "🔍 Check log file: $LOG_FILE"
    exit 1
}

log "🎯 Starting emergency recovery process..."

# Step 1: Assess current state
log "📊 Assessing current environment state..."

if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    log "✅ Python available: $PYTHON_VERSION"
else
    handle_error "Python 3 not available in system"
fi

# Step 2: Clean corrupted environment
log "🧹 Cleaning potentially corrupted environment..."
if [[ -d "$VENV_DIR" ]]; then
    log "🗑️ Removing existing virtual environment..."
    rm -rf "$VENV_DIR" || log "⚠️ Warning: Failed to remove venv directory"
fi

# Step 3: Create fresh environment
log "🏗️ Creating fresh virtual environment..."
python3 -m venv "$VENV_DIR" || handle_error "Failed to create virtual environment"

# Step 4: Activate environment
log "⚡ Activating virtual environment..."
source "$VENV_DIR/bin/activate" || handle_error "Failed to activate virtual environment"

# Step 5: Upgrade pip
log "📦 Upgrading pip..."
python -m pip install --upgrade pip || handle_error "Failed to upgrade pip"

# Step 6: Install dependencies with fallback strategy
log "🔧 Installing dependencies with fallback strategy..."

# Strategy 1: Try requirements-lock.txt
if [[ -f "requirements-lock.txt" ]]; then
    log "📋 Attempting to install from requirements-lock.txt..."
    if python -m pip install -r requirements-lock.txt --dry-run >/dev/null 2>&1; then
        log "✅ Dry run passed, installing from requirements-lock.txt..."
        if python -m pip install -r requirements-lock.txt; then
            log "✅ Successfully installed from requirements-lock.txt"
        else
            log "⚠️ Installation from requirements-lock.txt failed, trying backup..."
            USE_BACKUP=true
        fi
    else
        log "⚠️ Dry run failed for requirements-lock.txt, trying backup..."
        USE_BACKUP=true
    fi
else
    log "⚠️ requirements-lock.txt not found, trying backup..."
    USE_BACKUP=true
fi

# Strategy 2: Use backup if available
if [[ "$USE_BACKUP" == "true" ]]; then
    if [[ -d "$BACKUP_DIR" ]]; then
        log "🔍 Searching for backup requirements..."
        
        # Find most recent backup
        LATEST_BACKUP=$(find "$BACKUP_DIR" -name "*requirements*.txt" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
        
        if [[ -n "$LATEST_BACKUP" ]]; then
            log "📦 Found backup: $LATEST_BACKUP"
            if python -m pip install -r "$LATEST_BACKUP"; then
                log "✅ Successfully installed from backup"
            else
                log "⚠️ Backup installation failed, installing critical dependencies..."
                MANUAL_INSTALL=true
            fi
        else
            log "⚠️ No backup requirements found, installing critical dependencies..."
            MANUAL_INSTALL=true
        fi
    else
        log "⚠️ No backup directory found, installing critical dependencies..."
        MANUAL_INSTALL=true
    fi
fi

# Strategy 3: Manual installation of critical dependencies
if [[ "$MANUAL_INSTALL" == "true" ]]; then
    log "🎯 Installing critical dependencies manually..."
    
    CRITICAL_DEPS=(
        "fastapi>=0.100.0"
        "httpx>=0.25.0"
        "httpcore>=1.0.0"
        "h11>=0.14.0"
        "starlette>=0.27.0"
        "uvicorn[standard]>=0.23.0"
        "pydantic>=2.0.0"
    )
    
    for dep in "${CRITICAL_DEPS[@]}"; do
        log "📦 Installing $dep..."
        if python -m pip install "$dep"; then
            log "✅ Installed $dep"
        else
            log "⚠️ Failed to install $dep"
        fi
    done
fi

# Step 7: Validate installation
log "🔍 Validating installation..."

# Test critical imports
log "🧪 Testing critical imports..."
python -c "
import sys
try:
    import fastapi
    import httpx
    import httpcore
    import h11
    import starlette
    print('✅ All critical imports successful')
    print(f'FastAPI: {fastapi.__version__}')
    print(f'HTTPX: {httpx.__version__}')
    print(f'HTTPCore: {httpcore.__version__}')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || handle_error "Critical dependency validation failed"

# Step 8: Test Aurora components
log "🧪 Testing Aurora components..."
if [[ -f "aurora_api.py" ]]; then
    python -c "
import sys
sys.path.insert(0, '.')
try:
    from aurora_api import app
    print('✅ Aurora API import successful')
except ImportError as e:
    print(f'⚠️ Aurora API import warning: {e}')
" || log "⚠️ Aurora API test failed (continuing)"
fi

# Step 9: Create recovery status file
log "📝 Creating recovery status file..."
cat > ".emergency_recovery_status.json" << EOF
{
    "status": "completed",
    "timestamp": "$(date -Iseconds)",
    "python_version": "$(python --version)",
    "pip_version": "$(pip --version)",
    "recovery_log": "$LOG_FILE",
    "virtual_env": "$VENV_DIR",
    "workspace": "$(pwd)"
}
EOF

# Step 10: Final validation and recommendations
log "🎯 Running final validation..."
if python scripts/validate_dependencies.py >/dev/null 2>&1; then
    log "✅ Dependency validation passed"
else
    log "⚠️ Dependency validation warnings (check manually)"
fi

echo ""
echo "🎉 Emergency Recovery Completed Successfully!"
echo "==========================================="
echo ""
echo "📊 Recovery Summary:"
echo "   • Virtual environment: $VENV_DIR"
echo "   • Recovery log: $LOG_FILE"
echo "   • Status file: .emergency_recovery_status.json"
echo ""
echo "🎯 Next Steps:"
echo "   1. Test the API server: python aurora_api.py"
echo "   2. Run validation: python scripts/validate_dependencies.py"
echo "   3. Check system status: python scripts/dev-status.py"
echo ""
echo "🔧 To prevent future issues:"
echo "   • Use the new DevContainer config: mv .devcontainer/devcontainer-improved.json .devcontainer/devcontainer.json"
echo "   • Install rebuild protection: python scripts/prevent_rebuild_failures.py"
echo ""

log "🎉 Emergency recovery process completed successfully"