#!/bin/bash
# Aurora CloudBank Resource Monitor

echo "🔍 Aurora CloudBank Resource Usage Monitor"
echo "=========================================="

echo "📊 Current System Resources:"
echo "CPU Usage:"
cat /proc/loadavg
echo ""

echo "Memory Usage:"
free -h
echo ""

echo "🐍 Python Process Analysis:"
echo "VS Code Python Language Servers:"
ps aux | grep python | grep -E "(pylint|pylance)" | head -5
echo ""

echo "📁 Large Python Files Analysis:"
echo "Files > 1000 lines:"
find . -name "*.py" -exec wc -l {} + 2>/dev/null | awk '$1 > 1000 {print $1 " lines: " $2}' | sort -nr | head -10

echo ""
echo "📁 Largest directories by file count:"
find . -type d -name "*.py" -prune -o -type d -exec sh -c 'echo "$(find "$1" -name "*.py" | wc -l) files in $1"' _ {} \; 2>/dev/null | sort -nr | head -10

echo ""
echo "💾 Disk Usage by Directory:"
du -sh */ 2>/dev/null | sort -hr | head -10

echo ""
echo "🧪 Test File Analysis:"
find tests/ -name "*.py" -exec wc -l {} + 2>/dev/null | sort -nr | head -5
