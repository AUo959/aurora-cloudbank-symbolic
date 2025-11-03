#!/bin/bash

# ORION CloudBank - Station Status Monitor
# Integrated Health Check and Deployment Status Script

echo "🌌 ORION CloudBank Station Status Report"
echo "========================================"
echo "Date: $(date)"
echo "Location: $(pwd)"
echo

# System Health Check
echo "🔧 SYSTEM HEALTH CHECK"
echo "----------------------"

# Git Status
echo "📦 Repository Status:"
git status --porcelain | wc -l | xargs -I {} echo "  Uncommitted files: {}"
git branch --show-current | xargs -I {} echo "  Current branch: {}"
echo

# Disk Usage
echo "💾 Storage Status:"
df -h . | tail -1 | awk '{print "  Available space: " $4 " (" $5 " used)"}'
du -sh . | awk '{print "  Repository size: " $1}'
echo

# Python Environment
echo "🐍 Python Environment:"
/bin/python3 --version | sed 's/^/  /'
echo "  Package manager: pip $(pip3 --version 2>/dev/null | cut -d' ' -f2 || echo 'not available')"
echo

# File Structure Analysis
echo "📁 Project Structure:"
echo "  Core modules: $(find src -name "*.py" -o -name "*.js" | wc -l) files"
echo "  Documentation: $(find . -name "*.md" | wc -l) files"
echo "  Configuration: $(find . -name "*.json" -o -name "*.yaml" -o -name "*.yml" | wc -l) files"
echo

# Crew and Deployment Status
echo "👥 CREW & DEPLOYMENT STATUS"
echo "---------------------------"

if [ -f "staff_registry.json" ]; then
    echo "✅ Crew registry available"
    echo "  Total agents: $(grep -o '"id":' staff_registry.json | wc -l)"
else
    echo "⚠️  Crew registry not found"
fi

# Phase Status Check
echo
echo "🚀 DEPLOYMENT PHASES:"
echo "  L1 (Station Operations):"
if [ -f "src/core/command_node.js" ]; then
    echo "    ✅ Phase 1: Command node ready"
else
    echo "    ⚠️  Phase 1: Command node missing"
fi

if [ -f "aurora_gui_cloudhub_fastapi.py" ]; then
    echo "    ✅ Phase 2: GUI interface ready"
else
    echo "    ⚠️  Phase 2: GUI interface missing"
fi

echo "  L3 (Symbolic Mesh):"
if [ -f "src/core/ethics_layer.js" ]; then
    echo "    ✅ Phase 1: Ethics layer ready"
else
    echo "    ⚠️  Phase 1: Ethics layer missing"
fi

if [ -d "src/coordination" ]; then
    echo "    ✅ Phase 2: Coordination modules ready"
else
    echo "    ⚠️  Phase 2: Coordination modules missing"
fi

echo
echo "🎯 RECOMMENDED ACTIONS:"
echo "----------------------"

# Check for immediate actions needed
if ! command -v node &> /dev/null; then
    echo "  🔴 CRITICAL: Node.js environment needs configuration"
fi

if [ ! -f ".env" ]; then
    echo "  🟡 MEDIUM: Environment configuration needed"
else
    echo "  ✅ Environment file present"
fi

if [ ! -d "node_modules" ] && [ -f "package.json" ]; then
    echo "  🟡 MEDIUM: Node.js dependencies need installation"
fi

# Success indicators
total_py_files=$(find . -name "*.py" | wc -l)
total_js_files=$(find . -name "*.js" | wc -l)

if [ $total_py_files -gt 10 ] && [ $total_js_files -gt 10 ]; then
    echo "  ✅ Codebase appears comprehensive"
fi

echo
echo "📊 DEPLOYMENT READINESS: $([ -f "staff_registry.json" ] && [ -f "src/core/command_node.js" ] && echo "READY FOR L1 PHASE 1" || echo "PREPARATION NEEDED")"
echo
echo "Station Status Complete. Ready for crew operations! 🚀"
