#!/bin/bash
# Aurora CloudBank - Environment Setup Script
# Fixes Node.js/npm environment and prepares development environment

set -e

echo "🚀 Aurora CloudBank - Environment Setup"
echo "========================================"

# Function to log with timestamp
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# Function to check command success
check_status() {
    if [ $? -eq 0 ]; then
        log "✅ $1 - SUCCESS"
    else
        log "❌ $1 - FAILED"
        exit 1
    fi
}

log "Fixing Node.js environment..."

# Fix PATH for current session
export PATH="/usr/local/share/nvm/versions/node/v20.19.3/bin:$PATH"

# Verify Node.js and npm
log "Verifying Node.js installation..."
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
log "Node.js version: $NODE_VERSION"
log "npm version: $NPM_VERSION"

# Install dependencies
log "Installing project dependencies..."
npm install
check_status "Dependencies installation"

# Run initial linting
log "Running code quality checks..."
npm run lint
check_status "ESLint check"

# Run formatting check
npm run format:check
check_status "Prettier format check"

log "Setting up permanent PATH fix..."
# Add to .bashrc for persistent PATH
if ! grep -q "export PATH=\"/usr/local/share/nvm/versions/node/v20.19.3/bin:\$PATH\"" ~/.bashrc; then
    echo 'export PATH="/usr/local/share/nvm/versions/node/v20.19.3/bin:$PATH"' >> ~/.bashrc
    log "Added PATH fix to ~/.bashrc"
fi

echo ""
log "✅ Environment setup complete!"
echo "========================================"
echo "To activate in new terminals, run:"
echo "source ~/.bashrc"
echo ""
echo "Available commands:"
echo "  npm run lint      - Check code style"
echo "  npm run lint:fix  - Fix code style issues"
echo "  npm run format    - Format all files"
echo "  npm test          - Run tests"
echo "========================================"
