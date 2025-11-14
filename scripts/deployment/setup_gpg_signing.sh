#!/bin/bash

# 🔐 AURORA CLOUDBANK - GPG COMMIT SIGNING SETUP
# Comprehensive GPG configuration for secure git commits

echo "🔐 AURORA CLOUDBANK - GPG COMMIT SIGNING SETUP"
echo "=============================================="

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

# Step 1: Check if GPG is installed
echo ""
echo "📋 Step 1: Checking GPG installation..."
if command_exists gpg; then
    echo "✅ GPG is installed"
    GPG_VERSION=$(gpg --version | head -1)
    echo "   Version: $GPG_VERSION"
    GPG_CMD="gpg"
elif command_exists gpg2; then
    echo "✅ GPG2 is installed"
    GPG_VERSION=$(gpg2 --version | head -1)
    echo "   Version: $GPG_VERSION"
    GPG_CMD="gpg2"
else
    echo "❌ GPG not found. Installing..."
    if command_exists apt; then
        sudo apt update && sudo apt install -y gnupg
        GPG_CMD="gpg"
    elif command_exists yum; then
        sudo yum install -y gnupg2
        GPG_CMD="gpg2"
    else
        echo "❌ Unable to install GPG automatically. Please install manually."
        exit 1
    fi
fi

# Step 2: Check for existing GPG keys
echo ""
echo "📋 Step 2: Checking existing GPG keys..."
EXISTING_KEYS=$($GPG_CMD --list-secret-keys --keyid-format LONG 2>/dev/null)
if [ -n "$EXISTING_KEYS" ]; then
    echo "✅ Found existing GPG keys:"
    echo "$EXISTING_KEYS"
    echo ""
    read -p "Do you want to use an existing key? (y/n): " USE_EXISTING
else
    echo "ℹ️  No existing GPG keys found"
    USE_EXISTING="n"
fi

# Step 3: Generate new GPG key if needed
if [ "$USE_EXISTING" != "y" ]; then
    echo ""
    echo "📋 Step 3: Generating new GPG key..."
    echo "ℹ️  Please provide the following information:"
    
    read -p "Full Name (e.g., Aurora CloudBank Developer): " FULL_NAME
    read -p "Email (e.g., your-email@domain.com): " EMAIL
    read -p "Comment (optional, e.g., Aurora CloudBank Orion Station): " COMMENT
    
    # Create GPG key generation config
    cat > /tmp/gpg_gen_config << EOF
%echo Generating Aurora CloudBank GPG key
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: $FULL_NAME
Name-Comment: $COMMENT
Name-Email: $EMAIL
Expire-Date: 2y
%no-protection
%commit
%echo Done
EOF

    echo "🔐 Generating GPG key (this may take a moment)..."
    $GPG_CMD --batch --generate-key /tmp/gpg_gen_config
    
    # Clean up config file
    rm -f /tmp/gpg_gen_config
    
    if [ $? -eq 0 ]; then
        echo "✅ GPG key generated successfully!"
    else
        echo "❌ Failed to generate GPG key"
        exit 1
    fi
fi

# Step 4: Get the GPG key ID
echo ""
echo "📋 Step 4: Getting GPG key information..."
KEY_ID=$($GPG_CMD --list-secret-keys --keyid-format LONG | grep -E '^sec' | head -1 | sed 's/.*\/\([A-F0-9]*\) .*/\1/')

if [ -n "$KEY_ID" ]; then
    echo "✅ GPG Key ID: $KEY_ID"
    
    # Get key details
    echo ""
    echo "📋 Key Details:"
    $GPG_CMD --list-secret-keys --keyid-format LONG $KEY_ID
    
    # Export public key
    echo ""
    echo "📋 Public Key (for GitHub):"
    echo "================================================"
    $GPG_CMD --armor --export $KEY_ID
    echo "================================================"
else
    echo "❌ Could not find GPG key ID"
    exit 1
fi

