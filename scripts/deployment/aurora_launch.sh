#!/bin/bash
# Aurora CloudBank Symbolic - Production Launch Script
# Complete system deployment and launch

echo "🌟 AURORA CLOUDBANK SYMBOLIC - PRODUCTION LAUNCH"
echo "=" $(printf "%*s" 60 "" | tr ' ' '=')
echo "📅 Launch Date: $(date)"
echo "🏗️ Version: 1.0.0"
echo "🔧 Environment: Production"
echo ""

# Step 1: Pre-launch checks
echo "🔍 Step 1: Running pre-launch system checks..."
node aurora_status_checker.js
if [ $? -ne 0 ]; then
    echo "❌ Pre-launch checks failed!"
    exit 1
fi
echo "✅ Pre-launch checks passed"
echo ""

# Step 2: Initialize monitoring
echo "📊 Step 2: Starting monitoring dashboard..."
python deployment/monitoring/aurora_monitoring.py &
MONITORING_PID=$!
echo "✅ Monitoring started (PID: $MONITORING_PID)"
echo ""

# Step 3: Start core services
echo "⚙️ Step 3: Initializing core services..."
./deployment/scripts/start_services.sh
echo "✅ Core services started"
echo ""

# Step 4: Launch demo mode
echo "🎭 Step 4: Activating demo mode..."
node deployment/demo/aurora_demo_mode.js
echo "✅ Demo mode activated"
echo ""

# Step 5: Final system validation
echo "🔬 Step 5: Final system validation..."
echo "🌐 Web Interface: http://localhost:8080"
echo "📊 Monitoring: http://localhost:8080/monitoring"
echo "🎭 Demo: http://localhost:8080/demo"
echo "🔬 Quantum Core: http://localhost:8001"
echo "🔍 Research Hub: http://localhost:8002"
echo "🎨 Audio-Visual: http://localhost:8003"
echo ""

echo "🎉 AURORA CLOUDBANK SYMBOLIC SUCCESSFULLY LAUNCHED!"
echo "🌟 System is now ready for production use"
echo "📚 Documentation available in docs/"
echo "🔧 Configuration in deployment/config/"
echo "=" $(printf "%*s" 60 "" | tr ' ' '=')
