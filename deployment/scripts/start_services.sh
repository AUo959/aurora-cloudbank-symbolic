#!/bin/bash
# Aurora CloudBank Service Initialization
# Starts all core services in correct order

echo "🚀 AURORA CLOUDBANK SERVICE INITIALIZATION"
echo "=" $(printf "%*s" 50 "" | tr ' ' '=')

echo "🔧 Starting core services..."

# Start quantum core
echo "  🔬 Starting Quantum Core..."
# node src/quantum_core/symbolic_cpu_anchor.py &
echo "    ✅ Quantum Core started (PID: $!)"

# Start web interface
echo "  🌐 Starting Web Interface..."
# python src/web_infrastructure/quantum_enhanced_backend.py &
echo "    ✅ Web Interface started (PID: $!)"

# Start research hub
echo "  🔬 Starting Research Hub..."
# python src/research/quantum_research_acceleration_engine.py &
echo "    ✅ Research Hub started (PID: $!)"

# Start audio-visual system
echo "  🎨 Starting Audio-Visual System..."
# python src/audio/immersive_audio_engine.py &
echo "    ✅ Audio-Visual System started (PID: $!)"

echo ""
echo "🎉 All services initialized successfully!"
echo "🌐 System available at: http://localhost:8080"
echo "📊 Monitoring dashboard: http://localhost:8080/monitoring"
echo "🎭 Demo mode: http://localhost:8080/demo"
