#!/bin/bash
# Aurora GUI CloudHub – Local Dev Starter

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
	PYTHON_BIN="$(command -v python3)"
fi

if [[ -f "$REPO_ROOT/.env" ]]; then
	set -a
	# shellcheck disable=SC1091
	source "$REPO_ROOT/.env"
	set +a
fi

echo "🔧 Starting Aurora ZIP Wizard GUI on http://localhost:8080"

# Optional: Create virtual environment
# python3 -m venv venv && source venv/bin/activate

# Launch app
"$PYTHON_BIN" "$REPO_ROOT/api/aurora_gui_cloudhub_fastapi.py"
