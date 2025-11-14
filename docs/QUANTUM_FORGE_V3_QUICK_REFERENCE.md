# Quantum Forge v3.0 - Quick Reference Card

**⚡ Fast lookup for quantum-enhanced Aurora operations**

---

## 🚀 Quick Start (3 lines)

```python
from modules.quantum_forge import QuantumForge, get_quantum_integration, get_system_flow_orchestrator
forge = QuantumForge()
integration = get_quantum_integration(forge=forge)
orchestrator = get_system_flow_orchestrator(forge=forge)  # AUTO-STARTS ADAPTIVE RESONANCE
```

---

## 📦 Import Patterns

```python
# Core v2.0
from modules.quantum_forge import (
    QuantumForge, EthicsLevel, FlowstateMode
)

# Quantum Integration (Phase 1)
from modules.quantum_forge import (
    get_quantum_integration,
    AgentQuantumState
)

# Entanglement (Phase 2)
from modules.quantum_forge import (
    get_entanglement_network,
    EntanglementCluster
)

# Memory (Phase 3)
from modules.quantum_forge import (
    get_quantum_memory_enhancer
)

# Orchestration (Phase 4) - ADAPTIVE RESONANCE
from modules.quantum_forge import (
    get_system_flow_orchestrator,
    FlowstateMode
)

# Ethics (Phase 5)
from modules.quantum_forge import (
    get_ethics_quantum_gate
)
```

---

## ⚡ Common Operations

### Create Agent → Quantum State
```python
agent = forge.generate_agent("Optimize logistics", ["ORION"])
agent_qstate = integration.agent_to_quantum(agent)
print(f"Qubits: {agent_qstate.quantum_state.num_qubits}, Fidelity: {agent_qstate.fidelity:.4f}")
```

### Quantum Optimize Agent
```python
optimized = integration.optimize_agent_quantum(agent, optimization_rounds=3)
print(f"New alignment: {optimized.intent_alignment:.4f}")
```

### Create Entangled Team
```python
agents = [forge.generate_agent(f"Task {i}", ["ORION"]) for i in range(4)]
cluster = network.create_cluster(
    [a.agent_id for a in agents],
    topology="mesh",  # or "star", "ring", "tree"
    cluster_id="TEAM_1"
)
```

### Propagate State Update
```python
network.propagate_state_update(
    agents[0].agent_id,
    {"status": "complete", "results": {...}}
)
```

### Enhance Memory with Quantum
```python
memory = forge.create_memory_node({"data": "..."}, tags=["quantum"])
metadata = enhancer.enhance_memory(memory)
print(f"Coherence: {metadata.coherence_score:.4f}")
```

### Auto-Refresh Decoherent Memories
```python
result = enhancer.auto_refresh_decoherent(max_refreshes=10)
print(f"Refreshed: {result['refreshed']}")
```

### Check System Status
```python
metrics = orchestrator.get_system_metrics()
print(f"Load: {metrics.system_load:.2%}, Health: {metrics.average_health:.2%}")
```

### Adaptive Mode Transition
```python
# Automatic (recommended)
orchestrator.auto_optimize_system()

# Manual override
orchestrator.synchronize_all_modules(
    FlowstateMode.QUIESCENT,
    "High load detected - reducing complexity"
)
```

### Validate Quantum Gate
```python
result = ethics_gate.validate_gate_operation(
    gate_type="CNOT",
    qubits=[0, 1],
    intent_score=0.85
)
if result['allowed']:
    # Apply gate
    pass
```

---

## 🎯 Flowstate Modes (Phase 4)

| Mode | Load | Behavior | Use Case |
|------|------|----------|----------|
| **GENERATIVE** | <30% | Exploration, experiments | Off-peak, dev |
| **RESONANT** | 30-80% | Balanced operation | Normal production |
| **METAMORPHIC** | Any | Self-modification | Drift recovery |
| **QUIESCENT** | >80% | Reduced complexity | High-load protection |

**Automatic transitions:** Orchestrator handles this when you call `auto_optimize_system()`

---

## 🕸️ Entanglement Topologies

```python
# MESH - Fully connected (high coordination)
cluster = network.create_cluster(agent_ids, topology="mesh", cluster_id="ALL_TO_ALL")

# STAR - Hub and spoke (leader-follower)
cluster = network.create_cluster([leader, *workers], topology="star", cluster_id="HUB")

# RING - Circular (pipeline)
cluster = network.create_cluster(pipeline_stages, topology="ring", cluster_id="PIPE")

# TREE - Binary hierarchy (divide-and-conquer)
cluster = network.create_cluster(hierarchy, topology="tree", cluster_id="TREE")
```

---

## 📊 Metrics & Health

### Quantum Integration
```python
metrics = integration.metrics
print(f"Conversions: {metrics['total_conversions']}")
print(f"Avg fidelity: {metrics['average_fidelity']:.4f}")
```

### Entanglement Network
```python
health = network.monitor_network_health()
print(f"Active links: {health['active_links']}")
print(f"Weak links: {len(health['weak_links'])}")
```

