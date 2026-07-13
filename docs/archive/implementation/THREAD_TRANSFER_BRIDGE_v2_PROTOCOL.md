# Thread Transfer Bridge v2 - Protocol Specification

**Version**: 2.0.0  
**Thread**: T1→BRIDGE_V2→PROTOCOL  
**DLP**: context_tag=bridge_v2_protocol_spec  
**Anchor**: EOS_SEED_ORION_v2  
**Status**: PRODUCTION READY ✅

---

## Table of Contents

1. [Overview](#overview)
2. [Core Protocol](#core-protocol)
3. [Phase 1: Distributed Bridge Nodes](#phase-1-distributed-bridge-nodes)
4. [Phase 2: Cross-Repository Continuity](#phase-2-cross-repository-continuity)
5. [Phase 3: ML Drift Prediction](#phase-3-ml-drift-prediction)
6. [Phase 4: Multi-Layer Hierarchies](#phase-4-multi-layer-hierarchies)
7. [Error Handling](#error-handling)
8. [Security Protocols](#security-protocols)
9. [Performance Specifications](#performance-specifications)

---

## Overview

Thread Transfer Bridge v2 is a quantum-symbolic state continuity protocol that extends v1 with distributed consensus, cross-repository synchronization, machine learning drift prediction, and multi-layer hierarchical validation.

### Key Enhancements Over v1

| Feature | v1 | v2 |
|---------|----|----|
| **Deployment** | Single instance | Distributed multi-node cluster |
| **Scope** | Single repository | Cross-repository with anchor propagation |
| **Drift Management** | Reactive detection | Predictive forecasting with ML |
| **Validation** | Single layer | Multi-layer hierarchy (L1/L2/L3) |
| **Consensus** | N/A | Raft-based distributed consensus |
| **Auto-Correction** | Manual | Automated correction strategies |

### Protocol Guarantees

- **Consistency**: Raft consensus ensures distributed agreement
- **Durability**: All state changes logged and replicated
- **Availability**: Multi-node redundancy with automatic failover
- **Partition Tolerance**: Leader election during network splits
- **Drift Bounds**: <0.0% (L1), <0.1% (L2), <0.5% (L3)

---

## Core Protocol

### Thread Identity

Every thread transfer requires:

```json
{
  "thread_id": "unique-thread-identifier",
  "anchor": "EOS_SEED_ORION_v2",
  "dlp_tag": "context_tag=operation_identifier",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### State Transfer Format

```json
{
  "state": {
    "symbolic_hash": "sha256-hash-of-state",
    "srb_anchor": "current-anchor-point",
    "t1_timestamp": "temporal-anchor",
    "metadata": {
      "version": "2.0.0",
      "layer": "L1|L2|L3",
      "drift": 0.001
    }
  },
  "validation": {
    "signature": "cryptographic-signature",
    "witnesses": ["node-1", "node-2", "node-3"]
  }
}
```

### Handshake Stages

All v2 handshakes follow a multi-stage protocol:

1. **INIT**: Initial connection and capability negotiation
2. **AUTH**: Authentication and authorization verification
3. **SYNC**: State synchronization and anchor alignment
4. **VALIDATE**: Integrity checks and drift measurement
5. **COMMIT**: Finalize transfer and update logs
6. **(L2+ only) PROPAGATE**: Cross-repository anchor propagation
7. **(L2+ only) REPLICATE**: Multi-node state replication
8. **(L3 only) PKI_VERIFY**: Public key infrastructure verification
9. **(L3 only) WITNESS**: Multi-party attestation

**Stage Transitions:**
```
INIT → AUTH → SYNC → VALIDATE → COMMIT → [PROPAGATE → REPLICATE → PKI_VERIFY → WITNESS] → COMPLETE
```

---

## Phase 1: Distributed Bridge Nodes

### Node Registration Protocol

**Endpoint**: `POST /api/v2/nodes/register`

**Request Payload**:
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

**Response**:
```json
{
  "success": true,
  "node": {
    "node_id": "550e8400-e29b-41d4-a716-446655440000",
    "hostname": "node-01.aurora.local",
    "port": 8000,
    "region": "us-west-2",
    "status": "online",
    "registered_at": "2025-01-15T10:30:00Z"
  },
  "context_tag": "v2_node_registered"
}
```

**Protocol Flow**:
1. Node sends registration with capabilities
2. Registry validates hostname uniqueness
3. Node assigned UUID and added to cluster
4. Heartbeat monitoring begins (30s interval)
5. Load balancer notified of new node

### Raft Consensus Protocol

**State Machine**: FOLLOWER → CANDIDATE → LEADER

#### Leader Election

**Trigger Conditions**:
- Heartbeat timeout (150ms default)
- Explicit election request
- Leader failure detection

**Election Process**:
1. **FOLLOWER**: Increments term, transitions to CANDIDATE
2. **CANDIDATE**: Requests votes from all nodes
3. **Vote Grant Criteria**:
   - Candidate's term ≥ voter's term
   - Voter hasn't voted in this term
   - Candidate's log is up-to-date
4. **Majority Wins**: >50% votes → LEADER
5. **Election Timeout**: No majority → restart election

**Message Format**:
```json
{
  "type": "RequestVote",
  "term": 5,
  "candidate_id": "node-01",
  "last_log_index": 42,
  "last_log_term": 4
}
```

**Response**:
```json
{
  "type": "VoteResponse",
  "term": 5,
  "vote_granted": true,
  "voter_id": "node-02"
}
```

#### Log Replication

**Entry Format**:
```json
{
  "index": 43,
  "term": 5,
  "command": "thread_transfer",
  "data": {
    "thread_id": "test-thread-01",
    "source": "repo-a",
    "target": "repo-b",
    "anchor": "EOS_SEED_ORION_v2"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Replication Flow**:
1. **Leader** receives client command
2. **Leader** appends to local log
3. **Leader** sends AppendEntries RPC to all followers
4. **Followers** append entries if consistent
5. **Leader** waits for majority acknowledgment
6. **Leader** commits entry and applies to state machine
7. **Leader** notifies followers of commit

**AppendEntries RPC**:
```json
{
  "type": "AppendEntries",
  "term": 5,
  "leader_id": "node-01",
  "prev_log_index": 42,
  "prev_log_term": 4,
  "entries": [/* new log entries */],
  "leader_commit": 41
}
```

### Load Balancing

**Strategy**: Weighted round-robin based on:
- Current load (thread count)
- Node capacity
- Response latency
- Health status

**Selection Algorithm**:
```python
weight = (capacity - current_load) / capacity * (1.0 - latency_factor)
selected_node = max(nodes, key=lambda n: n.weight)
```

**Health Check Protocol**:
- Interval: 30 seconds
- Timeout: 5 seconds
- Failure threshold: 3 consecutive failures
- Auto-removal after threshold

---

## Phase 2: Cross-Repository Continuity

### Repository Registration

**Endpoint**: `POST /api/v2/repos/register`

**Request**:
```json
{
  "repo_id": "aurora-main",
  "repo_path": "/path/to/repo",
  "branch": "main",
  "remote_url": "git@github.com:user/repo.git"
}
```

**Validation**:
- ✅ Git repository exists
- ✅ Branch exists locally
- ✅ Working directory clean
- ✅ Remote accessible (if provided)

### Cross-Repository Bridge Protocol

**Endpoint**: `POST /api/v2/bridges/cross-repo`

**Bridge Creation Flow**:
1. **Validate** both repositories registered
2. **Create** bridge with unique ID
3. **Initialize** anchor tracking for both repos
4. **Establish** sync schedule
5. **Return** bridge metadata

**Bridge Metadata**:
```json
{
  "bridge_id": "bridge-aurora-to-opal",
  "source_repo": "aurora-main",
  "target_repo": "opal-main",
  "status": "active",
  "last_sync": "2025-01-15T10:30:00Z",
  "sync_count": 42,
  "anchor_pairs": [
    {
      "source_anchor": "EOS_SEED_ORION_v2",
      "target_anchor": "OPAL_SEED_ALPHA_v1",
      "propagated_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### Anchor Propagation Protocol

**Process**:
1. **Detect** anchor change in source repository
2. **Create** propagation task with source anchor
3. **Map** source anchor to target anchor format
4. **Validate** target repository state
5. **Write** anchor to target repository metadata
6. **Commit** anchor change to Git
7. **Notify** dependent bridges
8. **Update** propagation history

**Anchor Mapping**:
```python
{
  "source_format": "EOS_SEED_{CONSTELLATION}_{VERSION}",
  "target_format": "{REPO}_SEED_{IDENTIFIER}_{VERSION}",
  "mapping_rules": [
    "preserve_version",
    "preserve_timestamp",
    "add_source_reference"
  ]
}
```

### Cross-Repository Handshake

**7-Stage Protocol** (extends base 5 stages):

1. **INIT**: Verify both repos accessible
2. **AUTH**: Validate credentials for both repos
3. **SYNC**: Pull latest changes from both repos
4. **VALIDATE**: Check anchor consistency
5. **COMMIT**: Record handshake in both repos
6. **PROPAGATE**: Sync anchor from source to target
7. **REPLICATE**: Update distributed nodes

**Message Flow**:
```
Source Repo → Bridge Manager → Target Repo
     ↓              ↓                ↓
   INIT          VERIFY           INIT
   AUTH          ROUTE            AUTH
   SYNC         PROPAGATE         SYNC
  VALIDATE      REPLICATE       VALIDATE
  COMMIT         CONFIRM         COMMIT
```

---

## Phase 3: ML Drift Prediction

### Feature Vector Format

**11-Dimensional Input**:
```python
[
  drift_velocity,          # Current rate of drift change
  drift_acceleration,      # Second derivative of drift
  handshake_count,        # Number of recent handshakes
  avg_handshake_duration, # Mean handshake time (seconds)
  failed_handshake_ratio, # Failure rate (0.0-1.0)
  time_of_day,            # Hour of day (0-23)
  day_of_week,            # Day (0=Monday, 6=Sunday)
  thread_age_hours,       # Thread lifetime in hours
  anchor_changes,         # Number of anchor updates
  sync_frequency,         # Minutes between syncs
  node_count              # Active nodes in cluster
]
```

### Prediction Protocol

**Endpoint**: `POST /api/v2/drift/predict`

**Request**:
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

**Response**:
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
    "Consider increasing sync frequency"
  ],
  "context_tag": "v2_drift_predicted"
}
```

### Severity Classification

| Severity | Drift Range | Action |
|----------|-------------|--------|
| **NONE** | 0.0% - 0.001% | No action required |
| **LOW** | 0.001% - 0.01% | Monitor closely |
| **MEDIUM** | 0.01% - 0.1% | Increase sync frequency |
| **HIGH** | 0.1% - 0.5% | Trigger auto-correction |
| **CRITICAL** | > 0.5% | Emergency shutdown |

### Pattern Analysis

**Pattern Types Detected**:
- **STABLE**: Drift remains within 0.001% for >24h
- **TRENDING**: Consistent increase/decrease over time
- **CYCLICAL**: Periodic drift patterns (daily/weekly)
- **VOLATILE**: Erratic drift with high variance
- **ANOMALOUS**: Sudden spikes outside normal range

**Minimum Observations**: 24 data points (1 per hour for 24h)

### Auto-Correction Strategies

**Correction Actions** (priority-ranked):

1. **INCREASE_FREQUENCY** (Priority 1-2)
   - Reduce sync interval by 50%
   - Applies when: MEDIUM severity, trending drift

2. **RESYNC_ANCHOR** (Priority 2-3)
   - Force anchor re-synchronization
   - Applies when: MEDIUM-HIGH severity, anchor drift detected

3. **REBUILD_THREAD** (Priority 3-4)
   - Reconstruct thread from anchors
   - Applies when: HIGH severity, validation failures

4. **ADD_REDUNDANCY** (Priority 3-4)
   - Add backup nodes to cluster
   - Applies when: HIGH severity, node failures

5. **EMERGENCY_SHUTDOWN** (Priority 5 - CRITICAL)
   - Halt all operations safely
   - Applies when: CRITICAL severity, data integrity risk

**Evaluation Protocol**:
```python
if predicted_drift > 0.5:
    return [EMERGENCY_SHUTDOWN]
elif predicted_drift > 0.1:
    return [REBUILD_THREAD, ADD_REDUNDANCY]
elif predicted_drift > 0.01:
    return [RESYNC_ANCHOR, INCREASE_FREQUENCY]
else:
    return []  # No action needed
```

---

## Phase 4: Multi-Layer Hierarchies

### Layer Definitions

#### L1: Thread-to-Thread (Intra-Repository)

**Characteristics**:
- **Handshake Stages**: 5 (INIT, AUTH, SYNC, VALIDATE, COMMIT)
- **Max Drift**: 0.0% (perfect synchronization)
- **Use Case**: Single repository state transfers
- **Security**: Basic authentication
- **Performance**: <10ms handshake time

#### L2: Repository-to-Repository (Cross-Repository)

**Characteristics**:
- **Handshake Stages**: 7 (adds PROPAGATE, REPLICATE)
- **Max Drift**: 0.1%
- **Use Case**: Cross-repository continuity
- **Security**: SSH key authentication
- **Performance**: <100ms handshake time

#### L3: Cluster-to-Cluster (Multi-Organization)

**Characteristics**:
- **Handshake Stages**: 9 (adds PKI_VERIFY, WITNESS)
- **Max Drift**: 0.5%
- **Use Case**: Inter-organizational state transfer
- **Security**: PKI with multi-party attestation
- **Performance**: <1000ms handshake time

### Layer Bridge Creation

**Endpoint**: `POST /api/v2/layers/bridge`

**Request**:
```json
{
  "bridge_id": "l2-bridge-aurora-opal",
  "layer": "L2",
  "source_id": "aurora-main",
  "target_id": "opal-main",
  "thread_id": "cross-repo-thread-01"
}
```

**Validation Rules**:
- L1: source_id == target_id (same repo)
- L2: source_id != target_id (different repos, same org)
- L3: PKI certificates required, witness nodes specified

### Hierarchy Validation Protocol

**Cascade Validation** (L1 → L2 → L3):

```python
def validate_hierarchy(bridges: List[Bridge]) -> ValidationReport:
    issues = []
    
    # L1 Validation
    for l1_bridge in L1_bridges:
        if l1_bridge.drift > 0.0:
            issues.append(CRITICAL("L1 drift detected"))
    
    # L2 Validation (depends on L1)
    for l2_bridge in L2_bridges:
        if l2_bridge.drift > 0.001:
            issues.append(HIGH("L2 drift exceeds threshold"))
        if not l2_bridge.has_valid_l1_parent():
            issues.append(CRITICAL("L2 missing L1 parent"))
    
    # L3 Validation (depends on L2)
    for l3_bridge in L3_bridges:
        if l3_bridge.drift > 0.005:
            issues.append(HIGH("L3 drift exceeds threshold"))
        if not l3_bridge.has_pki_verification():
            issues.append(CRITICAL("L3 missing PKI"))
    
    return ValidationReport(issues)
```

**Validation Response**:
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

---

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "DRIFT_THRESHOLD_EXCEEDED",
    "message": "Predicted drift 0.6% exceeds maximum 0.5%",
    "details": {
      "current_drift": 0.002,
      "predicted_drift": 0.006,
      "threshold": 0.005,
      "severity": "CRITICAL"
    },
    "timestamp": "2025-01-15T10:30:00Z",
    "context_tag": "v2_error_drift_exceeded"
  }
}
```

### Error Codes

| Code | HTTP Status | Severity | Description |
|------|-------------|----------|-------------|
| `NODE_UNREACHABLE` | 503 | HIGH | Node failed health check |
| `CONSENSUS_FAILURE` | 500 | CRITICAL | Raft consensus failed |
| `DRIFT_THRESHOLD_EXCEEDED` | 400 | CRITICAL | Drift > layer max |
| `INVALID_ANCHOR` | 400 | HIGH | Anchor validation failed |
| `REPO_NOT_FOUND` | 404 | MEDIUM | Repository not registered |
| `HANDSHAKE_TIMEOUT` | 408 | HIGH | Handshake exceeded timeout |
| `AUTH_FAILURE` | 401 | CRITICAL | Authentication failed |
| `PKI_VERIFICATION_FAILED` | 403 | CRITICAL | L3 PKI check failed |

### Recovery Procedures

**Consensus Failure**:
1. Detect leader unavailable
2. Trigger election timeout
3. Elect new leader
4. Replay uncommitted log entries
5. Resume normal operation

**Drift Threshold Exceeded**:
1. Halt thread transfer
2. Calculate correction strategy
3. Apply auto-correction if available
4. Validate drift reduction
5. Resume or escalate to manual intervention

**Node Failure**:
1. Remove from load balancer
2. Redistribute load to healthy nodes
3. Attempt connection retry (3 attempts)
4. Mark offline after retry exhaustion
5. Alert administrator

---

## Security Protocols

### Authentication Layers

**L1**: Thread-level authentication
- Anchor signature verification
- DLP tag validation

**L2**: Repository-level authentication
- SSH key verification
- Git credential validation

**L3**: PKI authentication
- X.509 certificate verification
- Multi-party witness attestation
- Certificate revocation list (CRL) checking

### Cryptographic Standards

**Hashing**: SHA-256 for state hashing  
**Signing**: Ed25519 for anchor signatures  
**Encryption**: AES-256-GCM for state transfer  
**Key Exchange**: ECDH with Curve25519

### PKI Protocol (L3 Only)

**Certificate Requirements**:
```json
{
  "version": "X.509v3",
  "subject": "CN=aurora-node-01,O=AuroraOrg,C=US",
  "issuer": "CN=Aurora CA,O=AuroraOrg,C=US",
  "validity": {
    "not_before": "2025-01-01T00:00:00Z",
    "not_after": "2026-01-01T00:00:00Z"
  },
  "public_key": "Ed25519 public key",
  "extensions": {
    "key_usage": ["digitalSignature", "keyAgreement"],
    "extended_key_usage": ["serverAuth", "clientAuth"]
  }
}
```

**Witness Protocol**:
1. Primary node initiates handshake
2. Witness nodes (≥3) observe handshake
3. Each witness signs attestation
4. Primary collects signatures
5. Handshake valid if ≥2/3 witnesses agree

---

## Performance Specifications

### Latency Targets

| Operation | L1 | L2 | L3 |
|-----------|----|----|-----|
| **Handshake** | <10ms | <100ms | <1000ms |
| **Consensus** | <50ms | <50ms | <50ms |
| **Drift Prediction** | <100ms | <100ms | <100ms |
| **Validation** | <5ms | <20ms | <50ms |

### Throughput Targets

- **Thread Transfers**: 1000+ per second (per node)
- **Log Replication**: 10,000+ entries per second
- **Drift Predictions**: 100+ per second
- **Concurrent Bridges**: 1000+ active bridges

### Scalability

- **Max Nodes**: 100 per cluster
- **Max Repositories**: 1000 per instance
- **Max Bridges**: 10,000 active bridges
- **Max Threads**: 100,000 concurrent threads

### Resource Requirements

**Per Node**:
- CPU: 2+ cores
- Memory: 4GB+ RAM
- Storage: 50GB+ SSD
- Network: 1Gbps+ bandwidth

---

## Protocol Versioning

**Current Version**: 2.0.0

**Version Format**: MAJOR.MINOR.PATCH

**Compatibility**:
- v2.x.x → backward compatible with v1.x.x
- Breaking changes increment MAJOR
- New features increment MINOR
- Bug fixes increment PATCH

**Version Negotiation**:
```json
{
  "client_version": "2.0.0",
  "server_version": "2.1.0",
  "negotiated_version": "2.0.0",
  "features_available": ["raft", "drift_prediction", "cross_repo"]
}
```

---

## Appendix: Message Schemas

### Complete RequestVote RPC Schema

```json
{
  "type": "RequestVote",
  "term": "integer (current term)",
  "candidate_id": "string (node UUID)",
  "last_log_index": "integer (index of last log entry)",
  "last_log_term": "integer (term of last log entry)"
}
```

### Complete AppendEntries RPC Schema

```json
{
  "type": "AppendEntries",
  "term": "integer (leader's term)",
  "leader_id": "string (leader UUID)",
  "prev_log_index": "integer (index of log entry before new ones)",
  "prev_log_term": "integer (term of prev_log_index entry)",
  "entries": "array (log entries to store)",
  "leader_commit": "integer (leader's commit index)"
}
```

---

**Thread**: T1→BRIDGE_V2→PROTOCOL→COMPLETE  
**DLP**: context_tag=bridge_v2_protocol_specification_complete  
**Anchor**: EOS_SEED_ORION_v2  

**Document Status**: ✅ COMPLETE  
**Last Updated**: 2025-01-15  
**Maintainer**: Aurora CloudBank Core Team
