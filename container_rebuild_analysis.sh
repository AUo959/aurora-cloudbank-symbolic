#!/bin/bash

# 🔧 AURORA CLOUDBANK - CONTAINER REBUILD SCRIPT
# Comprehensive container rebuild and environment setup

echo "🔧 AURORA CLOUDBANK - CONTAINER REBUILD"
echo "======================================="

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2 (Exit code: $1)"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo ""
echo "📋 Step 1: Current Environment Analysis"
echo "======================================="
echo "🏗️  Workspace: $(pwd)"
echo "👤 User: $(whoami)"
echo "🖥️  Container: $(hostname)"
echo "📅 Date: $(date)"
echo ""

# Check current versions
echo "📋 Step 2: Checking Current Tool Versions"
echo "========================================"
echo "🔧 Checking installed tools..."

if command_exists node; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js not found"
fi

if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm: $NPM_VERSION"
else
    echo "❌ npm not found"
fi

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python3 not found"
fi

if command_exists pip; then
    PIP_VERSION=$(pip --version)
    echo "✅ pip: $PIP_VERSION"
else
    echo "❌ pip not found"
fi

if command_exists git; then
    GIT_VERSION=$(git --version)
    echo "✅ Git: $GIT_VERSION"
else
    echo "❌ Git not found"
fi

if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    echo "✅ Docker: $DOCKER_VERSION"
else
    echo "ℹ️  Docker not available in container (normal for Codespaces)"
fi

echo ""
echo "📋 Step 3: Container Configuration Check"
echo "========================================"

# Check devcontainer files
if [ -f ".devcontainer/devcontainer.json" ]; then
    echo "✅ DevContainer configuration found"
    echo "📄 DevContainer name: $(grep -o '"name":[^,]*' .devcontainer/devcontainer.json | cut -d'"' -f4)"
else
    echo "❌ DevContainer configuration not found"
fi

if [ -f ".devcontainer/Dockerfile" ]; then
    echo "✅ Dockerfile found"
    echo "📄 Base image: $(grep -o 'FROM.*' .devcontainer/Dockerfile | head -1)"
else
    echo "❌ Dockerfile not found"
fi

# Check package files
if [ -f "package.json" ]; then
    echo "✅ package.json found"
    if [ -f "node_modules/package.json" ] || [ -d "node_modules" ]; then
        echo "✅ node_modules exists"
    else
        echo "⚠️  node_modules not found - npm install may be needed"
    fi
else
    echo "❌ package.json not found"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
    if [ -d ".venv" ] || [ -d "venv" ]; then
        echo "✅ Python virtual environment found"
    else
        echo "⚠️  Python virtual environment not found"
    fi
else
    echo "❌ requirements.txt not found"
fi

echo ""
echo "📋 Step 4: Aurora CloudBank Specific Checks"
echo "========================================"

# Check Aurora-specific files
if [ -f ".aurora-cloudbank/gpg-config.json" ]; then
    echo "✅ Aurora GPG configuration found"
    GPG_KEY=$(grep -o '"gpg_key_id":[^,]*' .aurora-cloudbank/gpg-config.json | cut -d'"' -f4)
    echo "🔐 GPG Key: $GPG_KEY"
else
    echo "⚠️  Aurora GPG configuration not found"
fi

if [ -f "aurora_api.py" ]; then
    echo "✅ Aurora API found"
else
    echo "❌ Aurora API not found"
fi

if [ -f "aurora_gui_cloudhub_fastapi.py" ]; then
    echo "✅ Aurora GUI CloudHub found"
else
    echo "❌ Aurora GUI CloudHub not found"
fi

if [ -d "modules" ]; then
    echo "✅ Aurora modules directory found"
    MODULE_COUNT=$(find modules -name "*.py" | wc -l)
    echo "📦 Python modules: $MODULE_COUNT"
else
    echo "❌ Aurora modules directory not found"
fi

echo ""
echo "📋 Step 5: Dependency Installation"
echo "========================================"

# Install/update npm packages
if [ -f "package.json" ]; then
    echo "📦 Installing/updating npm packages..."
    npm install
    print_status $? "npm install completed"
