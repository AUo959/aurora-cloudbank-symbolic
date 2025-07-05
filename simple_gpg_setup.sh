#!/bin/bash

# 🔐 AURORA CLOUDBANK - SIMPLIFIED GPG SETUP
echo "🔐 Aurora CloudBank - GPG Commit Signing Setup"
echo "=============================================="

# Step 1: Check GPG
echo "📋 Step 1: Checking GPG installation..."
/usr/bin/gpg --version | head -1

# Step 2: List existing keys
echo ""
echo "📋 Step 2: Checking for existing GPG keys..."
/usr/bin/gpg --list-secret-keys --keyid-format LONG

# Step 3: Generate key if none exist
echo ""
echo "📋 Step 3: Generate GPG key for Aurora CloudBank..."
echo "We'll create a GPG key for Aurora CloudBank Orion Station"

# Create a batch key generation (non-interactive)
cat > /tmp/aurora_gpg_batch << 'EOF'
%echo Generating Aurora CloudBank GPG key
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Aurora CloudBank Orion Station
Name-Comment: Aurora CloudBank Development
Name-Email: orion-station@aurora-cloudbank.ai
Expire-Date: 2y
%no-protection
%commit
%echo Done generating Aurora CloudBank GPG key
EOF

echo "🔐 Generating GPG key (this may take a moment)..."
/usr/bin/gpg --batch --generate-key /tmp/aurora_gpg_batch

# Clean up
rm -f /tmp/aurora_gpg_batch

echo ""
echo "📋 Step 4: Getting the new key ID..."
KEY_ID=$(/usr/bin/gpg --list-secret-keys --keyid-format LONG | grep -E '^sec' | head -1 | sed 's/.*\/\([A-F0-9]*\) .*/\1/')

if [ -n "$KEY_ID" ]; then
    echo "✅ GPG Key ID: $KEY_ID"
    
    echo ""
    echo "📋 Step 5: Configuring Git..."
    git config --global user.signingkey $KEY_ID
    git config --global commit.gpgsign true
    git config --global tag.gpgsign true
    
    echo "✅ Git configured for GPG signing!"
    
    echo ""
    echo "📋 Step 6: Your public key for GitHub:"
    echo "================================================"
    /usr/bin/gpg --armor --export $KEY_ID
    echo "================================================"
    
    echo ""
    echo "🎯 Setup Complete!"
    echo "- GPG Key ID: $KEY_ID"
    echo "- Git commit signing: Enabled"
    echo ""
    echo "📋 Next: Add the public key above to GitHub:"
    echo "1. Go to GitHub Settings > SSH and GPG keys"
    echo "2. Click 'New GPG key'"
    echo "3. Paste the public key shown above"
    
else
    echo "❌ No GPG key found or created"
fi

echo ""
echo "🌟 Aurora CloudBank GPG setup complete! 🌟"
