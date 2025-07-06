#!/bin/bash

# Aurora CloudBank - Complete GPG Setup Script
echo "🔐 Aurora CloudBank - Complete GPG Setup Script"
echo "=============================================="

# === CONFIG ===
REAL_NAME="Aurora CloudBank Orion Station"
EMAIL="tlstreets@gmail.com"
KEY_COMMENT="Aurora GPG 2025"
KEY_TYPE="rsa"  # Using RSA for better compatibility
KEY_LENGTH="4096"
KEY_EXPIRE="1y"

# === STEP 0: Check prerequisites ===
echo "🔍 Checking prerequisites..."
if ! command -v gpg &> /dev/null; then
    echo "❌ GPG not found. Installing..."
    apt-get update && apt-get install -y gnupg
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install git first."
    exit 1
fi

# === STEP 1: Generate Key ===
echo "🔐 Generating GPG key for $REAL_NAME <$EMAIL>..."

# Create GPG batch file
cat > /tmp/gpg_batch_config << EOF
Key-Type: $KEY_TYPE
Key-Length: $KEY_LENGTH
Subkey-Type: $KEY_TYPE
Subkey-Length: $KEY_LENGTH
Name-Real: $REAL_NAME
Name-Comment: $KEY_COMMENT
Name-Email: $EMAIL
Expire-Date: $KEY_EXPIRE
%no-protection
%commit
%echo Done
EOF

# Generate key
gpg --batch --generate-key /tmp/gpg_batch_config

# Clean up batch file
rm -f /tmp/gpg_batch_config

# === STEP 2: Get Key ID ===
echo "🔍 Finding generated key..."
sleep 2  # Wait for key generation to complete

KEY_ID=$(gpg --list-secret-keys --keyid-format LONG "$EMAIL" 2>/dev/null | grep sec | head -1 | awk '{print $2}' | cut -d'/' -f2)
if [ -z "$KEY_ID" ]; then
  echo "❌ Failed to find generated key for $EMAIL."
  echo "🔍 Available keys:"
  gpg --list-secret-keys --keyid-format LONG
  exit 1
fi

echo "✅ Found key ID: $KEY_ID"

# === STEP 3: Set as default signing key ===
echo "⚙️ Configuring git..."
git config --global user.signingkey "$KEY_ID"
git config --global user.email "$EMAIL"
git config --global user.name "$REAL_NAME"
git config --global commit.gpgsign true

# === STEP 4: Export Public Key for GitHub ===
echo "📤 Exporting public key..."
gpg --armor --export "$KEY_ID" > gpg_pubkey_for_github.asc
echo "✅ GPG public key exported to gpg_pubkey_for_github.asc"

# === STEP 5: Display ===
echo ""
echo "🎉 GPG Setup Complete!"
echo "======================"
echo "📝 Add this key to GitHub → https://github.com/settings/keys (GPG section)"
echo "───────────────────────────────────────────────"
cat gpg_pubkey_for_github.asc
echo "───────────────────────────────────────────────"

# === STEP 6: Test Commit ===
echo ""
echo "🧪 You can now make a test commit:"
echo "git commit -S -m \"Test signed commit\""
echo ""
echo "📊 Current git configuration:"
git config --global --get user.name
git config --global --get user.email
git config --global --get user.signingkey
git config --global --get commit.gpgsign
