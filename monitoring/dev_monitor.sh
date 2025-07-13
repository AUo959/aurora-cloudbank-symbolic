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
