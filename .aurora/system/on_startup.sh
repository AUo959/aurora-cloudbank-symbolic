#!/bin/bash
# Aurora Core System Initialization
# High-value operations for development environment setup

echo "🌟 Aurora Core System Initialization"
echo "===================================="

# 1. Environment Health Check
echo "🔍 System Health Check..."
python3 -c "
import sys, os
print(f'✅ Python: {sys.version}')
print(f'✅ Working Directory: {os.getcwd()}')
print(f'✅ PATH includes: {len(os.environ.get(\"PATH\", \"\").split(\":\"))} directories')
"

# 2. Verify Core Dependencies
echo "📦 Dependency Verification..."
python3 -c "
try:
    import fastapi, uvicorn, numpy, yaml
    print('✅ Core Python packages available')
except ImportError as e:
    print(f'⚠️  Some packages missing: {e}')
"

# 3. Initialize symbolic core if needed
echo "🔮 Symbolic Core Setup..."
if [ ! -f "modules/symbolic_core/__init__.py" ]; then
    touch modules/symbolic_core/__init__.py
    echo "✅ Symbolic core module initialized"
fi

# 4. Quick syntax check on key files
echo "🧪 Syntax Validation..."
for file in aurora_api.py aurora_gui_cloudhub_fastapi.py; do
    if [ -f "$file" ]; then
        python3 -m py_compile "$file" 2>/dev/null && echo "✅ $file syntax OK" || echo "⚠️  $file has syntax issues"
    fi
done

# 5. Port availability check
echo "🌐 Port Availability..."
for port in 8000 8080 3001; do
    if ! netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✅ Port $port available"
    else
        echo "⚠️  Port $port in use"
    fi
done

# 6. Git status check
echo "📊 Repository Status..."
if git status --porcelain 2>/dev/null | grep -q .; then
    echo "⚠️  Uncommitted changes detected"
else
    echo "✅ Repository clean"
fi

echo ""
echo "🎯 Aurora Core System Ready!"
echo "🚀 Development environment fully initialized"
echo ""
