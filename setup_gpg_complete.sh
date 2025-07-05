#!/bin/bash

# === CONFIG ===
REAL_NAME="Aurora CloudBank Orion Station"
EMAIL="tlstreets@gmail.com"
KEY_COMMENT="Aurora GPG 2025"
KEY_TYPE="ed25519"
KEY_EXPIRE="1y"

# === STEP 1: Generate Key ===
echo "🔐 Generating GPG key for $REAL_NAME <$EMAIL>..."
gpg --batch --generate-key <<EOF
Key-Type: $KEY_TYPE
Key-Length: 4096
Subkey-Type: $KEY_TYPE
Name-Real: $REAL_NAME
Name-Comment: $KEY_COMMENT
Name-Email: $EMAIL
Expire-Date: $KEY_EXPIRE
%no-protection
%commit
EOF

# === STEP 2: Get Key ID ===
KEY_ID=$(gpg --list-secret-keys --keyid-format LONG "$EMAIL" | grep sec | awk '{print $2}' | cut -d'/' -f2)
if [ -z "$KEY_ID" ]; then
  echo "❌ Failed to find generated key for $EMAIL."
  exit 1
fi

# === STEP 3: Set as default signing key ===
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
echo "📝 Add this key to GitHub → https://github.com/settings/keys (GPG section)"
echo "───────────────────────────────────────────────"
cat gpg_pubkey_for_github.asc
echo "───────────────────────────────────────────────"

# === STEP 6: Test Commit ===
echo "🧪 You can now make a test commit:"
echo "git commit -S -m \"Test signed commit\""
