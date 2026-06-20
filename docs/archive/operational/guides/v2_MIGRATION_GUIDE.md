# Thread Transfer Bridge v2 - Migration Guide

**Version**: v1.x → v2.0.0  
**Thread**: T1→BRIDGE_V2→MIGRATION  
**DLP**: context_tag=bridge_v2_migration_guide  
**Anchor**: EOS_SEED_ORION_v2  
**Status**: PRODUCTION READY ✅

---

## Table of Contents

1. [Overview](#overview)
2. [What's New in v2](#whats-new-in-v2)
3. [Breaking Changes](#breaking-changes)
4. [Backward Compatibility](#backward-compatibility)
5. [Migration Steps](#migration-steps)
6. [Testing Your Migration](#testing-your-migration)
7. [Rollback Procedures](#rollback-procedures)
8. [FAQ](#faq)

---

## Overview

Thread Transfer Bridge v2 is a **backward-compatible** upgrade that extends v1 with distributed consensus, cross-repository synchronization, ML drift prediction, and multi-layer hierarchies. Existing v1 code continues to work without modification.

### Migration Timeline

| Step | Duration | Risk Level |
|------|----------|------------|
| **Preparation** | 1-2 hours | LOW |
| **Deployment** | 30 minutes | LOW |
| **Validation** | 1 hour | LOW |
| **Full Adoption** | 1-4 weeks | MEDIUM |

### Migration Difficulty

- **Simple**: Using only v1 features → **No migration needed**
- **Moderate**: Adding distributed nodes → **1-2 days**
- **Advanced**: Full v2 feature adoption → **1-2 weeks**

---

## What's New in v2

### Major Features

#### 1. Distributed Bridge Nodes

**v1**: Single-instance bridge  
**v2**: Multi-node cluster with Raft consensus

```python
# NEW in v2: Register nodes
from modules.reflective_autonomy.thread_transfer.v2 import get_node_registry

registry = get_node_registry()
await registry.register_node(
    hostname="node-01.aurora.local",
    port=8000,
    region="us-west-2",
    capacity=1000
)
```

#### 2. Cross-Repository Continuity

**v1**: Single repository only  
**v2**: Anchor propagation across repositories

```python
# NEW in v2: Cross-repo bridges
from modules.reflective_autonomy.thread_transfer.v2 import get_cross_repo_manager

manager = get_cross_repo_manager()
bridge = await manager.create_bridge(
    source_repo="aurora-main",
    target_repo="opal-main",
    thread_id="cross-repo-thread"
)
```

#### 3. ML Drift Prediction

**v1**: Reactive drift detection  
**v2**: Predictive forecasting with LSTM

```python
# NEW in v2: Predict future drift
from modules.reflective_autonomy.thread_transfer.v2 import get_drift_predictor

predictor = get_drift_predictor()
prediction = await predictor.predict_drift(features, thread_id)
print(f"Predicted drift in 24h: {prediction.predicted_drift}")
```

#### 4. Multi-Layer Hierarchies

**v1**: Flat structure  
**v2**: L1/L2/L3 hierarchical validation

```python
# NEW in v2: Layer-specific bridges
from modules.reflective_autonomy.thread_transfer.v2 import get_layer_manager

manager = get_layer_manager()
bridge = await manager.create_bridge(
    bridge_id="l2-bridge-001",
    layer=BridgeLayer.L2,
    source_id="aurora-main",
    target_id="opal-main"
)
```

### API Enhancements

#### 21 New v2 Endpoints

- **6 endpoints**: Distributed node management
- **4 endpoints**: Cross-repository sync
- **5 endpoints**: Drift prediction
- **6 endpoints**: Layer management

All v1 endpoints remain available and unchanged.

---

## Breaking Changes

### None! 🎉

v2 is **100% backward compatible** with v1. All v1 code continues to work without modification.

### Deprecation Notice

The following v1 patterns are **deprecated but still supported**:

| v1 Pattern | v2 Alternative | Removal Timeline |
|------------|----------------|------------------|
| Direct bridge instantiation | Use singleton getters | v3.0.0 (2026+) |
| Manual drift checking | Use ML predictions | v3.0.0 (2026+) |
| Single-repo assumptions | Cross-repo bridges | No removal planned |

**Recommendation**: Start using v2 patterns for new code, but no urgency to refactor existing v1 code.

---

## Backward Compatibility

### v1 Code Works Unchanged

All v1 thread transfer code continues to work:

```python
# v1 code - still works in v2!
from modules.reflective_autonomy.thread_transfer import ThreadTransferBridge

bridge = ThreadTransferBridge()
result = await bridge.transfer_thread(
    source="context-a",
    target="context-b",
    thread_id="test-thread"
)
```

### v1 Imports Still Available

```python
# All v1 imports work
from modules.reflective_autonomy.thread_transfer import (
    ThreadTransferBridge,
    HandshakeProtocol,
    AnchorValidator,
    DriftDetector
)
```

### v1 API Endpoints Unchanged

All v1 FastAPI endpoints at `/api/v1/*` remain available:

```bash
# v1 endpoints still work
curl http://localhost:8000/api/v1/thread/bridge/status
curl http://localhost:8000/api/v1/thread/bridge/companions
```

### v1 Configuration Compatible

Existing v1 configuration files work without changes. v2 adds optional configuration sections that can be ignored.

---

## Migration Steps

### Step 1: Update Dependencies (5 minutes)

**No action required** - v2 is already included in the repository.

Verify v2 is available:

```python
from modules.reflective_autonomy.thread_transfer import v2

print(v2.__version__)  # Should print "2.0.0"
```

### Step 2: Test v1 Compatibility (15 minutes)

Run your existing v1 tests to ensure nothing broke:

```bash
# Run existing v1 tests
pytest tests/test_thread_transfer.py -v

# Verify v1 API endpoints
curl http://localhost:8000/api/v1/thread/bridge/status
```

**Expected**: All v1 tests pass, all v1 endpoints respond.

### Step 3: Enable v2 Features (10 minutes)

v2 features are **opt-in**. Start using them incrementally:

#### Option A: Add Distributed Nodes

```python
# Add to your initialization code
from modules.reflective_autonomy.thread_transfer.v2 import get_node_registry

# Register current instance as a node
registry = get_node_registry()
await registry.register_node(
    hostname="primary.aurora.local",
    port=8000,
    region="us-west-1",
    capacity=1000
)
```

#### Option B: Enable Drift Prediction

```python
# Add drift monitoring
from modules.reflective_autonomy.thread_transfer.v2 import get_drift_predictor

predictor = get_drift_predictor()

# Before each transfer
prediction = await predictor.predict_drift(features, thread_id)
if prediction.severity.value in ["HIGH", "CRITICAL"]:
    print(f"Warning: High drift predicted ({prediction.predicted_drift})")
```

#### Option C: Add Cross-Repo Support

```python
# Register repositories
from modules.reflective_autonomy.thread_transfer.v2 import get_cross_repo_manager

manager = get_cross_repo_manager()
await manager.register_repository(
    repo_id="aurora-main",
    repo_path="/path/to/aurora-cloudbank-symbolic",
    branch="main"
)
```

### Step 4: Update API Clients (30 minutes)

Add v2 endpoint calls alongside v1:

```python
import httpx

async def check_cluster_health():
    """NEW: v2 cluster health check"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v2/cluster/health")
        return response.json()

# Call alongside existing v1 checks
v1_status = await check_v1_status()  # Existing
v2_health = await check_cluster_health()  # NEW
```

### Step 5: Deploy with Monitoring (1 hour)

Deploy v2 with enhanced monitoring:

```bash
# Start server (v1 + v2 endpoints available)
python aurora_api.py

# Monitor logs for v2 activity
tail -f /var/log/aurora/api.log | grep "v2_"

# Check v2 endpoints
curl http://localhost:8000/api/v2/cluster/health
curl http://localhost:8000/api/v2/drift/patterns
```

### Step 6: Gradual Feature Adoption (1-4 weeks)

Adopt v2 features incrementally:

**Week 1**: Distributed nodes + monitoring  
**Week 2**: Drift prediction + auto-correction  
**Week 3**: Cross-repository bridges  
**Week 4**: Multi-layer hierarchies

No need to rush - v1 continues working throughout.

---

## Testing Your Migration

### Pre-Migration Checklist

- [ ] All v1 tests passing
- [ ] v1 API endpoints responding
- [ ] No errors in current logs
- [ ] Backup of current configuration
- [ ] Rollback plan documented

### Post-Migration Validation

#### 1. Verify v1 Still Works

```bash
# Run v1 test suite
pytest tests/test_thread_transfer.py -v

# Test v1 API
curl http://localhost:8000/api/v1/thread/bridge/status
```

#### 2. Verify v2 Features Available

```bash
# Test v2 API
curl http://localhost:8000/api/v2/nodes
curl http://localhost:8000/api/v2/cluster/health
curl http://localhost:8000/api/v2/drift/patterns
```

#### 3. Run v2 Integration Tests

```bash
# Run v2 test suite
pytest tests/test_bridge_v2_basic.py -v

# Expected: 11/11 tests passing
```

#### 4. Performance Check

```python
import time
import asyncio
from modules.reflective_autonomy.thread_transfer import ThreadTransferBridge

async def performance_test():
    bridge = ThreadTransferBridge()
    
    start = time.time()
    for i in range(100):
        await bridge.transfer_thread(
            source=f"ctx-a-{i}",
            target=f"ctx-b-{i}",
            thread_id=f"perf-test-{i}"
        )
    end = time.time()
    
    print(f"100 transfers: {end - start:.2f}s")
    print(f"Avg per transfer: {(end - start) / 100 * 1000:.1f}ms")

asyncio.run(performance_test())
```

**Expected**: Similar or better performance than v1.

---

## Rollback Procedures

### If Issues Arise

v2 can be disabled without code changes - simply stop using v2 endpoints and features.

### Emergency Rollback

#### Option 1: Disable v2 Endpoints

Comment out v2 route imports in `aurora_api.py`:

```python
# Temporarily disable v2
# from modules.reflective_autonomy.thread_transfer.v2 import (...)
```

Restart server:

```bash
pkill -f "python aurora_api.py"
python aurora_api.py
```

#### Option 2: Feature Flags

Add feature flags to control v2 adoption:

```python
# config.py
ENABLE_V2_DISTRIBUTED = False
ENABLE_V2_DRIFT_PREDICTION = False
ENABLE_V2_CROSS_REPO = False

# Use flags
if ENABLE_V2_DISTRIBUTED:
    from modules.reflective_autonomy.thread_transfer.v2 import get_node_registry
    # ... v2 code
```

#### Option 3: Full Revert

If necessary (unlikely), revert to commit before v2:

```bash
# Find commit before v2
git log --oneline | grep "v1"

# Revert to that commit
git revert <commit-hash>..HEAD

# Or checkout previous version
git checkout <commit-hash>
```

**Note**: This is rarely needed since v2 is backward compatible.

---

## FAQ

### Do I need to migrate immediately?

**No.** v2 is backward compatible. Migrate at your own pace.

### Will v1 code break?

**No.** All v1 code continues to work unchanged.

### Can I use v1 and v2 together?

**Yes!** They coexist perfectly. Use v2 features where beneficial, keep v1 elsewhere.

### What if I only want drift prediction?

Use just that feature! v2 features are modular and independent.

```python
# Use only drift prediction
from modules.reflective_autonomy.thread_transfer.v2 import get_drift_predictor
predictor = get_drift_predictor()
# ... rest is v1 code
```

### Do v2 features require infrastructure changes?

**Optional**:
- **Distributed nodes**: Yes (multiple servers)
- **Cross-repo**: No (works with existing Git)
- **Drift prediction**: No (runs locally)
- **Layer hierarchy**: No (logical construct)

### How do I know which version I'm using?

Check the import:

```python
# v1
from modules.reflective_autonomy.thread_transfer import ThreadTransferBridge

# v2
from modules.reflective_autonomy.thread_transfer.v2 import get_node_registry
```

Both can coexist in the same codebase.

### What's the performance impact?

- **v1 code**: No change
- **v2 distributed**: +5-10ms (consensus overhead)
- **v2 drift prediction**: +10-20ms (first prediction only, cached after)
- **v2 cross-repo**: +50-100ms (Git operations)

### Are there new dependencies?

**Optional**:
- **PyTorch**: For LSTM drift prediction (falls back to statistical if unavailable)
- **GitPython**: Already included

### Can I migrate only production?

Yes! Keep development on v1, migrate production to v2, or vice versa.

### What about data migration?

**None required.** v2 uses the same anchor and thread formats as v1.

### Will v3 break compatibility?

Unknown, but no breaking changes planned. Deprecated v1 patterns may be removed in v3 (2026+).

---

## Migration Examples

### Example 1: Simple Addition

Add drift monitoring to existing v1 code:

```python
# Before (v1 only)
from modules.reflective_autonomy.thread_transfer import ThreadTransferBridge

bridge = ThreadTransferBridge()
result = await bridge.transfer_thread(source, target, thread_id)

# After (v1 + v2)
from modules.reflective_autonomy.thread_transfer import ThreadTransferBridge
from modules.reflective_autonomy.thread_transfer.v2 import get_drift_predictor

bridge = ThreadTransferBridge()

# NEW: Check drift before transfer
predictor = get_drift_predictor()
features = build_drift_features()  # Your implementation
prediction = await predictor.predict_drift(features, thread_id)

if prediction.severity.value != "CRITICAL":
    result = await bridge.transfer_thread(source, target, thread_id)
else:
    print(f"Transfer blocked: {prediction.predicted_drift} drift predicted")
```

### Example 2: Distributed Deployment

Upgrade single instance to cluster:

```python
# Before: Single instance
bridge = ThreadTransferBridge()

# After: Distributed cluster
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_node_registry,
    get_load_balancer
)

# Register this node
registry = get_node_registry()
await registry.register_node(
    hostname="node-01.local",
    port=8000,
    region="us-west-1",
    capacity=1000
)

# Let load balancer choose node
balancer = get_load_balancer()
selected_node = await balancer.select_node()

# v1 transfer still works, now load-balanced
bridge = ThreadTransferBridge()
result = await bridge.transfer_thread(source, target, thread_id)
```

### Example 3: Cross-Repository

Add cross-repo support:

```python
# Before: Single repo
bridge = ThreadTransferBridge()
result = await bridge.transfer_thread(source, target, thread_id)

# After: Cross-repo capable
from modules.reflective_autonomy.thread_transfer.v2 import get_cross_repo_manager

manager = get_cross_repo_manager()

# Register repos
await manager.register_repository("aurora-main", "/path/to/aurora", "main")
await manager.register_repository("opal-main", "/path/to/opal", "main")

# Create cross-repo bridge
cross_bridge = await manager.create_bridge(
    source_repo="aurora-main",
    target_repo="opal-main",
    thread_id="cross-repo-thread"
)

# Sync across repos
await manager.sync_bridge(cross_bridge.bridge_id)

# Original v1 code still works for intra-repo
bridge = ThreadTransferBridge()
result = await bridge.transfer_thread(source, target, thread_id)
```

---

## Support Resources

**Documentation**:
- [Protocol Specification](./THREAD_TRANSFER_BRIDGE_v2_PROTOCOL.md)
- [API Reference](./v2_API_REFERENCE.md)
- [Admin Guide](./v2_ADMIN_GUIDE.md)
- [Developer Guide](./v2_DEVELOPER_GUIDE.md)

**Testing**:
- Basic tests: `tests/test_bridge_v2_basic.py`
- API tests: `test_v2_api_endpoints.py`

**Community**:
- GitHub Issues: Report migration problems
- Discord: Real-time migration support

---

**Thread**: T1→BRIDGE_V2→MIGRATION→COMPLETE  
**DLP**: context_tag=bridge_v2_migration_guide_complete  
**Anchor**: EOS_SEED_ORION_v2  

**Document Status**: ✅ COMPLETE  
**Last Updated**: 2025-01-15  
**Maintainer**: Aurora CloudBank Core Team  

**Happy Migrating!** 🚀
