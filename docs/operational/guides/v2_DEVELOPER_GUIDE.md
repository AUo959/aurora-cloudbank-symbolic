# Thread Transfer Bridge v2 - Developer Guide

**Version**: 2.0.0  
**Thread**: T1→BRIDGE_V2→DEVELOPER  
**DLP**: context_tag=bridge_v2_developer_guide  
**Anchor**: EOS_SEED_ORION_v2  
**Status**: PRODUCTION READY ✅

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Code Examples](#code-examples)
4. [Best Practices](#best-practices)
5. [Common Patterns](#common-patterns)
6. [Testing Strategies](#testing-strategies)
7. [Extension Points](#extension-points)
8. [Performance Optimization](#performance-optimization)

---

## Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic

# Install dependencies
pip install -r requirements.txt

# Verify v2 available
python -c "from modules.reflective_autonomy.thread_transfer import v2; print(v2.__version__)"
```

### Quick Start

```python
import asyncio
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_node_registry,
    get_drift_predictor,
    get_layer_manager
)

async def main():
    # Register a node
    registry = get_node_registry()
    node = await registry.register_node(
        hostname="dev-node.local",
        port=8000,
        region="local",
        capacity=100
    )
    print(f"Node registered: {node.node_id}")
    
    # Predict drift
    predictor = get_drift_predictor()
    from modules.reflective_autonomy.thread_transfer.v2.drift_predictor import DriftFeatures
    
    features = DriftFeatures(
        drift_velocity=0.001,
        drift_acceleration=0.0001,
        handshake_count=10,
        average_handshake_duration=0.5,
        failed_handshake_ratio=0.01,
        time_of_day=14,
        day_of_week=3,
        thread_age_hours=24.0,
        anchor_changes=2,
        sync_frequency=60.0,
        node_count=3
    )
    
    prediction = await predictor.predict_drift(features, "test-thread")
    print(f"Predicted drift: {prediction.predicted_drift}")

asyncio.run(main())
```

---

## Core Concepts

### Singletons

All v2 managers use the singleton pattern for global state:

```python
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_node_registry,        # Node management
    get_load_balancer,        # Load balancing
    get_raft_consensus,       # Consensus protocol
    get_drift_predictor,      # Drift prediction
    get_pattern_analyzer,     # Pattern analysis
    get_auto_corrector,       # Auto-correction
    get_cross_repo_manager,   # Cross-repo bridges
    get_layer_manager,        # Layer management
    get_hierarchy_validator   # Hierarchy validation
)

# Always use getters - never instantiate directly
registry = get_node_registry()  # ✅ Correct
# registry = NodeRegistry()      # ❌ Wrong - loses global state
```

### Async/Await

All v2 operations are asynchronous:

```python
# ✅ Correct - use await
result = await predictor.predict_drift(features, thread_id)

# ❌ Wrong - missing await
result = predictor.predict_drift(features, thread_id)  # Returns coroutine
```

### Context Tags

Every operation returns a `context_tag` for DLP tracking:

```python
response = await registry.register_node(...)
print(response.get("context_tag"))  # "v2_node_registered"

# Always include context_tag in responses
return {
    "success": True,
    "data": result,
    "context_tag": "v2_operation_completed"  # ✅
}
```

---

## Code Examples

### Example 1: Build a Distributed Thread Transfer

```python
import asyncio
from modules.reflective_autonomy.thread_transfer import ThreadTransferBridge
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_node_registry,
    get_load_balancer,
    get_drift_predictor,
    DriftFeatures
)

async def distributed_transfer(source: str, target: str, thread_id: str):
    """Perform a distributed thread transfer with drift prediction."""
    
    # 1. Register local node (if not already registered)
    registry = get_node_registry()
    try:
        node = await registry.register_node(
            hostname="localhost",
            port=8000,
            region="local",
            capacity=100
        )
        print(f"✓ Node registered: {node.node_id}")
    except Exception as e:
        print(f"Node already registered or error: {e}")
    
    # 2. Select best node for transfer (load balancing)
    balancer = get_load_balancer()
    selected_node = await balancer.select_node()
    print(f"✓ Selected node: {selected_node.hostname if selected_node else 'local'}")
    
    # 3. Predict drift before transfer
    predictor = get_drift_predictor()
    features = DriftFeatures(
        drift_velocity=0.001,
        drift_acceleration=0.0001,
        handshake_count=10,
        average_handshake_duration=0.5,
        failed_handshake_ratio=0.01,
        time_of_day=datetime.now().hour,
        day_of_week=datetime.now().weekday(),
        thread_age_hours=24.0,
        anchor_changes=2,
        sync_frequency=60.0,
        node_count=len(await registry.list_nodes())
    )
    
    prediction = await predictor.predict_drift(features, thread_id)
    print(f"✓ Predicted drift: {prediction.predicted_drift} ({prediction.severity.value})")
    
    # 4. Check if drift is acceptable
    if prediction.severity.value in ["CRITICAL", "HIGH"]:
        print(f"✗ Transfer blocked: {prediction.severity.value} drift predicted")
        return None
    
    # 5. Perform transfer (v1 bridge)
    bridge = ThreadTransferBridge()
    result = await bridge.transfer_thread(source, target, thread_id)
    print(f"✓ Transfer complete: {result}")
    
    return result

# Usage
asyncio.run(distributed_transfer("context-a", "context-b", "test-thread"))
```

### Example 2: Cross-Repository Bridge

```python
import asyncio
from modules.reflective_autonomy.thread_transfer.v2 import get_cross_repo_manager

async def setup_cross_repo_bridge():
    """Create a bridge between two repositories."""
    
    manager = get_cross_repo_manager()
    
    # 1. Register repositories
    await manager.register_repository(
        repo_id="aurora-main",
        repo_path="/workspaces/aurora-cloudbank-symbolic",
        branch="main"
    )
    print("✓ Aurora repository registered")
    
    await manager.register_repository(
        repo_id="opal-main",
        repo_path="/workspaces/opal2-modular-system",
        branch="main"
    )
    print("✓ Opal repository registered")
    
    # 2. Create bridge
    bridge = await manager.create_bridge(
        source_repo="aurora-main",
        target_repo="opal-main",
        thread_id="cross-repo-thread"
    )
    print(f"✓ Bridge created: {bridge.bridge_id}")
    
    # 3. Sync repositories
    sync_result = await manager.sync_repository(
        repo_id="aurora-main",
        direction="pull"
    )
    print(f"✓ Aurora synced: {sync_result.commits_pulled} commits")
    
    # 4. Execute cross-repo handshake
    handshake_result = await manager.execute_handshake(bridge.bridge_id)
    print(f"✓ Handshake completed: {handshake_result.stages_completed} stages")
    
    return bridge

# Usage
asyncio.run(setup_cross_repo_bridge())
```

### Example 3: Multi-Layer Hierarchy

```python
import asyncio
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_layer_manager,
    get_hierarchy_validator,
    BridgeLayer
)

async def create_layered_architecture():
    """Create a 3-layer bridge hierarchy."""
    
    manager = get_layer_manager()
    validator = get_hierarchy_validator()
    
    # 1. Create L1 bridge (intra-repo)
    l1_bridge = await manager.create_bridge(
        bridge_id="l1-thread-to-thread",
        layer=BridgeLayer.L1,
        source_id="aurora-main",
        target_id="aurora-main",
        thread_id="test-thread"
    )
    print(f"✓ L1 bridge created: {l1_bridge.bridge_id}")
    
    # 2. Create L2 bridge (cross-repo)
    l2_bridge = await manager.create_bridge(
        bridge_id="l2-aurora-to-opal",
        layer=BridgeLayer.L2,
        source_id="aurora-main",
        target_id="opal-main",
        thread_id="test-thread"
    )
    print(f"✓ L2 bridge created: {l2_bridge.bridge_id}")
    
    # 3. Validate hierarchy
    bridges = await manager.list_bridges(thread_id="test-thread")
    report = await validator.validate_hierarchy(
        bridges=bridges,
        thread_id="test-thread",
        strict_mode=True
    )
    
    print(f"✓ Hierarchy valid: {report.valid}")
    print(f"  L1 bridges: {report.layer_status['L1']['count']}")
    print(f"  L2 bridges: {report.layer_status['L2']['count']}")
    
    if not report.valid:
        for issue in report.issues:
            print(f"  ⚠ {issue.message}")
    
    return report

# Usage
asyncio.run(create_layered_architecture())
```

---

## Best Practices

### 1. Always Use Singletons

```python
# ✅ Good - consistent state
registry = get_node_registry()
node1 = await registry.register_node(...)
node2 = await registry.register_node(...)
nodes = await registry.list_nodes()  # Returns both nodes

# ❌ Bad - isolated state
registry1 = NodeRegistry()
registry2 = NodeRegistry()
await registry1.register_node(...)
await registry2.list_nodes()  # Empty! Different instance
```

### 2. Handle Drift Proactively

```python
# ✅ Good - predict before transfer
prediction = await predictor.predict_drift(features, thread_id)
if prediction.severity.value not in ["CRITICAL", "HIGH"]:
    await bridge.transfer_thread(...)

# ❌ Bad - reactive only
await bridge.transfer_thread(...)
# Drift detected after the fact
```

### 3. Use Context Managers for Resources

```python
# ✅ Good - automatic cleanup
async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/api/v2/nodes")

# ❌ Bad - manual cleanup
client = httpx.AsyncClient()
response = await client.get("...")
await client.aclose()  # Easy to forget
```

### 4. Validate Input Data

```python
from pydantic import BaseModel, Field, validator

class NodeConfig(BaseModel):
    hostname: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., ge=1, le=65535)
    capacity: int = Field(..., ge=1)
    
    @validator('hostname')
    def validate_hostname(cls, v):
        if not v.replace('-', '').replace('.', '').isalnum():
            raise ValueError('Invalid hostname format')
        return v

# ✅ Good - validated input
config = NodeConfig(
    hostname="node-01.local",
    port=8000,
    capacity=1000
)
```

### 5. Use Structured Logging

```python
import logging
import json

logger = logging.getLogger(__name__)

# ✅ Good - structured
logger.info("Node registered", extra={
    "node_id": node.node_id,
    "hostname": node.hostname,
    "context_tag": "v2_node_registered"
})

# ❌ Bad - unstructured
logger.info(f"Node {node.node_id} registered at {node.hostname}")
```

---

## Common Patterns

### Pattern 1: Retry with Exponential Backoff

```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> T:
    """Retry a function with exponential backoff."""
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff
    
    raise RuntimeError("Max retries exceeded")

# Usage
async def register_with_retry():
    registry = get_node_registry()
    return await retry_with_backoff(
        lambda: registry.register_node(
            hostname="node-01.local",
            port=8000,
            region="us-west-1",
            capacity=1000
        )
    )
```

### Pattern 2: Circuit Breaker

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func):
        if self.state == "OPEN":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func()
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.failures = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"

# Usage
breaker = CircuitBreaker()

async def protected_operation():
    predictor = get_drift_predictor()
    return await breaker.call(
        lambda: predictor.predict_drift(features, thread_id)
    )
```

### Pattern 3: Observer Pattern for Events

```python
from typing import Callable, List
from dataclasses import dataclass

@dataclass
class Event:
    type: str
    data: dict

class EventBus:
    def __init__(self):
        self.listeners: dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    async def publish(self, event: Event):
        if event.type in self.listeners:
            for callback in self.listeners[event.type]:
                await callback(event)

# Usage
bus = EventBus()

async def on_node_registered(event: Event):
    print(f"Node {event.data['node_id']} registered!")

bus.subscribe("node_registered", on_node_registered)

# In your code
async def register_node_with_event():
    registry = get_node_registry()
    node = await registry.register_node(...)
    
    await bus.publish(Event(
        type="node_registered",
        data={"node_id": node.node_id, "hostname": node.hostname}
    ))
```

---

## Testing Strategies

### Unit Testing

```python
import pytest
from modules.reflective_autonomy.thread_transfer.v2 import get_drift_predictor, DriftFeatures

@pytest.mark.asyncio
@pytest.mark.unit
async def test_drift_prediction():
    """Test basic drift prediction."""
    predictor = get_drift_predictor()
    
    features = DriftFeatures(
        drift_velocity=0.001,
        drift_acceleration=0.0001,
        handshake_count=10,
        average_handshake_duration=0.5,
        failed_handshake_ratio=0.01,
        time_of_day=14,
        day_of_week=3,
        thread_age_hours=24.0,
        anchor_changes=2,
        sync_frequency=60.0,
        node_count=3
    )
    
    prediction = await predictor.predict_drift(features, "test-thread")
    
    assert prediction.predicted_drift >= 0.0
    assert prediction.severity in ["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert prediction.confidence in ["LOW", "MEDIUM", "HIGH"]
```

### Integration Testing

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_distributed_node_workflow():
    """Test complete node registration and health check workflow."""
    registry = get_node_registry()
    
    # Register node
    node = await registry.register_node(
        hostname="test-node.local",
        port=8000,
        region="test",
        capacity=100
    )
    
    # Verify registration
    retrieved = await registry.get_node(node.node_id)
    assert retrieved.hostname == "test-node.local"
    
    # Check health
    health = await registry.check_node_health(node.node_id)
    assert health.status == "healthy"
    
    # Cleanup
    await registry.unregister_node(node.node_id)
```

### Mocking External Dependencies

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_cross_repo_with_mock():
    """Test cross-repo bridge with mocked Git operations."""
    
    with patch('modules.reflective_autonomy.thread_transfer.v2.cross_repo_manager.GitRepo') as mock_git:
        # Setup mock
        mock_git.return_value.pull = AsyncMock(return_value={"commits": 5})
        
        manager = get_cross_repo_manager()
        result = await manager.sync_repository("aurora-main", direction="pull")
        
        assert result.commits_pulled == 5
        mock_git.return_value.pull.assert_called_once()
```

---

## Extension Points

### Custom Drift Model

```python
from modules.reflective_autonomy.thread_transfer.v2.drift_predictor import DriftPredictor, DriftPrediction

class CustomDriftPredictor(DriftPredictor):
    """Custom drift prediction model."""
    
    async def _predict_with_custom_model(self, features):
        # Your custom ML model here
        # e.g., integrate with TensorFlow, scikit-learn, etc.
        predicted_drift = your_model.predict(features)
        return predicted_drift
    
    async def predict_drift(self, features, thread_id):
        """Override to use custom model."""
        predicted_drift = await self._predict_with_custom_model(features)
        
        return DriftPrediction(
            predicted_drift=predicted_drift,
            severity=self._determine_severity(predicted_drift),
            confidence=self._determine_confidence(features),
            prediction_horizon_hours=24,
            # ... rest of fields
        )

# Use custom predictor
custom_predictor = CustomDriftPredictor()
```

### Custom Load Balancing Strategy

```python
from modules.reflective_autonomy.thread_transfer.v2.load_balancer import LoadBalancer

class GeographicLoadBalancer(LoadBalancer):
    """Load balancer that prioritizes geographic proximity."""
    
    async def select_node(self, preferred_region: str = None):
        """Select node with geographic preference."""
        nodes = await self.registry.list_nodes()
        
        if preferred_region:
            regional_nodes = [n for n in nodes if n.region == preferred_region]
            if regional_nodes:
                return min(regional_nodes, key=lambda n: n.current_load)
        
        # Fallback to standard selection
        return await super().select_node()

# Use custom balancer
geo_balancer = GeographicLoadBalancer()
node = await geo_balancer.select_node(preferred_region="us-west-1")
```

### Custom Correction Strategy

```python
from modules.reflective_autonomy.thread_transfer.v2.auto_corrector import AutoCorrector, CorrectionAction, CorrectionStrategy

class CustomAutoCorrector(AutoCorrector):
    """Auto-corrector with custom strategies."""
    
    async def evaluate_correction(self, predicted_drift, current_drift, thread_id, metadata=None):
        """Custom correction evaluation."""
        actions = await super().evaluate_correction(predicted_drift, current_drift, thread_id, metadata)
        
        # Add custom strategy
        if predicted_drift > 0.2:
            actions.append(CorrectionAction(
                strategy=CorrectionStrategy.CUSTOM,
                priority=4,
                description="Apply custom high-drift mitigation",
                parameters={"custom_param": "value"}
            ))
        
        return actions

# Use custom corrector
custom_corrector = CustomAutoCorrector()
```

---

## Performance Optimization

### 1. Connection Pooling

```python
import httpx

# ✅ Reuse client across requests
client = httpx.AsyncClient()

async def make_requests():
    for i in range(100):
        response = await client.get(f"http://localhost:8000/api/v2/nodes")

await client.aclose()

# ❌ Creating new client each time
async def make_requests_slow():
    for i in range(100):
        async with httpx.AsyncClient() as client:  # Slow!
            response = await client.get(f"http://localhost:8000/api/v2/nodes")
```

### 2. Batch Operations

```python
# ✅ Register multiple nodes in parallel
async def register_nodes_batch(nodes: List[dict]):
    registry = get_node_registry()
    tasks = [
        registry.register_node(**node_config)
        for node_config in nodes
    ]
    return await asyncio.gather(*tasks)

# ❌ Register nodes sequentially
async def register_nodes_slow(nodes: List[dict]):
    registry = get_node_registry()
    results = []
    for node_config in nodes:
        result = await registry.register_node(**node_config)
        results.append(result)
    return results
```

### 3. Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedPredictor:
    def __init__(self):
        self.predictor = get_drift_predictor()
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)
    
    async def predict_drift_cached(self, features, thread_id):
        cache_key = f"{thread_id}:{hash(features)}"
        
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return result
        
        result = await self.predictor.predict_drift(features, thread_id)
        self.cache[cache_key] = (result, datetime.now())
        return result
```

---

**Thread**: T1→BRIDGE_V2→DEVELOPER→COMPLETE  
**DLP**: context_tag=bridge_v2_developer_guide_complete  
**Anchor**: EOS_SEED_ORION_v2  

**Document Status**: ✅ COMPLETE  
**Last Updated**: 2025-01-15  
**Maintainer**: Aurora CloudBank Core Team  

**Happy Coding!** 🚀
