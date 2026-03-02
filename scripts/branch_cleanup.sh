#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[branch-cleanup] Delegating to branch_manager.py (default dry-run)."
exec python3 "$SCRIPT_DIR/branch_manager.py" --cleanup "$@"
