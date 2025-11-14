#!/bin/bash

# CI/CD Maintenance and Cleanup Script
# Helps resolve common CI/CD issues and cleanup temporary files

echo "🔧 Aurora CI/CD Maintenance Script"
echo "=================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Clean up temporary files that might cause CI issues
echo "🧹 Cleaning up temporary files..."
rm -rf /tmp/codeql-* 2>/dev/null || true
rm -rf /home/runner/work/_temp/proxy.log 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true
rm -rf __pycache__ 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "✅ Temporary files cleaned"

# Check GitHub Actions workflow files
echo "📋 Checking workflow files..."
if [ -d ".github/workflows" ]; then
    for workflow in .github/workflows/*.yml; do
        if [ -f "$workflow" ]; then
            echo "  ✅ Found: $(basename "$workflow")"
            # Basic YAML syntax check
            if command_exists python3; then
                python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null && echo "    ✅ Valid YAML" || echo "    ❌ Invalid YAML"
            fi
        fi
    done
else
    echo "  ⚠️  No .github/workflows directory found"
fi

# Check package.json and dependencies
echo "📦 Checking Node.js setup..."
if [ -f "package.json" ]; then
    echo "  ✅ package.json found"
    if command_exists npm; then
        npm --version && echo "    ✅ npm available" || echo "    ❌ npm not available"
    fi
    if command_exists node; then
        node --version && echo "    ✅ node available" || echo "    ❌ node not available"
    fi
else
    echo "  ℹ️  No package.json found (Node.js CI will be skipped)"
fi

# Check Python setup
echo "🐍 Checking Python setup..."
if [ -f "requirements.txt" ]; then
    echo "  ✅ requirements.txt found"
    if command_exists python3; then
        python3 --version && echo "    ✅ python3 available" || echo "    ❌ python3 not available"
    fi
    if command_exists pip3; then
        pip3 --version && echo "    ✅ pip3 available" || echo "    ❌ pip3 not available"
    fi
else
    echo "  ℹ️  No requirements.txt found"
fi

# Check Aurora-specific files
echo "🌅 Checking Aurora-specific files..."
aurora_files=(
    "symbolic_config.yaml"
    "devcontainer.json"
    "modules/symbolic_core/sonnet4_integration_hub.py"
    "aurora_api.py"
)

for file in "${aurora_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ⚠️  $file (missing)"
    fi
done

# Check for common CI issues
echo "🔍 Checking for common CI issues..."

# Check for merge conflict markers
if grep -r "<<<<<<< HEAD\|>>>>>>> \|=======" . --exclude-dir=.git 2>/dev/null; then
    echo "  ❌ Merge conflict markers found!"
else
    echo "  ✅ No merge conflict markers"
fi

# Check for large files that might cause issues
echo "📏 Checking for large files..."
find . -size +50M -type f 2>/dev/null | head -5 | while read -r file; do
    echo "  ⚠️  Large file: $file ($(du -h "$file" | cut -f1))"
done

# Generate CI status report
echo ""
echo "📊 CI/CD Status Report"
echo "====================="
echo "Date: $(date)"
echo "Repository: $(basename "$(pwd)")"
echo ""
echo "Workflow Files:"
ls -la .github/workflows/*.yml 2>/dev/null | wc -l | xargs echo "  Count:"
echo ""
echo "Project Files:"
[ -f "package.json" ] && echo "  ✅ Node.js project" || echo "  ❌ No Node.js project"
[ -f "requirements.txt" ] && echo "  ✅ Python project" || echo "  ❌ No Python project"
[ -f "devcontainer.json" ] && echo "  ✅ DevContainer configured" || echo "  ❌ No DevContainer"
[ -f "symbolic_config.yaml" ] && echo "  ✅ Aurora configured" || echo "  ❌ No Aurora config"
echo ""
echo "Recommendations:"
echo "  1. Review workflow files for syntax errors"
echo "  2. Ensure all dependencies are properly specified"
echo "  3. Test locally before pushing to avoid CI failures"
echo "  4. Monitor CI logs for proxy.log and cleanup issues"
echo ""
echo "✨ Maintenance complete!"
