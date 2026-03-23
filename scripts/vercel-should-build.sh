#!/bin/bash
# Vercel Ignored Build Step
# Exit 1 = Build, Exit 0 = Skip build
#
# This script determines if Vercel should build based on changed files.
# It supports an explicit kill switch so repository admins can disable
# preview deployments without disconnecting the Vercel project.

set -u

echo "🔍 Checking if Vercel build is needed..."

DISABLE_FLAG="${AURORA_DISABLE_VERCEL_BUILDS:-}"
if [ "$DISABLE_FLAG" = "1" ] || [ "$DISABLE_FLAG" = "true" ] || [ "$DISABLE_FLAG" = "TRUE" ]; then
    echo "⏭️  Vercel preview builds are explicitly disabled via AURORA_DISABLE_VERCEL_BUILDS"
    exit 0
fi

if [ -f ".vercel-disabled" ]; then
    echo "⏭️  Vercel preview builds are disabled by .vercel-disabled"
    exit 0
fi

# Frontend paths that should trigger builds
FRONTEND_PATHS="^(frontend/|static/|tests/web/|vercel\.json|\.vercelignore|package\.json|package-lock\.json|npm-shrinkwrap\.json|index\.html|web-demo\.html|aurora_dashboard\.html|scripts/build-web\.js)"

get_changed_files() {
    local merge_base

    if git rev-parse --verify origin/main >/dev/null 2>&1; then
        merge_base=$(git merge-base HEAD origin/main 2>/dev/null || true)
        if [ -n "$merge_base" ]; then
            git diff --name-only "$merge_base" HEAD
            return 0
        fi
    fi

    if git rev-parse --verify HEAD^ >/dev/null 2>&1; then
        git diff --name-only HEAD^ HEAD
        return 0
    fi

    return 1
}

CHANGED_FILES=$(get_changed_files || true)

if [ -z "$CHANGED_FILES" ]; then
    echo "⚠️  Could not determine changed files, defaulting to SKIP"
    echo "    Set AURORA_DISABLE_VERCEL_BUILDS=0 and review Vercel project settings if builds are expected."
    exit 0
fi

echo "📝 Changed files:"
echo "$CHANGED_FILES"
echo ""

# Check if any frontend files changed
if echo "$CHANGED_FILES" | grep -qE "$FRONTEND_PATHS"; then
    echo "✅ Frontend files changed - BUILD REQUIRED"
    exit 1
fi

echo "⏭️  Only backend/infrastructure files changed - SKIPPING BUILD"
exit 0
