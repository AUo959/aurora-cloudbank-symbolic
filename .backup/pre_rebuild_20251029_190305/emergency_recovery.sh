#!/bin/bash
# Emergency Recovery Script - Generated 20251029_190305
set -e

echo "🚨 Aurora CloudBank Emergency Recovery"
echo "====================================="

cd "/home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic"

# Remove corrupted environment
rm -rf .venv

# Create fresh environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install from backup
if [ -f "/home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic/.backup/pre_rebuild_20251029_190305/requirements-lock.txt" ]; then
    echo "Installing from backed up requirements-lock.txt..."
    pip install -r "/home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic/.backup/pre_rebuild_20251029_190305/requirements-lock.txt"
elif [ -f "/home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic/.backup/pre_rebuild_20251029_190305/pip_freeze.txt" ]; then
    echo "Installing from backed up pip freeze..."
    pip install -r "/home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic/.backup/pre_rebuild_20251029_190305/pip_freeze.txt"
else
    echo "❌ No backup requirements found"
    exit 1
fi

echo "✅ Emergency recovery completed"
