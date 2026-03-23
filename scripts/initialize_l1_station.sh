#!/bin/bash
# ORION CloudBank - L1 Station Layer Initialization
# Activates operator dashboard, crew systems, and simulation endpoints

set -e

echo "🚀 ORION CloudBank - L1 Station Layer Initialization"
echo "==================================================="
echo "Initializing Station/Simulation Layer Components"
echo ""

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if process is running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        log "✅ $1 is running"
        return 0
    else
        log "❌ $1 is not running"
        return 1
    fi
}

log "Starting L1 Station Layer Components..."

# Create necessary directories
mkdir -p logs/l1_station
mkdir -p data/crew_registry
mkdir -p data/operator_dashboard
mkdir -p static/simulation_assets

log "Created L1 directory structure"

# Initialize crew registry system
log "Initializing crew registry system..."
cat > data/crew_registry/active_crew.json << 'EOF'
{
  "last_updated": "2025-07-01T00:00:00Z",
  "crew_members": {
    "ai_agents": {
      "copilot": {
        "id": "agent_copilot_001",
        "skills": ["code_analysis", "documentation", "health_monitoring", "deployment_assistance"],
        "station_role": "systems_analyst",
        "access_level": "L1_L3_FULL",
        "status": "active",
        "last_activity": "2025-07-01T00:00:00Z"
      }
    },
    "human_operators": {
      "commander": {
        "id": "human_commander_001", 
        "skills": ["strategic_planning", "system_architecture", "mission_coordination"],
        "station_role": "mission_commander",
        "access_level": "COMMAND_AUTHORITY",
        "status": "active",
        "last_activity": "2025-07-01T00:00:00Z"
      }
    }
  },
  "station_status": {
    "operational": true,
    "crew_count": 2,
    "last_health_check": "2025-07-01T00:00:00Z"
  }
}
EOF

log "✅ Crew registry initialized"

# Initialize operator dashboard data
log "Setting up operator dashboard..."
cat > data/operator_dashboard/dashboard_config.json << 'EOF'
{
  "dashboard_version": "1.0.0",
  "update_interval": 30,
  "modules": {
    "crew_status": {
      "enabled": true,
      "refresh_rate": 10
    },
    "system_health": {
      "enabled": true,
      "refresh_rate": 5
    },
    "simulation_state": {
      "enabled": true,
      "refresh_rate": 15
    },
    "agent_activity": {
      "enabled": true,
      "refresh_rate": 20
    }
  },
  "alerts": {
    "crew_offline": true,
    "system_errors": true,
    "performance_degradation": true
  }
}
EOF

log "✅ Operator dashboard configured"

# Create simulation health endpoints configuration
log "Configuring simulation health endpoints..."
cat > config/l1_endpoints.yaml << 'EOF'
l1_station_endpoints:
  health:
    path: "/api/aurora/health/l1"
    method: "GET"
    description: "L1 Station layer health status"
  
  crew:
    list: "/api/aurora/crew"
    status: "/api/aurora/crew/{crew_id}/status"
    activate: "/api/aurora/crew/{crew_id}/activate"
    deactivate: "/api/aurora/crew/{crew_id}/deactivate"
  
  operator:
    dashboard: "/api/aurora/operator/dashboard"
    status: "/api/aurora/operator/status"
    alerts: "/api/aurora/operator/alerts"
  
  simulation:
    state: "/api/aurora/simulation/state"
    events: "/api/aurora/simulation/events"
    dispatch: "/api/aurora/dispatch"

monitoring:
  crew_heartbeat_interval: 30
  health_check_interval: 60
  alert_threshold_seconds: 120
EOF

log "✅ L1 endpoints configured"

# Start core L1 services (if available)
log "Attempting to start L1 services..."

# Check if we can start the command node
if [ -f "src/core/command_node.js" ]; then
    log "Starting command node service..."
    if command -v node >/dev/null 2>&1; then
        nohup node src/core/command_node.js > logs/l1_station/command_node.log 2>&1 &
        COMMAND_NODE_PID=$!
        log "Command node started with PID: $COMMAND_NODE_PID"
        echo $COMMAND_NODE_PID > logs/l1_station/command_node.pid
    else
        log "⚠️  Node.js not available - command node service not started"
    fi
