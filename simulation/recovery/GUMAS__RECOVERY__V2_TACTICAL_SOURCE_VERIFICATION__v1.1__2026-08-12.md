# GUMAS v2 Tactical Source Recovery Verification v1.1

**Verification date:** 2026-08-12  
**Layer:** L2  
**Status:** full historical tactical source recovered; integration defects unresolved  
**Authority boundary:** archival source remains immutable evidence; restoration work must be separately versioned.

## Executive finding

The current recovery classification is:

`GUMAS_V2_0_FULL_TACTICAL_SOURCE_RECOVERED__COMPLETE_HISTORICAL_IMPLEMENTATION__INTEGRATION_DEFECTS_UNRESOLVED`

The recovered GUMAS v2.0 package is the sole surviving implementation identified for the documented L2 tactical architecture. It contains the complete recovered 13-file `modules/gumas` package: `GUMASEngine`, `GUMASState`, `FleetState`, `CombatState`, `CombatResolver`, `TopologyManager`, `FLEET_MOVEMENT`, `FLEET_BATTLE`, `calc_combat_outcome`, topology/terrain support, and the expanded 15-phase lifecycle.

The earlier hypothesis that a separate later 2026-02-16 `engine.py` / `models.py` / `scenarios.py` tactical revision remains missing is retired as unsupported. The corrected local forensic census reported no artifact matching those anomalous documented LOC values across the searched surfaces, while ten module rows in the architecture documentation match the recovered package exactly. The inconsistent core-trio LOC rows are therefore treated as documentation drift unless contrary source evidence is later recovered.

## Evidence classes

### Independently verified in this ChatGPT/GitHub workstream

Three uploaded recovery artifacts were checked byte-for-byte.

#### Witness A

- file: `GUMAS_SIM_2.0__WITNESS_A__1f9dae31.zip`
- SHA-256: `1f9dae31d916e8d3815ca465177007f5359544bf9ade6e23a5bd8a123ff7ed23`
- size: 13,980,784 bytes
- layout: pre-reorganization single-tree GUMAS_SIM_2.0 archive

#### Witness B

- file: `GUMAS_SIM_2.0_2__WITNESS_B__60631444.zip`
- SHA-256: `606314440661ed9ddd17d0dc1b794595e9c2bdaccd12c4bbe61899a8a4d0166f`
- size: 14,279,553 bytes
- layout: post-reorganization split-tree GUMAS_SIM_2.0 archive

#### Reunified recovery package

