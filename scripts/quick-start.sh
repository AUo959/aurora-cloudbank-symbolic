#!/bin/bash
# Aurora Quick Development Server Launcher
# One-command setup for immediate development

echo "🚀 Aurora Quick Start Server"
echo "==========================="

# 1. Quick health check
echo "🔍 Pre-flight check..."
python3 -c "import fastapi, uvicorn; print('✅ FastAPI ready')" || exit 1

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
        python3 aurora_api.py
        ;;
    2)
        echo "🌟 Starting Aurora GUI CloudHub..."
        python3 aurora_gui_cloudhub_fastapi.py
        ;;
    3)
        echo "🌟 Starting both servers..."
        echo "📡 API Server on http://localhost:8000"
        echo "🖥️  GUI CloudHub on http://localhost:8080"
        python3 aurora_api.py &
        python3 aurora_gui_cloudhub_fastapi.py &
        echo "✅ Both servers running in background"
        echo "💡 Use 'jobs' to see running processes"
        echo "💡 Use 'kill %1 %2' to stop both servers"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
