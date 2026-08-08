# Aurora L1 Runtime Contract

**Version:** 1.0.0  
**Date:** 2026-08-08  
**Status:** Runtime contract for governed Orion L1 initialization and advancement  
**Machine-readable baseline:** `config/l1_runtime_baseline.json`  
**Reference implementation:** `simulation/l1_runtime.py`

## Purpose

This contract defines the minimum executable boundary for a live Orion Station
L1 run. It turns the August 7 preflight rulings into machine-testable behavior
without forcing unresolved canon into the simulation.

The live runtime is intentionally separate from two older surfaces:

- `.aurora/SIMULATION_STATE.json` is historical project state, not genesis;
- `simulation/orion_station_simulation_v2.py` is the canonical Phase-1
  institutional/task benchmark, not the whole L1 world.

## Lifecycle

```text
CanonRec authority + CloudBank runtime projection
                    |
                    v
               PREFLIGHT
        read-only validation, tick 0
                    |
                    v
                  INIT
     pinned revisions + seed + quarantines
       unique run ID, still tick 0
                    |
                    v
          AUTONOMOUS ADVANCEMENT
 world process -> records -> observation aperture
                    |
          explicit communications only
                    v
             EARTH-SIDE PILOT
```

Preflight and INIT are distinct. Preflight creates no run. INIT creates the
first advancement-capable run state but performs no advancement itself.

## Authority

CanonRec remains the cross-repository canon authority.

For the staff registry, CloudBank's differing registry is a
`runtime_projection_non_authoritative`. It may carry operationally useful data,
but it cannot overrule CanonRec on canon conflicts.

Run state is lower authority than both. Runtime facts begin as `run_state` and
must not become primary canon without explicit post-run review.

## Pilot boundary

Pilot is an Earth-side institutional operator role.

The runtime enforces:

- `residency = Earth`;
- `l1_entity = false`;
- no automatic station rank or command authority;
- observation controls are instrumentation, not physical motion;
- only explicit communications cross Earth→Orion;
- ambiguous operator text defaults to control-plane handling.

The identity/embodiment authority remains
`AURORA_ARCHITECTURE__ADDENDUM__EARTH_PILOT_L1_BOUNDARY__v1.0__2026-08-07.md`.

## Autonomous-world invariant

Observation must never influence the probability, location, urgency, or
dramatic relevance of world events.

The reference runtime therefore advances its RNG/world process independently of
observation calls. Two runs with the same seed and advancement sequence must
produce the same deterministic event classes even if one is observed more
frequently.

A no-material-event result is valid. The runtime does not manufacture content
to reward attention.

## Input routing

There are two classes of operator input.

### Control-plane input

Examples:

- `continue`
- `observe Deck C`
- `show Engineering`
- `stay with this scene`

Controls may advance the runtime or change the observation aperture. They are
not in-world speech.

### Explicit communications

An Earth→Orion communication must be explicitly typed/routed as a
communication. It enters the communications ledger as queued traffic and does
not automatically become a station action.

The receiving institution may later read, defer, answer, forward, ignore, or
act on the message under its own circumstances and authority.

## Epistemic model

The runtime keeps separate containers/classes for:

1. **world state** — run-level underlying state;
2. **character belief/knowledge** — what one entity believes or knows;
3. **station records** — sensors, logs, messages, institutional records;
4. **runtime observations** — instrumentation selected for exposure;
5. **Pilot knowledge** — information actually exposed to the Earth-side Pilot.

Each `EpistemicRecord` carries:

- record ID;
- subject/value;
- epistemic class;
- provenance;
- confidence;
- tick;
- canon status.

A mistaken character belief is permitted and is not automatically canon drift.
Runtime observation does not automatically become character knowledge.

## Population model

The bootstrap contract distinguishes typed concepts rather than one ambiguous
personnel counter.

Current safe initialization facts:

- 35 identified human records are evidence-supported;
- the inherited 36-human declaration is retired as the Phase-1 off-by-one found
  in issue #1454;
- no missing 36th named person is created;
- the historical `81` value remains a quarantined untyped aggregate pending
  #1455 provenance resolution;
- exact current human complement is therefore not asserted at genesis;
- AI/system entities are counted separately;
- background institutional crew may exist only as provenance-labeled aggregate
  or run state; lack of a biography is not evidence of non-existence.

The `PopulationSnapshot` type also permits a future evidence-supported state in
which, for example, human complement is 81 while identified/persona-resolved
subsets are smaller.

## Orbital-locus quarantine

The repository currently preserves two incompatible literal location claims.
The live runtime does not select either one by convenience.

Until #1456 is reconciled, the only causal-safe runtime statement is:

> Orion is spaceborne and remote from Earth; exact orbital locus is unavailable
> for causal use.

The runtime must not derive communications light-time, orbital lighting,
radiation environment, transfer windows, Earth visibility, docking/navigation
trajectories, or orbital mechanics from either disputed claim.

A quarantined contradiction is acceptable preflight state because it is denied
causal authority rather than silently resolved.

## Governance

Exceptional actionable state changes fail closed unless a `GovernanceReceipt`
contains all three Triplex stages:

1. L3 glyph arbitration;
2. continuity and relay verification;
3. L1 human consent.

The reference runtime verifies this receipt boundary. It does not claim to
execute network/model providers that are not actually wired.

Routine autonomous work may progress under standing institutional authority.

## Persistence and reproducibility

INIT records at minimum:

- unique run ID;
- creation timestamp;
- pinned CloudBank revision;
- pinned CanonRec revision;
- deterministic seed;
- runtime-contract version;
- station-cycle position;
- active quarantines;
- typed population snapshot;
- tick/status.

Run persistence is rejected if the requested run root is inside the repository.
The default is external user state under `~/.aurora/l1-runs`.

Normal runtime activity therefore cannot silently commit or rewrite canon.

## Canon-status boundary

Runtime facts begin as `run_state`.

A run artifact may be marked `candidate_promotion`, which records only a review
nomination. The reference runtime never promotes it to primary canon and never
performs a repository write as a side effect.

Promotion requires a separate review, current-canon conflict check, and normal
repository process.

## Benchmark separation

`OrionSimulationV2` remains the canonical Phase-1 benchmark. It is deliberately
kept as a narrower deterministic component so its historical CORS/CSRF/
WebSocket/eval→AST task graph cannot be mistaken for a new world's genesis.

This separation is structural, not cosmetic:

- benchmark tests exercise task simulation;
- L1 runtime tests exercise lifecycle, observation, epistemics, Pilot boundary,
  quarantines, persistence, and governance.

## Preflight-clearing criteria

The live L1 path is INIT-eligible when:

- CanonRec authority is explicit;
- staff authority no longer waits on an owner decision;
- Pilot cannot be embodied;
- the false missing-human claim is inactive;
- ambiguous historical population data is typed/quarantined;
- the orbital conflict is quarantined from causality;
- legacy `SIMULATION_STATE.json` is non-genesis;
- Phase-1 benchmark wiring points to v2;
- live L1 runtime is distinct from that benchmark;
- Picard_Delta_3 / Triplex exceptional-action policy fails closed;
- preflight leaves tick 0 and creates no run.

Warnings may remain for quarantined uncertainty. Warnings are not blockers when
the runtime cannot use the uncertain field causally.
