# Aurora CloudBank — Orion L1 INIT Protocol

**Version:** 2.1.0
**Last Updated:** 2026-08-08  
**Purpose:** Governed, reproducible initialization of a live Orion Station L1 run

---

## Authority and scope

This protocol replaces the legacy rehydration flow that treated
`.aurora/SIMULATION_STATE.json` as live genesis state.

The supported entry point is:

```bash
python .aurora/init_l1.py preflight
python .aurora/init_l1.py init --seed 1337
```

The machine-readable bootstrap contract is `config/l1_runtime_baseline.json`.
The live runtime implementation is `simulation/l1_runtime.py`.

The historical `.aurora/load_simulation.py` / `SIMULATION_STATE.json` path is
retained for provenance and compatibility investigation only. It is not the
L1 genesis authority.

---

## Core invariants

1. **Preflight does not advance L1.** It creates no run and leaves tick at 0.
2. **INIT creates a tick-zero run.** INIT itself does not simulate an event.
3. **Pilot remains on Earth.** Pilot is an institutional operator role, not an
   Orion character, avatar, visitor, camera-person, or automatic command seat.
4. **Observation is instrumentation.** Observation focus never moves Pilot into
   L1 and never causes events merely because they are watched.
5. **Communications are explicit.** Ambiguous operator text is control-plane
   input by default; only explicitly routed communications cross Earth→Orion.
6. **Orion is autonomous.** World processes advance independently of Pilot
   attention or silence.
7. **Epistemic states are distinct.** World truth, character belief, station
   records, runtime observation, and Pilot knowledge are not interchangeable.
8. **Run state is not primary canon.** Runtime-derived facts remain run-scoped
   unless separately reviewed and promoted.
9. **Resolved canon is projected precisely.** Orion's Lagrange-point siting is
   causal-safe; only the exact point/system and exact derived parameters remain
   quarantined.
10. **Actionable exceptional changes fail closed.** A complete Triplex receipt
    is required before `simulation/l1_runtime.py` applies a governed action.
11. **Normal runtime persistence stays outside the repository.** Ordinary L1
    operation does not write GitHub canon.

---

## Phase 0 — Preflight

Run:

```bash
python .aurora/init_l1.py preflight
```

Preflight validates, without creating a run:

- CanonRec is the cross-repository canon authority;
- the staff-registry boundary has an explicit authority decision;
- Pilot is Earth-side and non-embodied;
- the false `36th named human` claim is retired;
- ambiguous historical population counters are typed/quarantined;
- CanonRec's Lagrange-point siting ruling is active;
- exact-point and exact-light-time uncertainty remains narrowly quarantined;
- `.aurora/SIMULATION_STATE.json` is not genesis authority;
- `simulation/orion_station_simulation_v2.py` is the canonical Phase-1
  benchmark component;
- the benchmark is not mistaken for the entire live L1 world runtime;
- Picard_Delta_3 / Triplex fail-closed governance is active in the runtime
  contract.

A successful report contains:

```json
{
  "ready": true,
  "blockers": [],
  "tick": 0,
  "run_created": false
}
```

Warnings are permitted when an uncertainty is formally quarantined and cannot
influence causality. Warnings must not be silently converted into facts.

---

## Phase 1 — INIT

Run:

```bash
python .aurora/init_l1.py init --seed 1337
```

INIT:

1. re-runs preflight;
2. pins the exact CloudBank git revision;
3. pins the CanonRec revision/source boundary;
4. records the deterministic runtime seed;
5. records the runtime-contract version;
6. records the population snapshot and active quarantines;
7. creates a unique run ID;
8. creates a run state at **tick 0**;
9. persists the run outside the repository;
10. performs **no station advancement**.

The resulting run is advancement-capable but still at genesis.

---

## Phase 2 — Autonomous advancement

A live turn is a simulation advancement boundary, not a player turn.

The order is:

1. advance applicable autonomous world processes by plausible elapsed time;
2. propagate consequences and station records;
3. expose an observation aperture if requested;
4. process explicit Earth-side communications separately;
5. continue independently of Pilot attention.

Elapsed time is variable. It is not implicitly one hour.

A quiet advancement window is valid. The runtime must not manufacture drama,
character availability, emergencies, discoveries, or convenient explanations
for engagement.

Persisted runs continue through the governed continuation entry point:

```bash
python .aurora/run_l1.py status --run-id <uuid>
python .aurora/run_l1.py sensors --run-id <uuid>
python .aurora/run_l1.py advance --run-id <uuid> --minutes 1
python .aurora/run_l1.py await-response --run-id <uuid> \
  --message-id <uuid> --minutes 1 --max-windows 4
```

Continuation restores the deterministic replay position from the persisted
autonomous-event ledger. It rejects malformed run identifiers, mismatched
manifest paths, unsupported schemas, and runtime-contract or CanonRec drift.

The `sensors` command reports live simulation-ledger telemetry only. Unbound
physical channels remain explicitly unavailable; their framework defaults are
not presented as live readings. The accompanying logical schematic projects
only causal-safe topology. Historical deck layouts that conflict with current
locus, population, or Earth-side Pilot rulings remain reference-only.

---

## Observation controls

Examples of control-plane inputs:

