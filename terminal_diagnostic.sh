#!/bin/bash

# 🔧 AURORA CLOUDBANK - TERMINAL DIAGNOSTIC AND FIX
# Comprehensive terminal environment troubleshooting

echo "🔧 AURORA CLOUDBANK - TERMINAL DIAGNOSTIC AND FIX"
echo "================================================"

echo ""
echo "📋 Step 1: Basic Environment Check"
echo "Current working directory: $(pwd)"
echo "Current user: $(whoami)"
echo "Current shell: $SHELL"
echo "Terminal type: $TERM"
echo "PATH: $PATH"

echo ""
echo "📋 Step 2: Process Information"
echo "Current processes:"
ps aux | grep -E "(bash|zsh|sh|terminal)" | head -10

echo ""
echo "📋 Step 3: File Descriptor Check"
echo "Open file descriptors:"
ls -la /proc/$$/fd/

echo ""
echo "📋 Step 4: Terminal Device Check"
if [ -t 0 ]; then
    echo "✅ stdin is a terminal"
else
    echo "❌ stdin is NOT a terminal"
fi

if [ -t 1 ]; then
    echo "✅ stdout is a terminal"
else
    echo "❌ stdout is NOT a terminal"
fi

if [ -t 2 ]; then
    echo "✅ stderr is a terminal"
else
    echo "❌ stderr is NOT a terminal"
fi

echo ""
echo "📋 Step 5: TTY Information"
echo "Current TTY: $(tty 2>/dev/null || echo 'No TTY')"
echo "TTY devices available:"
ls -la /dev/pts/ 2>/dev/null || echo "No /dev/pts available"

echo ""
echo "📋 Step 6: Environment Variables"
echo "TERM: $TERM"
echo "DISPLAY: $DISPLAY"
echo "SSH_TTY: $SSH_TTY"
echo "GPG_TTY: $GPG_TTY"

echo ""
echo "📋 Step 7: VS Code Environment Check"
echo "VSCODE_* variables:"
env | grep VSCODE || echo "No VS Code environment variables found"

echo ""
echo "📋 Step 8: Codespace Environment Check"
echo "CODESPACE_* variables:"
env | grep CODESPACE || echo "No Codespace environment variables found"

echo ""
echo "📋 Step 9: Git Configuration Check"
echo "Git user configuration:"
git config --get user.name || echo "No git user.name set"
git config --get user.email || echo "No git user.email set"
git config --get user.signingkey || echo "No git signing key set"

echo ""
echo "📋 Step 10: GPG Environment Check"
echo "GPG version: $(gpg --version | head -1)"
echo "GPG keys available:"
gpg --list-secret-keys --keyid-format LONG 2>/dev/null || echo "No GPG keys found"

echo ""
echo "📋 Step 11: Terminal Capabilities Test"
echo "Testing basic commands:"
echo "  - echo test: $(echo test)"
echo "  - date: $(date)"
echo "  - pwd: $(pwd)"
echo "  - ls count: $(ls -1 | wc -l) files"

echo ""
echo "📋 Step 12: Interactive vs Non-Interactive Check"
case $- in
    *i*) echo "✅ Shell is interactive" ;;
    *) echo "❌ Shell is NOT interactive" ;;
esac

echo ""
echo "📋 Step 13: Terminal Size Check"
echo "Terminal size: ${COLUMNS}x${LINES}"
echo "stty size: $(stty size 2>/dev/null || echo 'stty not available')"

echo ""
echo "📋 Step 14: Signal Handling Check"
echo "Available signals:"
kill -l | head -5

echo ""
echo "📋 Step 15: Resource Limits"
echo "Process limits:"
ulimit -a | head -10

echo ""
echo "🔧 TERMINAL DIAGNOSTIC COMPLETE"
echo "==============================="
echo ""
echo "📋 Common Terminal Issues and Fixes:"
echo ""
echo "1. **Terminal Disposal Issue:**"
echo "   - VS Code may be disposing terminals after inactivity"
echo "   - Solution: Create new terminal or restart VS Code"
echo ""
echo "2. **TTY/GPG Issues:**"
echo "   - GPG_TTY not properly set"
echo "   - Solution: export GPG_TTY=\$(tty)"
echo ""
echo "3. **Process Management:**"
echo "   - Too many background processes"
echo "   - Solution: Kill zombie processes"
echo ""
echo "4. **VS Code Extension Conflicts:**"
echo "   - Terminal extensions interfering"
echo "   - Solution: Disable extensions temporarily"
echo ""
echo "5. **Codespace Resource Limits:**"
echo "   - Memory or CPU constraints"
echo "   - Solution: Restart codespace"

echo ""
echo "🛠️ RECOMMENDED FIXES:"
echo "====================="
echo ""
echo "# Fix 1: Reset Terminal Environment"
echo "export TERM=xterm-256color"
echo "export GPG_TTY=\$(tty)"
echo "source ~/.bashrc"
echo ""
echo "# Fix 2: Restart GPG Agent"
echo "gpgconf --kill gpg-agent"
echo "gpgconf --launch gpg-agent"
echo ""
echo "# Fix 3: Clear Process Table"
echo "jobs -l"
echo "kill %1 %2 %3  # Kill background jobs"
echo ""
echo "# Fix 4: Restart Git Configuration"
echo "git config --global user.name 'Aurora CloudBank Orion Station'"
echo "git config --global user.email 'orion-station@aurora-cloudbank.ai'"
echo "git config --global user.signingkey C99D828826F276C8"
echo ""
echo "# Fix 5: Terminal Reset"
echo "reset"
echo "clear"

echo ""
echo "✅ Run this diagnostic to identify the specific issue!"
