#!/bin/bash

# 🔧 Aurora CloudBank - Terminal & Git Fix (No Container Rebuild Required)
echo "🔧 Aurora CloudBank - Terminal & Git Fix"
echo "========================================"

# Step 1: Fix terminal environment
echo "📋 Setting up terminal environment..."
export PS1="node@aurora:\w\$ "
export PYTHONUNBUFFERED=1
export HISTCONTROL=ignoredups:erasedups

# Step 2: Fix git configuration
echo "🔧 Configuring git..."
git config --global user.name "Aurora CloudBank" 2>/dev/null || true
git config --global user.email "aurora@cloudbank.dev" 2>/dev/null || true
git config --global init.defaultBranch main 2>/dev/null || true
git config --global commit.gpgsign false 2>/dev/null || true

# Step 3: Check git remote and switch to HTTPS if needed
echo "🔗 Checking git remote..."
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "none")
echo "Current remote: $REMOTE_URL"

if [[ "$REMOTE_URL" == git@github.com:* ]]; then
    echo "⚠️  SSH remote detected, switching to HTTPS..."
    HTTPS_URL=$(echo "$REMOTE_URL" | sed 's/git@github.com:/https:\/\/github.com\//')
    git remote set-url origin "$HTTPS_URL"
    echo "✅ Remote changed to: $(git remote get-url origin)"
fi

# Step 4: Check authentication
echo "🔐 Checking git authentication..."
echo "Git config:"
git config --list | grep -E "(user|remote)" || echo "Basic config set"

# Step 5: Test git status
echo "📊 Testing git status..."
git status --porcelain 2>/dev/null || echo "Git status check failed"

# Step 6: Apply bashrc fix
echo "🛠️  Applying bashrc fix..."
if [ -f /workspaces/aurora-cloudbank-symbolic/.devcontainer/bashrc ]; then
    cp /workspaces/aurora-cloudbank-symbolic/.devcontainer/bashrc ~/.bashrc
    source ~/.bashrc
    echo "✅ Bashrc applied"
else
    echo "⚠️  Custom bashrc not found, creating basic one..."
    cat > ~/.bashrc << 'EOF'
# Aurora CloudBank - Basic Bash Configuration
export PS1="node@aurora:\w\$ "
export PYTHONUNBUFFERED=1
export HISTCONTROL=ignoredups:erasedups
alias ll='ls -la'
alias la='ls -A'
EOF
    source ~/.bashrc
    echo "✅ Basic bashrc created"
fi

echo ""
echo "🎯 Fix complete! Try these commands:"
echo "   git status"
echo "   git add ."
echo "   git commit -m 'Fix terminal and git setup'"
echo "   git push origin main"
echo ""
echo "If push fails, you may need to authenticate with GitHub:"
echo "   - Use Personal Access Token for HTTPS"
echo "   - Or set up SSH keys"
