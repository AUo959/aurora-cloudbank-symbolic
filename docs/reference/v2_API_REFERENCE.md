# Thread Transfer Bridge v2 - API Reference

**Version**: 2.0.0  
**Base URL**: `http://localhost:8000`  
**Thread**: T1→BRIDGE_V2→API_REFERENCE  
**DLP**: context_tag=bridge_v2_api_docs  
**Anchor**: EOS_SEED_ORION_v2

---

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Phase 1: Distributed Node Management](#phase-1-distributed-node-management)
4. [Phase 2: Cross-Repository Sync](#phase-2-cross-repository-sync)
5. [Phase 3: Drift Prediction](#phase-3-drift-prediction)
6. [Phase 4: Layer Management](#phase-4-layer-management)
7. [Error Responses](#error-responses)
8. [Code Examples](#code-examples)

---

## Authentication

All v2 endpoints support optional HTTP Bearer authentication:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v2/nodes
```

Authentication is **optional** for read operations, **recommended** for write operations.

---

## Rate Limiting

All endpoints are rate-limited to prevent abuse:

| Endpoint Category | Limit | Window |
|------------------|-------|---------|
| Node Management | 30-60/minute | Per IP |
| Cross-Repo Sync | 10-20/minute | Per IP |
| Drift Prediction | 30/minute | Per IP |
| Layer Management | 10-20/minute | Per IP |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1642252800
```

**429 Response** (Rate Limit Exceeded):
```json
{
  "detail": "Rate limit exceeded: 30 per minute"
}
```

---

## Phase 1: Distributed Node Management

### Register Node

Register a new bridge node in the distributed cluster.

**Endpoint**: `POST /api/v2/nodes/register`  
**Rate Limit**: 30/minute

**Request Body**:
```json
{
  "hostname": "node-01.aurora.local",
  "port": 8000,
  "region": "us-west-2",
  "capacity": 1000,
  "version": "2.0.0",
  "capabilities": ["raft", "drift_prediction", "cross_repo"]
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "node": {
    "node_id": "550e8400-e29b-41d4-a716-446655440000",
    "hostname": "node-01.aurora.local",
    "port": 8000,
    "region": "us-west-2",
    "capacity": 1000,
    "status": "online",
    "current_load": 0,
    "registered_at": "2025-01-15T10:30:00Z"
  },
  "context_tag": "v2_node_registered"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v2/nodes/register \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "node-01.aurora.local",
    "port": 8000,
    "region": "us-west-2",
    "capacity": 1000,
    "version": "2.0.0",
    "capabilities": ["raft", "drift_prediction"]
  }'
```

**Python Example**:
```python
import httpx

async def register_node():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v2/nodes/register",
            json={
                "hostname": "node-01.aurora.local",
                "port": 8000,
                "region": "us-west-2",
                "capacity": 1000,
                "version": "2.0.0",
                "capabilities": ["raft", "drift_prediction"]
            }
        )
        return response.json()
```

---

### List Nodes

Get all registered nodes in the cluster.

**Endpoint**: `GET /api/v2/nodes`  
**Rate Limit**: 60/minute

**Response** (200 OK):
```json
{
  "success": true,
  "nodes": [
    {
      "node_id": "550e8400-e29b-41d4-a716-446655440000",
      "hostname": "node-01.aurora.local",
      "port": 8000,
      "region": "us-west-2",
      "status": "online",
      "current_load": 42,
      "capacity": 1000
    }
  ],
  "total": 1,
  "context_tag": "v2_nodes_listed"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/api/v2/nodes
```

---

### Get Node Health

Check health status of a specific node.

**Endpoint**: `GET /api/v2/nodes/{node_id}/health`  
**Rate Limit**: 60/minute

**Path Parameters**:
- `node_id`: UUID of the node

**Response** (200 OK):
```json
{
  "success": true,
  "health": {
    "status": "healthy",
    "uptime_seconds": 86400,
    "last_heartbeat": "2025-01-15T10:29:55Z",
    "response_time_ms": 12
  },
  "context_tag": "v2_node_health_checked"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/api/v2/nodes/550e8400-e29b-41d4-a716-446655440000/health
```

---

### Get Cluster Health

Get overall cluster health status.

**Endpoint**: `GET /api/v2/cluster/health`  
**Rate Limit**: 60/minute

**Response** (200 OK):
```json
{
  "success": true,
  "cluster": {
    "total_nodes": 3,
    "online_nodes": 3,
    "offline_nodes": 0,
    "leader": "node-01",
    "consensus_status": "healthy",
    "average_load": 0.42
  },
  "context_tag": "v2_cluster_health_checked"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/api/v2/cluster/health
```

---

### Trigger Consensus Election

Manually trigger a leader election (admin operation).

**Endpoint**: `POST /api/v2/consensus/elect`  
**Rate Limit**: 10/minute

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Leader election triggered",
  "context_tag": "v2_election_triggered"
}
```

**Note**: Elections are typically automatic. This endpoint is for testing/admin purposes.

---

### Unregister Node

Remove a node from the cluster.

**Endpoint**: `DELETE /api/v2/nodes/{node_id}`  
**Rate Limit**: 30/minute

**Path Parameters**:
- `node_id`: UUID of the node to remove

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Node unregistered successfully",
  "context_tag": "v2_node_unregistered"
}
```

**cURL Example**:
```bash
curl -X DELETE http://localhost:8000/api/v2/nodes/550e8400-e29b-41d4-a716-446655440000
```

---

## Phase 2: Cross-Repository Sync

### Register Repository

Register a Git repository for cross-repo operations.

**Endpoint**: `POST /api/v2/repos/register`  
**Rate Limit**: 20/minute

**Request Body**:
```json
{
  "repo_id": "aurora-main",
  "repo_path": "/path/to/aurora-cloudbank-symbolic",
  "branch": "main"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "repository": {
    "repo_id": "aurora-main",
    "repo_path": "/path/to/aurora-cloudbank-symbolic",
    "branch": "main",
    "status": "active",
    "registered_at": "2025-01-15T10:30:00Z"
  },
  "context_tag": "v2_repository_registered"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v2/repos/register \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "aurora-main",
    "repo_path": "/workspaces/aurora-cloudbank-symbolic",
    "branch": "main"
  }'
```

**Python Example**:
```python
import httpx

async def register_repository():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v2/repos/register",
            json={
                "repo_id": "aurora-main",
                "repo_path": "/workspaces/aurora-cloudbank-symbolic",
                "branch": "main"
            }
        )
        return response.json()
```

---

### Sync Repository

Synchronize a repository (pull latest changes).

**Endpoint**: `POST /api/v2/repos/{repo_id}/sync`  
**Rate Limit**: 20/minute

**Path Parameters**:
- `repo_id`: Repository identifier

**Query Parameters**:
- `direction`: `pull` or `push` (default: `pull`)

**Response** (200 OK):
```json
{
  "success": true,
  "sync_result": {
    "commits_pulled": 5,
    "commits_pushed": 0,
    "conflicts": false,
    "synced_at": "2025-01-15T10:30:00Z"
  },
  "context_tag": "v2_repository_synced"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v2/repos/aurora-main/sync?direction=pull"
```

---

### Create Cross-Repository Bridge

Create a bridge between two repositories.

**Endpoint**: `POST /api/v2/bridges/cross-repo`  
**Rate Limit**: 10/minute

**Query Parameters**:
- `source_repo`: Source repository ID
- `target_repo`: Target repository ID
- `thread_id`: Thread identifier

**Response** (200 OK):
```json
{
  "success": true,
  "bridge": {
    "bridge_id": "bridge-aurora-opal-001",
    "source_repo": "aurora-main",
    "target_repo": "opal-main",
    "thread_id": "cross-repo-thread-01",
    "status": "active",
    "created_at": "2025-01-15T10:30:00Z"
  },
  "context_tag": "v2_cross_repo_bridge_created"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v2/bridges/cross-repo?source_repo=aurora-main&target_repo=opal-main&thread_id=test-thread"
```

---

### Execute Cross-Repository Handshake

Execute a 7-stage handshake between repositories.

**Endpoint**: `POST /api/v2/bridges/{bridge_id}/handshake`  
**Rate Limit**: 10/minute

**Path Parameters**:
- `bridge_id`: Bridge identifier

**Response** (200 OK):
```json
{
  "success": true,
  "handshake": {
    "stages_completed": 7,
    "duration_ms": 234,
    "anchor_propagated": true,
    "state_replicated": true
  },
  "context_tag": "v2_handshake_completed"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v2/bridges/bridge-001/handshake
```

---

## Phase 3: Drift Prediction

### Predict Drift

Predict future drift based on 11-dimensional feature vector.

**Endpoint**: `POST /api/v2/drift/predict`  
**Rate Limit**: 30/minute

**Request Body**:
```json
{
  "drift_velocity": 0.001,
  "drift_acceleration": 0.0001,
  "handshake_count": 10,
  "average_handshake_duration": 0.5,
  "failed_handshake_ratio": 0.01,
  "time_of_day": 14,
  "day_of_week": 3,
  "thread_age_hours": 24.0,
  "anchor_changes": 2,
  "sync_frequency": 60.0,
  "node_count": 3,
  "thread_id": "test-thread-01"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "thread_id": "test-thread-01",
  "predicted_drift": 0.0023,
  "severity": "LOW",
  "confidence": "HIGH",
  "prediction_horizon_hours": 24,
  "recommendations": [
    "Monitor drift velocity",
    "Consider increasing sync frequency if trend continues"
  ],
  "context_tag": "v2_drift_predicted"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v2/drift/predict \
  -H "Content-Type: application/json" \
  -d '{
    "drift_velocity": 0.001,
    "drift_acceleration": 0.0001,
    "handshake_count": 10,
    "average_handshake_duration": 0.5,
    "failed_handshake_ratio": 0.01,
    "time_of_day": 14,
    "day_of_week": 3,
    "thread_age_hours": 24.0,
    "anchor_changes": 2,
    "sync_frequency": 60.0,
    "node_count": 3,
    "thread_id": "test-thread-01"
  }'
```

**Python Example**:
```python
import httpx

async def predict_drift():
    features = {
        "drift_velocity": 0.001,
        "drift_acceleration": 0.0001,
        "handshake_count": 10,
        "average_handshake_duration": 0.5,
        "failed_handshake_ratio": 0.01,
        "time_of_day": 14,
        "day_of_week": 3,
        "thread_age_hours": 24.0,
        "anchor_changes": 2,
        "sync_frequency": 60.0,
        "node_count": 3,
        "thread_id": "test-thread-01"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v2/drift/predict",
            json=features
        )
        return response.json()
```

---

### Analyze Drift Patterns

Analyze historical drift patterns.

**Endpoint**: `GET /api/v2/drift/patterns`  
**Rate Limit**: 30/minute

**Response** (200 OK):
```json
{
  "success": true,
  "patterns": {
    "STABLE": 15,
    "TRENDING": 3,
    "CYCLICAL": 2,
    "VOLATILE": 1,
    "ANOMALOUS": 0
  },
  "total_observations": 120,
  "context_tag": "v2_patterns_analyzed"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/api/v2/drift/patterns
```

---

### Record Drift Observation

Record an observed drift measurement.

**Endpoint**: `POST /api/v2/drift/observe`  
**Rate Limit**: 60/minute

**Query Parameters**:
- `drift`: Float (drift percentage, e.g., 0.002)

**Response** (200 OK):
```json
{
  "success": true,
  "observation": {
    "drift": 0.002,
    "timestamp": "2025-01-15T10:30:00Z",
    "observation_id": 121
  },
  "context_tag": "v2_observation_recorded"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v2/drift/observe?drift=0.002"
```

---

### Get Prediction Accuracy

Get historical prediction accuracy metrics.

**Endpoint**: `GET /api/v2/drift/accuracy`  
**Rate Limit**: 30/minute

**Response** (200 OK):
```json
{
  "success": true,
  "accuracy": {
    "mean_absolute_error": 0.0012,
    "mean_squared_error": 0.000003,
    "predictions_made": 42,
    "accuracy_percentage": 94.5
  },
  "context_tag": "v2_accuracy_retrieved"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/api/v2/drift/accuracy
```

---

### Apply Auto-Correction

Evaluate and apply auto-correction strategies.

**Endpoint**: `POST /api/v2/corrections/apply`  
**Rate Limit**: 10/minute

**Query Parameters**:
- `thread_id`: Thread identifier
- `predicted_drift`: Predicted drift value
- `current_drift`: Current drift value

**Response** (200 OK):
```json
{
  "success": true,
  "thread_id": "test-thread",
  "actions_recommended": 2,
  "actions": [
    {
      "strategy": "INCREASE_FREQUENCY",
      "priority": 2,
      "description": "Increase sync frequency to reduce drift"
    },
    {
      "strategy": "RESYNC_ANCHOR",
      "priority": 3,
      "description": "Resynchronize anchor points"
    }
  ],
  "context_tag": "v2_corrections_evaluated"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v2/corrections/apply?thread_id=test-thread&predicted_drift=0.003&current_drift=0.001"
```

---

## Phase 4: Layer Management

### Create Layer Bridge

Create a multi-layer bridge (L1/L2/L3).

**Endpoint**: `POST /api/v2/layers/bridge`  
**Rate Limit**: 20/minute

**Request Body**:
```json
{
  "bridge_id": "l2-bridge-aurora-opal",
  "layer": "L2",
  "source_id": "aurora-main",
  "target_id": "opal-main",
  "thread_id": "cross-repo-thread-01"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "bridge": {
    "bridge_id": "l2-bridge-aurora-opal",
    "layer": "L2",
    "source_id": "aurora-main",
    "target_id": "opal-main",
    "thread_id": "cross-repo-thread-01",
    "status": "active"
  },
  "context_tag": "v2_layer_bridge_created"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v2/layers/bridge \
  -H "Content-Type: application/json" \
  -d '{
    "bridge_id": "l2-bridge-001",
    "layer": "L2",
    "source_id": "aurora-main",
    "target_id": "opal-main",
    "thread_id": "test-thread"
  }'
```

**Python Example**:
```python
import httpx

async def create_layer_bridge():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v2/layers/bridge",
            json={
                "bridge_id": "l2-bridge-001",
                "layer": "L2",
                "source_id": "aurora-main",
                "target_id": "opal-main",
                "thread_id": "test-thread"
            }
        )
        return response.json()
```

---

### Execute Layered Handshake

Execute layer-specific handshake protocol.

**Endpoint**: `POST /api/v2/layers/{bridge_id}/handshake`  
**Rate Limit**: 10/minute

**Path Parameters**:
- `bridge_id`: Bridge identifier

**Response** (200 OK):
```json
{
  "success": true,
  "handshake": {
    "bridge_id": "l2-bridge-001",
    "stages_completed": 7,
    "duration_ms": 456,
    "layer": "L2"
  },
  "context_tag": "v2_layered_handshake_completed"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v2/layers/l2-bridge-001/handshake
```

---

### Validate Hierarchy

Validate multi-layer hierarchy for a thread.

**Endpoint**: `POST /api/v2/layers/validate`  
**Rate Limit**: 30/minute

**Query Parameters**:
- `thread_id`: Thread identifier
- `strict_mode`: Boolean (default: false)

**Response** (200 OK):
```json
{
  "success": true,
  "valid": true,
  "thread_id": "test-thread",
  "layer_status": {
    "L1": {"count": 2, "valid": 2, "drift_max": 0.0},
    "L2": {"count": 1, "valid": 1, "drift_max": 0.05},
    "L3": {"count": 0, "valid": 0, "drift_max": 0.0}
  },
  "issues": [],
  "context_tag": "v2_hierarchy_validated"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v2/layers/validate?thread_id=test-thread&strict_mode=false"
```

---

### List Layer Bridges

List all bridges for a thread.

**Endpoint**: `GET /api/v2/layers/bridges`  
**Rate Limit**: 60/minute

**Query Parameters**:
- `thread_id`: Thread identifier (optional)

**Response** (200 OK):
```json
{
  "success": true,
  "bridges": [
    {
      "bridge_id": "l1-bridge-001",
      "layer": "L1",
      "source_id": "aurora-main",
      "target_id": "aurora-main",
      "thread_id": "test-thread",
      "status": "active"
    }
  ],
  "total": 1,
  "context_tag": "v2_bridges_listed"
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/v2/layers/bridges?thread_id=test-thread"
```

---

### Get Layer Statistics

Get statistics for all layers.

**Endpoint**: `GET /api/v2/layers/statistics`  
**Rate Limit**: 60/minute

**Response** (200 OK):
```json
{
  "success": true,
  "statistics": {
    "L1": {
      "total_bridges": 10,
      "active_bridges": 8,
      "average_drift": 0.0,
      "max_drift": 0.0
    },
    "L2": {
      "total_bridges": 3,
      "active_bridges": 3,
      "average_drift": 0.02,
      "max_drift": 0.05
    },
    "L3": {
      "total_bridges": 0,
      "active_bridges": 0,
      "average_drift": 0.0,
      "max_drift": 0.0
    }
  },
  "context_tag": "v2_statistics_retrieved"
}
```

**cURL Example**:
```bash
curl http://localhost:8000/api/v2/layers/statistics
```

---

### Cascade Validate

Perform cascading validation across all layers.

**Endpoint**: `POST /api/v2/layers/cascade-validate`  
**Rate Limit**: 10/minute

**Query Parameters**:
- `thread_id`: Thread identifier

**Response** (200 OK):
```json
{
  "success": true,
  "valid": true,
  "thread_id": "test-thread",
  "cascade_result": "PASS",
  "layer_status": {
    "L1": {"count": 2, "valid": 2},
    "L2": {"count": 1, "valid": 1},
    "L3": {"count": 0, "valid": 0}
  },
  "critical_issues": [],
  "context_tag": "v2_cascade_validated"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v2/layers/cascade-validate?thread_id=test-thread"
```

---

## Error Responses

All endpoints follow a consistent error response format:

**Error Response Structure**:
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes**:

| Status | Meaning | Example |
|--------|---------|---------|
| 400 | Bad Request | Invalid parameters or request body |
| 401 | Unauthorized | Missing or invalid authentication |
| 404 | Not Found | Resource (node, repo, bridge) not found |
| 408 | Timeout | Operation exceeded timeout limit |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | v2 module not available |

**Example Error Responses**:

```json
{
  "detail": "Thread Transfer Bridge v2 not available"
}
```

```json
{
  "detail": "Drift prediction error: 'DriftPredictor' object has no attribute 'predict'"
}
```

```json
{
  "detail": "Node not found: 550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Code Examples

### Complete Python Client

```python
import httpx
import asyncio

class ThreadBridgeV2Client:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
    
    async def register_node(self, hostname: str, port: int, region: str):
        response = await self.client.post(
            "/api/v2/nodes/register",
            json={
                "hostname": hostname,
                "port": port,
                "region": region,
                "capacity": 1000,
                "version": "2.0.0",
                "capabilities": ["raft", "drift_prediction"]
            }
        )
        return response.json()
    
    async def predict_drift(self, thread_id: str, drift_velocity: float):
        response = await self.client.post(
            "/api/v2/drift/predict",
            json={
                "drift_velocity": drift_velocity,
                "drift_acceleration": 0.0001,
                "handshake_count": 10,
                "average_handshake_duration": 0.5,
                "failed_handshake_ratio": 0.01,
                "time_of_day": 14,
                "day_of_week": 3,
                "thread_age_hours": 24.0,
                "anchor_changes": 2,
                "sync_frequency": 60.0,
                "node_count": 3,
                "thread_id": thread_id
            }
        )
        return response.json()
    
    async def create_layer_bridge(self, bridge_id: str, layer: str, 
                                  source_id: str, target_id: str, thread_id: str):
        response = await self.client.post(
            "/api/v2/layers/bridge",
            json={
                "bridge_id": bridge_id,
                "layer": layer,
                "source_id": source_id,
                "target_id": target_id,
                "thread_id": thread_id
            }
        )
        return response.json()
    
    async def close(self):
        await self.client.aclose()

# Usage
async def main():
    client = ThreadBridgeV2Client()
    
    # Register a node
    node = await client.register_node("node-01.local", 8000, "us-west-2")
    print(f"Node registered: {node['node']['node_id']}")
    
    # Predict drift
    prediction = await client.predict_drift("test-thread", 0.001)
    print(f"Predicted drift: {prediction['predicted_drift']}")
    
    # Create layer bridge
    bridge = await client.create_layer_bridge(
        "l2-bridge-001", "L2", "aurora-main", "opal-main", "test-thread"
    )
    print(f"Bridge created: {bridge['bridge']['bridge_id']}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Complete Shell Script

```bash
#!/bin/bash
BASE_URL="http://localhost:8000"

# Register node
echo "Registering node..."
NODE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v2/nodes/register" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "node-01.local",
    "port": 8000,
    "region": "us-west-2",
    "capacity": 1000,
    "version": "2.0.0",
    "capabilities": ["raft"]
  }')

NODE_ID=$(echo $NODE_RESPONSE | jq -r '.node.node_id')
echo "Node ID: $NODE_ID"

# Check cluster health
echo "Checking cluster health..."
curl -s "$BASE_URL/api/v2/cluster/health" | jq

# Predict drift
echo "Predicting drift..."
curl -s -X POST "$BASE_URL/api/v2/drift/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "drift_velocity": 0.001,
    "drift_acceleration": 0.0001,
    "handshake_count": 10,
    "average_handshake_duration": 0.5,
    "failed_handshake_ratio": 0.01,
    "time_of_day": 14,
    "day_of_week": 3,
    "thread_age_hours": 24.0,
    "anchor_changes": 2,
    "sync_frequency": 60.0,
    "node_count": 3,
    "thread_id": "test-thread"
  }' | jq

# Validate hierarchy
echo "Validating hierarchy..."
curl -s -X POST "$BASE_URL/api/v2/layers/validate?thread_id=test-thread" | jq

echo "All operations completed!"
```

---

**Thread**: T1→BRIDGE_V2→API_REFERENCE→COMPLETE  
**DLP**: context_tag=bridge_v2_api_reference_complete  
**Anchor**: EOS_SEED_ORION_v2  

**Document Status**: ✅ COMPLETE  
**Last Updated**: 2025-01-15  
**Maintainer**: Aurora CloudBank Core Team