else
    echo "⚠️  Skipping npm install - package.json not found"
fi

# Install/update Python packages
if [ -f "requirements.txt" ]; then
    echo "📦 Installing/updating Python packages..."
    pip install -r requirements.txt --upgrade
    print_status $? "pip install completed"
else
    echo "⚠️  Skipping pip install - requirements.txt not found"
fi

echo ""
echo "📋 Step 6: Aurora CloudBank Setup"
echo "========================================"

# Run Aurora-specific setup if available
if [ -f "setup_gpg_signing.sh" ]; then
    echo "🔐 GPG signing setup available"
    if [ -f ".aurora-cloudbank/gpg-config.json" ]; then
        echo "✅ GPG already configured"
    else
        echo "⚠️  GPG setup script available but not configured"
        echo "💡 Run ./setup_gpg_signing.sh to configure GPG signing"
    fi
else
    echo "⚠️  GPG setup script not found"
fi

# Check git configuration
if command_exists git; then
    echo "🔍 Checking git configuration..."
    GIT_USER=$(git config --global user.name 2>/dev/null || echo "Not set")
    GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "Not set")
    GIT_SIGNING=$(git config --global commit.gpgsign 2>/dev/null || echo "false")
    
    echo "👤 Git user: $GIT_USER"
    echo "📧 Git email: $GIT_EMAIL"
    echo "🔐 GPG signing: $GIT_SIGNING"
fi

echo ""
echo "📋 Step 7: Environment Variables & Configuration"
echo "========================================"

# Check for environment files
if [ -f ".env" ]; then
    echo "✅ .env file found"
    ENV_COUNT=$(grep -c "^[^#]" .env 2>/dev/null || echo "0")
    echo "📝 Environment variables: $ENV_COUNT"
else
    echo "⚠️  .env file not found"
    if [ -f ".env.example" ]; then
        echo "📄 .env.example available - copy to .env if needed"
    fi
fi

# Check Aurora configuration
if [ -f "symbolic_config.yaml" ]; then
    echo "✅ Aurora symbolic configuration found"
else
    echo "⚠️  Aurora symbolic configuration not found"
fi

echo ""
echo "📋 Step 8: Final Environment Test"
echo "========================================"

# Test key components
echo "🧪 Testing key components..."

# Test Node.js/npm
if command_exists node && command_exists npm; then
    echo "✅ Node.js environment: Ready"
else
    echo "❌ Node.js environment: Issues detected"
fi

# Test Python
if command_exists python3 && command_exists pip; then
    echo "✅ Python environment: Ready"
else
    echo "❌ Python environment: Issues detected"
fi

# Test Git
if command_exists git; then
    echo "✅ Git environment: Ready"
else
    echo "❌ Git environment: Issues detected"
fi

echo ""
echo "🎯 CONTAINER REBUILD SUMMARY"
echo "========================================"
echo "📊 Environment Status:"
echo "   • Node.js: $(command_exists node && echo "✅ Ready" || echo "❌ Issues")"
echo "   • Python: $(command_exists python3 && echo "✅ Ready" || echo "❌ Issues")"
echo "   • Git: $(command_exists git && echo "✅ Ready" || echo "❌ Issues")"
echo "   • Aurora GPG: $([ -f ".aurora-cloudbank/gpg-config.json" ] && echo "✅ Configured" || echo "⚠️ Pending")"
echo ""
echo "💡 Next Steps:"
echo "1. If there are any ❌ issues above, address them first"
echo "2. Run './setup_gpg_signing.sh' if GPG not configured"
echo "3. Copy .env.example to .env if needed"
echo "4. Test your Aurora CloudBank applications"
echo ""
echo "🚀 Ready to continue Aurora CloudBank development!"
echo ""
echo "📋 Quick Commands:"
echo "   • Test Aurora API: python3 aurora_api.py"
echo "   • Test Aurora GUI: python3 aurora_gui_cloudhub_fastapi.py"
echo "   • Run tests: npm test (if configured)"
echo "   • Check git status: git status"
echo ""
echo "🔧 Container rebuild analysis complete!"
