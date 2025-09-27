#!/bin/bash

# Aurora CloudBank Rebuild Prevention System
# Comprehensive protection against DevContainer rebuild failures

set -e

echo "🛡️ Aurora CloudBank Rebuild Prevention System"
echo "=============================================="

# Configuration
WORKSPACE_ROOT="$(pwd)"
PREVENTION_STATUS=".rebuild_prevention_active"
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

echo "📊 Prevention System Status Check"
echo "Time: $CURRENT_TIME"
echo "Workspace: $WORKSPACE_ROOT"
echo ""

# Check if prevention system is active
if [[ -f ".rebuild_prevention_status.json" ]]; then
    echo "✅ Prevention system status file found"
    if command -v jq >/dev/null 2>&1; then
        STATUS=$(jq -r '.status' .rebuild_prevention_status.json 2>/dev/null || echo "unknown")
        TIMESTAMP=$(jq -r '.timestamp' .rebuild_prevention_status.json 2>/dev/null || echo "unknown")
        echo "   Status: $STATUS"
        echo "   Last update: $TIMESTAMP"
    else
        echo "   (jq not available, showing raw content)"
        head -3 .rebuild_prevention_status.json
    fi
else
    echo "⚠️ Prevention system not yet initialized"
fi

echo ""
echo "🔍 System Component Status:"

# Check DevContainer configuration
if [[ -f ".devcontainer/devcontainer-improved.json" ]]; then
    echo "✅ Improved DevContainer configuration available"
else
    echo "⚠️ Improved DevContainer configuration not found"
fi

# Check emergency recovery script
if [[ -f "scripts/emergency_rebuild_recovery.sh" ]]; then
    echo "✅ Emergency recovery script available"
else
    echo "❌ Emergency recovery script missing"
fi

# Check prevention script
if [[ -f "scripts/prevent_rebuild_failures.py" ]]; then
    echo "✅ Prevention system script available"
else
    echo "❌ Prevention system script missing"
fi

# Check git hooks
if git config core.hooksPath >/dev/null 2>&1; then
    HOOKS_PATH=$(git config core.hooksPath)
    echo "✅ Git hooks configured: $HOOKS_PATH"
else
    echo "⚠️ Git hooks not configured"
fi

# Check backup system
if [[ -d ".backup" ]]; then
    BACKUP_COUNT=$(find .backup -name "*.txt" -type f | wc -l)
    echo "✅ Backup system active ($BACKUP_COUNT backup files)"
else
    echo "⚠️ Backup system not initialized"
fi

echo ""
echo "🎯 Next Steps to Complete Prevention Setup:"
echo ""

if [[ ! -f ".devcontainer/devcontainer.json.backup" ]]; then
    echo "1. 📝 Backup current DevContainer config:"
    echo "   cp .devcontainer/devcontainer.json .devcontainer/devcontainer.json.backup"
    echo ""
fi

echo "2. 🔧 Apply improved DevContainer configuration:"
echo "   cp .devcontainer/devcontainer-improved.json .devcontainer/devcontainer.json"
echo ""

echo "3. 🧪 Test the prevention system:"
echo "   python3 scripts/prevent_rebuild_failures.py"
echo ""

echo "4. 🚨 Test emergency recovery (if needed):"
echo "   bash scripts/emergency_rebuild_recovery.sh"
echo ""

echo "5. 🔄 When rebuilding the container:"
echo "   • The prevention system will automatically run"
echo "   • Backups will be created before rebuild"
echo "   • Emergency recovery will be available if needed"
echo ""

echo "🎉 Aurora CloudBank Rebuild Protection System Ready!"

# Create activation marker
echo "{\"status\":\"prevention_system_ready\",\"timestamp\":\"$CURRENT_TIME\"}" > "$PREVENTION_STATUS"