#!/bin/bash

echo "🔍 System Tool Check for Aurora CloudBank"
echo "========================================"

echo ""
echo "📋 Checking for GPG:"
if command -v gpg &> /dev/null; then
    echo "✅ GPG found: $(which gpg)"
    gpg --version | head -1
else
    echo "❌ GPG not found"
fi

echo ""
echo "📋 Checking for Git:"
if command -v git &> /dev/null; then
    echo "✅ Git found: $(which git)"
    git --version
else
    echo "❌ Git not found"
fi

echo ""
echo "📋 Checking for Python:"
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found: $(which python3)"
    python3 --version
else
    echo "❌ Python3 not found"
fi

echo ""
echo "📋 Checking for Node.js:"
if command -v node &> /dev/null; then
    echo "✅ Node.js found: $(which node)"
    node --version
else
    echo "❌ Node.js not found"
fi

echo ""
echo "📋 System Information:"
echo "OS: $(uname -s)"
echo "Architecture: $(uname -m)"
echo "Kernel: $(uname -r)"

echo ""
echo "📋 Package Manager Check:"
if command -v apt &> /dev/null; then
    echo "✅ APT available"
elif command -v yum &> /dev/null; then
    echo "✅ YUM available"
elif command -v pacman &> /dev/null; then
    echo "✅ Pacman available"
else
    echo "❓ No common package manager found"
fi

echo ""
echo "📋 GPG Installation Check:"
if [ -f "/usr/bin/gpg" ]; then
    echo "✅ GPG binary found at /usr/bin/gpg"
elif [ -f "/usr/local/bin/gpg" ]; then
    echo "✅ GPG binary found at /usr/local/bin/gpg"
else
    echo "❌ No GPG binary found in standard locations"
    echo "Checking for gnupg package..."
    if command -v apt &> /dev/null; then
        apt list --installed 2>/dev/null | grep -i gnupg || echo "gnupg not installed via apt"
    fi
fi

echo ""
echo "✅ System tool check complete!"
