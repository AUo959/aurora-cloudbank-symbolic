# Aurora L1 Runtime Contract

**Version:** 1.2.0
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

Fleet identity is currently a CloudBank
`runtime_projection_non_authoritative`, governed by
`config/l1_fleet_authority_receipt.json`. The active projection selects the
ORF/ORS/ORP/ORD identity surface in `src/entities/fleet/`. Detailed
`simulation/fleet/` records remain design provenance, and their dated 2025
missions, coordinates, assignments, and counters are not current 2026 run
state. The conflicting Dark Matter aggregate at `.aurora/canonical/fleet.json`
is legacy provenance only.

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

Fleet advancement is a second deterministic world process namespaced by seed,
fleet identity, and tick. It does not consume observation state or the station
event generator's replay position. It advances only qualitative mission,
status, proximity, and docking/location classes; exact trajectories and
coordinates remain quarantined.

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

Queued traffic is not delivered in the same tick. The runtime records delivery
only after a positive advancement window, using the approximate nonzero latency
model described below. Delivery becomes a station record; it is not itself a
reply or evidence that the named recipient has acted.

The receiving institution may later read, defer, answer, forward, ignore, or
act on the message under its own circumstances and authority.

### Bounded character causality

The reference implementation provides one initial character actor for
Commander Alex Thorne (`CMD_001`). The actor is bounded by a
`runtime_projection_non_authoritative` profile in
`config/l1_character_actor_profiles.json`; that projection consumes canon and
cannot amend it.

For each delivered message explicitly addressed to `CMD_001`, the actor must:

1. validate its identity and behavioral anchors against repository authority;
2. construct an actor-local context from the inbound message, station records,
   Alex's character knowledge, recent events, prior Alex actions, and explicit
   unresolved facts;
3. classify the request and select a concrete command action;
4. record duties, principles, evidence, gaps, alternatives, rationale,
   operational steps, and commitments in a character-action receipt;
5. persist that receipt before queuing the response; and
6. link the response to the receipt with `caused_by_action_id`.

The actor-local context must not include runtime observations, Pilot-position
knowledge, or operator personal knowledge. Observation therefore cannot cause
Alex to know, notice, or say something. A later Alex decision may consider his
own prior active commitments, allowing bounded continuity without converting
run state into biography.

`bounded_character_action_v1` is deterministic and auditable. It does not use
free-form model improvisation. Different message meanings may select different
actions, but claims in the rendered response remain limited to the actor's
available evidence. The current scope does not claim general agency for every
character.

The character-action receipt and the spoken response have a strict one-way
boundary. Audit fields such as canon status, profile projection, runtime state,
knowledge gaps, policy identifiers, and observation bookkeeping may constrain
what Alex is allowed to claim, but they are not facts in Alex's lived L1 frame
and MUST NOT be rendered as his dialogue. A missing or unresolved audit fact is
normally expressed through omission, not by having Alex explain the runtime's
uncertainty. The response renderer receives only the selected action, relevant
station event, prior character commitments, and the canon-bounded voice opening.
Known control-plane phrases fail the L1 speech boundary closed.

Alex's L1 profile uses the authoritative roster projection: Station Commander,
Command & Ethics, `L4_COMMAND`. Conflicting legacy descriptions of `L5_COMMAND`
or a workspace project-manager/system-architect role are not inputs to this L1
actor. A source conflict or missing roster anchor fails actor construction
closed.

## Epistemic model

The runtime keeps separate containers/classes for:

1. **world state** — run-level underlying state;
2. **character belief/knowledge** — what one entity believes or knows;
3. **station records** — sensors, logs, messages, institutional records;
4. **runtime observations** — instrumentation selected for exposure;
5. **Pilot knowledge** — information actually exposed to the Earth-side Pilot.
6. **character actions** — auditable decisions produced from one character's
   bounded information aperture and linked to any resulting communication.

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

## Fleet state and observation providers

`L1RunState.fleet` carries typed state for each projected asset:

- identity and display name;
- asset class and autonomy class;
- run-scoped status and mission-state class;
- qualitative docking/location class;
- authority receipt and source provenance;
- deterministic fleet-process replay position.

The fleet, proximity, docking, and drone observation providers read this state
without advancing it. A bound provider returns `available` with the receipt and
projection role. An unbound provider returns
`unavailable / provider_unbound`; it must never turn missing provider data into
a claim that no craft are active. Exact range, docking bay, and navigation
trajectory remain unavailable.

ORD policy and physical flight are separate domains. `modules/ord/` may create
an MCP-validation `DispatchOrder`, but the order has no physical effect. The
explicit ORD-to-L1 adapter first creates a non-executing proposal; physical
drone mission state changes only after a separate call supplies a complete
Triplex governance receipt.

Restoration applies the same boundary to persisted state. Every active
`active_explicit_adapter` entity must match one exact fleet transition, a
complete Triplex receipt named by that transition, and the corresponding
governed activation event. A syntactically valid ORD mission state without
that linked evidence is rejected rather than exposed as resumed physical
state.

## Lagrange-point authority and remaining uncertainty

CanonRec's owner ruling establishes the current siting class:

> Orion Station is stationed at a Lagrange point in real space.

The historical `38,600 km` value is a STAGING parameter and is not current
siting authority. The historical `Earth-Moon L4` value remains a named
candidate, not exact current canon. Issue #1456 therefore remains open only for
the exact libration point, primary-body system, range, and exact derived
parameters.

The runtime uses the canonical Lagrange-point class and CanonRec's explicitly
approximate, nonzero one-way communications model. A message queued at one tick
is delivered only after a positive advancement window. Exact communications
light-time, orbital lighting, radiation environment, transfer windows, Earth
visibility, docking/navigation trajectories, and orbital mechanics remain
quarantined until the exact point is reconciled.

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
- exact SHA-256 of the fleet authority receipt bytes retained at INIT;
- station-cycle position;
- active quarantines;
- typed population snapshot;
- the fleet authority receipt, typed fleet projection, and fleet replay
  position;
- tick/status.

Contract `1.2.0` accepts persisted `1.1.0` continuation states from PR #1480.
When their fleet field is absent, the runtime reconstructs it from seed plus the
contiguous autonomous-event ledger without advancing the tick, station cycle,
or central replay generator. The verified current fleet-receipt digest is
attached to that in-memory upgrade. The upgraded state is persisted only on a
later explicit run mutation, including advancement, governed action, or the
normal recording of an observation into the run-scoped epistemic ledgers.
Loading by itself remains non-mutating.

Current-contract persisted runs with a fleet-receipt digest must match the
receipt bytes verified by preflight. A `1.2.0` state created before the digest
field was introduced may bind the verified digest in memory only after its
complete bound fleet projection and governed ORD adapter evidence pass current
validation. Loading remains non-mutating; the digest is persisted only by a
later explicit run mutation. A present but mismatched digest is always rejected.

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
- the fleet authority receipt and all hashed sources match;
- historical fleet missions cannot seed current run state;
- ORD MCP policy cannot become physical flight without the explicit adapter;
- preflight leaves tick 0 and creates no run.

Warnings may remain for quarantined uncertainty. Warnings are not blockers when
the runtime cannot use the uncertain field causally.
