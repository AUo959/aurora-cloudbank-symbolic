#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(pwd)"
VENV_DIR="${WORKSPACE_DIR}/.venv"

# The .venv path is a mounted Docker volume; it may come up root-owned.
if [[ -d "${VENV_DIR}" ]] && [[ ! -w "${VENV_DIR}" ]]; then
  echo "🔧 Repairing permissions on ${VENV_DIR} (requires sudo)..."
  sudo chown -R "$(id -u)":"$(id -g)" "${VENV_DIR}" 2>/dev/null || true
fi

python3 scripts/prevent_rebuild_failures.py || echo 'Post-start validation completed with warnings'
