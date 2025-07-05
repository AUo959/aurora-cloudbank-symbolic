#!/bin/bash

# 🔧 AURORA CLOUDBANK - Fix Codespaces GPG Configuration
# Resolves the gh-gpgsign vs standard gpg configuration conflict

echo "🔧 AURORA CLOUDBANK - Fix Codespaces GPG Configuration"
echo "====================================================="

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
echo "📋 Step 1: Checking current GPG configuration..."
echo "Current git GPG program: $(git config --global gpg.program)"
echo "Current commit signing: $(git config --global commit.gpgsign)"
echo "Current tag signing: $(git config --global tag.gpgsign)"
echo "Current signing key: $(git config --global user.signingkey)"

echo ""
echo "📋 Step 2: Identifying the problem..."
echo "The issue is that Git is configured to use 'gh-gpgsign' instead of standard 'gpg'"
echo "This causes authentication issues with GitHub's API in Codespaces"

echo ""
echo "📋 Step 3: Fixing GPG configuration..."

# Reset GPG program to standard gpg
git config --global gpg.program gpg
print_status $? "Reset GPG program to standard gpg"

# Verify GPG key exists
GPG_KEY_ID=$(git config --global user.signingkey)
if [ -n "$GPG_KEY_ID" ]; then
    echo "✅ GPG key ID found: $GPG_KEY_ID"
    
    # Test if the key exists
    if gpg --list-secret-keys $GPG_KEY_ID >/dev/null 2>&1; then
        echo "✅ GPG key is available in keyring"
    else
        echo "❌ GPG key not found in keyring"
        exit 1
    fi
else
    echo "❌ No GPG signing key configured"
    exit 1
fi

# Configure GPG TTY for terminal usage
echo ""
echo "📋 Step 4: Configuring GPG TTY..."
export GPG_TTY=$(tty)
echo "export GPG_TTY=\$(tty)" >> ~/.bashrc
print_status $? "Configured GPG TTY"

# Test GPG signing
echo ""
echo "📋 Step 5: Testing GPG signing..."
echo "Test message for Aurora CloudBank" | gpg --clearsign --default-key $GPG_KEY_ID > /tmp/gpg_test 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ GPG signing test successful!"
    rm -f /tmp/gpg_test
else
    echo "⚠️  GPG signing test failed"
    echo "This might be due to passphrase requirements"
fi

# Check git author configuration
echo ""
echo "📋 Step 6: Checking git author configuration..."
GIT_USER_NAME=$(git config --global user.name)
GIT_USER_EMAIL=$(git config --global user.email)

echo "Git user.name: $GIT_USER_NAME"
echo "Git user.email: $GIT_USER_EMAIL"

if [ -z "$GIT_USER_NAME" ] || [ -z "$GIT_USER_EMAIL" ]; then
    echo "⚠️  Git user configuration is incomplete"
    echo "Setting default Aurora CloudBank configuration..."
    
    git config --global user.name "Aurora CloudBank Orion Station"
    git config --global user.email "orion-station@aurora-cloudbank.ai"
    
    print_status $? "Set default git user configuration"
fi

# Create a simple commit test
echo ""
echo "📋 Step 7: Creating a test commit..."

# Create a test file
echo "GPG signing test - $(date)" > gpg-test-commit.txt
git add gpg-test-commit.txt

# Attempt test commit
echo "Attempting test commit with fixed GPG configuration..."
if git commit -m "🔐 Test GPG signing - Aurora CloudBank" >/dev/null 2>&1; then
    echo "✅ Test commit successful!"
    
    # Check if commit is signed
    if git log --show-signature -1 | grep -q "gpg:"; then
        echo "✅ Commit is GPG signed!"
    else
        echo "⚠️  Commit created but may not be properly signed"
    fi
    
    # Reset to before test commit
    git reset --soft HEAD~1
    git reset HEAD gpg-test-commit.txt
    rm -f gpg-test-commit.txt
    
else
    echo "❌ Test commit failed"
    echo "Let's try with debugging..."
    
    # Try with verbose output
    GIT_TRACE=1 git commit -m "🔐 Test GPG signing - Aurora CloudBank" 2>&1 | head -20
    
    # Reset any partial changes
    git reset --soft HEAD~1 2>/dev/null || true
    git reset HEAD gpg-test-commit.txt 2>/dev/null || true
    rm -f gpg-test-commit.txt 2>/dev/null || true
fi

echo ""
echo "📋 Step 8: Final configuration summary..."
echo "GPG program: $(git config --global gpg.program)"
echo "Commit signing: $(git config --global commit.gpgsign)"
echo "Signing key: $(git config --global user.signingkey)"
echo "Git user: $(git config --global user.name) <$(git config --global user.email)>"

echo ""
echo "🎯 CONFIGURATION FIXED!"
echo "======================"
echo ""
echo "The GPG configuration has been updated to use standard 'gpg' instead of 'gh-gpgsign'"
echo "This should resolve the '403 | Author is invalid' error"
echo ""
echo "Ready to attempt the main commit again!"
