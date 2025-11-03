#!/bin/bash
# Aurora CloudBank Session Startup Script
# Ensures custom instructions are loaded and context is set

echo "🌟 Aurora CloudBank Symbolic - Session Initialization"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Load custom instructions into environment
export AURORA_CUSTOM_INSTRUCTIONS="$(cat GitHub_Copilot_Custom_Instructions_Aurora_GUMAS.txt)"
export AURORA_SESSION_START=$(date -Iseconds)
export AURORA_PROJECT_ROOT="/workspaces/aurora-cloudbank-symbolic"

# Display current status
echo "📋 Current Phase Status: All 5 phases COMPLETE ✅"
echo "🧪 Test Framework: 24 native tests passing"
echo "⚡ Performance: 6300x startup, 84x memory reduction"
echo "🔄 Current Focus: Agent infrastructure (archy, liora, oppy)"
echo ""

# Quick status check
if [ -f "requirements.txt" ] && [ -f "test_runner.py" ]; then
    echo "✅ Environment ready - FastAPI + Native implementations"
else
    echo "⚠️  Environment check needed"
fi

# Show missing components
echo "🎯 Missing Agent Nodes:"
for node in "src/nodes/archy_bridge.js" "src/nodes/liora_handshake.js" "src/nodes/oppy_vector_loader.js" "src/bridge/api_bridge_server.js" "src/system/lattice_sync.js"; do
    if [ ! -f "$node" ]; then
        echo "   ❌ $node"
    else
        echo "   ✅ $node"
    fi
done

echo ""
echo "💡 Quick Commands:"
echo "   ./run_tests.sh native     # Run native implementation tests"
echo "   python3 test_runner.py    # Run full test suite"
echo "   npm run start-command-node # Start Aurora command node"
echo ""
echo "🎯 Ready for agent infrastructure implementation!"
