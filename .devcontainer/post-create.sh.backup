#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(pwd)"
VENV_DIR="${WORKSPACE_DIR}/.venv"

printf '\n🚀 Aurora CloudBank DevContainer setup starting...\n'

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install --upgrade wheel setuptools

if [[ -f "requirements-lock.txt" ]]; then
  python -m pip install -r requirements-lock.txt
fi

if [[ -f "requirements-test.txt" ]]; then
  python -m pip install -r requirements-test.txt
fi

if [[ -d "npm" || -f "package.json" ]]; then
  npm install || true
fi

deactivate

cp -f .devcontainer/bashrc ~/.bashrc

if git config --get user.name >/dev/null 2>&1; then
  :
else
  git config --global user.name "Aurora CloudBank"
fi

if git config --get user.email >/dev/null 2>&1; then
  :
else
  git config --global user.email "aurora@cloudbank.dev"
fi

git config --global init.defaultBranch main || true
git config --global commit.gpgsign true || true

printf '\n✅ DevContainer setup complete. Python interpreter: %s\n' "${VENV_DIR}/bin/python"
