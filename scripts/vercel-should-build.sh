#!/bin/bash
# Vercel Ignored Build Step
# Exit 1 = Build, Exit 0 = Skip build
#
# This script determines if Vercel should build based on changed files.
# It only builds if frontend-related files or deployment configs change.

echo "🔍 Checking if Vercel build is needed..."

# Frontend paths that should trigger builds
FRONTEND_PATHS="^(static/|tests/web/|vercel\.json|\.vercelignore)"

# Get changed files compared to previous commit
CHANGED_FILES=$(git diff HEAD^ HEAD --name-only)

if [ -z "$CHANGED_FILES" ]; then
    echo "⚠️  No changed files detected, defaulting to build"
    exit 1
fi

echo "📝 Changed files:"
echo "$CHANGED_FILES"
echo ""

# Check if any frontend files changed
if echo "$CHANGED_FILES" | grep -qE "$FRONTEND_PATHS"; then
    echo "✅ Frontend files changed - BUILD REQUIRED"
    exit 1
else
    echo "⏭️  Only backend/infrastructure files changed - SKIPPING BUILD"
    exit 0
fi
