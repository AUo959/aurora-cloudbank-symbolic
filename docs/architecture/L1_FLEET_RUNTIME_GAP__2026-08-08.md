# Orion L1 Fleet Runtime Gap — Investigation Note

**Date:** 2026-08-08  
**Status:** investigation finding / non-canon  
**Run context:** first governed discovery-through-observation L1 run, paused at tick 7

## Finding

The live governed L1 runtime does not currently ingest the repository's fleet, probe, or drone entity surfaces. As a result, a fleet/autonomous-craft observation request can only see generic station records and cannot confirm or deny physical fleet activity.

This is an ingestion/provider gap, not evidence that Orion has no active external craft.

## Evidence surfaces

### Legacy aggregate fleet surface

`.aurora/canonical/fleet.json` contains an older 11-vessel Dark Matter-era fleet model. This surface predates the later specialized ORF/ORS/ORP/ORD fleet architecture and must not be promoted directly into live run state without provenance reconciliation.

### Current modular entity surfaces

`src/entities/fleet/` exposes:

- vessels: ORF-01 Constancy; ORS-01 Helios; ORS-02 Liora; ORS-03 Archimedes; ORS-04 Pioneer; ORS-05 Lacewing;
- probes: ORP-1 Alpha Surveyor; ORP-2 Beta Array;
- drones: ORD-1 Gamma Swarm; ORD-2 Delta Scout; ORD-3 Shadowfax; ORD-4 Wisp.

`src/entities/fleet_entities.py` is a compatibility shim over these modular registries.

### ORD policy layer

`modules/ord/` provides deterministic dispatch/inspection policy for the ORD family, but its own README explicitly says wiring into live dispatch surfaces is a separate step. The policy library therefore must not be mistaken for live L1 craft activation.

### Live runtime

`simulation/l1_runtime.py` initializes station, locus, communications, and population state only. `event_for_roll()` in `simulation/l1_runtime_support.py` exposes four generic event classes: routine shift handoff, maintenance queue progress, research queue progress, and no-material-event. No fleet registry, mission state, craft process, or drone process is loaded into `L1RunState`.

The observation aperture reads recent station records. Therefore absence of fleet records currently means **provider not bound**, not **craft absent**.

## Required correction

1. Reconcile fleet authority/provenance between the Dark Matter-era aggregate registry and the later ORF/ORS/ORP/ORD architecture.
2. Add a machine-readable fleet projection and provenance receipt to the L1 baseline.
3. Add typed fleet state to `L1RunState` (asset identity, class, autonomy, status, mission state, docking/location class, provenance).
4. Add deterministic fleet world-process advancement independent of observation.
5. Add observation providers for fleet/proximity/docking/drone activity with explicit unavailable states where no provider exists.
6. Integrate ORD policy only through an explicit adapter; do not equate MCP policy dispatch with physical drone flight automatically.
7. Preserve historical mission timestamps/status as provenance rather than treating 2025 mission snapshots as current 2026 run state.
8. Add replay/non-centrality/provenance tests.

## Runtime correction for the paused experiment

Until this gap is resolved, fleet/autonomous-craft observations must report:

> Fleet physical-state provider is unbound; no conclusion about current craft activity can be drawn from absence of station records.

The simulation should remain paused while fleet authority and ingestion are repaired if fleet behavior is intended to participate in the experimental world model.
