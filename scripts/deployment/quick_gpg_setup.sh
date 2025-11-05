#!/bin/bash

# Quick GPG Setup for Aurora CloudBank
echo "🔐 Setting up GPG for Aurora CloudBank Orion Station..."

# Check if GPG is available
if command -v gpg >/dev/null 2>&1; then
    echo "✅ GPG is available"
    
    # Check for existing keys
    if gpg --list-secret-keys | grep -q "sec"; then
        echo "✅ GPG key already exists"
        KEY_ID=$(gpg --list-secret-keys --keyid-format LONG | grep "sec" | head -1 | sed 's/.*\/\([A-F0-9]*\) .*/\1/')
        echo "Using existing key: $KEY_ID"
    else
        echo "ℹ️  No GPG key found. Please run the full setup:"
        echo "   bash setup_gpg_signing.sh"
        exit 1
    fi
    
    # Configure git for GPG signing
    echo "🔧 Configuring Git for GPG signing..."
    git config --global user.signingkey "$KEY_ID"
    git config --global commit.gpgsign true
    git config --global tag.gpgsign true
    
    # Set GPG TTY
    export GPG_TTY=$(tty)
    echo 'export GPG_TTY=$(tty)' >> ~/.bashrc
    
    echo "✅ GPG commit signing configured for Aurora CloudBank!"
    echo "📋 Your GPG Key ID: $KEY_ID"
    echo ""
    echo "📋 To add your public key to GitHub:"
    echo "gpg --armor --export $KEY_ID"
    
else
    echo "❌ GPG not found. Installing..."
    sudo apt update && sudo apt install -y gnupg
    echo "✅ GPG installed. Please run setup_gpg_signing.sh to generate keys"
fi
