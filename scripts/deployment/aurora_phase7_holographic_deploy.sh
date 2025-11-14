#!/bin/bash

# Aurora CloudBank Phase 7: Holographic Command Interface Launcher
# Beautiful, spectacular interface deployment with Aurora Custom GPT integration

set -e

echo "🌟 AURORA CLOUDBANK PHASE 7 DEPLOYMENT"
echo "======================================"
echo ""

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${CYAN}[AURORA]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner
echo -e "${PURPLE}"
cat << "EOF"
     ___   _   _  ____   ___  ____      _    
    / _ \ | | | ||  _ \ / _ \|  _ \    / \   
   | |_| || | | || |_) | | | | |_) |  / _ \  
   |  _  || |_| ||  _ <| |_| |  _ <  / ___ \ 
   |_| |_| \___/ |_| \_\\___/|_| \_\/_/   \_\
                                            
   CloudBank v3.5.1 - Holographic Interface
EOF
echo -e "${NC}"

# Check prerequisites
print_status "Checking Phase 7 prerequisites..."

if [ ! -f "src/integrations/aurora_custom_gpt_bridge.js" ]; then
    print_error "Aurora Custom GPT Bridge not found!"
    exit 1
fi

if [ ! -f "src/config/orion_core_config.js" ]; then
    print_error "ORION Core configuration not found!"
    exit 1
fi

if [ ! -f "src/interface/holographic_command_interface.html" ]; then
    print_error "Holographic Command Interface not found!"
    exit 1
fi

if [ ! -f "src/orchestrators/holographic_interface_orchestrator.js" ]; then
    print_error "Holographic Interface Orchestrator not found!"
    exit 1
fi

print_success "All Phase 7 components found"

# Install dependencies if needed
print_status "Checking Node.js dependencies..."

if [ ! -d "node_modules" ]; then
    print_warning "Node modules not found, installing dependencies..."
    npm install express socket.io http
fi

print_success "Dependencies ready"

# Check if ports are available
print_status "Checking port availability..."

if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 8080 is already in use"
    echo "Would you like to:"
    echo "1) Kill existing process and continue"
    echo "2) Use a different port"
    echo "3) Exit"
    read -p "Choice (1-3): " choice
    
    case $choice in
        1)
            print_status "Terminating existing process on port 8080..."
            sudo kill -9 $(lsof -Pi :8080 -sTCP:LISTEN -t) 2>/dev/null || true
            sleep 2
            ;;
        2)
            read -p "Enter new port: " new_port
            export AURORA_HOLOGRAPHIC_PORT=$new_port
            print_info "Using port $new_port"
            ;;
        3)
            print_info "Deployment cancelled"
            exit 0
            ;;
    esac
fi

print_success "Port ready for Aurora Holographic Interface"

# Start L2 Integration Server in background
print_status "Starting L2 Integration Server..."

if [ -f "src/servers/l2_integration_server.py" ]; then
    python3 src/servers/l2_integration_server.py &
    L2_PID=$!
    sleep 3
    
    if ps -p $L2_PID > /dev/null; then
        print_success "L2 Integration Server started (PID: $L2_PID)"
    else
        print_warning "L2 Integration Server may have failed to start"
    fi
else
    print_warning "L2 Integration Server not found, continuing without it"
fi

# Deploy Holographic Interface
print_status "Deploying Aurora CloudBank Holographic Command Interface..."

echo ""
echo -e "${CYAN}🌟 PHASE 7: HOLOGRAPHIC COMMAND INTERFACE${NC}"
echo -e "${CYAN}===========================================${NC}"
echo ""

# Start the holographic interface orchestrator
export NODE_ENV=production
export AURORA_LOG_LEVEL=info

print_status "Launching holographic interface orchestrator..."

node src/orchestrators/holographic_interface_orchestrator.js &
ORCHESTRATOR_PID=$!

# Wait for startup
sleep 5

# Check if the orchestrator started successfully
if ps -p $ORCHESTRATOR_PID > /dev/null; then
    print_success "Holographic Interface Orchestrator started (PID: $ORCHESTRATOR_PID)"
    
    # Display access information
    echo ""
    echo -e "${GREEN}🎯 AURORA CLOUDBANK HOLOGRAPHIC INTERFACE DEPLOYED!${NC}"
    echo -e "${GREEN}====================================================${NC}"
    echo ""
    print_info "Interface URL: http://localhost:${AURORA_HOLOGRAPHIC_PORT:-8080}"
    print_info "Aurora Custom GPT: https://chatgpt.com/g/g-67ef3c2412cc81918ebf8ee9908e36a7-aurora-v2-4-stellar-accord"
    echo ""
    echo -e "${CYAN}🌟 Available Features:${NC}"
    echo "   • Beautiful holographic command interface"
    echo "   • Real-time agent constellation visualization"
    echo "   • Aurora Custom GPT bridge integration"
    echo "   • Interactive command execution"
    echo "   • Live system status monitoring"
    echo "   • WebSocket-based real-time updates"
    echo ""
    echo -e "${PURPLE}✨ Agent Constellation Status:${NC}"
    echo "   • ARCHY: Architecture & System Design"
    echo "   • OPPY: Optimization & Performance"
    echo "   • LIORA: Learning & Adaptation"
    echo "   • STARLING_AU: Stellar Communication"
    echo "   • RIVERTHREAD_808: Data Flow & Threading"
    echo ""
    echo -e "${YELLOW}🔗 Integration Endpoints:${NC}"
    echo "   • GET  /api/holographic/status"
    echo "   • POST /api/holographic/command"
    echo "   • GET  /api/holographic/agents"
    echo ""
    
    # Create process management file
    cat > aurora_holographic_processes.txt << EOF
# Aurora CloudBank Phase 7 Process Information
# Generated: $(date)

HOLOGRAPHIC_ORCHESTRATOR_PID=$ORCHESTRATOR_PID
L2_INTEGRATION_SERVER_PID=${L2_PID:-"not_started"}
HOLOGRAPHIC_PORT=${AURORA_HOLOGRAPHIC_PORT:-8080}
STATUS=running
DEPLOYED_AT=$(date -u)

# To stop all processes:
# kill $ORCHESTRATOR_PID
# kill ${L2_PID:-0}
EOF

    print_success "Process information saved to aurora_holographic_processes.txt"
    
    # Wait for user input or signal
    echo ""
    print_info "Press Ctrl+C to stop the holographic interface"
    echo ""
    
    # Trap signals for graceful shutdown
    trap 'print_status "Shutting down Aurora Holographic Interface..."; kill $ORCHESTRATOR_PID 2>/dev/null; kill ${L2_PID:-0} 2>/dev/null; print_success "Aurora CloudBank Phase 7 shutdown complete"; exit 0' INT TERM
    
    # Wait for processes
    wait $ORCHESTRATOR_PID
    
else
    print_error "Failed to start Holographic Interface Orchestrator"
    
    # Cleanup
    kill ${L2_PID:-0} 2>/dev/null || true
    exit 1
fi
