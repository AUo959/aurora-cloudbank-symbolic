# Symbolic Data Architecture

**Status:** Scoped architecture reference

**Authority boundary:** This document describes the Vector Symbolic Architecture (VSA) data surface. For the canonical L1/L2/L3 residency and operational-scope model, use [`LAYER_ARCHITECTURE.md`](LAYER_ARCHITECTURE.md).

## VSA data layer

Aurora represents symbolic values as high-dimensional vectors through [`modules/symbolic_core/vsa.py`](../../modules/symbolic_core/vsa.py). The implementation provides deterministic vector construction and symbolic operations including binding, superposition, and similarity.

The repository also contains related implementations for quantum-enhanced and native vector paths. Their shared terminology does not make them interchangeable; callers and tests determine which implementation is active on a given runtime path.

## Schema surface

[`schemas/symbolic_core_symbolicvector.schema.json`](../../schemas/symbolic_core_symbolicvector.schema.json) defines the repository's JSON Schema representation for a `SymbolicVector`. It records the symbolic label, dimension, and bipolar vector payload.

The schema is a validation contract, not evidence that every REST or WebSocket endpoint currently emits that shape. Verify endpoint conformance against the active route implementation, generated API inventory, and tests before making a runtime-wide claim.

The earlier narrative schema guide is retained under [`docs/archive/symbolicvector_api_schema.md`](../archive/symbolicvector_api_schema.md) for historical context only.

## Extension points

Symbolic, quantum, and geometric modules expose several integration surfaces. New integrations should:

1. name the concrete vector implementation they consume,
2. validate serialized payloads against the applicable schema,
3. preserve DLP context and layer boundaries, and
4. add executable tests for the route or adapter being changed.

## References

- [`modules/symbolic_core/vsa.py`](../../modules/symbolic_core/vsa.py)
- [`modules/symbolic_core/quantum_symbolic_vector.py`](../../modules/symbolic_core/quantum_symbolic_vector.py)
- [`src/core/native_vsa.py`](../../src/core/native_vsa.py)
- [`schemas/symbolic_core_symbolicvector.schema.json`](../../schemas/symbolic_core_symbolicvector.schema.json)
