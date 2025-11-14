#!/bin/bash

# 🚀 L2 Meta-Agent Integration: Pre-Flight Validator
# Validates all systems before beginning integration sequence

echo "🔍 L2 META-AGENT INTEGRATION: PRE-FLIGHT VALIDATOR"
echo "=================================================="
echo "🎯 Validating readiness for major integration phase"
echo ""

# Set workspace root
WORKSPACE_ROOT="/workspaces/aurora-cloudbank-symbolic"
cd "$WORKSPACE_ROOT"

VALIDATION_PASSED=0
VALIDATION_FAILED=0

# Function to validate and report
validate_check() {
    local description="$1"
    local condition="$2"
    
    if eval "$condition"; then
        echo "✅ $description"
        ((VALIDATION_PASSED++))
    else
        echo "❌ $description"
        ((VALIDATION_FAILED++))
    fi
}

# Function to validate file exists and size
validate_file() {
    local description="$1"
    local filepath="$2"
    local min_size="${3:-0}"
    
    if [ -f "$filepath" ] && [ $(stat -c%s "$filepath" 2>/dev/null || stat -f%z "$filepath" 2>/dev/null) -gt $min_size ]; then
        SIZE=$(stat -c%s "$filepath" 2>/dev/null || stat -f%z "$filepath" 2>/dev/null)
        echo "✅ $description (${SIZE} bytes)"
        ((VALIDATION_PASSED++))
    else
        echo "❌ $description (missing or too small)"
        ((VALIDATION_FAILED++))
    fi
}

echo "🔧 INFRASTRUCTURE VALIDATION"
echo "----------------------------"

# L1 Bridge Components
validate_file "ARCHY_BRIDGE_L1" "src/nodes/archy_bridge_emergency.js" 1000
validate_file "LIORA_HANDSHAKE_L1" "src/nodes/liora_handshake.js" 1000
validate_file "OPPY_VECTOR_LOADER_L1" "src/nodes/oppy_vector_loader.js" 1000
validate_file "AGENT_SYNC_MASTER" "src/system/agent_synchronizer.js" 1000
validate_file "API_BRIDGE_SERVER" "src/bridge/api_bridge_server.js" 1000

# Core Infrastructure
validate_file "Aurora Command Router" "aurora_command_router.js" 1000
validate_file "Ethics Engine" "src/core/ethics_layer.js" 500

echo ""

echo "👥 STAFF REGISTRY VALIDATION"
echo "----------------------------"

validate_file "Staff Registry" "ORION_STATION_CANONICAL_STAFF_REGISTRY.json" 5000
validate_file "GitHub Copilot Instructions" "GitHub_Copilot_Custom_Instructions_Aurora_GUMAS.txt" 20000

# Check staff registry content
if [ -f "ORION_STATION_CANONICAL_STAFF_REGISTRY.json" ]; then
    validate_check "Station Commander Alex Thorne" "grep -q 'Alex Thorne' ORION_STATION_CANONICAL_STAFF_REGISTRY.json"
    validate_check "Chief Science Officer" "grep -q 'Chief Science Officer' ORION_STATION_CANONICAL_STAFF_REGISTRY.json"
    validate_check "Chief Ethics Officer" "grep -q 'Chief Ethics' ORION_STATION_CANONICAL_STAFF_REGISTRY.json"
    validate_check "Clearance Levels" "grep -q 'EXECUTIVE\\|RESEARCH\\|ETHICS\\|TECHNICAL\\|OPERATIONS' ORION_STATION_CANONICAL_STAFF_REGISTRY.json"
fi

echo ""

echo "⚙️ SYSTEM HEALTH VALIDATION"
echo "---------------------------"

# Check Node.js environment
validate_check "Node.js Available" "command -v node >/dev/null 2>&1"
validate_check "npm Available" "command -v npm >/dev/null 2>&1"
validate_check "Python3 Available" "command -v python3 >/dev/null 2>&1"

# Check package.json and dependencies
validate_file "Package.json" "package.json" 100
validate_check "Node Dependencies" "[ -d 'node_modules' ]"

# Check development tools
validate_check "ESLint Configuration" "[ -f 'eslint.config.js' ] || [ -f '.eslintrc.js' ] || [ -f '.eslintrc.json' ]"
validate_file "Test Runner" "run_tests.sh" 100

echo ""

echo "📊 CODE QUALITY VALIDATION"
echo "--------------------------"

