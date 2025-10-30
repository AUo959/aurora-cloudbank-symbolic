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

# ENHANCED FAILSAFE SETUP - Never fail silently
printf '🛡️ Aurora CloudBank Failsafe Setup Starting...\n'

# Create status tracking
STATUS_FILE=".devcontainer_status.json"
echo '{"status":"starting","timestamp":"'$(date -Iseconds)'"}' > "$STATUS_FILE"

# Function to log and exit on failure
failsafe_exit() {
    local error_msg="$1"
    printf '❌ FAILSAFE EXIT: %s\n' "$error_msg"
    echo '{"status":"failed","error":"'"$error_msg"'","timestamp":"'$(date -Iseconds)'"}' > "$STATUS_FILE"
    exit 1
}

# Use our comprehensive setup script if available
if [[ -f "scripts/setup_environment.sh" ]]; then
    printf '🔧 Running Aurora comprehensive setup...\n'
    if bash scripts/setup_environment.sh; then
        printf '✅ Comprehensive setup completed successfully\n'
    else
        printf '⚠️ Comprehensive setup failed, running failsafe recovery...\n'
        # Failsafe recovery
        rm -rf "${VENV_DIR}" || true
        python3 -m venv "${VENV_DIR}"
        source "${VENV_DIR}/bin/activate"
        python -m pip install --upgrade pip
        
        if [[ -f "requirements-lock.txt" ]]; then
            if python -m pip install -r requirements-lock.txt --dry-run >/dev/null 2>&1; then
                python -m pip install -r requirements-lock.txt || failsafe_exit "Failed to install dependencies"
            else
                failsafe_exit "Dependency conflicts in requirements-lock.txt"
            fi
        fi
    fi
else
    printf '⚠️ Comprehensive setup script not found, using enhanced fallback...\n'
    
    # Enhanced fallback with comprehensive error checking
    rm -rf "${VENV_DIR}" || true
    python3 -m venv "${VENV_DIR}" || failsafe_exit "Failed to create virtual environment"
    source "${VENV_DIR}/bin/activate" || failsafe_exit "Failed to activate virtual environment"
    
    python -m pip install --upgrade pip || failsafe_exit "Failed to upgrade pip"
    python -m pip install --upgrade wheel setuptools || printf '⚠️ Warning: Failed to upgrade wheel/setuptools\n'
    
    if [[ -f "requirements-lock.txt" ]]; then
        printf '🧪 Testing dependency resolution...\n'
        if python -m pip install -r requirements-lock.txt --dry-run >/dev/null 2>&1; then
            printf '✅ Dependency resolution test passed\n'
            python -m pip install -r requirements-lock.txt || failsafe_exit "Failed to install requirements"
        else
            failsafe_exit "Dependency conflicts detected in requirements-lock.txt"
        fi
    else
        printf '⚠️ No requirements-lock.txt found\n'
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

# Deactivate virtual environment if one is active
if command -v deactivate &> /dev/null && [[ -n "${VIRTUAL_ENV:-}" ]]; then
  deactivate
fi

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
