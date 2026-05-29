#!/bin/bash
# Aurora CloudBank Symbolic — canonical service starter (#759)
#
# Historical context: this script previously referenced
# aurora_api_server.py, aurora_master_integration.py, aurora_cli.py,
# and a handful of root-level demo scripts that no longer exist. The
# canonical FastAPI entrypoint is api/aurora_api.py; the canonical
# uvicorn command is `uvicorn api.aurora_api:app`. See CLAUDE.md and
# docs/operational/PUSH_2026Q2_PLAN.md.
#
# Modes:
#   1) API server (uvicorn)            — production-like
#   2) API server (auto-reload)        — development
#   3) Run scoped tests                — quick CI-style verification
#
# Override behaviour via env vars:
#   AURORA_HOST   (default 0.0.0.0)
#   AURORA_PORT   (default 8000)

set -euo pipefail

cd "$(dirname "$0")/../.."

if [ ! -f "api/aurora_api.py" ]; then
    echo "❌ api/aurora_api.py not found — wrong working directory?" >&2
    exit 1
fi

HOST="${AURORA_HOST:-0.0.0.0}"
PORT="${AURORA_PORT:-8000}"

mkdir -p logs

echo "🎮 Aurora CloudBank — startup mode:"
echo "  1) API server (uvicorn) at ${HOST}:${PORT}"
echo "  2) API server with --reload (development)"
echo "  3) Run scoped test suite"
read -rp "Enter choice (1-3): " choice

case "$choice" in
    1)
        echo "🌐 Starting uvicorn on ${HOST}:${PORT}..."
        exec uvicorn api.aurora_api:app --host "$HOST" --port "$PORT"
        ;;
    2)
        echo "🔧 Starting uvicorn with --reload on ${HOST}:${PORT}..."
        exec uvicorn api.aurora_api:app --host "$HOST" --port "$PORT" --reload
        ;;
    3)
        echo "🧪 Running scoped tests..."
        exec pytest -m "not slow" -q
        ;;
    *)
        echo "❓ Invalid choice." >&2
        exit 1
        ;;
esac