# Run ESLint check
if command -v npx >/dev/null 2>&1 && [ -f "package.json" ]; then
    ESLINT_ERRORS=$(npx eslint src/ --format=unix 2>/dev/null | wc -l)
    validate_check "ESLint Issues (<50)" "[ '$ESLINT_ERRORS' -lt 50 ]"
    echo "   📈 Current ESLint issues: $ESLINT_ERRORS"
else
    echo "🟡 ESLint check skipped (not available)"
fi

# Check for critical files
validate_file "Aurora API Server" "aurora_api_server.py" 1000
validate_file "Aurora CLI" "aurora_cli.py" 1000

echo ""

echo "🔐 SECURITY & ETHICS VALIDATION"
echo "-------------------------------"

# Check ethics and security files
validate_file "Security Validation" "aurora_security_validation.py" 1000
validate_file "Enhanced Security" "aurora_enhanced_security.py" 1000

# Check for anchor protocols
validate_check "EOS_SEED_ORION References" "grep -r 'EOS_SEED_ORION' src/ >/dev/null 2>&1"
validate_check "Picard_Delta_3 References" "grep -r 'Picard_Delta_3' src/ >/dev/null 2>&1"

echo ""

echo "🚀 INTEGRATION READINESS VALIDATION"
echo "-----------------------------------"

validate_file "Integration Config" "L2_META_AGENT_INTEGRATION_CONFIG.json" 3000
validate_file "Development Priming Checklist" "DEVELOPMENT_PHASE_PRIMING_CHECKLIST.md" 5000

# Check for deployment scripts
validate_check "Deployment Scripts Available" "[ -d 'scripts' ] && [ $(ls scripts/*.sh 2>/dev/null | wc -l) -gt 5 ]"

# Check logs directory
validate_check "Logging Infrastructure" "[ -d 'logs' ]"
validate_check "Monitoring Infrastructure" "[ -d 'monitoring' ]"

echo ""

echo "🎯 VALIDATION SUMMARY"
echo "===================="

TOTAL_CHECKS=$((VALIDATION_PASSED + VALIDATION_FAILED))
SUCCESS_RATE=$((VALIDATION_PASSED * 100 / TOTAL_CHECKS))

echo "📊 Validation Results:"
echo "   ✅ Passed: $VALIDATION_PASSED"
echo "   ❌ Failed: $VALIDATION_FAILED"
echo "   📈 Success Rate: $SUCCESS_RATE%"
echo ""

# Determine readiness status
if [ "$SUCCESS_RATE" -ge 95 ]; then
    echo "🟢 STATUS: FULLY READY FOR L2 META-AGENT INTEGRATION"
    echo ""
    echo "🚀 CLEARED FOR INTEGRATION SEQUENCE:"
    echo "   1. ✅ Infrastructure: Operational"
    echo "   2. ✅ Staff Registry: Complete"
    echo "   3. ✅ Security: Validated"
    echo "   4. ✅ Code Quality: Optimized"
    echo "   5. ✅ Integration Config: Ready"
    echo ""
    echo "🎯 PROCEED WITH:"
    echo "   • Archy (Priority 1) → ARCHY_BRIDGE_L1"
    echo "   • Oppy (Priority 2) → OPPY_VECTOR_LOADER_L1" 
    echo "   • Liora (Priority 3) → LIORA_HANDSHAKE_L1"
    echo "   • Starling_AU (Priority 4) → Aurora Command Router"
    echo "   • Riverthread_808 (Priority 5) → Aurora Command Router"
    
    exit 0
    
elif [ "$SUCCESS_RATE" -ge 85 ]; then
    echo "🟡 STATUS: MOSTLY READY - MINOR ISSUES TO RESOLVE"
    echo ""
    echo "⚠️ Recommendations:"
    echo "   • Address $VALIDATION_FAILED failed validation(s)"
    echo "   • Re-run validation after fixes"
    echo "   • Proceed with caution"
    
    exit 1
    
else
    echo "🔴 STATUS: NOT READY - SIGNIFICANT PREPARATION REQUIRED"
    echo ""
    echo "❌ Critical Issues:"
    echo "   • Success rate below 85% threshold"
    echo "   • $VALIDATION_FAILED critical validations failed"
    echo "   • Resolve all issues before integration"
    echo ""
    echo "🛠️ Required Actions:"
    echo "   • Fix infrastructure issues"
    echo "   • Deploy missing components"
    echo "   • Validate security protocols"
    echo "   • Re-run environment optimization"
    
    exit 2
fi