# Step 5: Configure Git to use GPG
echo ""
echo "📋 Step 5: Configuring Git for GPG signing..."

# Set the GPG key for git
git config --global user.signingkey $KEY_ID
print_status $? "Set Git signing key"

# Enable GPG signing for commits
git config --global commit.gpgsign true
print_status $? "Enabled GPG commit signing"

# Enable GPG signing for tags
git config --global tag.gpgsign true
print_status $? "Enabled GPG tag signing"

# Set GPG program (if needed)
if [ "$GPG_CMD" = "gpg2" ]; then
    git config --global gpg.program gpg2
    print_status $? "Set GPG program to gpg2"
fi

# Step 6: Configure GPG TTY (for terminal usage)
echo ""
echo "📋 Step 6: Configuring GPG TTY..."
echo 'export GPG_TTY=$(tty)' >> ~/.bashrc
echo 'export GPG_TTY=$(tty)' >> ~/.profile 2>/dev/null || true
export GPG_TTY=$(tty)
print_status $? "Configured GPG TTY"

# Step 7: Test GPG signing
echo ""
echo "📋 Step 7: Testing GPG signing..."
echo "Test message for Aurora CloudBank" | $GPG_CMD --clearsign --default-key $KEY_ID > /tmp/gpg_test 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ GPG signing test successful!"
    rm -f /tmp/gpg_test
else
    echo "⚠️  GPG signing test failed - you may need to set a passphrase"
fi

# Step 8: Create Aurora CloudBank specific configuration
echo ""
echo "📋 Step 8: Creating Aurora CloudBank GPG configuration..."

# Create GPG configuration for the project
mkdir -p .aurora-cloudbank
cat > .aurora-cloudbank/gpg-config.json << EOF
{
  "project": "Aurora CloudBank Orion Station",
  "gpg_key_id": "$KEY_ID",
  "configured_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "commit_signing": true,
  "tag_signing": true,
  "verification_required": true,
  "security_level": "enhanced"
}
EOF

echo "✅ Created Aurora CloudBank GPG configuration"

# Step 9: Display next steps
echo ""
echo "🎯 SETUP COMPLETE!"
echo "=================="
echo ""
echo "📋 Next Steps:"
echo "1. Add your public key to GitHub:"
echo "   - Go to GitHub Settings > SSH and GPG keys"
echo "   - Click 'New GPG key'"
echo "   - Paste the public key shown above"
echo ""
echo "2. Test a signed commit:"
echo "   git commit -m 'Test signed commit for Aurora CloudBank'"
echo ""
echo "3. Verify commit signature:"
echo "   git log --show-signature -1"
echo ""
echo "📊 Configuration Summary:"
echo "- GPG Key ID: $KEY_ID"
echo "- Commit signing: Enabled"
echo "- Tag signing: Enabled"
echo "- GPG program: $GPG_CMD"
echo ""
echo "🔐 Your Aurora CloudBank commits are now secured with GPG signing!"

# Step 10: Create backup script
echo ""
echo "📋 Creating GPG backup script..."
cat > .aurora-cloudbank/backup-gpg-key.sh << EOF
#!/bin/bash
# Aurora CloudBank GPG Key Backup Script

echo "🔐 Backing up Aurora CloudBank GPG key..."
mkdir -p gpg-backup
gpg --export-secret-keys --armor $KEY_ID > gpg-backup/aurora-cloudbank-private-key.asc
gpg --export --armor $KEY_ID > gpg-backup/aurora-cloudbank-public-key.asc
echo "✅ GPG keys backed up to gpg-backup/ directory"
echo "⚠️  Keep the private key secure and never commit it to the repository!"
EOF

chmod +x .aurora-cloudbank/backup-gpg-key.sh
echo "✅ Created GPG backup script at .aurora-cloudbank/backup-gpg-key.sh"

echo ""
echo "🌟 Aurora CloudBank GPG Setup Complete! 🌟"
