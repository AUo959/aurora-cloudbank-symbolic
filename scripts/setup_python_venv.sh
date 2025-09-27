#!/usr/bin/env bash
# Aurora CloudBank Python environment bootstrapper
#
# This helper prevents PEP 668 "externally-managed-environment" errors by
# installing the minimal Debian packages (python3-pip, python3-venv) and then
# provisioning a user-scoped virtual environment with the baseline tooling
# expected by the repository (numpy + pytest).

set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-/bin/python3}"
VENV_NAME="${AURORA_VENV_NAME:-aurora-cloudbank}"
VENV_ROOT="${AURORA_VENV_ROOT:-${HOME}/.venvs}"
VENV_PATH="${VENV_ROOT}/${VENV_NAME}"
REQUIRED_DEB_PACKAGES=(python3-pip python3-venv)
PYTHON_PACKAGES=(numpy pytest)

info() {
    printf '[setup-python] %s\n' "$*"
}

warn() {
    printf '[setup-python][WARN] %s\n' "$*" >&2
}

require_sudo() {
    if ! command -v sudo >/dev/null 2>&1; then
        warn "sudo is required to install system packages (python3-pip, python3-venv)."
        warn "Run this script inside the provided devcontainer or install the packages manually."
        exit 1
    fi
}

ensure_deb_packages() {
    local missing=()
    for pkg in "${REQUIRED_DEB_PACKAGES[@]}"; do
        if ! dpkg -s "$pkg" >/dev/null 2>&1; then
            missing+=("$pkg")
        fi
    done

    if ((${#missing[@]})); then
        require_sudo
        info "Installing Debian packages: ${missing[*]}"
        sudo apt-get update
        sudo apt-get install -y "${missing[@]}"
    else
        info "Required Debian packages already installed."
    fi
}

ensure_virtualenv() {
    mkdir -p "$VENV_ROOT"
    if [[ -d "$VENV_PATH" ]]; then
        info "Using existing virtual environment at ${VENV_PATH}"
    else
        info "Creating virtual environment at ${VENV_PATH}"
        "$PYTHON_BIN" -m venv "$VENV_PATH"
    fi
}

upgrade_pip() {
    info "Upgrading pip inside ${VENV_PATH}"
    "$VENV_PATH/bin/python" -m pip install --upgrade pip
}

install_python_packages() {
    info "Installing Python packages: ${PYTHON_PACKAGES[*]}"
    "$VENV_PATH/bin/pip" install --upgrade "${PYTHON_PACKAGES[@]}"
}

print_success() {
    cat <<EOF

[setup-python] Success!
[setup-python] Virtual environment: ${VENV_PATH}
[setup-python] Activate with: source ${VENV_PATH}/bin/activate
[setup-python] Or run directly: ${VENV_PATH}/bin/python -m pytest tests/...
EOF
}

main() {
    info "Using Python binary: ${PYTHON_BIN}"
    ensure_deb_packages
    ensure_virtualenv
    upgrade_pip
    install_python_packages
    print_success
}

main "$@"
