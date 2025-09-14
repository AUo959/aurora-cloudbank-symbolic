#!/bin/bash
# Aurora CloudBank Dependency Validation Script
# Quick validation of critical dependencies

cd "/home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic"

echo "🔧 Aurora CloudBank: Quick dependency validation..."

# Check if Python is working and has pip
if python3 -m pip --version >/dev/null 2>&1; then
    echo "✅ Python and pip are available"
else
    echo "❌ Python/pip issue detected"
    exit 1
fi

# Check for package.json if it exists
if [ -f "package.json" ]; then
    if command -v npm >/dev/null 2>&1; then
        echo "✅ Node.js and npm are available"
    else
        echo "⚠️  Node.js/npm not available but package.json exists"
    fi
fi

echo "🚀 Basic dependency validation complete"
