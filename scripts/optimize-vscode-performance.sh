#!/bin/bash
# VS Code Extension Performance Optimization Script
# Optimizes extension settings and cleans up performance issues

echo "🚀 VS Code Extension Performance Optimization"
echo "=============================================="

# Check current resource usage
echo ""
echo "📊 Current Extension Resource Usage:"
echo "Extension Hosts: $(ps aux | grep -c 'extensionHost')"
echo "SonarQube Processes: $(ps aux | grep -c 'sonarlint')"
echo "TypeScript Servers: $(ps aux | grep -c 'tsserver')"
echo "Pylance Servers: $(ps aux | grep -c 'pylance')"

# Memory usage summary
echo ""
echo "💾 Memory Usage by Extension Type:"
ps aux --sort=-%mem | grep -E "(extensionHost|sonarlint|tsserver|pylance)" | head -5 | awk '{print $11, $6/1024 "MB"}'

# Create optimized workspace settings
echo ""
echo "⚙️ Creating optimized workspace settings..."

mkdir -p .vscode

cat > .vscode/settings.json << 'EOF'
{
  "// Performance Optimizations": true,

  "// SonarQube - Reduce resource usage": true,
  "sonarlint.rules": {
    "javascript:ConsoleLogging": "off",
    "python:S1192": "off",
    "typescript:S1541": "off",
    "javascript:S1541": "off"
  },
  "sonarlint.connectedMode.automatic": false,
  "sonarlint.disableTelemetry": true,

  "// TypeScript - Optimize performance": true,
  "typescript.suggest.autoImports": "off",
  "typescript.preferences.includePackageJsonAutoImports": "off",
  "typescript.disableAutomaticTypeAcquisition": true,
  "typescript.updateImportsOnFileMove.enabled": "never",

  "// Python - Optimize Pylance performance": true,
  "python.analysis.autoImportCompletions": false,
  "python.analysis.autoSearchPaths": false,
  "python.analysis.packageIndexDepths": [
    {
      "name": "",
      "depth": 2
    }
  ],

  "// File Watching - Exclude heavy directories": true,
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/**": true,
    "**/.venv/**": true,
    "**/venv/**": true,
    "**/dist/**": true,
    "**/build/**": true,
    "**/__pycache__/**": true,
    "**/.pytest_cache/**": true,
    "**/coverage/**": true
  },

  "// Search - Exclude heavy directories": true,
  "search.exclude": {
    "**/node_modules": true,
    "**/bower_components": true,
    "**/.venv": true,
    "**/venv": true,
    "**/dist": true,
    "**/build": true,
    "**/__pycache__": true,
    "**/.git": true
  },

  "// General Performance": true,
  "extensions.autoUpdate": false,
  "extensions.autoCheckUpdates": false,
  "git.enabled": true,
  "git.autorefresh": false,
  "git.autofetch": false,

  "// Disable heavy features for Aurora project": true,
  "eslint.workingDirectories": ["./"],
  "eslint.codeActionsOnSave.mode": "problems",

  "// Editor Performance": true,
  "editor.occurrencesHighlight": false,
  "editor.selectionHighlight": false,
  "editor.renderWhitespace": "none",
  "editor.minimap.enabled": false,
  "breadcrumbs.enabled": false
}
EOF

# Create extension-specific optimization settings
echo ""
echo "🔧 Creating extension-specific optimizations..."

# Check if SonarQube is causing issues
if pgrep -f "sonarlint" > /dev/null; then
    echo "⚠️ SonarQube detected - Creating optimization config..."

    cat > .vscode/sonarlint.json << 'EOF'
{
  "rules": {
    "javascript:ConsoleLogging": {
      "level": "off"
    },
    "python:S1192": {
      "level": "off"
    },
    "typescript:S1541": {
      "level": "off"
    }
  },
  "excludeRules": [
    "javascript:S117",
    "python:S117",
    "typescript:S117"
  ]
}
EOF
fi

# Create performance monitoring script
echo ""
echo "📈 Creating performance monitoring script..."

cat > scripts/monitor-vscode-performance.sh << 'EOF'
#!/bin/bash
# Monitor VS Code Extension Performance

echo "🔍 VS Code Performance Monitor"
echo "=============================="

echo ""
echo "💾 Memory Usage (Top Extensions):"
ps aux --sort=-%mem | grep -E "(code|node.*extension|sonarlint|pylance|tsserver)" | head -10 | awk '{printf "%-50s %sMB\n", $11, $6/1024}'

echo ""
echo "🔄 Extension Processes:"
echo "Extension Hosts: $(pgrep -f extensionHost | wc -l)"
echo "SonarQube: $(pgrep -f sonarlint | wc -l)"
echo "TypeScript: $(pgrep -f tsserver | wc -l)"
echo "Pylance: $(pgrep -f pylance | wc -l)"

echo ""
echo "📊 Total Resource Usage:"
total_mem=$(ps aux | grep -E "(extensionHost|sonarlint|tsserver|pylance)" | awk '{sum += $6} END {print sum/1024}')
echo "Total Extension Memory: ${total_mem}MB"

echo ""
echo "🎯 Performance Recommendations:"
if [ "$(pgrep -f sonarlint | wc -l)" -gt 1 ]; then
    echo "⚠️ Multiple SonarQube instances detected - consider disabling"
fi

if [ "${total_mem%.*}" -gt 1000 ]; then
    echo "⚠️ High memory usage detected (${total_mem}MB)"
    echo "   Consider closing unused VS Code windows"
fi

echo "✅ Use 'code --disable-extensions' for lightweight sessions"
echo "✅ Regularly restart VS Code to clear memory leaks"
EOF

chmod +x scripts/monitor-vscode-performance.sh

# Performance summary
echo ""
echo "✅ Optimization Complete!"
echo ""
echo "📋 Changes Made:"
echo "• Created optimized .vscode/settings.json"
echo "• Disabled heavy SonarQube rules"
echo "• Optimized TypeScript and Python settings"
echo "• Excluded heavy directories from file watching"
echo "• Created performance monitoring script"
echo ""
echo "🚀 Next Steps:"
echo "1. Restart VS Code to apply settings"
echo "2. Run 'bash scripts/monitor-vscode-performance.sh' to monitor"
echo "3. Consider disabling SonarQube during active development"
echo ""
echo "💡 Tips:"
echo "• Use Ctrl+Shift+P → 'Developer: Inspect Context Keys' to debug performance"
echo "• Use Ctrl+Shift+P → 'Developer: Startup Performance' for detailed analysis"
echo "• Consider using 'code --disable-extensions' for lightweight editing"
