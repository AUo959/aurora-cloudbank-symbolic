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

# Install GitHub CLI if not present
if ! command -v gh &> /dev/null; then
  printf '📦 Installing GitHub CLI...\n'
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
  sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
  sudo apt update -qq && sudo apt install gh -y -qq
  printf '✅ GitHub CLI installed successfully\n'
fi

# Setup bash profile with venv activation
if [[ ! -f "${HOME}/.bash_profile" ]]; then
  touch "${HOME}/.bash_profile"
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
