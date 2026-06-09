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

# Clean up any remaining canonical API processes
pkill -f "api.aurora_api:app" 2>/dev/null || true
pkill -f "api/aurora_api.py" 2>/dev/null || true

echo "🎉 Aurora CloudBank services stopped"
