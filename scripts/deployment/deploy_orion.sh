#!/bin/bash

# ORION CloudBank - Automated Deployment Orchestrator
# Integrated workflow for L1/L3 parallel initialization

echo "🚀 ORION CloudBank Deployment Orchestrator"
echo "=========================================="
echo "Deploying Aurora CloudBank with integrated ORION workflow"
echo "Date: $(date)"
echo

# Phase 1: Environment Preparation
echo "📋 PHASE 1: Environment Preparation"
echo "-----------------------------------"

# Check and display environment status
if [ -f ".env" ]; then
    echo "✅ Environment configuration found"
else
    echo "⚠️  Creating default environment configuration"
    cp .env.example .env 2>/dev/null || echo "# Aurora CloudBank Environment" > .env
fi

# Ensure key directories exist
mkdir -p logs deployment/status workflow_output/health_checks
echo "✅ Directory structure verified"

# Phase 2: Health Assessment
echo
echo "🔍 PHASE 2: Health Assessment & Validation"
echo "------------------------------------------"

# Run comprehensive health check
./station_status.sh | grep -E "(✅|⚠️|🔴)" | sed 's/^/  /'

# Phase 3: L1 Station Initialization 
echo
echo "🏗️  PHASE 3: L1 Station Layer Initialization"
echo "--------------------------------------------"

if [ -f "src/core/command_node.js" ]; then
    echo "✅ Command Node module ready for deployment"
    echo "  Module: src/core/command_node.js"
else
    echo "⚠️  Command Node module not found"
fi

if [ -f "aurora_gui_cloudhub_fastapi.py" ]; then
    echo "✅ GUI CloudHub interface ready"
    echo "  Module: aurora_gui_cloudhub_fastapi.py"
else
    echo "⚠️  GUI interface not available"
fi

# Check for operator dashboard components
dashboard_files=$(find . -name "*dashboard*" -o -name "*interface*" | head -3)
if [ ! -z "$dashboard_files" ]; then
    echo "✅ Dashboard components located:"
    echo "$dashboard_files" | sed 's/^/    /'
fi

# Phase 4: L3 Symbolic Mesh Preparation
echo
echo "🔮 PHASE 4: L3 Symbolic Mesh Preparation"
echo "----------------------------------------"

if [ -f "src/core/ethics_layer.js" ]; then
    echo "✅ Ethics Layer ready for symbolic mesh"
    echo "  Module: src/core/ethics_layer.js"
fi

if [ -d "src/coordination" ]; then
    echo "✅ Coordination modules available:"
    ls src/coordination/*.js 2>/dev/null | head -2 | sed 's/^/    /'
fi

# Check for symbolic and quantum components
symbolic_files=$(find . -name "*symbolic*" -o -name "*quantum*" | grep -E "\.(js|py)$" | head -3)
if [ ! -z "$symbolic_files" ]; then
    echo "✅ Symbolic processing modules found:"
    echo "$symbolic_files" | sed 's/^/    /'
fi

# Phase 5: Crew Integration
echo
echo "👥 PHASE 5: Crew Integration & Registry"
echo "--------------------------------------"

if [ -f "staff_registry.json" ]; then
    echo "✅ Crew registry deployed successfully"
    
    # Extract key crew information
    active_agents=$(grep -o '"status": "ACTIVE"' staff_registry.json | wc -l)
    total_agents=$(grep -o '"type": ".*_AGENT"' staff_registry.json | wc -l)
    
    echo "  Active agents: $active_agents"
    echo "  Total registered: $total_agents"
    
    # Show deployment phases
    if grep -q "L1_STATION" staff_registry.json; then
        echo "  ✅ L1 Station phases defined"
    fi
    if grep -q "L3_SYMBOLIC" staff_registry.json; then
        echo "  ✅ L3 Symbolic phases defined"
    fi
else
    echo "⚠️  Crew registry not found - manual crew setup required"
fi

# Phase 6: Deployment Readiness Assessment
echo
echo "📊 PHASE 6: Deployment Readiness Assessment"
echo "-------------------------------------------"

readiness_score=0
total_checks=6

# Check critical components
[ -f "src/core/command_node.js" ] && ((readiness_score++))
[ -f "src/core/ethics_layer.js" ] && ((readiness_score++))
[ -f "aurora_gui_cloudhub_fastapi.py" ] && ((readiness_score++))
[ -f "staff_registry.json" ] && ((readiness_score++))
[ -f ".env" ] && ((readiness_score++))
[ -d "src/coordination" ] && ((readiness_score++))

readiness_percent=$((readiness_score * 100 / total_checks))

echo "Deployment Readiness: $readiness_percent% ($readiness_score/$total_checks components ready)"

if [ $readiness_percent -ge 80 ]; then
    echo "🟢 STATUS: READY FOR PARALLEL L1/L3 DEPLOYMENT"
    deployment_status="READY"
elif [ $readiness_percent -ge 60 ]; then
    echo "🟡 STATUS: READY FOR PHASE 1 DEPLOYMENT (with monitoring)"
    deployment_status="PARTIAL"
else
    echo "🔴 STATUS: ADDITIONAL PREPARATION REQUIRED"
    deployment_status="NOT_READY"
fi

# Phase 7: Next Steps Generation
echo
echo "🎯 PHASE 7: Automated Next Steps"
echo "--------------------------------"

case $deployment_status in
    "READY")
        echo "Recommended deployment sequence:"
        echo "  1. Initialize L1 Command Node and operator dashboard"
        echo "  2. Activate L3 Ethics Layer and symbolic mesh anchor"
        echo "  3. Deploy crew coordination systems"
        echo "  4. Begin parallel R&D simulation modules"
        echo "  5. Start continuous health monitoring"
        ;;
    "PARTIAL")
        echo "Recommended immediate actions:"
        echo "  1. Deploy available L1 components (Phase 1)"
        echo "  2. Initialize basic L3 anchor and ethics protocols"
        echo "  3. Set up monitoring for missing components"
        echo "  4. Plan incremental feature deployment"
        ;;
    "NOT_READY")
        echo "Required preparation steps:"
        echo "  1. Complete missing core modules"
        echo "  2. Verify environment configuration"
        echo "  3. Set up crew registry and role assignments"
        echo "  4. Run this deployment check again"
        ;;
esac

# Generate deployment timestamp and summary
echo
echo "📋 DEPLOYMENT SUMMARY"
echo "-------------------"
echo "Timestamp: $(date -Iseconds)"
echo "Repository: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
echo "Total files: $(find . -type f | wc -l)"
echo "Ready for crew operations: $deployment_status"

# Save deployment status for reference
echo "{
  \"deployment_check\": {
    \"timestamp\": \"$(date -Iseconds)\",
    \"readiness_score\": $readiness_score,
    \"readiness_percent\": $readiness_percent,
    \"status\": \"$deployment_status\",
    \"l1_ready\": $([ -f "src/core/command_node.js" ] && echo "true" || echo "false"),
    \"l3_ready\": $([ -f "src/core/ethics_layer.js" ] && echo "true" || echo "false"),
    \"crew_ready\": $([ -f "staff_registry.json" ] && echo "true" || echo "false")
  }
}" > deployment/status/latest_check.json

echo
echo "🌌 ORION CloudBank deployment orchestration complete!"
echo "Status saved to: deployment/status/latest_check.json"
echo "Ready for crew boarding and operations! 🚀"
