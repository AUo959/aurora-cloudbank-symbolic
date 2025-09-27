#!/bin/bash
# Aurora CloudBank Pre-Rebuild Protection Hook
set -e

echo "🛡️ Aurora CloudBank Pre-Rebuild Protection"
echo "==========================================="

# Run backup and validation
python3 "/workspaces/aurora-cloudbank-symbolic/scripts/prevent_rebuild_failures.py" --pre-rebuild

echo "✅ Pre-rebuild protection completed"
