# CASK — Cultural Awareness & Symbolic Knowledge Module

> **Status**: v1.0 — knowledge-layer data in design phase; Cultural Cognition Framework and Recursive Ethics Validator are runtime-ready.

## Overview

CASK exposes Aurora's cultural-awareness design surface as discoverable JSON endpoints and implements two runtime components from the CASK architecture: the **Recursive Ethics Validator** (Picard_Delta_3 compliant) and the **Cultural Cognition Framework** (sensitivity scorer).

---

## Components

| # | Component | Layer | Status |
|---|-----------|-------|--------|
| 1 | Global Cross-Linguistic Database | knowledge | design |
| 2 | Ethics & Value Systems Index | knowledge | design |
| 3 | Cultural Cognition Framework | knowledge | **runtime** |
| 4 | Historical Institutional Systems | knowledge | design |
| 5 | Language-to-Symbolic Fusion Layer | knowledge | design |
| 6 | Symbolic Vector Chain Compressor (SVCC) | processing | design |
| 7 | GPT Native Encoding Layer | processing | design |
| 8 | Agent Simulation Generation Module | processing | design |
| 9 | Recursive Ethics Validator | validation_runtime | **runtime** |
| 10 | ORION Simulation Runtime | validation_runtime | design |

---

## REST API

All endpoints are read-only (GET). The router is mounted at `/api/cask`.

### `GET /api/cask/topology`

Returns the layered component topology as structured JSON.

```json
{
  "layers": [
    {"id": "knowledge", "label": "Knowledge", "y": 5},
    {"id": "processing", "label": "Processing", "y": 2.8},
    {"id": "validation_runtime", "label": "Validation & Runtime", "y": 0.8}
  ],
  "components": [...],
  "total_components": 10,
  "runtime_components": 2,
  "design_components": 8
}
```

### `GET /api/cask/specs/technical`

Returns technical specification per component as plain JSON records.

```json
{
  "data": [{"Component": "...", "Technical_Specification": "...", ...}],
  "total": 10,
  "source": "technical_specifications"
}
```

### `GET /api/cask/specs/vs-sota`

Returns comparison against state-of-the-art per technical domain.

### `GET /api/cask/specs/risk`

Returns the risk assessment matrix (category, probability, impact, mitigation, priority).

---

## Runtime Components

### Cultural Cognition Framework (`modules/cask/cultural_cognition.py`)

```python
from modules.cask import score_cultural_sensitivity

result = score_cultural_sensitivity(
    "We adapt content for indigenous communities using multilingual approaches.",
    context={"domain": "governance", "num_languages": 3, "target_regions": ["Africa", "Asia"]},
)
print(result.score)   # e.g. 0.42
print(result.level)   # "medium" | "low" | "high"
print(result.positive_matches)
```

**Score bands**: score < 0.3 → `"low"` | 0.3 ≤ score < 0.6 → `"medium"` | score ≥ 0.6 → `"high"`

**Context keys**:
- `domain` — `"governance"`, `"legal"`, or `"ethics"` add +0.05
- `num_languages` — integer ≥ 2 adds proportional bonus (capped +0.10)
- `target_regions` — list; each region adds 0.02 (capped +0.10)

### Recursive Ethics Validator (`modules/cask/recursive_ethics_validator.py`)

```python
from modules.cask import RecursiveEthicsValidator

validator = RecursiveEthicsValidator(max_chain_depth=5)

verdict = validator.validate(
    "generate_agent",
    {"language": "swahili", "region": "east_africa"},
    agent_id="sim_engine_01",
    context_tag="cask_run_20260101T120000",
)

if verdict.blocked:
    raise RuntimeError("Action blocked by ethics chain")

print(verdict.allowed)         # True / False
print(verdict.violation_count) # 0 if clean
```

**Registered rules**:

| Rule ID | Severity | Auto-block | Trigger conditions |
|---------|----------|------------|--------------------|
| `cask_cultural_hegemony` | HIGH | No | `cultural_override`, `value_flattening` |
| `cask_ethics_chain_break` | CRITICAL | **Yes** | `ethics_bypass`, `chain_skip` |
| `cask_bias_injection` | HIGH | No | `bias_detected`, `cultural_bias` |
| `cask_safety_boundary` | CRITICAL | **Yes** | `recursion_depth_exceeded`, `simulation_unsafe` |

Rules are registered into the engine instance used by this validator.  To aggregate violations into the central audit trail, inject a shared `EthicsEngine` configured with a `violations_path`; by default a fresh per-instance engine is created.

---

## Module Layout

```
modules/cask/
├── __init__.py               # Public exports
├── analysis.py               # Static record dicts (specs data, no external deps)
├── api.py                    # FastAPI router (/api/cask)
├── charts.py                 # Plotly topology charts (CLI tool)
├── cultural_cognition.py     # score_cultural_sensitivity()
└── recursive_ethics_validator.py  # RecursiveEthicsValidator
```

---

## Testing

```bash
pytest tests/test_cask_runtime.py -v -m "unit or api"
```
