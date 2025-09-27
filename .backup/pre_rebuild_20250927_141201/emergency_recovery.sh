#!/bin/bash
# Emergency Recovery Script - Generated 20250927_141201
set -e

echo "🚨 Aurora CloudBank Emergency Recovery"
echo "=====================================" 

cd "/workspaces/aurora-cloudbank-symbolic"

# Remove corrupted environment
rm -rf .venv

# Create fresh environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install from backup
if [ -f "/workspaces/aurora-cloudbank-symbolic/.backup/pre_rebuild_20250927_141201/requirements-lock.txt" ]; then
    echo "Installing from backed up requirements-lock.txt..."
    pip install -r "/workspaces/aurora-cloudbank-symbolic/.backup/pre_rebuild_20250927_141201/requirements-lock.txt"
elif [ -f "/workspaces/aurora-cloudbank-symbolic/.backup/pre_rebuild_20250927_141201/pip_freeze.txt" ]; then
    echo "Installing from backed up pip freeze..."
    pip install -r "/workspaces/aurora-cloudbank-symbolic/.backup/pre_rebuild_20250927_141201/pip_freeze.txt"
else
    echo "❌ No backup requirements found"
    exit 1
fi

echo "✅ Emergency recovery completed"
