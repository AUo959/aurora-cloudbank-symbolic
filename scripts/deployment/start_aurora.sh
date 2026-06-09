#!/bin/bash
# Aurora CloudBank Startup Script
# Canonical entrypoint: uvicorn api.aurora_api:app
#
# Legacy note: older Phase 3-4 scripts referenced aurora_api_server.py,
# aurora_master_integration.py, and aurora_cli.py at the repo root.
# Those files are no longer part of the canonical runtime. See:
#   docs/architecture/RUNTIME_PATH_DRIFT_LEDGER.md

set -e

echo "Aurora CloudBank Startup"
echo "========================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not installed"
    exit 1
fi
echo "Python: $(python3 --version)"

# Check for uvicorn
if ! python3 -m uvicorn --version &> /dev/null; then
    echo "ERROR: uvicorn is not installed. Run: pip install uvicorn"
    exit 1
fi

# Verify canonical entrypoint exists
if [ ! -f "api/aurora_api.py" ]; then
    echo "ERROR: api/aurora_api.py not found. Run from the repository root."
    exit 1
fi
echo "Entrypoint: api/aurora_api.py (canonical)"

echo ""
echo "Startup modes:"
echo "  1) API server (foreground)"
echo "  2) API server (background, logs to logs/api_server.log)"
echo "  3) API server with auto-reload (development)"
echo ""
read -p "Enter choice (1-3): " choice

mkdir -p logs

UVICORN_CMD="python3 -m uvicorn api.aurora_api:app --host 0.0.0.0 --port 8000"

case $choice in
    1)
        echo "Starting API server (foreground)..."
        exec $UVICORN_CMD
        ;;
    2)
        echo "Starting API server (background)..."
        nohup $UVICORN_CMD > logs/api_server.log 2>&1 &
        echo $! > api-server.pid
        echo "Started (PID: $(cat api-server.pid))"
        echo "Logs:  logs/api_server.log"
        echo "API:   http://localhost:8000"
        echo "Docs:  http://localhost:8000/docs"
        echo "Stop:  ./scripts/deployment/stop_aurora.sh"
        ;;
    3)
        echo "Starting API server (dev mode with --reload)..."
        exec $UVICORN_CMD --reload
        ;;
    *)
        echo "Invalid choice."
        exit 1
        ;;
esac
