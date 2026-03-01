#!/bin/bash
# Aurora CloudBank Comprehensive Startup Script
# Launches all Phase 4 real-world applications

set -e

echo "🚀 Aurora CloudBank Phase 4 Startup"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check required files
REQUIRED_FILES=(
    "aurora_quantum_processor.py"
    "aurora_consciousness_engine.py" 
    "aurora_adaptive_learning.py"
    "aurora_master_integration.py"
    "aurora_api_server.py"
    "aurora_cli.py"
    "aurora_dashboard.html"
)

echo "🔍 Checking required files..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        MISSING_FILES=true
    fi
done

if [ "$MISSING_FILES" = true ]; then
    echo "⚠️ Some required files are missing"
    echo "💡 Please ensure all Aurora CloudBank Phase 3-4 files are present"
    exit 1
fi

# Function to start service in background
start_service() {
    local service_name="$1"
    local command="$2"
    local log_file="$3"
    
    echo "🌟 Starting $service_name..."
    nohup $command > "$log_file" 2>&1 &
    local pid=$!
    echo "$pid" > "${service_name,,}.pid"
    echo "✅ $service_name started (PID: $pid)"
}

# Create logs directory
mkdir -p logs

# Start services based on user choice
echo ""
echo "🎮 Choose startup mode:"
echo "1) API Server only"
echo "2) CLI Interactive mode"
echo "3) Full integration test"
echo "4) All services"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🌐 Starting API Server..."
        python3 aurora_api_server.py
        ;;
    2)
        echo "⌨️ Starting CLI Interactive mode..."
        python3 aurora_cli.py --interactive
        ;;
    3)
        echo "🧪 Running full integration test..."
        python3 aurora_master_integration.py
        ;;
    4)
        echo "🚀 Starting all services..."
        
        # Start API server in background
        start_service "API-Server" "python3 aurora_api_server.py" "logs/api_server.log"
        
        # Wait a moment for API server to start
        sleep 3
        
        # Run integration test
        echo "🧪 Running integration test..."
        python3 aurora_master_integration.py
        
        echo ""
        echo "🎉 All services started!"
        echo "🔗 API Server: http://localhost:8000"
        echo "📖 API Docs: http://localhost:8000/docs"
        echo "📊 Dashboard: http://localhost:8000"
        echo ""
        echo "📋 Service Status:"
        if [ -f "api-server.pid" ]; then
            echo "✅ API Server running (PID: $(cat api-server.pid))"
        fi
        
        echo ""
        echo "🛑 To stop services, run: ./stop_aurora.sh"
        ;;
    *)
        echo "❓ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 Aurora CloudBank startup complete!"
