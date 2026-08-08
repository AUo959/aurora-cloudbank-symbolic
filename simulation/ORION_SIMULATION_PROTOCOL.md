# Orion Station Phase-1 Benchmark Protocol

**Version:** 2.0  
**Updated:** 2026-08-08  
**Status:** Canonical deterministic benchmark component

## Purpose

This protocol standardizes the historical Phase-1 Orion institutional/task
benchmark. It is useful for deterministic regression testing of assignment,
collaboration, and emergent-event mechanics.

The legacy `fatigue` field remains only as non-evaluative compatibility state.
It must never affect task assignment, work speed, progress, completion, scores,
or any other evaluation surface.

It is **not** the live Orion L1 world runtime and is **not** the INIT entry
point. Live L1 initialization is governed by `.aurora/SIMULATION_INIT_PROTOCOL.md`
and implemented by `simulation/l1_runtime.py`.

## Canonical implementation

Use:

```bash
python simulation/orion_station_simulation_v2.py --seed 1337 --ticks 20 --no-emergent
```

Canonical class:

```python
OrionSimulationV2
```

Canonical module:

```text
simulation/orion_station_simulation_v2.py
```

`simulation/orion_station_simulation.py` is the superseded v1 implementation.
It may remain temporarily for historical compatibility, but tests, demos, and
documentation must not designate it as active.

## Why v2 is canonical

- it loads characters from `L1_CANON_CHARACTER_ROSTER.md` rather than using the
  original hard-coded profile set;
- it supports the expanded character registry;
- it includes canonical specialization/collaboration data;
- it received maintained behavioral fixes after v1 stopped receiving
  substantive changes;
- repository history already resolved the v1/v2 designation in favor of v2.

## Benchmark task set

The benchmark intentionally preserves the historical Phase-1 security tasks:

- T1 — CORS Fix
- T2 — CSRF Validation
- T3 — WebSocket Auth
- T4 — Replace `eval()` with AST

These tasks are a regression fixture. Their presence does not mean a newly
initialized live Orion Station run begins by replaying this old project sprint.

## Reproducibility

- `--seed <int>` controls deterministic RNG behavior.
- `--ticks <int>` sets the maximum benchmark length.
- `--no-emergent` disables stochastic emergent events.
- `--transcript-out <path>` writes a benchmark transcript.
- `--json-out <path>` writes a result summary.

Example:

```bash
python simulation/orion_station_simulation_v2.py \
  --seed 1337 \
  --ticks 20 \
  --no-emergent \
  --transcript-out /tmp/orion-phase1.txt \
  --json-out /tmp/orion-phase1.json
```

## Success criteria

- `completed == True`
- completed task IDs are exactly `T1`, `T2`, `T3`, `T4`
- deterministic runs are reproducible for the same seed/configuration
- first-tick working-agent emergence remains possible when emergent events are
  enabled
- canonical character names are used

## Authority boundary

The benchmark may generate transcript text and task outcomes, but those outputs
are benchmark/run artifacts, not primary Orion canon.

The live L1 runtime has additional invariants that this benchmark does not own:

- Earth-side Pilot boundary;
- discovery-through-observation;
- explicit epistemic-state separation;
- population/persona semantics;
- canonical Lagrange-point siting with exact-point quarantine;
- run lifecycle and canon-promotion boundary;
- Triplex fail-closed authorization for exceptional actionable changes.

Do not expand this benchmark into the general world runtime by accretion. Those
responsibilities belong to `simulation/l1_runtime.py` and its runtime contract.

## Related files

- `simulation/orion_station_simulation_v2.py`
- `simulation/character_loader.py`
- `tests/test_orion_simulation.py`
- `simulation/interactive_collab_demo.py`
- `.aurora/SIMULATION_INIT_PROTOCOL.md`
- `simulation/l1_runtime.py`
