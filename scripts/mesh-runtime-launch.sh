#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python"

load_env_file() {
  local env_file="$1"
  if [[ -f "$env_file" ]]; then
    set -a
    source "$env_file"
    set +a
  fi
}

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Mesh runtime launcher could not find $PYTHON_BIN" >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/runtime/mesh"
load_env_file "$REPO_ROOT/.env"
load_env_file "$REPO_ROOT/.env.mesh"
export PYTHONUNBUFFERED=1

exec "$PYTHON_BIN" "$REPO_ROOT/src/servers/l2_integration_server.py" --host 127.0.0.1 --port 8000
