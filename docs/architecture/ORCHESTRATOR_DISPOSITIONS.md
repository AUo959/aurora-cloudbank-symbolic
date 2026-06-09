# Orchestrator Dispositions

**Issue**: #777 — Decide fate of shell orchestrators  
**Resolved**: 2026-06-09

This document records the production disposition of each orchestrator class
identified in issue #777.

---

## Summary

| Orchestrator | Module | Disposition | Production entry point |
|---|---|---|---|
| `UnifiedAIInterface` | `modules/ai_core/unified_ai_interface.py` | **Wired** | `POST /api/ai/complete`, `GET /api/ai/models` |
| `SystemFlowOrchestrator` | `modules/quantum_forge/system_flow_orchestrator.py` | **Wired** | `GET /api/quantum-forge/flow/status`, `POST /api/quantum-forge/flow/optimize` |
| `HybridQuantumOrchestrator` | `modules/nexus/quantum/hybrid_orchestrator.py` | **Wired-internally** | Via `modules/nexus/quantum/recursion_bridge.py` |
| `MultiDimensionalOrchestrator` | `modules/nexus/multidim/dimensional_orchestrator.py` | **Demoted** | Non-production; see `examples/orchestrators/multidim_example.py` |

---

## Details

### `UnifiedAIInterface` — Wired

**Endpoints added** (see `api/aurora_api.py`):
- `POST /api/ai/complete` — complete a prompt; auto-selects model by `task_type`
- `GET /api/ai/models` — list models and capability profiles

**Supported task types**: `general`, `reasoning`, `code_generation`, `analysis`
(resolved against `FALLBACK_CHAINS` in `UnifiedAIInterface`).

Gracefully disabled if `modules.ai_core` cannot import (logs a warning, endpoints return 404).

---

### `SystemFlowOrchestrator` — Wired

**Endpoints added** (see `api/aurora_api.py`):
- `GET /api/quantum-forge/flow/status` — returns `export_flow_manifest()`: current phase, module health, drift count
- `POST /api/quantum-forge/flow/optimize` — triggers `auto_optimize_system()` pass (auth required)

Gracefully disabled if `modules.quantum_forge` cannot import.

---

### `HybridQuantumOrchestrator` — Wired-internally

`HybridQuantumOrchestrator` is imported by `modules/nexus/quantum/recursion_bridge.py`,
which constitutes its production path. It is not directly exposed as a REST endpoint.

No code changes needed; disposition documented in the module docstring.

---

### `MultiDimensionalOrchestrator` — Demoted

No production API caller exists. The class uses "consciousness" terminology and
makes assumptions (e.g. `unified_consciousness = 0.99`) that are not grounded in
the Aurora production data model.

**Changes made**:
- Module docstring updated with `DISPOSITION: non-production / experimental`
- `__init__` emits a `warnings.warn(...)` at instantiation
- Example usage: `examples/orchestrators/multidim_example.py`

No production code imports this class; no further migration required.
