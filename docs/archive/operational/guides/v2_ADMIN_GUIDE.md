# Thread Transfer Bridge v2 - Administration Guide

**Version**: 2.0.0  
**Thread**: T1→BRIDGE_V2→ADMIN  
**DLP**: context_tag=bridge_v2_admin_guide  
**Anchor**: EOS_SEED_ORION_v2  
**Status**: PRODUCTION READY ✅

---

## Table of Contents

1. [Deployment](#deployment)
2. [Configuration](#configuration)
3. [Monitoring](#monitoring)
4. [Performance Tuning](#performance-tuning)
5. [Troubleshooting](#troubleshooting)
6. [Backup and Recovery](#backup-and-recovery)
7. [Security](#security)
8. [Maintenance](#maintenance)

---

## Deployment

### Single-Node Deployment

**Use Case**: Development, small-scale production

**Steps**:

1. **Ensure dependencies installed**:
```bash
cd /workspaces/aurora-cloudbank-symbolic
pip install -r requirements.txt
```

2. **Start the server**:
```bash
python aurora_api.py
```

3. **Verify v2 available**:
```bash
curl http://localhost:8000/api/v2/cluster/health
```

**Expected Response**:
```json
{
  "success": true,
  "cluster": {
    "total_nodes": 0,
    "online_nodes": 0,
    "leader": null,
    "consensus_status": "not_initialized"
  }
}
```

### Multi-Node Cluster Deployment

**Use Case**: High-availability production

**Architecture**:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Node 1    │────▶│   Node 2    │────▶│   Node 3    │
│  (Leader)   │◀────│  (Follower) │◀────│  (Follower) │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                    Load Balancer
```

**Steps**:

1. **Deploy on Node 1** (Primary):
```bash
# Start API server
python aurora_api.py --host 0.0.0.0 --port 8000

# Register as first node
curl -X POST http://localhost:8000/api/v2/nodes/register \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "node-01.aurora.local",
    "port": 8000,
    "region": "us-west-1",
    "capacity": 1000,
    "version": "2.0.0",
    "capabilities": ["raft", "drift_prediction", "cross_repo"]
  }'
```

2. **Deploy on Node 2** (Replica):
```bash
# Start API server
python aurora_api.py --host 0.0.0.0 --port 8000

# Register as second node
curl -X POST http://node-01.aurora.local:8000/api/v2/nodes/register \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "node-02.aurora.local",
    "port": 8000,
    "region": "us-west-2",
    "capacity": 1000,
    "version": "2.0.0",
    "capabilities": ["raft", "drift_prediction"]
  }'
```

3. **Deploy on Node 3** (Replica):
```bash
# Same as Node 2, adjust hostname
curl -X POST http://node-01.aurora.local:8000/api/v2/nodes/register \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "node-03.aurora.local",
    "port": 8000,
    "region": "us-east-1",
    "capacity": 1000,
    "version": "2.0.0",
    "capabilities": ["raft"]
  }'
```

4. **Verify cluster health**:
```bash
curl http://node-01.aurora.local:8000/api/v2/cluster/health
```

**Expected**:
```json
{
  "cluster": {
    "total_nodes": 3,
    "online_nodes": 3,
    "leader": "node-01",
    "consensus_status": "healthy"
  }
}
```

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "aurora_api.py"]
```

**Docker Compose** (3-node cluster):
```yaml
version: '3.8'

services:
  node1:
    build: .
    ports:
      - "8001:8000"
    environment:
      - NODE_HOSTNAME=node-01
      - NODE_PORT=8000
      - NODE_REGION=us-west-1
    volumes:
      - ./data/node1:/app/data

  node2:
    build: .
    ports:
      - "8002:8000"
    environment:
      - NODE_HOSTNAME=node-02
      - NODE_PORT=8000
      - NODE_REGION=us-west-2
    volumes:
      - ./data/node2:/app/data

  node3:
    build: .
    ports:
      - "8003:8000"
    environment:
      - NODE_HOSTNAME=node-03
      - NODE_PORT=8000
      - NODE_REGION=us-east-1
    volumes:
      - ./data/node3:/app/data
```

**Start cluster**:
```bash
docker-compose up -d
```

---

## Configuration

### Environment Variables

```bash
# Server Configuration
export AURORA_HOST="0.0.0.0"
export AURORA_PORT="8000"
export AURORA_WORKERS="4"

# v2 Configuration
export V2_ENABLE_DISTRIBUTED="true"
export V2_ENABLE_DRIFT_PREDICTION="true"
export V2_ENABLE_CROSS_REPO="true"

# Raft Consensus
export RAFT_ELECTION_TIMEOUT_MS="150"
export RAFT_HEARTBEAT_INTERVAL_MS="50"
export RAFT_LOG_MAX_SIZE="10000"

# Drift Prediction
export DRIFT_PREDICTION_HORIZON_HOURS="24"
export DRIFT_THRESHOLD_LOW="0.001"
export DRIFT_THRESHOLD_HIGH="0.1"
export DRIFT_THRESHOLD_CRITICAL="0.5"

# Performance
export MAX_CONCURRENT_TRANSFERS="100"
export TRANSFER_TIMEOUT_SECONDS="30"
export HEALTHCHECK_INTERVAL_SECONDS="30"
```

### Configuration File

Create `config/bridge_v2.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  
distributed:
  enabled: true
  node:
    hostname: "node-01.aurora.local"
    region: "us-west-1"
    capacity: 1000
  consensus:
    election_timeout_ms: 150
    heartbeat_interval_ms: 50
    log_max_size: 10000

drift_prediction:
  enabled: true
  horizon_hours: 24
  thresholds:
    low: 0.001
    medium: 0.01
    high: 0.1
    critical: 0.5
  model:
    type: "lstm"  # or "statistical"
    hidden_size: 64
    num_layers: 2

cross_repo:
  enabled: true
  repositories:
    - repo_id: "aurora-main"
      path: "/workspaces/aurora-cloudbank-symbolic"
      branch: "main"
  sync_interval_minutes: 60

performance:
  max_concurrent_transfers: 100
  transfer_timeout_seconds: 30
  healthcheck_interval_seconds: 30
  rate_limits:
    node_management: "30/minute"
    cross_repo: "20/minute"
    drift_prediction: "30/minute"
    layer_management: "20/minute"

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  format: "json"
  file: "/var/log/aurora/bridge_v2.log"
  rotate_size_mb: 100
  rotate_count: 10
```

**Load configuration**:
```python
import yaml

with open("config/bridge_v2.yaml") as f:
    config = yaml.safe_load(f)
```

---

## Monitoring

### Health Checks

**Cluster Health**:
```bash
# Overall cluster status
curl http://localhost:8000/api/v2/cluster/health

# Individual node health
curl http://localhost:8000/api/v2/nodes/{node_id}/health
```

**Key Metrics**:
- `total_nodes`: Total registered nodes
- `online_nodes`: Nodes responding to heartbeats
- `leader`: Current Raft leader
- `consensus_status`: "healthy", "no_leader", "split_brain"
- `average_load`: Average thread count across nodes

### Prometheus Metrics

**Expose metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Counters
transfers_total = Counter('bridge_transfers_total', 'Total thread transfers')
transfers_failed = Counter('bridge_transfers_failed', 'Failed transfers')

# Histograms
transfer_duration = Histogram('bridge_transfer_duration_seconds', 'Transfer duration')
drift_prediction_duration = Histogram('drift_prediction_duration_seconds', 'Prediction duration')

# Gauges
active_nodes = Gauge('bridge_active_nodes', 'Active nodes in cluster')
current_drift = Gauge('bridge_current_drift', 'Current drift measurement')

# Start metrics server
start_http_server(9090)
```

**Prometheus scrape config**:
```yaml
scrape_configs:
  - job_name: 'aurora_bridge_v2'
    static_configs:
      - targets: ['localhost:9090']
```

### Grafana Dashboards

**Key Dashboard Panels**:

1. **Cluster Overview**:
   - Total nodes (gauge)
   - Online/offline nodes (pie chart)
   - Leader status (stat)

2. **Performance**:
   - Transfer rate (graph)
   - Transfer latency (heatmap)
   - Error rate (graph)

3. **Drift Monitoring**:
   - Current drift (gauge)
   - Predicted drift (graph)
   - Drift severity distribution (bar chart)

4. **Consensus**:
   - Leader elections (counter)
   - Log replication lag (graph)
   - Consensus errors (alert)

### Log Monitoring

**Log Aggregation** (ELK Stack):

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "component": "raft_consensus",
  "message": "Leader elected",
  "context": {
    "leader_id": "node-01",
    "term": 5,
    "votes_received": 2
  }
}
```

**Alert Rules**:

```yaml
# Alertmanager rules
groups:
  - name: bridge_v2
    rules:
      - alert: ClusterNoLeader
        expr: bridge_leader_present == 0
        for: 1m
        annotations:
          summary: "No Raft leader elected"
          
      - alert: HighDriftDetected
        expr: bridge_current_drift > 0.1
        for: 5m
        annotations:
          summary: "High drift detected: {{ $value }}"
          
      - alert: NodeOffline
        expr: bridge_active_nodes < 2
        for: 2m
        annotations:
          summary: "Cluster degraded: {{ $value }} nodes"
```

---

## Performance Tuning

### Raft Consensus Tuning

**Election Timeout**:
- **Default**: 150ms
- **Low latency network**: 100ms
- **High latency network**: 300ms

```yaml
consensus:
  election_timeout_ms: 150  # Adjust based on network
```

**Heartbeat Interval**:
- **Rule**: Should be < election_timeout / 3
- **Default**: 50ms
- **Formula**: `election_timeout_ms / 3`

```yaml
consensus:
  heartbeat_interval_ms: 50
```

### Drift Prediction Tuning

**Model Selection**:
```yaml
drift_prediction:
  model:
    type: "lstm"  # Better accuracy, requires PyTorch
    # OR
    type: "statistical"  # Faster, no ML dependencies
```

**Prediction Horizon**:
- **Short-term** (1-6h): Higher accuracy, faster response
- **Long-term** (24-48h): Lower accuracy, better planning

```yaml
drift_prediction:
  horizon_hours: 24  # Balance accuracy and planning
```

### Load Balancing Tuning

**Capacity Planning**:
```python
# Set based on:
# - CPU cores (100-200 per core)
# - Memory (500-1000 per GB)
# - Network bandwidth
capacity = 1000  # Threads per node
```

**Selection Algorithm Weights**:
```yaml
load_balancing:
  weight_capacity: 0.4    # 40% capacity-based
  weight_latency: 0.3     # 30% latency-based
  weight_regional: 0.2    # 20% region-based
  weight_random: 0.1      # 10% randomization
```

### Database Tuning

**Connection Pooling**:
```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/aurora",
    pool_size=20,           # Max connections
    max_overflow=10,        # Extra connections when needed
    pool_pre_ping=True,     # Verify connections
    pool_recycle=3600       # Recycle after 1h
)
```

---

## Troubleshooting

### Issue: No Leader Elected

**Symptoms**:
```json
{
  "consensus_status": "no_leader",
  "leader": null
}
```

**Diagnosis**:
```bash
# Check node connectivity
curl http://node-01:8000/api/v2/nodes
curl http://node-02:8000/api/v2/nodes
curl http://node-03:8000/api/v2/nodes

# Check logs
grep "election" /var/log/aurora/bridge_v2.log
```

**Solutions**:
1. **Network issues**: Verify nodes can reach each other
2. **Split brain**: Restart minority partition nodes
3. **Timeout too short**: Increase `election_timeout_ms`

### Issue: High Drift Detected

**Symptoms**:
```json
{
  "predicted_drift": 0.15,
  "severity": "HIGH"
}
```

**Diagnosis**:
```bash
# Check drift patterns
curl http://localhost:8000/api/v2/drift/patterns

# Check prediction accuracy
curl http://localhost:8000/api/v2/drift/accuracy
```

**Solutions**:
1. **Increase sync frequency**: More frequent synchronization
2. **Apply auto-correction**: Trigger correction actions
3. **Resync anchors**: Force anchor re-synchronization

```bash
# Apply corrections
curl -X POST "http://localhost:8000/api/v2/corrections/apply?thread_id=test&predicted_drift=0.15&current_drift=0.05"
```

### Issue: Node Unresponsive

**Symptoms**:
```json
{
  "online_nodes": 2,
  "offline_nodes": 1
}
```

**Diagnosis**:
```bash
# Check specific node
curl http://node-03:8000/api/v2/nodes/{node_id}/health

# Check heartbeat logs
grep "heartbeat" /var/log/aurora/bridge_v2.log | grep node-03
```

**Solutions**:
1. **Temporary failure**: Wait for automatic recovery (3 failed heartbeats)
2. **Permanent failure**: Unregister node
```bash
curl -X DELETE http://localhost:8000/api/v2/nodes/{node_id}
```
3. **Replace node**: Register new node with same ID

### Issue: High Latency

**Symptoms**:
- Transfer times > 100ms
- Consensus latency > 50ms

**Diagnosis**:
```bash
# Measure endpoint latency
time curl http://localhost:8000/api/v2/drift/predict -X POST -d '{...}'

# Check resource usage
top -p $(pgrep -f aurora_api)
```

**Solutions**:
1. **CPU bound**: Add more workers
```bash
export AURORA_WORKERS="8"  # Increase from 4
```
2. **I/O bound**: Enable async I/O, add read replicas
3. **Network bound**: Co-locate nodes, increase bandwidth

---

## Backup and Recovery

### What to Backup

1. **Raft Log**: `/var/lib/aurora/raft/log.db`
2. **Configuration**: `config/bridge_v2.yaml`
3. **Anchor History**: `/var/lib/aurora/anchors/`
4. **Drift History**: `/var/lib/aurora/drift/observations.db`

### Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/backup/aurora/$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

# Backup Raft log
cp -r /var/lib/aurora/raft "$BACKUP_DIR/"

# Backup configuration
cp config/bridge_v2.yaml "$BACKUP_DIR/"

# Backup anchors
cp -r /var/lib/aurora/anchors "$BACKUP_DIR/"

# Backup drift data
cp /var/lib/aurora/drift/observations.db "$BACKUP_DIR/"

# Create manifest
cat > "$BACKUP_DIR/manifest.json" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "version": "2.0.0",
  "nodes_backed_up": 3,
  "size_bytes": $(du -sb "$BACKUP_DIR" | cut -f1)
}
EOF

echo "Backup completed: $BACKUP_DIR"
```

### Recovery Procedure

1. **Stop services**:
```bash
pkill -f aurora_api
```

2. **Restore files**:
```bash
RESTORE_FROM="/backup/aurora/20250115_103000"

cp -r "$RESTORE_FROM/raft" /var/lib/aurora/
cp "$RESTORE_FROM/bridge_v2.yaml" config/
cp -r "$RESTORE_FROM/anchors" /var/lib/aurora/
cp "$RESTORE_FROM/observations.db" /var/lib/aurora/drift/
```

3. **Restart services**:
```bash
python aurora_api.py
```

4. **Verify recovery**:
```bash
curl http://localhost:8000/api/v2/cluster/health
```

---

## Security

### Authentication

**Enable Bearer Token Authentication**:
```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/v2/nodes/register")
async def register_node(credentials: HTTPAuthorizationCredentials = Security(security)):
    # Verify token
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
```

### TLS/SSL

**Enable HTTPS**:
```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Run with SSL
uvicorn aurora_api:app --host 0.0.0.0 --port 8000 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### Firewall Rules

```bash
# Allow inbound v2 API
sudo ufw allow 8000/tcp

# Allow node-to-node communication
sudo ufw allow from 10.0.0.0/8 to any port 8000

# Block external access to metrics
sudo ufw deny 9090/tcp
```

---

## Maintenance

### Regular Tasks

**Daily**:
- Check cluster health
- Review error logs
- Monitor drift trends

**Weekly**:
- Backup Raft log and configuration
- Review performance metrics
- Update drift prediction model

**Monthly**:
- Rotate logs
- Vacuum databases
- Update dependencies
- Security patches

### Maintenance Windows

**Plan downtime**:
```bash
# 1. Stop accepting new transfers
curl -X POST http://localhost:8000/admin/drain

# 2. Wait for active transfers to complete
watch 'curl -s http://localhost:8000/api/v2/cluster/health | jq .cluster.average_load'

# 3. Stop service
pkill -f aurora_api

# 4. Perform maintenance
# ...

# 5. Restart service
python aurora_api.py

# 6. Verify health
curl http://localhost:8000/api/v2/cluster/health
```

---

**Thread**: T1→BRIDGE_V2→ADMIN→COMPLETE  
**DLP**: context_tag=bridge_v2_admin_guide_complete  
**Anchor**: EOS_SEED_ORION_v2  

**Document Status**: ✅ COMPLETE  
**Last Updated**: 2025-01-15  
**Maintainer**: Aurora CloudBank Core Team
