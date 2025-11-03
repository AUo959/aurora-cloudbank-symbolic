#!/bin/bash
# Aggressive Pylance Disabling for Codespaces

echo "🔧 Aggressive Pylance Disabling for Performance"
echo "=============================================="

# 1. Kill existing Pylance processes
echo "🔪 Killing existing Pylance processes..."
pkill -f "ms-python.vscode-pylance" || true
pkill -f "pylance" || true

# 2. Disable Pylance extension via VS Code settings
echo "⚙️  Configuring VS Code user settings..."
mkdir -p ~/.vscode-remote/data/Machine
cat > ~/.vscode-remote/data/Machine/settings.json << 'EOF'
{
    "python.languageServer": "None",
    "python.analysis.indexing": false,
    "python.analysis.autoImportCompletions": false,
    "python.analysis.autoSearchPaths": false,
    "python.analysis.diagnosticMode": "off",
    "python.analysis.typeCheckingMode": "off",
    "python.linting.enabled": false,
    "python.linting.pylintEnabled": false,
    "pylance.insidersChannel": "off",
    "extensions.autoUpdate": false,
    "extensions.ignoreRecommendations": true
}
EOF

# 3. Create extension disable configuration
echo "🚫 Creating extension disable configuration..."
mkdir -p ~/.vscode-remote/data/Machine
cat > ~/.vscode-remote/data/Machine/extensions.json << 'EOF'
{
    "disabled": [
        "ms-python.vscode-pylance"
    ],
    "recommendations": []
}
EOF

# 4. Check if Pylance is still running
echo "🔍 Checking Pylance status..."
if pgrep -f "pylance" > /dev/null; then
    echo "⚠️  Pylance still running, applying nuclear option..."
    
    # Create a wrapper script that prevents Pylance from starting
    sudo mkdir -p /usr/local/bin/pylance-blocker
    sudo cat > /usr/local/bin/pylance-blocker/block.sh << 'EOF'
#!/bin/bash
# Block Pylance from consuming resources
echo "Pylance blocked for performance optimization"
sleep 3600
EOF
    sudo chmod +x /usr/local/bin/pylance-blocker/block.sh
else
    echo "✅ Pylance processes terminated"
fi

# 5. Update workspace settings with maximum restrictions
echo "📝 Updating workspace settings with maximum restrictions..."
cat > .vscode/settings.json << 'EOF'
{
    "python.languageServer": "None",
    "python.analysis.indexing": false,
    "python.analysis.autoImportCompletions": false,
    "python.analysis.autoSearchPaths": false,
    "python.analysis.diagnosticMode": "off",
    "python.analysis.typeCheckingMode": "off",
    "python.linting.enabled": false,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.linting.banditEnabled": false,
    "python.linting.mypyEnabled": false,
    "python.linting.prospectorEnabled": false,
    "python.linting.pydocstyleEnabled": false,
    "python.linting.pylamaEnabled": false,
    "python.testing.autoTestDiscoverOnSaveEnabled": false,
    "pylance.insidersChannel": "off",
    "editor.semanticHighlighting.enabled": false,
    "typescript.suggest.autoImports": "off",
    "typescript.updateImportsOnFileMove.enabled": "never",
    "javascript.suggest.autoImports": "off",
    "files.watcherExclude": {
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true,
        "**/node_modules/**": true,
        "**/.venv/**": true,
        "**/__pycache__/**": true,
        "**/*.pyc": true,
        "**/.pytest_cache/**": true,
        "**/coverage/**": true,
        "**/.coverage": true,
        "**/*.egg-info/**": true,
        "**/dist/**": true,
        "**/build/**": true
    },
    "search.exclude": {
        "**/node_modules": true,
        "**/.venv": true,
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true,
        "**/coverage": true,
        "**/.coverage": true,
        "**/*.egg-info": true,
        "**/dist": true,
        "**/build": true
    },
    "extensions.autoUpdate": false,
    "extensions.ignoreRecommendations": true,
    "telemetry.telemetryLevel": "off"
}
EOF

echo ""
echo "🎯 Aggressive Pylance disabling complete!"
echo "📊 Memory should be freed up immediately"
echo "🔄 Run './monitor_resources.sh' to verify performance improvement"
