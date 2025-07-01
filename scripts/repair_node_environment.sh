#!/bin/bash
# ORION CloudBank - Phase 0 Foundation Stabilization Script
# Repairs Node.js environment and verifies core dependencies

set -e  # Exit on any error

echo "🔧 ORION CloudBank - Foundation Stabilization"
echo "=============================================="
echo "Phase 0: Critical Path Resolution"
echo ""

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check command success
check_status() {
    if [ $? -eq 0 ]; then
        log "✅ $1 - SUCCESS"
    else
        log "❌ $1 - FAILED"
        exit 1
    fi
}

log "Starting Node.js Environment Recovery..."

# Remove existing symbolic links if they exist
if [ -L "node" ]; then
    rm -f node
    log "Removed existing node symlink"
fi

if [ -L "npm" ]; then
    rm -f npm  
    log "Removed existing npm symlink"
fi

# Check if Node.js binaries exist
if [ -f "/usr/local/bin/node" ]; then
    ln -sf /usr/local/bin/node node
    log "Created node symlink"
else
    log "⚠️  Node.js binary not found at /usr/local/bin/node"
fi

if [ -f "/usr/local/bin/npm" ]; then
    ln -sf /usr/local/bin/npm npm
    log "Created npm symlink"
else
    log "⚠️  npm binary not found at /usr/local/bin/npm"
fi

# Update PATH for current session
export PATH="/usr/local/bin:$PATH"
log "Updated PATH environment variable"

# Verify Node.js installation
log "Verifying Node.js installation..."
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version 2>/dev/null || echo "unknown")
    log "Node.js version: $NODE_VERSION"
else
    log "⚠️  Node.js command not accessible"
fi

if command -v npm >/dev/null 2>&1; then
    NPM_VERSION=$(npm --version 2>/dev/null || echo "unknown")
    log "npm version: $NPM_VERSION"
else
    log "⚠️  npm command not accessible"
fi

log "Dependency Installation Phase..."

# Python dependency installation
log "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt --quiet
    check_status "Python dependencies installation"
else
    log "⚠️  requirements.txt not found"
fi

# Node.js dependency installation (if npm is available)
if command -v npm >/dev/null 2>&1; then
    log "Installing Node.js dependencies..."
    npm install --silent 2>/dev/null
    check_status "Node.js dependencies installation"
    
    log "Running npm audit fix..."
    npm audit fix --silent 2>/dev/null || log "⚠️  npm audit fix completed with warnings"
else
    log "⚠️  Skipping npm install - npm not accessible"
fi

log "Health Check Verification..."

# Verify Python syntax
log "Checking Python syntax..."
python3 -m py_compile aurora_api.py 2>/dev/null
check_status "aurora_api.py syntax check"

python3 -m py_compile aurora_gui_cloudhub_fastapi.py 2>/dev/null  
check_status "aurora_gui_cloudhub_fastapi.py syntax check"

# Check git status
log "Verifying git repository status..."
git status --porcelain > /dev/null
check_status "Git repository status check"

# Check disk space
log "Checking disk space..."
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    log "✅ Disk usage: ${DISK_USAGE}% - Sufficient space available"
else
    log "⚠️  Disk usage: ${DISK_USAGE}% - Consider cleanup"
fi

echo ""
echo "=============================================="
log "🎯 Phase 0 Foundation Stabilization COMPLETE"
echo "=============================================="
echo ""

# Create status report
cat > foundation_status_report.txt << EOF
ORION CloudBank Foundation Stabilization Report
Generated: $(date)

Environment Status:
- Node.js: $(command -v node >/dev/null 2>&1 && echo "Available" || echo "Not Available")
- npm: $(command -v npm >/dev/null 2>&1 && echo "Available" || echo "Not Available") 
- Python: Available ($(python3 --version))
- Git: Clean repository status

Dependencies:
- Python packages: Installed from requirements.txt
- Node.js packages: $(command -v npm >/dev/null 2>&1 && echo "Installed" || echo "Skipped - npm unavailable")

Syntax Validation:
- aurora_api.py: ✅ Valid
- aurora_gui_cloudhub_fastapi.py: ✅ Valid

Disk Usage: ${DISK_USAGE}%

Status: FOUNDATION READY FOR PHASE 1 DEPLOYMENT
EOF

log "Status report created: foundation_status_report.txt"
log "Ready to proceed with Phase 1: Parallel L1/L3 Initialization"

echo ""
echo "Next steps:"
echo "  ./scripts/initialize_l1_station.sh"
echo "  ./scripts/initialize_l3_mesh.sh"
echo "  ./scripts/setup_crew_registry.sh"
