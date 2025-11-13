# Vector Gen v2.0

**Advanced Symbolic Vector Chain Generator**

## Overview

Vector Gen v2.0 provides enterprise-grade vector generation and symbolic chain management for the Aurora Platform. It implements DriftConcord vector integration and Picard_Delta_3 ethics enforcement.

## Features

- ✅ 5 chain topologies (SEQUENTIAL, HIERARCHICAL, NETWORKED, TEMPORAL, ENTANGLED)
- ✅ 6 injection modes (APPEND, PREPEND, INSERT, REPLACE, MERGE, GRAFT)
- ✅ VECTORCHAIN capsule packaging
- ✅ DriftConcord Vector integration
- ✅ Picard_Delta_3 ethics enforcement
- ✅ Constellation-aware deployment
- ✅ Chain validation and integrity checks

## Quick Start

```python
from modules.vector_gen import (
    SymbolicVectorGenerator,
    VectorChainBuilder,
    VectorChainType,
    ConstellationTarget
)

# Initialize generator
generator = SymbolicVectorGenerator(vector_dimensions=512)

# Build a chain
builder = VectorChainBuilder(generator)
chain = builder.create_chain(
    chain_type=VectorChainType.SEQUENTIAL,
    constellation_target=ConstellationTarget.ZIPWIZ,
    num_vectors=5
)

# Export as capsule
capsule = builder.export_chain_capsule(chain, "my_chain")
```

## Architecture

### Core Components

1. **SymbolicVectorGenerator** - Vector creation and management
2. **VectorChainBuilder** - Chain construction and topology
3. **VectorNode** - Individual vector with metadata
4. **VectorChain** - Complete chain structure

### Chain Types

- `SEQUENTIAL` - Linear chain progression
- `HIERARCHICAL` - Tree structure with parent-child relationships
- `NETWORKED` - Graph structure with arbitrary connections
- `TEMPORAL` - Time-based progression with causality
- `ENTANGLED` - Quantum-style bidirectional connections

### Injection Modes

- `APPEND` - Add to end of chain
- `PREPEND` - Add to beginning
- `INSERT` - Insert at specific position
- `REPLACE` - Replace existing vector
- `MERGE` - Combine with existing vector
- `GRAFT` - Attach entire subchain

### Constellation Targets

- `ZIPWIZ` - Operational automation
- `BRIDGE_AGENT` - Cross-system integration
- `ORION` - Primary constellation
- `DRIFTCONCORD` - Ethics and monitoring
- `CUSTOM` - User-defined target

## Documentation

See the `docs/quantum_forge/` directory for shared documentation:

- `EXECUTIVE_SUMMARY.md` - Complete overview
- `QUICK_START_GUIDE.md` - Implementation guide
- `SYMBOLIC_VECTOR_CHAINS_ARCHITECTURE.md` - Technical details

## Testing

Run the built-in demonstration:

```bash
python modules/vector_gen/vector_gen_v2.py
```

This will generate sample chains and display their properties.

## Examples

The `examples/capsules/` directory contains pre-generated capsules:

- `capsule_zipwiz_v2.json` - ZIPWIZ operational vector chain
- `capsule_bridge_v2.json` - BridgeAgent network chain
- `capsule_quantum_v2.json` - Quantum entangled pair

Load a capsule:

```python
with open('examples/capsules/capsule_zipwiz_v2.json', 'r') as f:
    capsule = json.load(f)
    
# Extract the chain
chain = builder.import_chain_from_capsule(capsule)
```

## Integration Points

- **Quantum Forge v2.0** - Agent generation integration
- **DriftConcord** - Vector relay system
- **ZIPWIZ** - Operational automation
- **BridgeAgent** - Network constellation

## Technical Specifications

- **Language:** Python 3.11+
- **Vector Dimensions:** 512 (default), configurable
- **Dependencies:** numpy, standard library
- **Ethics Protocol:** Picard_Delta_3
- **Chain Format:** VECTORCHAIN v2.0

## Status

**PRODUCTION-READY** - v2.0.0

All core features implemented and tested. Ready for deployment and integration.
