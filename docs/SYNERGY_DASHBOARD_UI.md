# Aurora Component Synergy Dashboard UI

## Overview

The Aurora Component Synergy Dashboard UI is a comprehensive real-time monitoring and visualization system for R-2 agent component interactions, health metrics, and integration opportunities. It provides an interactive web interface for monitoring component topology, interaction patterns, and optimization opportunities.

## Features

### 1. Component Monitoring
- **Real-time Health Metrics**: Track health scores (0-100%) for all registered components
- **Status Indicators**: Active, degraded, and offline status with visual badges
- **Resource Usage**: Monitor CPU and memory usage per component
- **Uptime Tracking**: View component uptime and last heartbeat timestamps

### 2. Component Topology Visualization
- **Network Graph**: Interactive SVG-based topology visualization
- **Component Relationships**: Visual representation of component interactions
- **Cluster Groups**: Components grouped by category (memory, privacy, audit, etc.)
- **Health-based Coloring**: Node colors reflect component health status

### 3. Interaction Flow Analysis
- **Communication Patterns**: Track source → target interactions
- **Frequency Metrics**: Monitor interaction frequency per day
- **Latency Monitoring**: Track average latency for each interaction
- **Success Rates**: Monitor interaction success rates

### 4. Synergy Score Metrics
- **Component Pair Analysis**: Calculate synergy scores for component pairs
- **Trend Indicators**: Track whether synergy is increasing, stable, or decreasing
- **Integration Levels**: Classify as full, partial, or no integration
- **Optimization Opportunities**: Identify specific improvements for better integration

### 5. Real-time Updates
- **WebSocket Connection**: Live updates via WebSocket protocol
- **Auto-refresh**: Automatic data refresh every 5 seconds
- **Event-driven Updates**: Push-based component status changes

### 6. User Interface Features
- **Filtering**: Filter components by status (all, active, degraded, offline)
- **Search**: Full-text search across component names and IDs
- **Drill-down Views**: Click any component for detailed information
- **Responsive Design**: Mobile and tablet-friendly layout

## Architecture

### Backend (FastAPI)

**API Module**: `src/synergy/dashboard_api.py`

Endpoints:
- `GET /api/synergy/components` - List all components with status
- `GET /api/synergy/topology` - Get complete topology with nodes/edges/clusters
- `GET /api/synergy/interactions` - Get interaction flows with metrics
- `GET /api/synergy/synergy-scores` - Get synergy scores and opportunities
- `GET /api/synergy/metrics` - Get aggregated dashboard metrics
- `GET /api/synergy/health` - Health check endpoint

### Frontend (Vanilla JavaScript + HTML/CSS)

**Dashboard Script**: `static/js/synergy-dashboard.js`
**Dashboard Page**: `static/synergy-dashboard.html`

## Component Registry

The dashboard monitors these R-2 agent components:

| Component | Category | Description |
|-----------|----------|-------------|
| AuMemManager | memory | Quantum memory management with 56K capacity |
| Data Guardian | privacy | PII detection and redaction |
| Insight Ledger | audit | Cryptographic audit trail |
| Quantum Simulator | compute | Quantum scenario simulation |
| DLP Tracker | governance | Data lineage and provenance tracking |
| ChatGPT Agent Mode | ai_integration | Agent tool registry and session management |
| Symbolic Engine | computation | Chain notation and T1/SRB anchor processing |
| Thread Transfer Bridge | continuity | Cross-thread state continuity |

## Usage

### Accessing the Dashboard

1. **Start Aurora API Server**:
   ```bash
   cd /home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic
   python api/aurora_api.py
   ```

2. **Open Dashboard**:
   Navigate to `http://localhost:8000/static/synergy-dashboard.html`

### API Usage Examples

**Get All Components**:
```bash
curl http://localhost:8000/api/synergy/components
```

**Get Active Components Only**:
```bash
curl http://localhost:8000/api/synergy/components?status_filter=active
```

**Get Component Topology**:
```bash
curl http://localhost:8000/api/synergy/topology
```

## Testing

```bash
# Run all synergy dashboard tests
pytest tests/test_synergy_dashboard.py -v
```

## DLP Tracking

All dashboard operations include DLP tracking with appropriate context tags:
- `synergy_dashboard_components`
- `synergy_dashboard_topology`
- `synergy_dashboard_interactions`
- `synergy_dashboard_synergy_scores`
- `synergy_dashboard_metrics`

## Security

- WebSocket connections require token authentication
- Content Security Policy enforced on dashboard page
- Input validation via Pydantic models
- DLP tracking for audit trail
