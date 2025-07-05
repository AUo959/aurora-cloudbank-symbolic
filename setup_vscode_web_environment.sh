#!/bin/bash

# 🔧 Aurora CloudBank - Manual Environment Setup for VS Code Web
echo "🔧 Aurora CloudBank - Manual Environment Setup"
echo "==============================================="

# Step 1: Install missing Python packages
echo "📦 Installing Python development tools..."
pip install --user black isort flake8 pylint autopep8 bandit mypy

# Step 2: Install Node.js development tools
echo "📦 Installing Node.js development tools..."
npm install -g eslint prettier markdownlint-cli

# Step 3: Configure git properly
echo "🔧 Configuring git..."
git config --global user.name "Aurora CloudBank Orion Station"
git config --global user.email "tlstreets@gmail.com"
git config --global commit.gpgsign true
git config --global init.defaultBranch main

# Step 4: Apply bashrc configuration
echo "🛠️ Applying shell configuration..."
if [ -f .devcontainer/bashrc ]; then
    cp .devcontainer/bashrc ~/.bashrc
    source ~/.bashrc
    echo "✅ Custom bashrc applied"
else
    echo "⚠️ Custom bashrc not found, using default"
fi

# Step 5: Install project dependencies
echo "📦 Installing project dependencies..."
pip install -r requirements.txt || echo "⚠️ requirements.txt not found or failed"
npm install || echo "⚠️ npm install failed or no package.json"

# Step 6: Test installation
echo "🧪 Testing installations..."
echo "Python version: $(python3 --version)"
echo "Node version: $(node --version)"
echo "Git version: $(git --version)"
echo "Black version: $(black --version)"
echo "ESLint version: $(npx eslint --version)"

echo ""
echo "✅ Manual environment setup complete!"
echo "🎯 VS Code Web environment optimized for Aurora CloudBank development"