- file: `GUMAS_V2_TACTICAL_RECOVERY__2026-08-12.zip`
- SHA-256: `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`
- `MANIFEST_SHA256.txt` SHA-256: `566ef508641b1fb3c43c47bc85ae7dbf881f756476b8199a77f795561ae37b86`
- `MANIFEST_LOC.txt` SHA-256: `08cd9c13b6b5b71b5001565593f3ecf48b810c42b22f49f3ea0e2f46b583c191`
- canonical recovered `modules/gumas` tree digest: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`

Every recovered GUMAS module SHA-256 matches the corresponding module in both historical witnesses. All 13 recovered Python modules parse successfully with Python AST parsing. No recovered module was modified or executed during verification.

### Local-device forensic findings supplied by Claude

The following conclusions come from the corrected local recovery sweep and are recorded as external forensic evidence. Their underlying local artifacts have not all been independently imported into this workstream.

- master file index: 188,824 files
- 749 ZIP archives opened and content-searched
- 1,479 nested archives recursively inspected
- 149 Office documents extracted/searched
- 700 PDFs text-extracted/searched
- 41 notebooks searched
- 15,757 bytecode files inventoried; no Aurora-context orphan `.pyc` without adjacent source
- six Git repositories scanned at object level, including unreachable objects where available
- approximately 1 GB of Codex session history searched
- ChatGPT export corpus searched
- `~/Documents`, `~/.Trash`, Time Machine/APFS snapshots, and network-only GitHub enumeration remain outside that local sandbox's completed coverage

The corrected sweep reported exactly one GUMAS L2 tactical implementation: the recovered 13-module package. No alternate `combat.py`, `topology.py`, `CombatResolver`, `resolve_combat`, or second tactical revision was found.

## Recovered module identity

| Module | LOC | SHA-256 |
|---|---:|---|
| `__init__.py` | 34 | `81a3a120873df3e7507b6c76210e42746cf00697d3f985b379f7136695a60b38` |
| `combat.py` | 374 | `ff486487b9dbac8abbc87824ead5ae0aadfdce7ab366c0a0cc164bb36053bfb6` |
| `doctrine.py` | 532 | `04d250595b6c7d0ab8373eb17998e69f76f55d08701c12cdf38d64148e031fdc` |
| `economics.py` | 536 | `0c0faf9af1e2bc4d82623b60fb83fe29608efa267ecfc955b67a67b320f973cb` |
| `engine.py` | 1620 | `5a0517646285fcfc1dd54c229361c69110d13a468e3ac6aa2561ac0f14258598` |
| `forecaster.py` | 583 | `2bea7ad4366668422bac3fa1707be1744331588b86a85c0b8402f554b9d4b813` |
| `formulas.py` | 921 | `d5435511abec6d734d28828669ecb6d3c37cb1c8cc52886758bd982b11bb9a9e` |
| `media.py` | 474 | `7ccdc15fb11f513c71e3732d2420fb35c498f2ab8000b623d3a131a68fbe6ac5` |
| `models.py` | 1095 | `75a464ac6d1986a70b9baeed249f00241797d61b31340368b93cc9fc00d7bbed` |
| `precursors.py` | 455 | `7a5f4ffbd5b7d6f7488137cfa1511ff26ec95b9d6be75aa475ad4de1e00fd134` |
| `scenarios.py` | 1837 | `305053324231d9d87650319bbbdbf3899bec7aae0aedfeb6e716b194e0d78648` |
| `sentinels.py` | 715 | `23899a9da0121709e37e69ed19bc7083d6127c1b5e8073449ccd8ddf71f737c2` |
| `topology.py` | 905 | `5375e91c95d49885ac4573f17b009c32b38fda8b755020f12f501beddc865d0b` |

The recovered package manifest identifies itself as `GUMAS L2 Multi-Agent Galactic Simulation Package v2.0` with anchor `GUMAS-PACKAGE-V2`.

## Corrected lineage interpretation

The local forensic addenda report that `GUMAS_SIM_2.5.zip` is not a tactical successor to v2.0. It is a direct derivative of the pre-tactical `L2_GUMAS_ENGINE v1.0.0` package: `models.py` and `formulas.py` are reported byte-identical and the other two core files differ by only twelve lines total. Its bundled validation metadata identifies `scenario_id: gumas_canonical_v1`.

Accordingly, `GUMAS_SIM_2.5` must not be used as evidence that v2 tactical combat was validated. The historical v1 seeded-replay result remains evidence only for deterministic behavior of that pre-tactical core lineage.

The same forensic addenda report that FORGE v3.0 supplies Phases 16–20 as a mixin but imports its base engine from the v1-derived `GUMAS_SIM_2.5/SIM_ENGINE_OUTPUTS` path rather than from recovered v2.0. Thus v3 subsystem test success does not establish execution of v2 Phases 8–9 or combat-facing technology effects.

These lineage re-attributions should be independently byte-compared if the referenced v1.0.0 and v3 artifacts are later uploaded to this workstream.

## Archive execution evidence

Both historical witnesses contain matching compiled bytecode entries:

- `combat.cpython-310.pyc` — 9,442 bytes, CRC32 `b8e3d494`
- `topology.cpython-310.pyc` — 13,627 bytes, CRC32 `d2d52879`

These are provenance evidence that those modules were imported under CPython 3.10. They do not prove that all combat execution paths completed successfully.

## Combat integration state

The archival source remains untouched. Independent static inspection of the recovered bytes identified two defects.

### 1. Phase 9 passes `combat=None`

`GUMASEngine._combat_resolution_tick()` calls `CombatResolver.resolve_battle(combat=None, ...)`, while `resolve_battle()` dereferences `combat.condition` and later `combat.location`. A real contested-location Phase 9 run is therefore not executable as recovered.

### 2. Explicit `FLEET_BATTLE` handler calls undefined method

`GUMASEngine._handle_fleet_battle()` calls `CombatResolver.resolve_combat(...)`, but the recovered resolver defines `resolve_battle()` and no `resolve_combat()` method.

### 3. Historical API intent is internally inconsistent

The corrected local sweep found `Aurora_Archive_2.0.zip` containing `GUMAS_2_0_DEEP_DIVE_CORRECTED.md`, which reportedly documents a third resolver contract:

`resolve_battle(attackers, defenders, location) -> BattleResult`

This differs from both:

- recovered `combat.py`: `resolve_battle(combat, attacker_fleets, defender_fleets, topology_manager) -> Dict`
- recovered `engine.py` event handler: `resolve_combat(fid_a, fleets_a, fid_b, fleets_b, location)`

The three-way disagreement is evidence that the tactical subsystem was abandoned mid-integration. It also means restoration must select and document an intended compatibility contract rather than merely rename one missing method.

## Additional artifacts found by corrected sweep

### DuelSim — unrelated sibling combat project

The corrected search surfaced approximately 15,000 LOC under `GUMAS_SIM_2.5/DuelSim/`. It is reported to be a historical fencing-duel simulator using weapon/style/fencer abstractions and contains no GUMAS, `EOS_SEED_ORION`, `Picard_Delta_3`, or L2 anchor relationship. Classification: unrelated Category F; useful inventory evidence, not a candidate GUMAS tactical implementation.

### GUMAS v2 document-embedded pre-tactical source trilogy

Three 2026-02-06 DOCX files reportedly contain executable source blocks for an alternate/pre-tactical GUMAS lineage. They define core political/treaty/coalition/forecasting structures but no fleet/combat/topology classes. Classification: Category C historical source evidence for pre-tactical lineage, not an alternate tactical engine.

### Documentation drift

The corrected sweep found additional contemporaneous documents with mutually inconsistent event taxonomies, resolver signatures, LOC counts, and capability claims. Documentation is therefore supporting lineage evidence only when corroborated by source bytes; executable source takes precedence for implementation claims.

## Restoration constraints

Restoration may now proceed from the recovered v2.0 package, but only under these rules:

1. preserve both witness ZIPs and the recovered source tree byte-for-byte;
2. never patch the archival copy in place;
3. create a separately versioned restored implementation with explicit source digest;
4. resolve the combat API contract deliberately, recording why the chosen compatibility path is the minimal faithful restoration;
5. add tests that exercise Phase 8 movement, Phase 9 contested-node combat, explicit `FLEET_BATTLE` handling, terrain modifiers, retreat/loss allocation, and deterministic replay;
6. keep the physically bounded per-vessel planetoid layer subordinate to restored GUMAS authority rather than rewriting historical GUMAS as if it already contained Newtonian per-vessel combat;
7. pin engine/restoration/adapter/baseline digests into Run-0 identity.

## Control-run status

`BLOCKED_PENDING_TACTICAL_RESTORATION_AND_FIXTURE_INTEGRATION`

The source-recovery blocker is closed. The remaining blockers are combat-contract restoration, deterministic physical extension integration, and validation.
