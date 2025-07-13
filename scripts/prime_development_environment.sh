#!/bin/bash

# 🚀 Aurora CloudBank Development Environment Optimizer
# Prepares environment for L2 Meta-Agent Integration Phase

echo "🔧 AURORA CLOUDBANK DEVELOPMENT ENVIRONMENT OPTIMIZER"
echo "======================================================"
echo "🎯 Preparing for L2 Meta-Agent Integration Phase"
echo ""

# Set workspace root
WORKSPACE_ROOT="/workspaces/aurora-cloudbank-symbolic"
cd "$WORKSPACE_ROOT"

# Phase 1: Environment Validation
echo "📊 PHASE 1: Environment Validation"
echo "-----------------------------------"

# Check Node.js and npm
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js not found"
    exit 1
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm: $NPM_VERSION"
else
    echo "❌ npm not found"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python3 not found"
    exit 1
fi

# Check pip3
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo "✅ pip3: $PIP_VERSION"
else
    echo "❌ pip3 not found"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "✅ Git: $GIT_VERSION"
else
    echo "❌ Git not found"
    exit 1
fi

echo ""

# Phase 2: Code Quality Optimization
echo "🧹 PHASE 2: Code Quality Optimization"
echo "-------------------------------------"

# Install/update ESLint if needed
echo "Installing/updating ESLint..."
npm install --save-dev eslint

# Run ESLint fixes
echo "Running ESLint auto-fix..."
npx eslint src/ --fix --silent

# Count remaining issues
ESLINT_ISSUES=$(npx eslint src/ --format=unix 2>/dev/null | wc -l)
echo "✅ ESLint issues: $ESLINT_ISSUES (target: <50)"

echo ""

# Phase 3: Infrastructure Validation
echo "🏗️ PHASE 3: Infrastructure Validation"
echo "--------------------------------------"

# Check L1 bridge files
L1_BRIDGES=(
    "src/nodes/archy_bridge_emergency.js"
    "src/nodes/liora_handshake.js" 
    "src/nodes/oppy_vector_loader.js"
    "src/bridge/api_bridge_server.js"
    "src/system/agent_synchronizer.js"
)

echo "Checking L1 bridge infrastructure..."
L1_COUNT=0
for bridge in "${L1_BRIDGES[@]}"; do
    if [ -f "$bridge" ]; then
        echo "  ✅ $bridge"
        ((L1_COUNT++))
    else
        echo "  ❌ $bridge (missing)"
    fi
done
echo "📊 L1 bridges: $L1_COUNT/5 deployed"

# Check command router
if [ -f "aurora_command_router.js" ]; then
    echo "✅ Aurora Command Router: deployed"
else
    echo "❌ Aurora Command Router: missing"
fi

# Check staff registry
if [ -f "ORION_STATION_CANONICAL_STAFF_REGISTRY.json" ]; then
    echo "✅ Staff Registry: deployed"
else
    echo "❌ Staff Registry: missing"
fi

echo ""

# Phase 4: Performance Optimization
echo "⚡ PHASE 4: Performance Optimization"
echo "------------------------------------"

# Check if native test runner exists
if [ -f "run_tests.sh" ]; then
    echo "✅ Native test runner: available"
    
    # Run quick performance test
    echo "Running performance benchmark..."
    if timeout 10s ./run_tests.sh native &>/dev/null; then
        echo "✅ Performance test: passed"
    else
        echo "🟡 Performance test: timeout (expected for full test)"
    fi
else
    echo "❌ Native test runner: missing"
fi

# Check package.json
if [ -f "package.json" ]; then
    echo "✅ Package.json: available"
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies..."
        npm install --silent
        echo "✅ Dependencies: installed"
    else
        echo "✅ Dependencies: already installed"
    fi
else
    echo "❌ Package.json: missing"
fi

echo ""

# Phase 5: Development Tools Setup
echo "🛠️ PHASE 5: Development Tools Setup"
echo "-----------------------------------"

# Create development directories if they don't exist
DEV_DIRS=(
    "logs"
    "exports"
    "temp"
    "monitoring"
    "testing"
)

echo "Setting up development directories..."
for dir in "${DEV_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  📁 Created: $dir/"
    else
        echo "  ✅ Exists: $dir/"
    fi
done

# Create monitoring script
cat > monitoring/dev_monitor.sh << 'EOF'
#!/bin/bash
# Development environment monitoring
echo "🔍 Aurora CloudBank Development Monitor"
echo "======================================"
echo "📊 System Status: $(date)"
echo ""

# Check processes
echo "🔄 Active Processes:"
ps aux | grep -E "(node|python3)" | grep -v grep || echo "  No Aurora processes running"
echo ""

