#!/bin/bash
# Dev Container Conflict Resolution for Aurora CloudBank

echo "🔧 Aurora CloudBank Dev Container Conflict Resolution"
echo "=================================================="

echo ""
echo "🔍 CONFLICT ANALYSIS:"
echo "1. /.devcontainer/devcontainer.json - PERFORMANCE CONFLICTING CONFIG"
echo "   - Forces Pylint + Pylance extensions"
echo "   - Enables python.linting.enabled: true"
echo "   - Overrides workspace performance settings"
echo ""
echo "2. /devcontainer.json - MINIMAL CONFIG"
echo "   - Uses custom Dockerfile"
echo "   - Minimal extensions"
echo "   - Custom postCreate script"
echo ""
echo "3. /.vscode/settings.json - PERFORMANCE OPTIMIZED"
echo "   - Disables heavy language servers"
echo "   - Performance optimizations applied"
echo ""

echo "🎯 RESOLUTION STRATEGY:"
echo "======================"
echo ""
echo "Option 1: Update .devcontainer/devcontainer.json (RECOMMENDED)"
echo "   - Remove conflicting Python linting settings"
echo "   - Remove heavy extensions"
echo "   - Let workspace settings.json take precedence"
echo ""
echo "Option 2: Use minimal /devcontainer.json"
echo "   - Remove .devcontainer/ folder"
echo "   - Use root-level devcontainer.json"
echo ""
echo "Option 3: Container rebuild with fixed config"
echo "   - Apply fixes and rebuild dev container"
echo ""

read -p "Which option would you like to proceed with? (1/2/3): " choice

case $choice in
    1)
        echo "🔧 Fixing .devcontainer/devcontainer.json..."

        # Backup original
        cp .devcontainer/devcontainer.json .devcontainer/devcontainer.json.backup

        # Create performance-optimized dev container config
        cat > .devcontainer/devcontainer.json << 'EOF'
{
  "name": "Aurora CloudBank Performance Optimized",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:20",
  "postCreateCommand": "bash -c 'pip install -r requirements.txt || true; npm install || true; git config --global user.name \"Aurora CloudBank\" || true; git config --global user.email \"aurora@cloudbank.dev\" || true; git config --global init.defaultBranch main || true; echo \"DevContainer setup complete - Aurora CloudBank ready!\"'",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "GitHub.copilot",
        "GitHub.copilot-chat",
        "eamodio.gitlens",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode"
      ],
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash",
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": false,
        "python.linting.pylintEnabled": false,
        "python.analysis.indexing": false,
        "editor.formatOnSave": false,
        "files.associations": {
          "*.jsonc": "jsonc"
        }
      }
    }
  },
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    },
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.11"
    },
    "ghcr.io/devcontainers/features/git:1": {
      "version": "latest"
    }
  }
}
EOF
        echo "✅ Updated .devcontainer/devcontainer.json with performance optimizations"
        echo "📁 Backup saved as .devcontainer/devcontainer.json.backup"
        ;;
    2)
        echo "🔧 Using minimal devcontainer.json..."
        mv .devcontainer .devcontainer.backup
        echo "✅ Moved .devcontainer to .devcontainer.backup"
        echo "✅ Root /devcontainer.json will be used"
        ;;
    3)
        echo "🔧 Ready for container rebuild..."
        echo "📋 Steps after applying fixes:"
        echo "1. Close VS Code"
        echo "2. Reopen in container"
        echo "3. VS Code will rebuild with new config"
        ;;
    *)
        echo "❌ Invalid option selected"
        exit 1
        ;;
esac

echo ""
echo "🎯 NEXT STEPS:"
echo "============="
echo "1. Apply the chosen fix above"
echo "2. Reload VS Code window OR rebuild container"
echo "3. Verify performance improvements"
echo ""
echo "💡 The dev container conflicts were preventing your"
echo "   performance optimizations from taking effect!"
