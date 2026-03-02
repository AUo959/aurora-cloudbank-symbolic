#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "[setup-dependencies] Diagnostic mode (no changes applied)."
echo "Repository: $REPO_ROOT"

if [ -f requirements.txt ]; then
  py_req_count=$(grep -Ev '^\s*#|^\s*$' requirements.txt | wc -l | tr -d ' ')
  echo "- requirements.txt detected (${py_req_count} entries)"
else
  echo "- requirements.txt not found"
fi

if [ -f package.json ]; then
  echo "- package.json detected"
else
  echo "- package.json not found"
fi

if command -v python3 >/dev/null 2>&1; then
  echo "- python3: $(python3 --version 2>/dev/null)"
else
  echo "- python3 not installed"
fi

if command -v npm >/dev/null 2>&1; then
  echo "- npm: $(npm --version 2>/dev/null)"
else
  echo "- npm not installed"
fi

echo "Guidance: install deps manually using project-approved commands (for example, python3 -m pip install -r requirements.txt or npm ci)."
