#!/bin/bash
# Aurora CloudBank Performance Optimization Script

echo "🔧 Optimizing Aurora CloudBank Workspace Performance..."

# 1. Clean up Python cache files
echo "🧹 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# 2. Clean up test artifacts
echo "🧪 Cleaning test artifacts..."
rm -rf htmlcov/ .coverage .pytest_cache/ 2>/dev/null || true

# 3. Clean up temporary files
echo "🗑️ Cleaning temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.log" -size +10M -delete 2>/dev/null || true

# 4. Optimize Git performance
echo "🔄 Optimizing Git performance..."
git config core.preloadindex true
git config core.fscache true
git config gc.auto 256

# 5. Set memory limits for Python processes
echo "🧠 Setting memory optimization..."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# 6. Check VS Code extensions causing high CPU
echo "📊 Performance analysis:"
echo "Large Python files (>1000 lines):"
find . -name "*.py" -exec wc -l {} + | sort -nr | head -5

echo "Memory usage by Python processes:"
ps aux | grep python | grep -v grep | awk '{print $6 " " $11}' | sort -nr | head -5

echo "✅ Performance optimization complete!"
echo ""
echo "💡 Additional recommendations:"
echo "1. Consider splitting large Python files (>1000 lines)"
echo "2. Disable Pylance for large files temporarily"
echo "3. Use workspace-specific Python interpreter"
echo "4. Consider excluding large directories from VS Code indexing"

# 7. Create .pylintrc to reduce linting overhead
cat > .pylintrc << 'EOF'
[MASTER]
disable=all
enable=E,F
jobs=1
persistent=no

[REPORTS]
output-format=text
reports=no

[MESSAGES CONTROL]
disable=C,R,W
EOF

echo "🔧 Created optimized .pylintrc"
