# Quick Start Guide - Quantum Forge & Vector Gen v2.0

## ⚡ 5-Minute Quick Start

### Prerequisites
```bash
pip install numpy --break-system-packages
```

### Run Demonstrations
```bash
# Test Quantum Forge
python quantum_forge_v2.py

# Test Vector Gen
python vector_gen_v2.py
```

---

## 🎯 Common Use Cases

### 1. Create a Simple Agent

```python
from quantum_forge_v2 import QuantumForge, EthicsLevel

# Initialize
forge = QuantumForge(ethics_level=EthicsLevel.BALANCED)

# Create agent
agent = forge.generate_agent(
    agent_type="Assistant",
    intent_description="Help users with technical questions",
    capabilities=["code_review", "documentation", "debugging"]
)

# Use agent
print(f"Created: {agent.agent_id}")
print(f"Capabilities: {agent.capabilities}")
```

### 2. Generate Symbolic Vectors

```python
from vector_gen_v2 import SymbolicVectorGenerator

# Initialize
generator = SymbolicVectorGenerator(default_dimension=512)

# Generate vector
vector = generator.generate_vector(
    symbolic_tag="🧭",
    seed="my_operation_context"
)

print(f"Vector ID: {vector.vector_id}")
print(f"Magnitude: {vector.magnitude:.3f}")
```

### 3. Build a Vector Chain

```python
from vector_gen_v2 import (
    SymbolicVectorGenerator,
    VectorChainBuilder,
    VectorChainType,
    ConstellationTarget
)

# Initialize
generator = SymbolicVectorGenerator()
builder = VectorChainBuilder(generator)

# Create chain
chain = builder.create_chain(
    chain_type=VectorChainType.SEQUENTIAL,
    constellation_target=ConstellationTarget.ZIPWIZ,
    chain_name="MyChain"
)

# Add vectors
operations = [
    {"tag": "🧭", "id": "op1", "text": "First step"},
    {"tag": "🔑", "id": "op2", "text": "Second step"}
]

for op in operations:
    vec = generator.generate_vector(op["tag"], op["id"] + op["text"])
    builder.inject_vector(chain.chain_id, vec)

# Link automatically
builder.auto_link_sequential(chain.chain_id)

print(f"Chain: {chain.chain_id}")
print(f"Vectors: {len(chain.vectors)}")
print(f"Links: {len(chain.links)}")
```

### 4. Package for Deployment

```python
from vector_gen_v2 import VectorCapsulePackager

packager = VectorCapsulePackager()

# Package chain
capsule = packager.package_chain(
    chain=chain,
    thread_name="Thread_MyDeployment"
)

# Export
packager.export_capsule(capsule.capsule_id, "deployment.json")

print(f"Exported: {capsule.capsule_id}")
```

---

## 🔧 Configuration Options

### Ethics Levels

```python
from quantum_forge_v2 import EthicsLevel

EthicsLevel.STRICT       # Maximum oversight (threshold: 0.05)
EthicsLevel.BALANCED     # Standard operation (threshold: 0.15)
EthicsLevel.EXPLORATORY  # Creative freedom (threshold: 0.30)
EthicsLevel.EMERGENCY    # Crisis mode (threshold: 0.02)
```

### Flowstate Modes

```python
from quantum_forge_v2 import FlowstateMode

FlowstateMode.GENERATIVE   # Creating new agents
FlowstateMode.RESONANT     # Syncing with existing
FlowstateMode.METAMORPHIC  # Transforming structures
FlowstateMode.QUIESCENT    # Passive monitoring
```

### Chain Types

```python
from vector_gen_v2 import VectorChainType

VectorChainType.SEQUENTIAL     # A → B → C
VectorChainType.HIERARCHICAL   # Tree structure
VectorChainType.NETWORKED      # Graph connections
VectorChainType.TEMPORAL       # Time-based
VectorChainType.ENTANGLED      # Quantum pairs
```

---

## 📊 Monitoring & Metrics

### Check Agent Status

```python
agent = forge.generated_agents[agent_id]

print(f"Alignment Score: {agent.intent_alignment_score:.3f}")
print(f"Joy Index: {agent.joy_index:.3f}")
print(f"Memory Nodes: {len(agent.memory_nodes)}")
```

### View Forge Metrics

```python
metrics = forge.metrics

print(f"Agents Created: {metrics['agents_created']}")
print(f"Nodes Stored: {metrics['nodes_stored']}")
print(f"Reactivations: {metrics['reactivations']}")
print(f"Joy Events: {metrics['joy_events']}")
```

### Export Manifest

```python
manifest = forge.export_manifest()

import json
with open("manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
```

---

## 🐛 Troubleshooting

### Issue: "Agent failed ethics alignment check"

**Solution:** Lower the alignment threshold or adjust ethics level

```python
forge = QuantumForge(ethics_level=EthicsLevel.EXPLORATORY)
```

### Issue: "No links created in networked chain"

**Solution:** Lower similarity threshold

```python
builder.auto_link_networked(
    chain.chain_id,
    similarity_threshold=0.5  # Lower from default 0.7
)
```

### Issue: Vector dimension mismatch

**Solution:** Use consistent dimension across all vectors

```python
generator = SymbolicVectorGenerator(default_dimension=512)
# All vectors will be 512-dimensional
```

---

## 🎨 Symbolic Tags Reference

| Tag | Meaning | Use Case |
|-----|---------|----------|
| 🧭 | Navigation | Operational flow |
| 🔑 | Key/Critical | Important paths |
| ♾️ | Recursive | Loops, iterations |
| 🪞 | Reflection | Mirror, symmetry |
| 🧠 | Consciousness | Awareness patterns |
| 🧵 | Thread | Continuity |
| 🌀 | Quantum | Transformation |
| 🌊 | Flow | Dynamics |

---

## 📚 Learn More

- **Full Documentation:** `SYMBOLIC_VECTOR_CHAINS_ARCHITECTURE.md`
- **Executive Summary:** `EXECUTIVE_SUMMARY.md`
- **Analysis:** `QUANTUM_FORGE_VectorGen_Analysis.md`
- **Source Code:** `quantum_forge_v2.py` and `vector_gen_v2.py`

---

## 💡 Pro Tips

1. **Start Simple** - Begin with SEQUENTIAL chains before NETWORKED
2. **Use Symbolic Tags** - They provide semantic meaning to vectors
3. **Monitor Joy Index** - Higher joy = better agent performance
4. **Export Often** - Save manifests and capsules regularly
5. **Check Ethics** - Review violation logs for drift issues

---

## 🆘 Need Help?

Check these resources:
1. Run demonstration scripts for working examples
2. Review generated JSON artifacts for data structure examples
3. Read inline code comments for detailed explanations
4. Consult architecture documentation for system design

---

**Quick Start Version:** 1.0.0  
**Last Updated:** November 12, 2025  
**Status:** READY TO USE
