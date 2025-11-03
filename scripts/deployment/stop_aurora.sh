#!/bin/bash
# Aurora CloudBank Stop Script

echo "🛑 Stopping Aurora CloudBank services..."

# Stop services by PID
if [ -f "api-server.pid" ]; then
    PID=$(cat api-server.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✅ API Server stopped"
    fi
    rm api-server.pid
fi

# Clean up any remaining processes
pkill -f "aurora_api_server.py" 2>/dev/null || true
pkill -f "aurora_cli.py" 2>/dev/null || true

echo "🎉 Aurora CloudBank services stopped"
