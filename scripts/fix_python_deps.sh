#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[fix-python-deps] Delegating to setup_dependencies.sh"
"$SCRIPT_DIR/setup_dependencies.sh" "$@"
