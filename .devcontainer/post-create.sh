#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(pwd)"
VENV_DIR="${WORKSPACE_DIR}/.venv"

printf '\n🚀 Aurora CloudBank DevContainer setup starting...\n'

# Make scripts executable first
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true

# Setup git hooks for dependency validation
if [[ -f ".githooks/pre-commit" ]]; then
    chmod +x .githooks/pre-commit
    git config core.hooksPath .githooks
    printf '✅ Git hooks configured\n'
fi

# Use our comprehensive setup script if available
if [[ -f "scripts/setup_environment.sh" ]]; then
    printf '🔧 Running Aurora environment setup...\n'
    bash scripts/setup_environment.sh
else
    # Fallback to basic setup with validation
    printf '⚠️ Using fallback setup (setup_environment.sh not found)\n'
    
    python3 -m venv "${VENV_DIR}"
    source "${VENV_DIR}/bin/activate"
    
    python -m pip install --upgrade pip
    python -m pip install --upgrade wheel setuptools
    
    if [[ -f "requirements-lock.txt" ]]; then
        # Test dependency resolution before installing
        printf '🧪 Testing dependency resolution...\n'
        if python -m pip install -r requirements-lock.txt --dry-run; then
            printf '✅ Dependency resolution test passed\n'
            python -m pip install -r requirements-lock.txt
        else
            printf '❌ Dependency conflicts detected!\n'
            printf '💡 Check requirements-lock.txt for version conflicts\n'
            exit 1
        fi
    fi
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

# Create activation helper
cat > activate_aurora.sh << 'EOF'
#!/bin/bash
# Quick activation script for Aurora CloudBank environment

if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
    echo "✅ Aurora CloudBank environment activated"
    echo "🌐 API docs: http://localhost:8000/docs (when running)"
    echo "🧪 Run tests: python -m pytest tests/"
    echo "🔧 Validate deps: python scripts/validate_dependencies.py"
else
    echo "❌ Virtual environment not found"
    echo "Run: bash scripts/setup_environment.sh"
fi
EOF

chmod +x activate_aurora.sh

# Validate the setup
if [[ -f "scripts/validate_dependencies.py" ]] && [[ -d "${VENV_DIR}" ]]; then
    source "${VENV_DIR}/bin/activate"
    if python scripts/validate_dependencies.py; then
        printf '🎯 Aurora CloudBank validation passed!\n'
    else
        printf '⚠️ Validation warnings detected\n'
    fi
fi

printf '\n✅ DevContainer setup complete. Python interpreter: %s\n' "${VENV_DIR}/bin/python"
printf '📝 Quick start: source activate_aurora.sh\n'
printf '🔧 Validate setup: python scripts/validate_dependencies.py\n'
