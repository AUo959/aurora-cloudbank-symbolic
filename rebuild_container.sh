#!/bin/bash

# 🔧 AURORA CLOUDBANK - DEV CONTAINER REBUILD SCRIPT
# Comprehensive container rebuild with dependency management

echo "🔧 AURORA CLOUDBANK - DEV CONTAINER REBUILD"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
    fi
}

echo ""
echo "📋 Step 1: Checking current environment..."
echo "Current working directory: $(pwd)"
echo "Container environment: $(uname -a)"

# Check if we're in a devcontainer
if [ -f "/.devcontainer-build" ] || [ -n "$CODESPACES" ]; then
    echo "✅ Running in dev container environment"
else
    echo "⚠️  Not in dev container - this script is optimized for container environments"
fi

echo ""
echo "📋 Step 2: Checking dependencies..."

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python3 not found"
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js not found"
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm: $NPM_VERSION"
else
    echo "❌ npm not found"
fi

# Check Git
if command_exists git; then
    GIT_VERSION=$(git --version)
    echo "✅ Git: $GIT_VERSION"
else
    echo "❌ Git not found"
fi

echo ""
echo "📋 Step 3: Updating package managers..."

# Update apt if available
if command_exists apt; then
    echo "🔄 Updating apt package list..."
    sudo apt update
    print_status $? "Updated apt package list"
fi

# Update pip
if command_exists pip3; then
    echo "🔄 Updating pip..."
    pip3 install --upgrade pip
    print_status $? "Updated pip"
fi

# Update npm
if command_exists npm; then
    echo "🔄 Updating npm..."
    npm install -g npm@latest
    print_status $? "Updated npm"
fi

echo ""
echo "📋 Step 4: Installing/Updating Python dependencies..."

if [ -f "requirements.txt" ]; then
    echo "🔄 Installing Python requirements..."
    pip3 install -r requirements.txt
    print_status $? "Installed Python requirements"
else
    echo "⚠️  No requirements.txt found"
fi

echo ""
echo "📋 Step 5: Installing/Updating Node.js dependencies..."

if [ -f "package.json" ]; then
    echo "🔄 Installing npm dependencies..."
    npm install
    print_status $? "Installed npm dependencies"
else
    echo "ℹ️  No package.json found - skipping npm install"
fi

echo ""
echo "📋 Step 6: Installing additional Aurora CloudBank tools..."

# Install additional tools that might be useful
echo "🔄 Installing additional development tools..."

# Install GPG if not present
if ! command_exists gpg; then
    echo "🔄 Installing GPG..."
    sudo apt install -y gnupg
    print_status $? "Installed GPG"
fi

# Install jq for JSON processing
if ! command_exists jq; then
    echo "🔄 Installing jq..."
    sudo apt install -y jq
    print_status $? "Installed jq"
fi

# Install tree for directory visualization
if ! command_exists tree; then
    echo "🔄 Installing tree..."
    sudo apt install -y tree
    print_status $? "Installed tree"
fi

# Install curl if not present
if ! command_exists curl; then
    echo "🔄 Installing curl..."
    sudo apt install -y curl
    print_status $? "Installed curl"
fi

echo ""
echo "📋 Step 7: Configuring development environment..."

# Set up Git if not configured
if [ -z "$(git config --global user.name)" ]; then
    echo "⚠️  Git user.name not configured"
    echo "   Run: git config --global user.name 'Your Name'"
fi

if [ -z "$(git config --global user.email)" ]; then
    echo "⚠️  Git user.email not configured"
    echo "   Run: git config --global user.email 'your-email@domain.com'"
fi

# Check GPG configuration
if command_exists gpg; then
    GPG_KEYS=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null)
    if [ -n "$GPG_KEYS" ]; then
        echo "✅ GPG keys configured"
    else
        echo "ℹ️  No GPG keys found - run setup_gpg_signing.sh to configure"
    fi
fi

echo ""
echo "📋 Step 8: Verifying Aurora CloudBank project structure..."

# Check for key project files
PROJECT_FILES=(
    ".devcontainer/devcontainer.json"
    ".devcontainer/Dockerfile"
    "requirements.txt"
    "README.md"
)

echo "🔍 Checking project files:"
for file in "${PROJECT_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "⚠️  $file (missing)"
    fi
done

echo ""
echo "📋 Step 9: Running health checks..."

# Test Python imports
echo "🔍 Testing Python environment..."
python3 -c "import sys; print('Python executable:', sys.executable)" 2>/dev/null
print_status $? "Python environment test"

# Test key Python packages
python3 -c "import yaml, fastapi, uvicorn, pandas, plotly" 2>/dev/null
print_status $? "Key Python packages test"

# Test Node.js
echo "🔍 Testing Node.js environment..."
node -e "console.log('Node.js version:', process.version)" 2>/dev/null
print_status $? "Node.js environment test"

echo ""
echo "📋 Step 10: Environment summary..."
echo "=========================================="
echo "🐍 Python: $(python3 --version 2>/dev/null || echo 'Not available')"
echo "📦 pip: $(pip3 --version 2>/dev/null || echo 'Not available')"
echo "🟢 Node.js: $(node --version 2>/dev/null || echo 'Not available')"
echo "📦 npm: $(npm --version 2>/dev/null || echo 'Not available')"
echo "🔐 GPG: $(gpg --version 2>/dev/null | head -1 || echo 'Not available')"
echo "🔧 Git: $(git --version 2>/dev/null || echo 'Not available')"

# Check available memory and disk space
echo ""
echo "💾 System Resources:"
echo "Memory: $(free -h | grep '^Mem:' | awk '{print $2}' 2>/dev/null || echo 'Unknown')"
echo "Disk: $(df -h . | tail -1 | awk '{print $2}' 2>/dev/null || echo 'Unknown')"

echo ""
echo "🎯 CONTAINER REBUILD COMPLETE!"
echo "============================="
echo ""
echo "✅ Your Aurora CloudBank development environment is ready!"
echo ""
echo "🔧 Next steps:"
echo "1. Test your environment with: python3 -c 'print(\"Aurora CloudBank Ready!\")'"
echo "2. Check GPG setup: git log --show-signature -1"
echo "3. Run your application: python3 your_app.py or npm start"
echo ""
echo "🌟 Aurora CloudBank Container Rebuild Complete! 🌟"
