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

## Evidence hierarchy

Two evidence classes are intentionally separated.

### Independently verified in this workstream

The recovered v2.0 source tree is independently hash-verified against two historical archive witnesses.

- Witness A SHA-256: `1f9dae31d916e8d3815ca465177007f5359544bf9ade6e23a5bd8a123ff7ed23`
- Witness B SHA-256: `606314440661ed9ddd17d0dc1b794595e9c2bdaccd12c4bbe61899a8a4d0166f`
- Recovery package SHA-256: `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`
- canonical recovered `modules/gumas` tree digest: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`
- package anchor: `GUMAS-PACKAGE-V2`

All 13 recovered module hashes agree across both witnesses and all recovered Python modules parse successfully.

### Local forensic evidence supplied by Claude

The re-attribution of v1.0.0, `GUMAS_SIM_2.5`, v3.0 wiring, the corrected 188,824-file search census, the DuelSim classification, and the third historical combat API signature come from a local-device forensic sweep. Their underlying local artifacts have not all been separately imported into this workstream.

They are therefore accepted as strong recovery evidence but remain distinguishable from the independently re-hashed witness package above.

## Authority candidate

Authority references should identify the recovered v2.0 package and source digest rather than rely only on ambiguous symbols such as `GUMASEngine` or `GUMASState`, which occur across multiple lineages.

Current recovered tactical authority candidate:

`GUMAS v2.0 / GUMAS-PACKAGE-V2 / modules-gumas tree SHA-256 a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`

This identifies the historical implementation. Executable authority for Run 0 will be the separately versioned restoration derived from it, with its own source digest.

## `GUMAS_SIM_2.5` re-attribution

The local forensic addenda report that `GUMAS_SIM_2.5.zip` (SHA-256 `6d91d36104b2da89d66e37f6b9b97691470762d4793763784988fb8db84db8c5`) is a direct derivative of `L2_GUMAS_ENGINE v1.0.0`, not a successor to recovered v2.0:

- `models.py` reported byte-identical to v1.0.0
- `formulas.py` reported byte-identical to v1.0.0
- `engine.py` and `scenarios.py` reported to differ by twelve lines total
- bundled validation metadata reportedly identifies `scenario_id: gumas_canonical_v1`
- payload lacks `combat.py`, `topology.py`, `FleetState`, `CombatState`, `FLEET_MOVEMENT`, and `FLEET_BATTLE`

The `2.5` label must therefore not be used as evidence of v2 tactical validation. The historical deterministic replay associated with that payload remains useful as a pre-tactical core reproducibility smoke test only.

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

## Corrected search-completeness record

The original recovery sweep is superseded by the corrected local forensic method. Reported completed coverage:

- master index: 188,824 files
- filename search uses substring rather than prefix-only globs
- 13 combat/topology/fleet/battle symbol variants searched case-insensitively
- 749/749 ZIP archives opened and content-searched
- 1,479/1,479 nested archives recursively inspected
- 149/149 Office documents text-extracted and searched
- 700/700 PDFs text-extracted and searched
- 41 notebooks searched
- 15,757 bytecode files inventoried; no Aurora-context orphan tactical bytecode found without adjacent source
- all six local Git repositories scanned at object level, including unreachable objects where available
- Codex sessions and ChatGPT export corpus searched

The corrected sweep found no second GUMAS L2 tactical implementation and no `resolve_combat` definition on any searched surface.

Remaining inaccessible or separately gated surfaces were reported as `~/Documents`, `~/.Trash`, Time Machine/APFS snapshots, and network-only GitHub branch/PR enumeration.

## Newly surfaced but non-authoritative artifacts

### DuelSim

Approximately 15,000 LOC of combat-oriented code under `GUMAS_SIM_2.5/DuelSim/` was surfaced by the corrected search. It is a historical fencing-duel simulator using weapon/style/fencer abstractions and has no GUMAS L2 anchors. Classification: unrelated sibling project, Category F.

### GUMAS v2 DOCX trilogy

Three 2026-02-06 DOCX files reportedly contain document-embedded executable source for a pre-tactical GUMAS branch. They contain core political/treaty/coalition/forecasting structures but no combat/topology/fleet classes. Classification: Category C historical source evidence for pre-tactical lineage, not an alternate tactical engine.

### Corrected architecture archive

`Aurora_Archive_2.0.zip` reportedly contains corrected architecture documents, including a third resolver signature. Classification: documentation evidence. It strengthens the mid-integration-abandonment conclusion but does not replace executable source.

## Operational consequence

For the deterministic flash-rebellion control project:

- historical source provenance is closed;
- recovered v2.0 is the restoration base;
- `GUMAS_SIM_2.5` is not tactical authority;
- v3.0 is not evidence that v2 combat ever executed;
- combat contract restoration is required before Run 0;
- restoration must be separately versioned and source-digested;
- the physical per-vessel planetoid layer remains a separately versioned bounded extension subordinate to restored v2.0 authority.
