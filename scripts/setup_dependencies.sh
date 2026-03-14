#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENSURE_PYTHON_SCRIPT="$SCRIPT_DIR/ensure_python.sh"
PYTHON_VERSION="${AURORA_PYTHON_VERSION:-$(tr -d '[:space:]' < "$REPO_ROOT/.python-version" 2>/dev/null || echo 3.11.11)}"
VENV_DIR="${AURORA_VENV_DIR:-$REPO_ROOT/.venv}"
INSTALL_OPTIONAL=0
EXECUTE=0
INSTALL_PYTHON=0
PYTHON_BIN="${AURORA_PYTHON_BIN:-}"
UV_BIN="${AURORA_UV_BIN:-}"
UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"

cd "$REPO_ROOT"

if [ -z "$UV_BIN" ]; then
  if command -v uv >/dev/null 2>&1; then
    UV_BIN="$(command -v uv)"
  elif [ -x "$HOME/.local/bin/uv" ]; then
    UV_BIN="$HOME/.local/bin/uv"
  fi
fi

usage() {
  cat <<EOF
Usage: $(basename "$0") [--execute] [--install-python] [--include-optional] [--python-version VERSION]

Diagnose or bootstrap the Aurora Python environment.

Modes:
  Diagnostic mode:    Diagnose interpreter and dependency readiness without writing
  --execute           Create/update .venv and install dependencies
  --install-python    Attempt to install the required Python runtime before bootstrapping
  --include-optional  Install requirements-optional.txt when present

Environment overrides:
  AURORA_PYTHON_VERSION   Desired interpreter version (default: .python-version)
  AURORA_PYTHON_BIN       Explicit interpreter path to use
  AURORA_VENV_DIR         Virtualenv path (default: $REPO_ROOT/.venv)
  AURORA_PYTHON_INSTALLER Preferred installer for ensure_python.sh (auto|uv|pyenv|brew)

Guidance: default mode is a no-op diagnostic check. Re-run with --execute for installs.
EOF
}

diagnose() {
  echo "[setup-dependencies] Repository: $REPO_ROOT"
  echo "[setup-dependencies] Desired Python version: $PYTHON_VERSION"
  echo "[setup-dependencies] Virtual environment path: $VENV_DIR"
  if [ -n "$PYTHON_BIN" ]; then
    echo "[setup-dependencies] Explicit interpreter override: $PYTHON_BIN"
  fi

  if compatible_python="$("$ENSURE_PYTHON_SCRIPT" --python-version "$PYTHON_VERSION" --print-path 2>/dev/null)"; then
    echo "[setup-dependencies] Compatible interpreter detected: $compatible_python"
    "$compatible_python" --version
  else
    echo "[setup-dependencies] Compatible interpreter not detected."
    "$ENSURE_PYTHON_SCRIPT" --python-version "$PYTHON_VERSION" || true
  fi

  if [ -f requirements.txt ]; then
    echo "[setup-dependencies] requirements.txt detected"
    rg -n "^(fastapi|pytest-asyncio|schedule)" requirements.txt || true
  else
    echo "[setup-dependencies] requirements.txt missing"
  fi

  if [ -d "$VENV_DIR" ]; then
    echo "[setup-dependencies] Existing virtual environment detected"
  else
    echo "[setup-dependencies] Virtual environment not present"
  fi

  echo "[setup-dependencies] Diagnostic mode: dry-run complete. Re-run with --execute to build .venv."
  echo "[setup-dependencies] Guidance: add --install-python if Python 3.11 needs to be installed first."
}

use_uv_workflow() {
  [ -n "$UV_BIN" ]
}

while [ $# -gt 0 ]; do
  case "$1" in
    --execute)
      EXECUTE=1
      ;;
    --install-python)
      INSTALL_PYTHON=1
      ;;
    --include-optional)
      INSTALL_OPTIONAL=1
      ;;
    --python-version)
      shift
      PYTHON_VERSION="${1:-}"
      [ -n "$PYTHON_VERSION" ] || { echo "[setup-dependencies] Missing value for --python-version" >&2; exit 2; }
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[setup-dependencies] Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [ "$EXECUTE" -eq 0 ]; then
  diagnose
  exit 0
fi

if [ ! -x "$ENSURE_PYTHON_SCRIPT" ]; then
  echo "[setup-dependencies] ensure_python.sh is missing or not executable" >&2
  exit 1
fi

if [ -z "$PYTHON_BIN" ]; then
  ensure_args=(--python-version "$PYTHON_VERSION" --print-path)
  if [ "$INSTALL_PYTHON" -eq 1 ]; then
    ensure_args+=(--install)
  fi
  if ! PYTHON_BIN="$("$ENSURE_PYTHON_SCRIPT" "${ensure_args[@]}")"; then
    echo "[setup-dependencies] Unable to resolve a compatible Python interpreter." >&2
    echo "[setup-dependencies] Re-run with --install-python after installing uv, pyenv, or brew on this machine." >&2
    exit 1
  fi
fi

if [ ! -f requirements.txt ]; then
  echo "[setup-dependencies] requirements.txt not found." >&2
  exit 1
fi

echo "[setup-dependencies] Repository: $REPO_ROOT"
echo "[setup-dependencies] Using interpreter: $PYTHON_BIN"
echo "[setup-dependencies] Creating virtual environment at $VENV_DIR"
if use_uv_workflow; then
  echo "[setup-dependencies] Using uv-managed virtual environment workflow"
  UV_CACHE_DIR="$UV_CACHE_DIR" "$UV_BIN" venv --clear --python "$PYTHON_BIN" "$VENV_DIR"
else
  "$PYTHON_BIN" -m venv --clear "$VENV_DIR"
  echo "[setup-dependencies] Upgrading pip"
  "$VENV_DIR/bin/python" -m pip install --upgrade pip
fi

echo "[setup-dependencies] Installing core Python requirements"
if use_uv_workflow; then
  UV_CACHE_DIR="$UV_CACHE_DIR" "$UV_BIN" pip install --python "$VENV_DIR/bin/python" -r requirements.txt
else
  "$VENV_DIR/bin/python" -m pip install -r requirements.txt
fi

if [ "$INSTALL_OPTIONAL" -eq 1 ] && [ -f requirements-optional.txt ]; then
  echo "[setup-dependencies] Installing optional Python requirements"
  if use_uv_workflow; then
    UV_CACHE_DIR="$UV_CACHE_DIR" "$UV_BIN" pip install --python "$VENV_DIR/bin/python" -r requirements-optional.txt
  else
    "$VENV_DIR/bin/python" -m pip install -r requirements-optional.txt
  fi
fi

echo "[setup-dependencies] Verifying critical packages"
"$VENV_DIR/bin/python" - <<'PY'
import fastapi
import pytest_asyncio
import sys

print(f"python={sys.version.split()[0]}")
print(f"fastapi={fastapi.__version__}")
print(f"pytest_asyncio={pytest_asyncio.__version__}")
PY

if [ -f package.json ]; then
  echo "[setup-dependencies] package.json detected. Node dependencies remain an explicit separate step."
fi

echo "[setup-dependencies] Python environment ready at $VENV_DIR"
