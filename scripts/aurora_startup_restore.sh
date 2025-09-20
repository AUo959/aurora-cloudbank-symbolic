#!/bin/bash
# Aurora CloudBank Dependency Restoration Script
# Automatically restores dependencies on system startup

cd "/home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic"

echo "🔧 Aurora CloudBank: Checking dependency health..."

# Check if dependencies are healthy
python3 scripts/aurora_comprehensive_dependency_manager.py --health-check > /tmp/aurora_health.log 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  Dependencies need restoration, attempting recovery..."
    python3 /home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic/scripts/aurora_dependency_persistence.py --restore-from-latest
    
    # If restoration fails, try installing from requirements
    if [ $? -ne 0 ]; then
        echo "🔄 Fallback: Installing from requirements..."
        python3 scripts/aurora_comprehensive_dependency_manager.py --install
    fi
else
    echo "✅ Dependencies are healthy"
fi

echo "🚀 Aurora CloudBank dependency check complete"
