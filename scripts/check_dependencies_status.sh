#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "[check-dependencies-status] Diagnostic mode."

if command -v python3 >/dev/null 2>&1; then
  echo "- python3: $(python3 --version 2>/dev/null)"
  if python3 -m pip --version >/dev/null 2>&1; then
    echo "- pip available"
    if python3 -m pip check >/dev/null 2>&1; then
      echo "- pip dependency check: ok"
    else
      echo "- pip dependency check: issues detected (run 'python3 -m pip check' for details)"
    fi
  else
    echo "- pip unavailable"
  fi
else
  echo "- python3 unavailable"
fi

if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "- npm: $(npm --version 2>/dev/null)"
    if [ -d node_modules ]; then
      if npm ls --depth=0 >/dev/null 2>&1; then
        echo "- npm dependency tree: ok"
      else
        echo "- npm dependency tree: issues detected (run 'npm ls --depth=0' for details)"
      fi
    else
      echo "- node_modules missing (dependency tree check skipped)"
    fi
  else
    echo "- npm unavailable"
  fi
fi
