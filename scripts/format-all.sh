#!/bin/bash

# Aurora CloudBank - Automated Formatting Script
# This script applies all formatting rules consistently

echo "🎨 Aurora CloudBank - Automated Formatting"
echo "========================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must be run from project root directory"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "🔧 Step 1: JavaScript/TypeScript formatting..."
npx eslint . --fix
npx prettier --write "**/*.{js,ts,json,yml,yaml}"

echo ""
echo "📝 Step 2: Markdown formatting..."
npx markdownlint --fix "**/*.md" || echo "⚠️ Some markdown files need manual review"

echo ""
echo "🐍 Step 3: Python formatting (if available)..."
if command -v black &> /dev/null; then
    black . --line-length 88 --target-version py311
else
    echo "ℹ️ Black not available, skipping Python formatting"
fi

if command -v isort &> /dev/null; then
    isort . --profile black
else
    echo "ℹ️ isort not available, skipping Python import sorting"
fi

echo ""
echo "✅ Formatting complete!"
echo ""
echo "📊 Current status:"
echo "• ESLint: $(npx eslint . 2>/dev/null | grep -E "warning|error" | wc -l) issues remaining"
echo "• Prettier: $(npx prettier --check . 2>/dev/null | wc -l) files need formatting"
echo "• Markdownlint: $(npx markdownlint **/*.md 2>/dev/null | wc -l) markdown issues"

echo ""
echo "🚀 Ready for commit!"