### Quantum Memory
```python
status = enhancer.monitor_coherence()
print(f"Coherent: {status['coherent']}, Decoherent: {status['decoherent']}")
```

### System Orchestration
```python
metrics = orchestrator.get_system_metrics()
print(f"Phase: {metrics.current_phase.value}")
print(f"Drifting modules: {metrics.drifting_modules}")
```

### Ethics Gate
```python
metrics = ethics_gate.get_ethics_metrics()
print(f"Block rate: {metrics['block_rate']:.2%}")
```

---

## 🔧 Configuration Snippets

### High Fidelity (Slow, Accurate)
```python
integration.fidelity_threshold = 0.99
agent_qstate.coherence_time = 600  # 10 minutes
```

### Balanced (Recommended)
```python
integration.fidelity_threshold = 0.95
agent_qstate.coherence_time = 300  # 5 minutes
```

### Fast (Lower Accuracy)
```python
integration.fidelity_threshold = 0.90
agent_qstate.coherence_time = 150  # 2.5 minutes
```

### Aggressive Memory Refresh
```python
enhancer.auto_refresh_interval = 180  # 3 minutes
enhancer.max_refreshes_per_cycle = 20
```

### Conservative Orchestration
```python
orchestrator.auto_optimize_interval = 300  # 5 minutes
orchestrator.load_high_threshold = 0.9  # QUIESCENT at 90%
```

---

## 🚨 Troubleshooting One-Liners

### Low Fidelity
```python
agent_qstate.coherence_time = 600; integration.agent_to_quantum(agent)
```

### Weak Entanglement
```python
network.refresh_all_entanglements()
```

### Memory Decoherence
```python
enhancer.auto_refresh_decoherent(max_refreshes=20)
```

### System Not Adapting
```python
orchestrator.auto_optimize_system()
```

### Too Many Blocks
```python
ethics_gate = get_ethics_quantum_gate(EthicsLevel.BALANCED)  # Lower from STRICT
```

---

## 📦 Export Manifests

```python
manifests = {
    "integration": integration.export_integration_manifest(),
    "network": network.export_network_manifest(),
    "memory": enhancer.export_quantum_memory_manifest(),
    "orchestration": orchestrator.export_flow_manifest(),
    "ethics": ethics_gate.export_ethics_manifest()
}

# All manifests include: version, timestamp, metrics, integrity_hash
```

---

## 🎯 Auto-Registration (Orchestrator)

These 8 modules automatically participate in adaptive resonance:

1. **aumemmanager** - Memory management
2. **quantum_simulator** - Quantum circuits
3. **data_guardian** - Ethics enforcement
4. **insight_ledger** - Temporal tracking
5. **gumas_ethics** - Compliance
6. **monitoring_dashboard** - Behavioral drift
7. **r2_telemetry** - Telemetry
8. **quantum_forge** - Agent generation

**Add custom module:**
```python
orchestrator.register_module("my_module", FlowstateMode.RESONANT)
```

---

## ⚡ Performance Quick Wins

```python
# 1. Use star topology for most use cases (not mesh)
cluster = network.create_cluster(agents, topology="star")

# 2. Batch memory refreshes
enhancer.auto_refresh_decoherent(max_refreshes=10)

# 3. Let orchestrator auto-optimize
orchestrator.auto_optimize_system()  # Every 60s

# 4. Use balanced ethics level
ethics_gate = get_ethics_quantum_gate(EthicsLevel.BALANCED)

# 5. Monitor coherence every 5 minutes
status = enhancer.monitor_coherence()
```

---

## 📚 Full Documentation

- **Complete Guide:** `docs/QUANTUM_FORGE_V3_COMPLETE_GUIDE.md` (1,200+ lines)
- **Implementation Summary:** `docs/QUANTUM_FORGE_V3_IMPLEMENTATION_SUMMARY.md`
- **Full Demo:** `examples/quantum_forge_v3_complete_demo.py`
- **Module Code:** `modules/quantum_forge/*.py`

---

## 🎯 Essential Pattern

**Always initialize in this order:**

```python
# 1. Core
forge = QuantumForge(ethics_level=EthicsLevel.STRICT)

# 2. Quantum Integration (requires forge)
integration = get_quantum_integration(forge=forge)

# 3. Entanglement Network (requires forge + integration)
network = get_entanglement_network(forge=forge, integration=integration)

# 4. Memory Enhancer (requires forge)
enhancer = get_quantum_memory_enhancer(forge=forge)

# 5. System Orchestrator (requires forge) - STARTS ADAPTIVE RESONANCE
orchestrator = get_system_flow_orchestrator(forge=forge)

# 6. Ethics Gate (optional)
ethics_gate = get_ethics_quantum_gate(ethics_level=EthicsLevel.STRICT)

# Now all systems breathing together with adaptive resonance!
```

---

**Quantum Forge v3.0** - Quick Reference | See full guide for details
