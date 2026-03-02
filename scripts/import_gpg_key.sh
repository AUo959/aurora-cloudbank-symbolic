#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "[import-gpg-key] Diagnostic mode (no import executed)."

if [ "${1:-}" != "" ]; then
  if [ -f "$1" ]; then
    echo "- candidate key file exists: $1"
  else
    echo "- provided key file not found: $1"
  fi
else
  echo "- no key file argument provided"
fi

echo "Guidance: to import explicitly, run: gpg --import <path-to-keyfile>."
