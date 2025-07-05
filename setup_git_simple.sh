#!/bin/bash

# Aurora CloudBank - Simple GPG Setup (No Terminal Dependencies)
echo "🔐 Aurora CloudBank - Simple GPG Setup"

# Configuration
REAL_NAME="Aurora CloudBank Orion Station"
EMAIL="tlstreets@gmail.com"
KEY_COMMENT="Aurora GPG 2025"

# Step 1: Basic git configuration (works without GPG)
echo "⚙️ Setting up basic git configuration..."
git config --global user.email "$EMAIL"
git config --global user.name "$REAL_NAME"
git config --global init.defaultBranch main

# Step 2: Disable GPG signing for now (to unblock commits)
git config --global commit.gpgsign false

# Step 3: Create instructions file
cat > GPG_SETUP_INSTRUCTIONS.md << 'EOF'
# 🔐 Aurora CloudBank GPG Setup Instructions

## Manual GPG Setup (if needed)

Since the devcontainer environment has restrictions, you can set up GPG manually:

### Option 1: Use GitHub Web Interface (Recommended)
1. Go to https://github.com/settings/keys
2. Click "New GPG key"
3. Generate a key using GitHub's web interface

### Option 2: Local GPG Setup
```bash
# Generate GPG key
gpg --full-generate-key

# List keys to get ID
gpg --list-secret-keys --keyid-format LONG

# Export public key (replace KEY_ID with actual ID)
gpg --armor --export KEY_ID

# Configure git
git config --global user.signingkey KEY_ID
git config --global commit.gpgsign true
```

### Option 3: Use Without GPG Signing
The current setup disables GPG signing so commits work normally.
This is perfectly fine for development work.

## Current Configuration
- Name: Aurora CloudBank Orion Station
- Email: tlstreets@gmail.com
- GPG Signing: Disabled (for compatibility)
EOF

echo "✅ Basic git configuration complete!"
echo "📝 GPG setup instructions saved to GPG_SETUP_INSTRUCTIONS.md"
echo "🚀 You can now commit and push normally"
echo ""
echo "Current git config:"
echo "Name: $(git config --global --get user.name)"
echo "Email: $(git config --global --get user.email)"
echo "GPG Signing: $(git config --global --get commit.gpgsign)"
