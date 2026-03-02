#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "[setup-persistent-environment] Diagnostic mode (no environment files modified)."

for candidate in .env .env.example .devcontainer/devcontainer.json; do
  if [ -f "$candidate" ]; then
    echo "- present: $candidate"
  else
    echo "- missing: $candidate"
  fi
done

if [ -d .venv ]; then
  echo "- local virtual environment detected (.venv)"
else
  echo "- local virtual environment not detected (.venv)"
fi

echo "Guidance: create/update env files manually per project policy; this script intentionally performs diagnostics only."
