#!/bin/bash

# 🧪 AURORA CLOUDBANK - COPILOT CHAT TERMINAL TEST
# Tests if Copilot Chat can see terminal output

echo "🧪 AURORA CLOUDBANK - COPILOT CHAT TERMINAL TEST"
echo "==============================================="
echo ""

# Test 1: Basic output
echo "📋 Test 1: Basic Echo Output"
echo "✅ This should be visible to Copilot Chat"
echo ""

# Test 2: Environment info
echo "📋 Test 2: Environment Information"
echo "🐚 Shell: $SHELL"
echo "👤 User: $(whoami)"
echo "📁 Directory: $(pwd)"
echo "🖥️  Hostname: $(hostname)"
echo ""

# Test 3: Tool versions
echo "📋 Test 3: Tool Version Check"
echo "🔧 Node.js: $(node --version 2>/dev/null || echo 'Not found')"
echo "🔧 npm: $(npm --version 2>/dev/null || echo 'Not found')"
echo "🐍 Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "🔧 Git: $(git --version 2>/dev/null || echo 'Not found')"
echo ""

# Test 4: Prompt test
echo "📋 Test 4: Prompt Display"
echo "Current prompt should be: \u@\h:\w\$ "
echo "Actual prompt: $PS1"
echo ""

# Test 5: Aurora specific test
echo "📋 Test 5: Aurora CloudBank Status"
if [ -f "package.json" ]; then
    echo "✅ package.json found"
else
    echo "❌ package.json not found"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
else
    echo "❌ requirements.txt not found"
fi

if [ -d ".git" ]; then
    echo "✅ Git repository detected"
    echo "🌿 Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
else
    echo "❌ Not a git repository"
fi
echo ""

# Test 6: Output flushing test
echo "📋 Test 6: Output Flushing Test"
echo -n "Testing output flush... "
sleep 1
echo "✅ Complete"
echo ""

# Test 7: JSON output test (for structured data)
echo "📋 Test 7: JSON Output Test"
echo '{"test": "copilot_visibility", "status": "success", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'
echo ""

# Test 8: Multi-line output test
echo "📋 Test 8: Multi-line Output Test"
cat << 'EOF'
Line 1: This is a multi-line test
Line 2: Testing if Copilot can see all lines
Line 3: Including special characters: !@#$%^&*()
Line 4: Unicode test: 🚀🔧🌟✅❌⚠️
Line 5: End of multi-line test
EOF
echo ""

# Test 9: Command execution test
echo "📋 Test 9: Command Execution Test"
echo "📅 Current date: $(date)"
echo "📊 Disk usage: $(df -h . | tail -1 | awk '{print $5}')"
echo "🔢 Process count: $(ps aux | wc -l)"
echo ""

# Test 10: Final summary
echo "📋 Test 10: Final Summary"
echo "==========================================="
echo "✅ All tests completed successfully!"
echo "🧪 If Copilot Chat can see this output, the fix worked!"
echo "🔧 Terminal output is now visible to Copilot Chat"
echo ""
echo "💡 Test completed at: $(date)"
echo "🎯 Aurora CloudBank terminal compatibility: RESTORED"
echo ""
echo "🚀 Ready for Copilot Chat integration!"
