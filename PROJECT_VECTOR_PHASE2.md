# Aurora CloudBank Symbolic: Optimized Project Vector (Phase 2 Launch)

## Context
- Date: 2025-06-25
- Repo: aurora-cloudbank-symbolic
- Stage 1: Complete (robust symbolic core, type-safe, extensible, tested)

---

## Optimized Project Vector (Phase 2)

### 1. Quantum & Geometric Prototyping
- **Quantum Module**: Prototype a minimal quantum-inspired symbolic module (VSA/HD computing) using Python and Qiskit or PennyLane.
- **Geometric Algebra Utility**: Add a utility module for geometric algebra (e.g., using the `clifford` Python library).
- **Plugin System**: Refactor agent/simulation modules to support plugin-based solvers (classical, quantum, geometric).

### 2. Actionable Steps
- [ ] Create `quantum_symbolic.py` in `modules/symbolic_core/` for quantum-inspired symbolic ops (Qiskit/PennyLane backend).
- [ ] Create `geometric_algebra.py` in `modules/symbolic_core/` for geometric algebra utilities (Clifford algebra).
- [ ] Define abstract base class `SymbolicSolverPlugin` for plugin system in `modules/symbolic_core/plugin.py`.
- [ ] Refactor core agent/simulation logic to use plugin registry/discovery.
- [ ] Add tests for quantum and geometric modules in `tests/`.
- [ ] Update docs: architecture, extension points, and API schemas.

### 3. Dependencies
- [ ] Add `qiskit` and/or `pennylane` to `requirements.txt` (quantum)
- [ ] Add `clifford` to `requirements.txt` (geometric algebra)

### 4. Milestones
- **M1:** Minimal quantum symbolic prototype (unit tested)
- **M2:** Minimal geometric algebra utility (unit tested)
- **M3:** Plugin system skeleton and demo plugin
- **M4:** Documentation and API schema update

---

## Next: Begin with Quantum & Geometric Prototyping (Phase 2, Step 1)
- Proceed to create quantum and geometric modules, then implement plugin skeleton.