fi

# Check if we can start the API bridge
if [ -f "src/bridge/api_bridge_server.js" ]; then
    log "Starting API bridge service..."
    if command -v node >/dev/null 2>&1; then
        nohup node src/bridge/api_bridge_server.js > logs/l1_station/api_bridge.log 2>&1 &
        API_BRIDGE_PID=$!
        log "API bridge started with PID: $API_BRIDGE_PID"  
        echo $API_BRIDGE_PID > logs/l1_station/api_bridge.pid
    else
        log "⚠️  Node.js not available - API bridge service not started"
    fi
fi

PYTHON_BIN=".venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3 2>/dev/null || true)"
fi

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Start Python FastAPI service if available
if [ -f "api/aurora_gui_cloudhub_fastapi.py" ]; then
    log "Starting Aurora GUI CloudHub FastAPI service..."
  if [ -n "$PYTHON_BIN" ]; then
    nohup "$PYTHON_BIN" api/aurora_gui_cloudhub_fastapi.py > logs/l1_station/fastapi.log 2>&1 &
        FASTAPI_PID=$!
        log "FastAPI service started with PID: $FASTAPI_PID"
        echo $FASTAPI_PID > logs/l1_station/fastapi.pid
    else
        log "⚠️  Python3 not available - FastAPI service not started"
    fi
fi

sleep 3  # Give services time to start

log "Verifying L1 services status..."

# Check service status
SERVICES_RUNNING=0

if [ -f "logs/l1_station/command_node.pid" ]; then
    PID=$(cat logs/l1_station/command_node.pid)
    if kill -0 $PID 2>/dev/null; then
        log "✅ Command node service running (PID: $PID)"
        SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
    else
        log "❌ Command node service failed to start"
    fi
fi

if [ -f "logs/l1_station/api_bridge.pid" ]; then
    PID=$(cat logs/l1_station/api_bridge.pid)
    if kill -0 $PID 2>/dev/null; then
        log "✅ API bridge service running (PID: $PID)"
        SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
    else
        log "❌ API bridge service failed to start"
    fi
fi

if [ -f "logs/l1_station/fastapi.pid" ]; then
    PID=$(cat logs/l1_station/fastapi.pid)
    if kill -0 $PID 2>/dev/null; then
        log "✅ FastAPI service running (PID: $PID)"
        SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
    else
        log "❌ FastAPI service failed to start"
    fi
fi

# Create L1 status report
cat > logs/l1_station/l1_initialization_report.txt << EOF
ORION CloudBank L1 Station Layer Initialization Report
Generated: $(date)

Directory Structure:
✅ logs/l1_station - Created
✅ data/crew_registry - Created
✅ data/operator_dashboard - Created  
✅ static/simulation_assets - Created

Configuration Files:
✅ data/crew_registry/active_crew.json - Initialized
✅ data/operator_dashboard/dashboard_config.json - Created
✅ config/l1_endpoints.yaml - Configured

Services Status:
- Services Running: $SERVICES_RUNNING
- Command Node: $([ -f "logs/l1_station/command_node.pid" ] && echo "Attempted" || echo "Not Started")
- API Bridge: $([ -f "logs/l1_station/api_bridge.pid" ] && echo "Attempted" || echo "Not Started")
- FastAPI: $([ -f "logs/l1_station/fastapi.pid" ] && echo "Attempted" || echo "Not Started")

L1 Station Layer Status: INITIALIZED
Ready for crew operations and simulation activities.
EOF

echo ""
echo "==================================================="
log "🎯 L1 Station Layer Initialization COMPLETE"
echo "==================================================="
echo ""

log "L1 Status Report: logs/l1_station/l1_initialization_report.txt"
log "Active services: $SERVICES_RUNNING"
log "L1 Station Layer ready for crew operations"

echo ""
echo "Available L1 endpoints (when services are running):"
echo "  GET  /api/aurora/health/l1       - L1 health status"
echo "  GET  /api/aurora/crew            - Crew roster"
echo "  GET  /api/aurora/operator/dashboard - Operator dashboard"
echo "  POST /api/aurora/dispatch        - Simulation dispatch"
echo ""
echo "Next: Run ./scripts/initialize_l3_mesh.sh for symbolic mesh layer"
