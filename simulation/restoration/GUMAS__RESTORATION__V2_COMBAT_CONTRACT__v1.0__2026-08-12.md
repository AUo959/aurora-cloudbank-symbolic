# GUMAS v2 Tactical Restoration — Combat Contract v1.0

**Date:** 2026-08-12  
**Restoration version:** `2.0.1-restored.1`  
**Historical base:** `GUMAS-PACKAGE-V2`  
**Recovered tree SHA-256:** `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`  
**Recovery package SHA-256:** `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`  
**Task record:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.0__2026-08-12.md`

## Decision

The restoration adopts the executable contract actually defined by the recovered tactical module:

```python
CombatResolver.resolve_battle(
    combat: CombatState,
    attacker_fleets: List[FleetState],
    defender_fleets: List[FleetState],
    topology_manager=None,
) -> Dict[str, Any]
```

This contract is preferred because it is present in the recovered `combat.py`, uses the recovered `CombatState` model, and directly calls the recovered deterministic combat formulas. The archival source is not edited in place. The untouched recovery ZIP is represented losslessly as ordered base64 segments under `simulation/runtime/gumas_v2_restored/vendor/recovery_b64/`. At runtime the segments are reassembled, SHA-256 verified against the independently recovered witness, materialized only as an ephemeral ZIP, and imported through Python zip-import. Restoration behavior lives in a separate subclass wrapper, `restored_engine.py`.

The incompatible historical call sites are treated as integration defects:

1. automatic Phase 9 supplied `combat=None` even though the resolver dereferences `combat.condition`, `combat.turns_active`, and `combat.location`;
2. explicit `FLEET_BATTLE` called an undefined `resolve_combat(...)` method;
3. a later deep-dive document describes a third signature, but no executable implementation of that signature was recovered.

## Preservation and restoration structure

- `vendor/recovery_b64/part-*.b64` is a lossless segmented encoding of the untouched recovered package (`039c0f...`).
- The segments are decoded and cryptographically verified before any historical module import; a hash mismatch fails closed.
- The historical modules are imported from the verified reconstructed ZIP; there is no maintained unpacked copy that could drift from the witness.
- `restored_engine.py` subclasses the historical `GUMASEngine` and overrides only the inconsistent combat integration boundary.
- `restoration_smoke.py` is a focused executable receipt surface; it is not a second combat authority.
- `GUMAS__RESTORATION_MANIFEST__v1.0__2026-08-12.json` pins the historical tree, recovery package, restored contract, and file hashes.

## Minimal restoration behavior

### Automatic Phase 9

For every co-located faction pair:

1. location IDs are traversed in sorted order;
2. faction IDs are traversed in sorted order;
3. fleet lists are sorted by stable `fleet_id`;
4. a deterministic `CombatState` ID is created as:
   `combat::<location>::<sorted_faction_a>::<sorted_faction_b>`;
5. an existing unresolved combat state with that ID is reused;
6. battlefield condition is taken from an already prepared combat state when present;
7. otherwise a topology node explicitly marked `is_chokepoint` maps to `CHOKEPOINT`; all other historical aggregate locations default to `OPEN_SPACE`;
8. the shipped `resolve_battle(...)` method resolves the engagement;
9. the shipped `apply_fleet_losses(...)` applies losses;
10. `outcome_ratio` and `turns_active` are committed to `GUMASState.combat_zones`.

No new aggregate combat formula is introduced.

### Explicit `FLEET_BATTLE`

The explicit event path no longer attempts to call the nonexistent `resolve_combat(...)` API. During Phase 1 event processing it prepares the same deterministic `CombatState`, including an explicitly supplied battlefield condition when present. The authoritative resolution still occurs once, later in Phase 9.

This deliberately prevents a single explicit battle event from causing two aggregate combat resolutions in one tick.

## What this restoration does not claim

- It does not claim to reconstruct an unrecovered later API.
- It does not modify the recovered archival bytes.
- It does not add per-vessel physics.
- It does not add CanonRec class resolution.
- It does not define tactical withdrawal, surrender, targeting, or damage beyond the recovered aggregate engine.
- It does not make Run 0 executable yet.

Those remain later DTER phases.

## Determinism characterization

The recovered combat formulas used by `CombatResolver` are deterministic for fixed fleet state. The restoration additionally removes dictionary-order ambiguity in the aggregate combat traversal by sorting locations, factions, and fleet IDs.

Focused local verification on a two-fleet minimal state showed:

- automatic Phase 9 creates one `CombatState` and resolves one engagement;
- explicit `FLEET_BATTLE` prepares a `CHOKEPOINT` combat and still resolves only once in Phase 9;
- both sides receive recovered-formula losses;
- reversing initial fleet dictionary insertion order does not change normalized output;
- two identical executions produce the same normalized SHA-256:
  `de55355d1b489c1a89c63508d9fbe5779e0ac9e66248f28850c1012c266d07ea`.

Repository CI remains the promotion gate for this local result.

## Phase-1 exit criterion

Phase 1 may be considered complete only after repository tests confirm both automatic Phase 9 and explicit `FLEET_BATTLE` behavior and repeat the deterministic replay result on the committed restored source.
