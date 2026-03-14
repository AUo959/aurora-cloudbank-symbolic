#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
EXECUTE=0
INSTALL_OPTIONAL=0
CONFIGURE_GIT=0
APPLY_SHELL_CONFIG=0
GIT_NAME="${AURORA_GIT_NAME:-Aurora CloudBank Orion Station}"
GIT_EMAIL="${AURORA_GIT_EMAIL:-tlstreets@gmail.com}"

usage() {
  cat <<EOF
Usage: $(basename "$0") [--execute] [--include-optional] [--configure-git] [--apply-shell-config]

Diagnose or bootstrap the VS Code Web environment for this repository.

Diagnostic mode: default mode is a no-op environment check. Re-run with
--execute to build the Python environment and install Node dependencies.

Guidance: leave this script in diagnostic mode unless you explicitly want local
bootstrap changes.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --execute)
      EXECUTE=1
      ;;
    --include-optional)
      INSTALL_OPTIONAL=1
      ;;
    --configure-git)
      CONFIGURE_GIT=1
      ;;
    --apply-shell-config)
      APPLY_SHELL_CONFIG=1
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[setup-vscode-web-environment] Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

cd "$REPO_ROOT"

echo "Aurora VS Code Web Environment"
echo "=============================="
echo "[setup-vscode-web-environment] Repository: $REPO_ROOT"
for tool in python3 node npm git; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "  - $tool: $(command -v "$tool")"
  else
    echo "  - $tool: not installed"
  fi
done
[ -f requirements.txt ] && echo "  - requirements.txt present" || echo "  - requirements.txt missing"
[ -f package.json ] && echo "  - package.json present" || echo "  - package.json missing"
[ -f .devcontainer/bashrc ] && echo "  - .devcontainer/bashrc present" || echo "  - .devcontainer/bashrc missing"

if [ "$EXECUTE" -eq 0 ]; then
  echo "[setup-vscode-web-environment] Diagnostic mode: dry-run complete."
  echo "[setup-vscode-web-environment] Guidance: re-run with --execute to bootstrap dependencies."
  exit 0
fi

setup_cmd=("$REPO_ROOT/scripts/setup_dependencies.sh" --execute --install-python)
if [ "$INSTALL_OPTIONAL" -eq 1 ]; then
  setup_cmd+=(--include-optional)
fi

echo "[setup-vscode-web-environment] Bootstrapping Python environment"
"${setup_cmd[@]}"

if [ -f package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "[setup-vscode-web-environment] Installing Node dependencies"
    npm install
  else
    echo "[setup-vscode-web-environment] npm not installed; skipping Node bootstrap"
  fi
fi

if [ "$CONFIGURE_GIT" -eq 1 ]; then
  echo "[setup-vscode-web-environment] Configuring git identity"
  git config --global user.name "$GIT_NAME"
  git config --global user.email "$GIT_EMAIL"
  git config --global init.defaultBranch main
fi

if [ "$APPLY_SHELL_CONFIG" -eq 1 ] && [ -f .devcontainer/bashrc ]; then
  echo "[setup-vscode-web-environment] Applying shell configuration"
  cp .devcontainer/bashrc "$HOME/.bashrc"
fi

echo "[setup-vscode-web-environment] Environment bootstrap complete"
