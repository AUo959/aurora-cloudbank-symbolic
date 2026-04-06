#!/bin/bash
# Aurora Quick Development Server Launcher
# One-command setup for immediate development

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
    PYTHON_BIN="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)"
fi

if [[ -z "${PYTHON_BIN:-}" ]]; then
    echo "❌ Python interpreter not found. Please install Python 3 and ensure it's on your PATH, or create .venv." >&2
    exit 1
fi

if [[ -f "$REPO_ROOT/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$REPO_ROOT/.env"
    set +a
fi

echo "🚀 Aurora Quick Start Server"
echo "==========================="

# 1. Quick health check
echo "🔍 Pre-flight check..."
"$PYTHON_BIN" -c "import fastapi, uvicorn; print('✅ FastAPI ready')" || exit 1

# 2. Launch options
echo ""
echo "Choose your development server:"
echo "1) Aurora API Server (port 8000)"
echo "2) Aurora GUI CloudHub (port 8080)"
echo "3) Both servers (background)"
echo ""

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🌟 Starting Aurora API Server..."
        "$PYTHON_BIN" "$REPO_ROOT/api/aurora_api.py"
        ;;
    2)
        echo "🌟 Starting Aurora GUI CloudHub..."
        "$PYTHON_BIN" "$REPO_ROOT/api/aurora_gui_cloudhub_fastapi.py"
        ;;
    3)
        echo "🌟 Starting both servers..."
        echo "📡 API Server on http://localhost:8000"
        echo "🖥️  GUI CloudHub on http://localhost:8080"
        "$PYTHON_BIN" "$REPO_ROOT/api/aurora_api.py" &
        "$PYTHON_BIN" "$REPO_ROOT/api/aurora_gui_cloudhub_fastapi.py" &
        echo "✅ Both servers running in background"
        echo "💡 Use 'jobs' to see running processes"
        echo "💡 Use 'kill %1 %2' to stop both servers"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
