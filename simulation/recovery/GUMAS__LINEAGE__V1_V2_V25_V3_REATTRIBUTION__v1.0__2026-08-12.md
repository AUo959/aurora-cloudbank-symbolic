# GUMAS Lineage Re-attribution v1.0

**Date:** 2026-08-12  
**Layer:** L2  
**Status:** recovery-derived lineage record; implementation authority must be pinned by source digest

## Purpose

Record the corrected relationship among the pre-tactical GUMAS core, the recovered v2.0 tactical package, the later `GUMAS_SIM_2.5` bundle, and FORGE v3.0 so future work does not conflate version labels with implementation lineage.

## Current lineage model

```text
26_Engine 1.x
   |
   +--> L2_GUMAS_ENGINE v1.0.0 (2026-02-06, pre-tactical four-module core)
   |       |
   |       +--> GUMAS_SIM_2.5 (2026-02-16, reported direct v1.0.0 derivative)
   |               |
   |               +--> FORGE v3.0 mixin (Phases 16-20), reported wired to the v1-derived base
   |
   +--> GUMAS v2.0 package (2026-02-07)
           - 13 modules in modules/gumas
           - 15-phase lifecycle
           - combat.py + topology.py
           - FleetState / CombatState
           - CombatResolver
           - FLEET_MOVEMENT / FLEET_BATTLE
           - recovered 2026-08-12
           - historical combat integration defects unresolved
```

## Independently verified v2.0 authority candidate

The recovered v2.0 source tree is independently hash-verified against two historical archive witnesses.

- Witness A SHA-256: `1f9dae31d916e8d3815ca465177007f5359544bf9ade6e23a5bd8a123ff7ed23`
- Witness B SHA-256: `606314440661ed9ddd17d0dc1b794595e9c2bdaccd12c4bbe61899a8a4d0166f`
- Recovery package SHA-256: `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`
- canonical recovered `modules/gumas` tree digest: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`
- package anchor: `GUMAS-PACKAGE-V2`

Authority references should therefore identify this exact package/digest rather than rely only on the ambiguous class names `GUMASEngine` or `GUMASState`, which occur across multiple lineages.

## `GUMAS_SIM_2.5` re-attribution

The local-device forensic addenda report that `GUMAS_SIM_2.5.zip` (SHA-256 `6d91d36104b2da89d66e37f6b9b97691470762d4793763784988fb8db84db8c5`) is a direct derivative of `L2_GUMAS_ENGINE v1.0.0` rather than a successor to recovered v2.0:

- `models.py` reported byte-identical to v1.0.0
- `formulas.py` reported byte-identical to v1.0.0
- `engine.py` and `scenarios.py` reported to differ by twelve lines total
- bundled validation metadata reportedly identifies `scenario_id: gumas_canonical_v1`
- payload lacks `combat.py`, `topology.py`, `FleetState`, `CombatState`, `FLEET_MOVEMENT`, and `FLEET_BATTLE`

The `2.5` label must therefore not be used as evidence of v2 tactical validation. The historical deterministic replay associated with that payload remains useful as a pre-tactical core reproducibility smoke test only.

This byte-comparison against the v1.0.0 archive is currently recorded from the local forensic report; the v1.0.0 witness itself has not yet been independently imported into this GitHub/ChatGPT workstream.

## v2.0 completeness

The corrected local forensic sweep reports no alternate tactical revision and no artifact matching the anomalous `PK_02` core-trio LOC rows. Because ten other module rows match recovered source exactly and the same documentation family demonstrably mixes v1 payload facts with v2 capability descriptions, the previous hypothesis of a missing later validated core trio is retired unless contrary executable source is later produced.

Recovered v2.0 is therefore treated as the complete surviving historical tactical implementation, not as an incomplete authoring snapshot awaiting a presumed later engine/models/scenarios build.

## v3.0 re-attribution

The local forensic addenda report that `FORGE__GUMAS_v3.0__2026-02-19` adds Phases 16-20 through `GUMASEngineV3Mixin`, but resolves its parent import through `GUMAS_SIM_2.5/SIM_ENGINE_OUTPUTS`, i.e. the v1-derived branch rather than recovered v2.0.

Consequences reported from surviving runs:

- v3 subsystem tests may be valid for Phases 16-20 themselves;
- they do not validate recovered v2.0 Phases 8-9;
- combat-facing technology multipliers cannot reach the recovered `CombatResolver` when the v3 mixin is attached to the v1-derived base;
- repointing v3 to restored v2.0 would be a new integration change and requires owner approval plus validation.

## Combat-contract evidence

Three incompatible historical API contracts are now in evidence:

1. recovered `combat.py`:
   `resolve_battle(combat, attacker_fleets, defender_fleets, topology_manager) -> Dict`
2. recovered `engine.py` explicit event handler:
   `resolve_combat(fid_a, fleets_a, fid_b, fleets_b, location)`
3. corrected 2026-02-13 deep-dive document reported by the local sweep:
   `resolve_battle(attackers, defenders, location) -> BattleResult`

In addition, recovered Phase 9 passes `combat=None` into a resolver that dereferences `combat.condition` and `combat.location`.

The combined evidence supports **mid-integration abandonment**, not a completed tactical engine later lost. Restoration must therefore define the intended compatibility contract explicitly and test it; no archival file may be silently edited to manufacture consistency.

## Search-completeness note

The corrected local-device sweep reports coverage of 188,824 indexed files, 749 ZIP archives, 1,479 nested archives, 149 Office documents, 700 PDFs, 41 notebooks, 15,757 bytecode files, six Git repositories, AI-session archives, and ChatGPT exports. It found no second GUMAS L2 tactical implementation.

Remaining inaccessible/low-value surfaces reported by the sweep are `~/Documents`, `~/.Trash`, Time Machine/APFS snapshots, and network-only GitHub branch/PR enumeration.

## Operational consequence

For the deterministic flash-rebellion control project:

- historical source provenance is closed;
- recovered v2.0 is the restoration base;
- `GUMAS_SIM_2.5` is not tactical authority;
- v3.0 is not evidence that v2 combat ever executed;
- combat contract restoration is required before Run 0;
- the physical per-vessel planetoid layer remains a separately versioned bounded extension subordinate to restored v2.0 authority.
