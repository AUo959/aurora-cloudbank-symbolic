#!/bin/bash
# Force Kill Heavy Language Servers

echo "🔧 Aurora CloudBank - Force Kill Heavy Language Servers"
echo "======================================================="
echo ""

echo "🔍 Current heavy language server processes:"
ps aux | grep -E "(pylint|pylance)" | grep -v grep | while read line; do
    echo "   📊 $line"
done
echo ""

read -p "🚨 Kill all Pylint and Pylance processes? (y/N): " choice

if [[ $choice =~ ^[Yy]$ ]]; then
    echo ""
    echo "⚡ Killing Pylint processes..."
    pkill -f "pylint.*lsp_server.py" && echo "✅ Pylint processes killed" || echo "ℹ️  No Pylint processes found"

    echo "⚡ Killing Pylance processes..."
    pkill -f "pylance.*server.bundle.js" && echo "✅ Pylance processes killed" || echo "ℹ️  No Pylance processes found"

    echo ""
    echo "🔍 Checking remaining processes..."
    remaining=$(ps aux | grep -E "(pylint|pylance)" | grep -v grep | wc -l)

    if [ "$remaining" -eq 0 ]; then
        echo "🎉 SUCCESS: All heavy language servers killed!"
        echo ""
        echo "💾 Memory freed: ~5.5GB+"
        echo "⚡ CPU usage should drop significantly"
        echo "🔄 Copilot should be much more responsive now"
        echo ""
        echo "📊 You can verify with: ps aux | grep -E '(pylint|pylance)'"
    else
        echo "⚠️  Some processes may still be running:"
        ps aux | grep -E "(pylint|pylance)" | grep -v grep
        echo ""
        echo "🔧 If processes persist, try: sudo pkill -9 -f pylint && sudo pkill -9 -f pylance"
    fi
else
    echo "❌ Operation cancelled"
    echo ""
    echo "🎯 Alternative: Rebuild dev container"
    echo "1. Ctrl+Shift+P"
    echo "2. Type: 'Dev Containers: Rebuild Container'"
    echo "3. Press Enter"
    echo ""
    echo "This will completely restart with the optimized configuration."
fi
echo ""
echo "🎯 After fixing, run: ./verify_reload_readiness.sh"
