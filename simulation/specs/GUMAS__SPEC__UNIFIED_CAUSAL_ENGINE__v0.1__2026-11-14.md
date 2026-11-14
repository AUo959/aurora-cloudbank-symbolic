# GUMAS Unified — Causal Field Engine (P0 research contract)

**Version:** 0.1 | **Date:** 2026-11-14 | **Status:** PROPOSED / SYNTHETIC / L2-ONLY
**Provenance:** Design response to cross-scale causal-coherence discussion.
**Authority:** No CanonRec promotion, no L1/THREADCORE write authority.

## Why this exists

The current GUMASAdvancedEngine advances legacy political state plus Forge v3 population,
technology, negotiation, intelligence and rebellion phases. CloudBank PR #1506 adds a
separate deterministic tactical macrostep and authoritative combat ledger, while root
PR #85 proposes persistent ACE worlds and characters. These are not yet one
causally consistent multi-resolution world. No blanket renaming or silent merge is
authorized. P0 establishes a **new isolated research runtime** with a demonstrable
cross-scale invariant, not a replacement for any existing engine.

## Fundamental model

- Underlying simulated reality: an L2 World/Universe state X.
- An individual action is checked against the field of feasible physical actions.
- Institutional authorization is *not* a physical feasibility rule; rule-breaking
  actions may occur and are labeled as such.
- Micro (actor/site), meso (route/world), and macro (polity) views are projections
  of one committed state. Actor-specific information arrives only on an allowed path.
- A deterministic commit ledger records before/after state hashes, event causation,
  effective simulation time, effect metadata and hash-chain linkage.
- No state transition can directly create goods/energy; converted energy is
  represented as heat. These accounting invariants apply only to represented
  physical quantities, not legitimacy, trust, stability, or social entropy.

## P0 implementation (actual)

Package: simulation/runtime/gumas_unified/

1. PhysicsProfile: integer ceiling on signal/cargo velocities, in km/s.
   P0 uses an explicitly sublight setting (signal speed <= 299,792 km/s).
   Canonical FTL technologies are NOT modeled; they require a separately
   authorized, provenance-bound physical/technology profile.
2. Universe: integer simulation seconds; sites, actors, corridors, in-flight
   shipments, scheduled arrivals, energy-to-heat account, per-window route capacity.
3. CausalEngine: copy-validate-commit with a defensive snapshot getter;
   local dispatch, signal transmission, physical route disruption (synthetic
   fixture provenance only), discrete-event time advancement, site/polity/actor
   projections, and reproducible chain-linked receipts.
4. Political read-only adapter: accepts the serialized factions map used by
   the legacy GUMASState model, and projects legacy score fields for comparison.
   It never treats normalized political indices as physical supplies, and does
   not execute or import the older engine.
5. Synthetic corridor fixture: two sites in different polity frames, an
   identified governor and a remote observer, an infrastructure disruption,
   divergent individual choices, a delayed message, and transport arrival.

## Non-negotiable P0 invariants and measurements

- Physical possibility: missing corridor, unattainable capacity, remote
  actuation or insufficient cargo/energy rejects atomically.
- Time/cause: all actions have simulation seconds and a nonempty cause reference.
  A message cannot arrive before distance / signaling speed.
- Accounting: supplies at sites + supplies in transit remain constant;
  energy at sites + waste heat remains constant in the closed fixture.
- Projection: macro quantities are derived from committed local state, not
  independently updated. Incoming goods are distinct from available goods.
- Agency: chosen dispatch versus hold creates different physical histories;
  a policy-unauthorized but physically feasible action remains possible.
- Provenance: same initial state and choice sequence yields identical evidence;
  receipt hashes and links can be checked without involving wall-clock time.
- Isolation: synthetic L2 only, no external I/O, no L1 writes, no canon mutation.

## Explicit limitations / deferred contracts

P0 is a **minimal acceptance vertical slice**, not a production galaxy engine:
- It uses one-hop directed corridors, fixed speeds, integer commodity units,
  a closed two-site economy and an explicit scripted actor choice. It has no
  full transport routing, local physics solver, biology, orbital mechanics,
  general supply/demand market, autonomous actor decision policy, or source
  of stochastic shocks.
- State is in-memory. Snapshot/checkpoint persistence, concurrency controls,
  transactional I/O, crash recovery, signatures and full executable replay
  are future gates. The SHA256 ledger detects accidental tampering but is
  NOT a signed security boundary or proof that an event was physically executed.
- Same-input re-execution of the synthetic script is checked; rehydrating a
  transition history from receipts is not implemented. Hash verification is
  not equivalent to state transition replay.
- P0 site inventory is held by a site; group institutions, property rights,
  accessibility of stockpiles, coercion, injuries and legal consequences need
  modeled actors and processes. For now physical local access is a synthetic
  simplification; do not claim realistic seizures.
- Political data is observed read-only through the adapter. L2 political
  state is NOT integrated as an active mutator.
- ACE #85, CloudBank tactical #1506, and CanonRec are NOT imported, executed,
  or promoted. No blocked tactical Run 0 is authorized.
- Physical invariants apply to **represented** closed-system stocks, not the
  unmodeled wider universe. Temperature and energy degradation are bookkeeping,
  not a detailed thermodynamic solver.
- Historic rates of revolution, insurgency or regime collapse are NOT added.
  No assumption that nation-states are a necessary outcome is embedded.

## Proposed integration sequence (requires review)

G1. Review P0 fixture and contract with independent tests and CI; keep draft.
G2. Explicitly version time/space/quantity units and FTL-tech setting rules,
    observational permissions, and externally supplied causation.
G3. Build a guarded ACE #85 adapter for immutable identity snapshots; no
    background materialization and no L1 exposure.
G4. Build a separate GUMAS v2 tactical #1506 **read-only** evidence adapter
    when accepted constraints and PR gating permit. No execution of Run 0.
G5. Migrate selected v3 political effects from the legacy shadow adapter
    using a proposal-validator-commit path, fixing transition-only
    CIVIL_WAR_ONSET first. Add event hazards per elapsed time, actor
    organization models and counterfactual cross-polity testing.
G6. Add durable checkpoints, replay, resolution negotiation and vetted
    canonical initialization. Canon promotion remains outside this L2 kernel.

## External PR relationships

- CloudBank #1506: deterministic GUMAS v2 battle runtime (open draft, not merged).
- Root #85: persistent ACE worlds (open, not merged).
- Root #115: retired historical simulation-state authority and freshness repair.
- Root #100: design-only governed working-group lifecycle.
- Root #80: VPC governance process registry; does not itself confer canon.
- Root #97/#98/#99/#101: read-only UI/snapshot bridge; synthetic preview.
All references are integrations to review, NOT dependencies imported by P0.

## Run locally

From repository root:

    python -m unittest discover -s tests -p 'test_gumas_unified.py' -v
    python -m simulation.runtime.gumas_unified.scenario

Both use the Python standard library only, without credentials, external
network calls, canonical files or a service process.

## Acceptance and promotion policy

The P0 research PR remains **draft** and must not be merged merely because the
tests pass. Independent review should verify boundary isolation, semantics of
the provisional physical profile, resource accounting, event-hash handling,
and compatibility with existing repo CI. Promotion to a shared L2 runtime,
activation of external adapters or changes to canon require separate approval.
