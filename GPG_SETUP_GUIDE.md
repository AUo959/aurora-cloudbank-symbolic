# 🔐 AURORA CLOUDBANK - GPG COMMIT SIGNING GUIDE

## ✅ GPG SETUP FOR SECURE COMMITS

**Date:** July 5, 2025  
**Project:** Aurora CloudBank Orion Station  
**Purpose:** Enable GPG signing for secure git commits

### 📋 STEP-BY-STEP SETUP

#### **Step 1: Install GPG (if needed)**

```bash
# Ubuntu/Debian (Codespaces)
sudo apt update && sudo apt install gnupg

# Verify installation
gpg --version
```

#### **Step 2: Generate GPG Key**

```bash
# Generate new GPG key
gpg --gen-key

# Follow prompts:
# - Name: Aurora CloudBank Developer (or your name)
# - Email: your-email@domain.com
# - Comment: Aurora CloudBank Orion Station
# - Passphrase: (choose a secure passphrase)
```

#### **Step 3: Get Your GPG Key ID**

```bash
# List your GPG keys
gpg --list-secret-keys --keyid-format LONG

# Output will look like:
# sec   rsa4096/ABC123DEF456 2025-07-05 [SC] [expires: 2027-07-05]
# The key ID is: ABC123DEF456
```

#### **Step 4: Configure Git for GPG Signing**

```bash
# Replace YOUR_KEY_ID with your actual key ID
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# Configure GPG TTY (important for terminal use)
echo 'export GPG_TTY=$(tty)' >> ~/.bashrc
export GPG_TTY=$(tty)
```

#### **Step 5: Export Public Key for GitHub**

```bash
# Export your public key
gpg --armor --export YOUR_KEY_ID

# Copy the output (including -----BEGIN/END----- lines)
```

#### **Step 6: Add Key to GitHub**

1. Go to **GitHub Settings** → **SSH and GPG keys**
2. Click **"New GPG key"**
3. Paste your public key
4. Click **"Add GPG key"**

#### **Step 7: Test GPG Signing**

```bash
# Test a signed commit
echo "GPG test" > test.txt
git add test.txt
git commit -m "Test GPG signed commit for Aurora CloudBank"

# Verify the signature
git log --show-signature -1
```

### 🛠️ AURORA CLOUDBANK SPECIFIC CONFIGURATION

#### **Project GPG Settings**
```bash
# Set Aurora CloudBank specific git config
git config user.name "Aurora CloudBank Developer"
git config user.email "your-email@aurora-cloudbank.ai"
git config user.signingkey YOUR_KEY_ID
```

#### **Enhanced Security Settings**
```bash
# Require GPG signing for this project
git config commit.gpgsign true
git config tag.gpgsign true
git config merge.verifySignatures true
```

### 🔐 SECURITY BEST PRACTICES

#### **Key Management:**
- ✅ Use a strong passphrase for your GPG key
- ✅ Set key expiration (2 years recommended)
- ✅ Backup your private key securely
- ✅ Never commit private keys to the repository

#### **Commit Signing:**
- ✅ Sign all commits in Aurora CloudBank project
- ✅ Verify signatures before merging
- ✅ Use meaningful commit messages
- ✅ Include project context in commits

### 📊 VERIFICATION COMMANDS

#### **Check GPG Configuration:**
```bash
# Check Git GPG settings
git config --list | grep gpg

# Check GPG keys
gpg --list-keys
gpg --list-secret-keys

# Test GPG signing
echo "test" | gpg --clearsign
```

#### **Verify Commit Signatures:**
```bash
# Show signatures for recent commits
git log --show-signature -5

# Verify specific commit
git verify-commit COMMIT_HASH

# Check if commit is signed
git log --pretty="format:%h %G? %aN  %s"
# G = valid signature, N = no signature, B = bad signature
```

### 🎯 AURORA CLOUDBANK INTEGRATION

#### **Automated Signing Script:**
```bash
#!/bin/bash
# Aurora CloudBank commit script with GPG signing

export GPG_TTY=$(tty)
git add .
git commit -S -m "🔐 Aurora CloudBank Orion Station: $1"
git push origin main
```

#### **GitHub Actions Integration:**
```yaml
# Add to .github/workflows/gitwiz-quality-gates.yml
- name: Verify GPG Signatures
  run: |
    git log --show-signature -1
    git verify-commit HEAD
```

### 🌟 TROUBLESHOOTING

#### **Common Issues:**

**GPG Agent Issues:**
```bash
# Restart GPG agent
gpgconf --kill gpg-agent
gpgconf --launch gpg-agent
```

**TTY Issues:**
```bash
# Fix GPG TTY in scripts
export GPG_TTY=$(tty)
```

**Passphrase Issues:**
```bash
# Configure GPG agent for longer cache
echo "default-cache-ttl 28800" >> ~/.gnupg/gpg-agent.conf
echo "max-cache-ttl 86400" >> ~/.gnupg/gpg-agent.conf
```

### 🏁 COMPLETION CHECKLIST

- [ ] GPG installed and working
- [ ] GPG key generated with Aurora CloudBank details
- [ ] Git configured for GPG signing
- [ ] Public key added to GitHub
- [ ] Test commit signed successfully
- [ ] Signature verified on GitHub
- [ ] Aurora CloudBank project configured
- [ ] Backup of GPG key created

### 📋 NEXT STEPS

1. **Complete GPG setup** using this guide
2. **Test with Aurora CloudBank commit** 
3. **Configure GitHub Actions** for signature verification
4. **Update team documentation** with GPG requirements
5. **Set up automated signing** for deployment scripts

**Status:** 🔐 **GPG SIGNING READY FOR AURORA CLOUDBANK** 🔐

---

*This guide ensures all Aurora CloudBank Orion Station commits are cryptographically signed for enhanced security and authenticity.*
