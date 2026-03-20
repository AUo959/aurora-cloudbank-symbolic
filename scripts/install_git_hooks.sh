#!/bin/bash
# GitWiz Git Hooks Installer
# Installs and configures GitWiz git hooks for automated quality gates

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$REPO_ROOT/.git/hooks"
GITWIZ_HOOKS_DIR="$REPO_ROOT/scripts/git-hooks"

echo "🔧 Installing GitWiz Git Hooks..."

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install pre-commit hook
if [ -f "$GITWIZ_HOOKS_DIR/pre-commit" ]; then
    echo "📋 Installing pre-commit hook..."
    cp "$GITWIZ_HOOKS_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
    chmod +x "$HOOKS_DIR/pre-commit"
    echo "✅ Pre-commit hook installed"
else
    echo "❌ Pre-commit hook source not found"
fi

# Install post-commit hook for reporting
cat > "$HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
# GitWiz Post-commit Hook
# Runs quality analysis after commit

echo "📊 GitWiz Post-commit Analysis..."
cd "$(git rev-parse --show-toplevel)"

if [ -f "scripts/gitwiz_integrated_command.py" ]; then
    # Generate quick status report
    python3 scripts/gitwiz_integrated_command.py status > .gitwiz/last_commit_status.json 2>/dev/null || true
    echo "✅ Post-commit analysis complete"
fi
EOF

chmod +x "$HOOKS_DIR/post-commit"
echo "✅ Post-commit hook installed"

# Install pre-push hook for comprehensive checks
cat > "$HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash
# GitWiz Pre-push Hook
# Comprehensive quality check before push

echo "🚀 GitWiz Pre-push Quality Gate..."
cd "$(git rev-parse --show-toplevel)"

if [ -f "scripts/gitwiz_integrated_command.py" ]; then
    echo "🔍 Running comprehensive quality check..."
    python3 scripts/gitwiz_integrated_command.py quality-check --output summary
    
    if [ $? -eq 0 ]; then
        echo "✅ Pre-push quality gate passed!"
        exit 0
    else
        echo "❌ Pre-push quality gate failed!"
        echo "💡 Fix issues before pushing or use --no-verify to bypass"
        exit 1
    fi
fi
EOF

chmod +x "$HOOKS_DIR/pre-push"
echo "✅ Pre-push hook installed"

echo ""
echo "🎉 GitWiz Git Hooks Installation Complete!"
echo ""
echo "Installed hooks:"
echo "  📋 pre-commit  - Canonical Aurora validation wrapper"
echo "  📊 post-commit - Analysis after commit"
echo "  🚀 pre-push    - Comprehensive check before push"
echo ""
echo "Configuration:"
echo "  Pre-commit now routes through scripts/run_pre_commit.sh"
echo "  Use --no-verify to bypass hooks when needed"
echo ""
echo "Test the installation:"
echo "  git commit --dry-run (to test pre-commit)"
echo "  python3 scripts/gitwiz_integrated_command.py status"
