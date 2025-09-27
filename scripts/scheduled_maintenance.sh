#!/bin/bash
# Aurora CloudBank Scheduled Maintenance Script
# Runs branch cleanup and health monitoring

set -e

cd "$(dirname "$0")/.."

# Run branch cleanup
echo "[Maintenance] Running branch cleanup..."
python3 scripts/branch_cleanup.py

# Run health monitor
echo "[Maintenance] Running repository health monitor..."
python3 scripts/repo_health_monitor.py

echo "[Maintenance] Maintenance complete."
