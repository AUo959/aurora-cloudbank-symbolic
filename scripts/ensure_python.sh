#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VERSION_FILE="$REPO_ROOT/.python-version"
DEFAULT_VERSION="3.11.11"
PYTHON_VERSION="${AURORA_PYTHON_VERSION:-}"
PREFERRED_INSTALLER="${AURORA_PYTHON_INSTALLER:-auto}"
INSTALL=0
PRINT_PATH=0

if [ -z "$PYTHON_VERSION" ]; then
  if [ -f "$VERSION_FILE" ]; then
    PYTHON_VERSION="$(tr -d '[:space:]' < "$VERSION_FILE")"
  else
    PYTHON_VERSION="$DEFAULT_VERSION"
  fi
fi

usage() {
  cat <<EOF
Usage: $(basename "$0") [--install] [--print-path] [--python-version VERSION] [--installer auto|uv|pyenv|brew]

Diagnose or install a compatible Python 3.11 runtime for this repository.

Examples:
  $(basename "$0")
  $(basename "$0") --install
  $(basename "$0") --install --installer uv
  $(basename "$0") --print-path
EOF
}

major_minor() {
  local version="$1"
  echo "$version" | awk -F. '{print $1 "." $2}'
}

DESIRED_MM="$(major_minor "$PYTHON_VERSION")"
COMMAND_NAME="python${DESIRED_MM}"

python_version() {
  "$1" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null
}

is_compatible_python() {
  local interpreter="$1"
  local version

  if [ ! -x "$interpreter" ]; then
    return 1
  fi

  version="$(python_version "$interpreter")" || return 1
  [ "$(major_minor "$version")" = "$DESIRED_MM" ]
}

find_existing_python() {
  local explicit_bin="${AURORA_PYTHON_BIN:-}"
  local candidate

  if [ -n "$explicit_bin" ] && is_compatible_python "$explicit_bin"; then
    echo "$explicit_bin"
    return 0
  fi

  for candidate in "$REPO_ROOT/.venv/bin/python" "$COMMAND_NAME"; do
    if [ -x "$candidate" ] && is_compatible_python "$candidate"; then
      echo "$candidate"
      return 0
    fi
    if command -v "$candidate" >/dev/null 2>&1; then
      candidate="$(command -v "$candidate")"
      if is_compatible_python "$candidate"; then
        echo "$candidate"
        return 0
      fi
    fi
  done

  if command -v brew >/dev/null 2>&1; then
    candidate="$(brew --prefix "python@${DESIRED_MM}" 2>/dev/null || true)"
    if [ -n "$candidate" ] && is_compatible_python "$candidate/bin/${COMMAND_NAME}"; then
      echo "$candidate/bin/${COMMAND_NAME}"
      return 0
    fi
  fi

  if command -v pyenv >/dev/null 2>&1; then
    while IFS= read -r candidate; do
      [ -n "$candidate" ] || continue
      candidate="$(pyenv root)/versions/$candidate/bin/python"
      if is_compatible_python "$candidate"; then
        echo "$candidate"
        return 0
      fi
    done < <(pyenv versions --bare 2>/dev/null || true)
  fi

  return 1
}

resolve_pyenv_version() {
  local requested="$1"

  if [[ "$requested" == *.*.* ]]; then
    echo "$requested"
    return 0
  fi

  pyenv install --list 2>/dev/null | awk '/^[[:space:]]*3\.11\.[0-9]+$/ {gsub(/^[[:space:]]+/, "", $0); version=$0} END {print version}'
}

install_with_uv() {
  uv python install "$DESIRED_MM"
}

install_with_pyenv() {
  local resolved
  resolved="$(resolve_pyenv_version "$PYTHON_VERSION")"
  if [ -z "$resolved" ]; then
    echo "[ensure-python] Unable to resolve a pyenv patch release for $PYTHON_VERSION" >&2
    return 1
  fi
  pyenv install -s "$resolved"
}

install_with_brew() {
  brew install "python@${DESIRED_MM}"
}

install_python() {
  case "$PREFERRED_INSTALLER" in
    auto)
      if command -v uv >/dev/null 2>&1; then
        echo "[ensure-python] Installing Python via uv"
        install_with_uv
        return 0
      fi
      if command -v pyenv >/dev/null 2>&1; then
        echo "[ensure-python] Installing Python via pyenv"
        install_with_pyenv
        return 0
      fi
      if command -v brew >/dev/null 2>&1; then
        echo "[ensure-python] Installing Python via Homebrew"
        install_with_brew
        return 0
      fi
      ;;
    uv)
      command -v uv >/dev/null 2>&1 || { echo "[ensure-python] uv not found" >&2; return 1; }
      install_with_uv
      return 0
      ;;
    pyenv)
      command -v pyenv >/dev/null 2>&1 || { echo "[ensure-python] pyenv not found" >&2; return 1; }
      install_with_pyenv
      return 0
      ;;
    brew)
      command -v brew >/dev/null 2>&1 || { echo "[ensure-python] brew not found" >&2; return 1; }
      install_with_brew
      return 0
      ;;
    *)
      echo "[ensure-python] Unsupported installer: $PREFERRED_INSTALLER" >&2
      return 1
      ;;
  esac

  echo "[ensure-python] No supported installer found. Install one of: uv, pyenv, brew." >&2
  return 1
}

while [ $# -gt 0 ]; do
  case "$1" in
    --install)
      INSTALL=1
      ;;
    --print-path)
      PRINT_PATH=1
      ;;
    --python-version)
      shift
      PYTHON_VERSION="${1:-}"
      [ -n "$PYTHON_VERSION" ] || { echo "[ensure-python] Missing value for --python-version" >&2; exit 2; }
      DESIRED_MM="$(major_minor "$PYTHON_VERSION")"
      COMMAND_NAME="python${DESIRED_MM}"
      ;;
    --installer)
      shift
      PREFERRED_INSTALLER="${1:-}"
      [ -n "$PREFERRED_INSTALLER" ] || { echo "[ensure-python] Missing value for --installer" >&2; exit 2; }
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[ensure-python] Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if existing_python="$(find_existing_python 2>/dev/null)"; then
  if [ "$PRINT_PATH" -eq 1 ]; then
    echo "$existing_python"
  else
    echo "[ensure-python] Found compatible interpreter: $existing_python ($(python_version "$existing_python"))"
  fi
  exit 0
fi

if [ "$INSTALL" -eq 1 ]; then
  install_python
  if existing_python="$(find_existing_python 2>/dev/null)"; then
    if [ "$PRINT_PATH" -eq 1 ]; then
      echo "$existing_python"
    else
      echo "[ensure-python] Installed compatible interpreter: $existing_python ($(python_version "$existing_python"))"
    fi
    exit 0
  fi
fi

if [ "$PRINT_PATH" -eq 1 ]; then
  exit 1
fi

echo "[ensure-python] Repository: $REPO_ROOT"
echo "[ensure-python] Desired Python version: $PYTHON_VERSION"
echo "[ensure-python] Compatible interpreter: not found"
echo "[ensure-python] Available installers:"
for tool in uv pyenv brew; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "  - $tool: $(command -v "$tool")"
  else
    echo "  - $tool: not installed"
  fi
done
echo "[ensure-python] Re-run with --install once one of the supported installers is available."
exit 1