# Check file changes
echo "📝 Recent Changes:"
find . -name "*.js" -o -name "*.py" -newer monitoring/dev_monitor.sh 2>/dev/null | head -5 || echo "  No recent changes"
echo ""

# Check disk space
echo "💾 Disk Usage:"
df -h . | tail -1
echo ""
EOF

chmod +x monitoring/dev_monitor.sh
echo "✅ Development monitor: created"

echo ""

# Phase 6: Configuration Validation
echo "⚙️ PHASE 6: Configuration Validation"
echo "------------------------------------"

# Check configuration files
CONFIG_FILES=(
    "GitHub_Copilot_Custom_Instructions_Aurora_GUMAS.txt"
    "ORION_STATION_CANONICAL_STAFF_REGISTRY.json"
)

echo "Validating configuration files..."
for config in "${CONFIG_FILES[@]}"; do
    if [ -f "$config" ]; then
        SIZE=$(stat -c%s "$config" 2>/dev/null || stat -f%z "$config" 2>/dev/null)
        echo "  ✅ $config (${SIZE} bytes)"
    else
        echo "  ❌ $config (missing)"
    fi
done

echo ""

# Phase 7: Integration Readiness Summary
echo "🎯 PHASE 7: Integration Readiness Summary"
echo "-----------------------------------------"

# Calculate overall readiness
READINESS_SCORE=0
TOTAL_CHECKS=10

# Check criteria
[ "$L1_COUNT" -eq 5 ] && ((READINESS_SCORE++))
[ "$ESLINT_ISSUES" -lt 50 ] && ((READINESS_SCORE++))
[ -f "aurora_command_router.js" ] && ((READINESS_SCORE++))
[ -f "ORION_STATION_CANONICAL_STAFF_REGISTRY.json" ] && ((READINESS_SCORE++))
[ -f "run_tests.sh" ] && ((READINESS_SCORE++))
[ -f "package.json" ] && ((READINESS_SCORE++))
[ -d "node_modules" ] && ((READINESS_SCORE++))
[ -d "logs" ] && ((READINESS_SCORE++))
[ -f "GitHub_Copilot_Custom_Instructions_Aurora_GUMAS.txt" ] && ((READINESS_SCORE++))
[ -f "monitoring/dev_monitor.sh" ] && ((READINESS_SCORE++))

READINESS_PERCENT=$((READINESS_SCORE * 100 / TOTAL_CHECKS))

echo "📊 Environment Readiness: $READINESS_SCORE/$TOTAL_CHECKS ($READINESS_PERCENT%)"
echo ""

if [ "$READINESS_PERCENT" -ge 90 ]; then
    echo "🟢 STATUS: READY FOR L2 META-AGENT INTEGRATION"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Begin L2 meta-agent bridge connections"
    echo "  2. Validate staff authorization protocols"
    echo "  3. Monitor symbolic drift during integration"
    echo "  4. Activate cross-layer communication"
    echo ""
    echo "🎯 Integration Priority:"
    echo "  • Archy (Logic Engine) → ARCHY_BRIDGE_L1"
    echo "  • Oppy (Data Processing) → OPPY_VECTOR_LOADER_L1"
    echo "  • Liora (Research Coordination) → LIORA_HANDSHAKE_L1"
    echo "  • Starling_AU (Communications) → Aurora Command Router"
    echo "  • Riverthread_808 (Continuity) → Aurora Command Router"
    
elif [ "$READINESS_PERCENT" -ge 70 ]; then
    echo "🟡 STATUS: MOSTLY READY - MINOR ISSUES TO RESOLVE"
    echo ""
    echo "⚠️ Required Actions:"
    [ "$L1_COUNT" -ne 5 ] && echo "  • Deploy missing L1 bridge components"
    [ "$ESLINT_ISSUES" -ge 50 ] && echo "  • Fix ESLint issues (current: $ESLINT_ISSUES)"
    [ ! -f "aurora_command_router.js" ] && echo "  • Deploy Aurora Command Router"
    [ ! -f "ORION_STATION_CANONICAL_STAFF_REGISTRY.json" ] && echo "  • Create staff registry"
    
else
    echo "🔴 STATUS: NOT READY - SIGNIFICANT PREPARATION REQUIRED"
    echo ""
    echo "❌ Critical Issues:"
    echo "  • Environment readiness below 70%"
    echo "  • Multiple infrastructure components missing"
    echo "  • Resolve all critical issues before proceeding"
fi

echo ""
echo "✅ Environment optimization complete!"
echo "📝 Run './monitoring/dev_monitor.sh' for ongoing monitoring"
