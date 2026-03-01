#!/bin/bash
# Monitor VS Code Extension Performance

echo "🔍 VS Code Performance Monitor"
echo "=============================="

echo ""
echo "💾 Memory Usage (Top Extensions):"
ps aux --sort=-%mem | grep -E "(code|node.*extension|sonarlint|pylance|tsserver)" | head -10 | awk '{printf "%-50s %sMB\n", $11, $6/1024}'

echo ""
echo "🔄 Extension Processes:"
echo "Extension Hosts: $(pgrep -f extensionHost | wc -l)"
echo "SonarQube: $(pgrep -f sonarlint | wc -l)"
echo "TypeScript: $(pgrep -f tsserver | wc -l)"
echo "Pylance: $(pgrep -f pylance | wc -l)"

echo ""
echo "📊 Total Resource Usage:"
total_mem=$(ps aux | grep -E "(extensionHost|sonarlint|tsserver|pylance)" | awk '{sum += $6} END {print sum/1024}')
echo "Total Extension Memory: ${total_mem}MB"

echo ""
echo "🎯 Performance Recommendations:"
if [ "$(pgrep -f sonarlint | wc -l)" -gt 1 ]; then
    echo "⚠️ Multiple SonarQube instances detected - consider disabling"
fi

if [ "${total_mem%.*}" -gt 1000 ]; then
    echo "⚠️ High memory usage detected (${total_mem}MB)"
    echo "   Consider closing unused VS Code windows"
fi

echo "✅ Use 'code --disable-extensions' for lightweight sessions"
echo "✅ Regularly restart VS Code to clear memory leaks"
