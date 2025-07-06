#!/bin/bash

# 🔐 AURORA CLOUDBANK - DIRECT GPG SETUP
echo "🔐 AURORA CLOUDBANK - DIRECT GPG SETUP"
echo "====================================="

# Step 1: Generate GPG key directly
echo ""
echo "📋 Generating GPG key for Aurora CloudBank..."

# Create batch configuration for unattended key generation
cat > /tmp/aurora_gpg_batch << 'EOF'
%echo Generating Aurora CloudBank GPG key
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Aurora CloudBank Orion Station
Name-Comment: GPG Prime
Name-Email: orion-station@aurora-cloudbank.ai
Expire-Date: 2y
%no-protection
%commit
%echo Done
EOF

echo "🔐 Creating GPG key (no passphrase for development)..."
gpg --batch --generate-key /tmp/aurora_gpg_batch

# Clean up batch file
rm -f /tmp/aurora_gpg_batch

echo ""
echo "📋 Checking generated keys..."
gpg --list-secret-keys --keyid-format LONG

# Get the key ID
KEY_ID=$(gpg --list-secret-keys --keyid-format LONG | grep -E '^sec' | head -1 | sed 's/.*\/\([A-F0-9]*\) .*/\1/')

if [ -n "$KEY_ID" ]; then
    echo ""
    echo "✅ GPG Key ID found: $KEY_ID"
    
    # Configure Git
    echo ""
    echo "📋 Configuring Git for GPG signing..."
    git config --global user.signingkey $KEY_ID
    git config --global commit.gpgsign true
    git config --global tag.gpgsign true
    
    # Set GPG TTY
    export GPG_TTY=$(tty)
    echo 'export GPG_TTY=$(tty)' >> ~/.bashrc
    
    echo ""
    echo "📋 Your GPG Public Key (add this to GitHub):"
    echo "================================================"
    gpg --armor --export $KEY_ID
    echo "================================================"
    
    echo ""
    echo "✅ GPG setup complete!"
    echo "📋 Key ID: $KEY_ID"
    echo "📋 Git signing: Enabled"
    
    # Test signing
    echo ""
    echo "📋 Testing GPG signing..."
    echo "Aurora CloudBank Test" | gpg --clearsign --default-key $KEY_ID >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ GPG signing test successful!"
    else
        echo "⚠️  GPG signing test had issues"
    fi
    
else
    echo "❌ Could not find generated GPG key"
    echo "📋 Available keys:"
    gpg --list-keys
fi

echo ""
echo "🌟 Aurora CloudBank GPG Setup Complete! 🌟"