- `continue`
- `observe Deck C`
- `show Engineering`
- `stay with this scene`

These affect runtime exposure only. They are not physical Pilot actions.
Observation may reveal instrumentation unavailable through ordinary station
communications, but such output must be labeled as instrumentation.

Observation does not change autonomous event probability.

---

## Earth→Orion communications

A communication must be explicitly routed as a communication.

A Pilot message:

- originates on Earth;
- is queued/routed as communications traffic;
- does not automatically become an L1 action;
- may be read, deferred, forwarded, answered, ignored, or acted upon according
  to Orion's institutional circumstances and authority;
- grants no implied rank or command authority to the sender.

The runtime uses CanonRec's provenance-labeled approximate, nonzero one-way
latency model. A queued message is not delivered at the same tick; it becomes a
station record only after a positive advancement window. This models elapsed
time without pretending the unresolved exact range or exact light-time is
known.

A station response is a separate communication. The initial deterministic
response policy is restricted to Commander Alex Thorne (`CMD_001`) and to
delivered traffic explicitly addressed to that endpoint. It reports only
run-ledger facts, records the utterance as run-scoped testimony, and requires a
later positive advancement window before delivery to Earth. The policy does not
promote testimony into canon or let Pilot dictate the response text.

Ambiguous text must not silently become transmitted speech.

---

## Population baseline

The runtime distinguishes population concepts rather than collapsing them into
one counter.

Current safe baseline:

- **35 identified human records** are evidence-supported;
- the inherited **36-human declaration is a retired Phase-1 off-by-one**, not a
  missing-person requirement;
- the historical `81` value is retained only as a quarantined, untyped
  aggregate pending its population-schema provenance work;
- exact current human complement is therefore not asserted at INIT;
- AI/system entities are counted separately from humans;
- lack of a resolved persona does not imply non-existence;
- no identities or biographies may be fabricated merely to satisfy an
  aggregate count.

See `config/l1_runtime_baseline.json` and issue #1454/#1455 provenance.

---

## Lagrange-point siting and exact-point quarantine

CanonRec's owner ruling resolves the current siting class:

> **Orion Station is stationed at a Lagrange point in real space.**

The historical `38,600 km` datum is STAGING and is not current siting
authority. `Earth-Moon L4` remains a historical named candidate, not exact
current canon. Issue #1456 remains open for the narrower question of the exact
libration point and primary-body system.

The runtime may therefore use Lagrange-point siting and a provenance-labeled
approximate nonzero communications latency. It must not claim exact
communications light-time, orbital lighting, radiation environment, transfer
windows, Earth visibility, docking/navigation trajectories, or orbital
mechanics until the exact point is reconciled.

---

## Governance

The runtime contract uses **Picard_Delta_3** and fails closed for exceptional
state-changing actions unless a complete Triplex receipt records:

1. L3 glyph arbitration;
2. continuity and relay verification;
3. L1 human consent.

`simulation/l1_runtime.py` does not pretend to execute unavailable external
providers. It verifies the receipt boundary and rejects incomplete actionable
mutations.

Routine autonomous processes may proceed under standing institutional authority
when they do not cross an exceptional governance boundary.

---

## Historical Phase-1 benchmark

`simulation/orion_station_simulation_v2.py` is the canonical implementation of
the deterministic Phase-1 task benchmark.

It supersedes `simulation/orion_station_simulation.py` and remains valuable for
reproducible institutional/task modeling. It is **not** the live Orion L1 world
runtime and is not the INIT entry point.

See `simulation/ORION_SIMULATION_PROTOCOL.md`.

---

## Canon promotion boundary

Normal runtime activity performs no repository mutation.

Run-derived facts use run-scoped status. A runtime artifact may be nominated as
a `candidate_promotion`, but promotion into primary canon requires a separate
review/conflict-check workflow. A compelling narrative is not canon authority.

---

## Validation checklist

Before issuing INIT:

- [ ] `python .aurora/init_l1.py preflight` returns `ready: true`
- [ ] blocker list is empty
- [ ] tick remains 0
- [ ] no run has been created by preflight
- [ ] Pilot is Earth-side and non-embodied
- [ ] CanonRec authority boundary is explicit
- [ ] false 36th-person claim is inactive
- [ ] Lagrange-point siting authority is active
- [ ] exact point/system uncertainty is narrowly quarantined
- [ ] communications require a positive advancement window
- [ ] legacy state is non-genesis
- [ ] canonical Phase-1 benchmark is v2
- [ ] Triplex fail-closed policy is present

After INIT:

- [ ] a unique run ID exists
- [ ] CloudBank and CanonRec revisions are pinned
- [ ] seed is persisted
- [ ] tick is exactly 0
- [ ] event ledger is empty
- [ ] run persistence is outside the repository

---

## Related documents

- `config/l1_runtime_baseline.json`
- `simulation/l1_runtime.py`
- `docs/architecture/AURORA_L1_RUNTIME_CONTRACT.md`
- `docs/architecture/AURORA_ARCHITECTURE__ADDENDUM__EARTH_PILOT_L1_BOUNDARY__v1.0__2026-08-07.md`
- `docs/CANON_PROVENANCE.md`
- `simulation/ORION_SIMULATION_PROTOCOL.md`
- `CANON_INDEX.md`
