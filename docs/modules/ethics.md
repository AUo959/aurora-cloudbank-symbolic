# Ethics Module

**Status:** Implemented across multiple runtime surfaces
**Layer:** L3 policy and continuity overlay, enforced across L1 and L2
**Authority:** Runtime code and tests

## Purpose

The Ethics module evaluates proposed actions, blocks configured violations,
records audit evidence, and preserves autonomy, consent, layer integrity,
collective welfare, and transparency. It is a family of coordinated surfaces,
not one interchangeable engine.

## Current Surfaces

| Surface | Role |
|---|---|
| [`src/monitoring/ethics_engine.py`](../../src/monitoring/ethics_engine.py) | Local rule evaluation and violation records |
| [`src/monitoring/ethics_gate.py`](../../src/monitoring/ethics_gate.py) | Fail-closed inline action gate |
| [`modules/gumas/api/routes.py`](../../modules/gumas/api/routes.py) | GUMAS ethics HTTP routes, including `/gumas/evaluate` |
| [`src/aurora/ethics/ethics_gate.py`](../../src/aurora/ethics/ethics_gate.py) | Adapter that normalizes GUMAS verdicts for relay and compliance callers |
| [`modules/ethics_field/`](../../modules/ethics_field/) | Five-dimension geometric ethics evaluation |

The two files named `ethics_gate.py` serve different call paths. Their shared
name does not make their policy or callers interchangeable.

## GUMAS and Picard_Delta_3

The GUMAS adapter sends evaluation requests to `/gumas/evaluate` and attaches
DLP and anchor evidence. The machine-executable Picard_Delta_3 dimension is
[`modules/ethics_field/dimension_evaluators/picard_delta_3.py`](../../modules/ethics_field/dimension_evaluators/picard_delta_3.py).
References to Picard_Delta_3 elsewhere may be governance anchors only; they do
not prove that this evaluator runs on that call path.

## Related References

- [`docs/ethics/README.md`](../ethics/README.md) — ethics authority and status map
- [`docs/GEOMETRIC_ETHICS_ARCHITECTURE.md`](../GEOMETRIC_ETHICS_ARCHITECTURE.md) — geometric v1 architecture
- [`docs/architecture/LAYER_ARCHITECTURE.md`](../architecture/LAYER_ARCHITECTURE.md) — L1/L2/L3 terminology
- [`QGIA_Integration/01_QUANTUM_FORGE_AxiomManifest.md`](../../QGIA_Integration/01_QUANTUM_FORGE_AxiomManifest.md) — complementary QGIA doctrine nodes, not automatic runtime wiring

## Validation

Focused evidence includes `tests/test_ethics_engine.py`,
`tests/test_monitoring_ethics_gate.py`, `tests/test_ethics_gate.py`,
`tests/test_gumas_ethics.py`, and `tests/test_ethics_field.py`.
