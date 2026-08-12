# GUMAS v2 Tactical Source Recovery Verification v1.0

**Verification date:** 2026-08-12  
**Layer:** L2  
**Status:** historical source recovered; integration validation pending  
**Authority boundary:** archival source is preserved as evidence and is not modified by this receipt.

## Executive finding

Independent verification of the uploaded recovery package and two historical archive witnesses supports the classification:

`historical_v2_0_tactical_authoring_source_recovered_later_validated_core_revision_unverified`

The historical GUMAS v2.0 tactical implementation is no longer considered missing. The recovered authoring revision contains the documented fleet/combat subsystem, including `CombatResolver`, `FleetState`, `CombatState`, `FLEET_MOVEMENT`, `FLEET_BATTLE`, `calc_combat_outcome`, topology/terrain support, and the expanded engine lifecycle.

The exact later core-trio revision described by the 2026-02-16 validation documentation remains unverified because the recovered `engine.py`, `models.py`, and `scenarios.py` line counts differ from that later documentation.

## Uploaded artifact verification

### Witness A

- file: `GUMAS_SIM_2.0__WITNESS_A__1f9dae31.zip`
- SHA-256: `1f9dae31d916e8d3815ca465177007f5359544bf9ade6e23a5bd8a123ff7ed23`
- size: 13,980,784 bytes
- layout: pre-reorganization single-tree GUMAS_SIM_2.0 archive

### Witness B

- file: `GUMAS_SIM_2.0_2__WITNESS_B__60631444.zip`
- SHA-256: `606314440661ed9ddd17d0dc1b794595e9c2bdaccd12c4bbe61899a8a4d0166f`
- size: 14,279,553 bytes
- layout: post-reorganization split-tree GUMAS_SIM_2.0 archive

### Reunified recovery package

- file: `GUMAS_V2_TACTICAL_RECOVERY__2026-08-12.zip`
- SHA-256: `039c0f48341aa9847b8400e45a29e41fef734a2b2e80b78bfe3de1abc165ec07`
- `MANIFEST_SHA256.txt` SHA-256: `566ef508641b1fb3c43c47bc85ae7dbf881f756476b8199a77f795561ae37b86`
- `MANIFEST_LOC.txt` SHA-256: `08cd9c13b6b5b71b5001565593f3ecf48b810c42b22f49f3ea0e2f46b583c191`
- canonical recovered `modules/gumas` tree digest: `a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`

The canonical tree digest above is SHA-256 over sorted lines of the form `<file_sha256>  modules/gumas/<filename>\n` for the 13 recovered GUMAS package files.

## Recovered module identity

All recovered module SHA-256 values match the corresponding files in both Witness A and Witness B.

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

All 13 Python modules parse successfully with Python AST parsing. No recovered module was modified or executed during this verification.

## Tactical symbols independently confirmed

- `GUMASEngine` — `engine.py:78`
- `CombatResolver(self._rng)` — `engine.py:111`
- `TopologyManager(state.topology)` — `engine.py:178`
- Phase 8 `_fleet_movement_tick` — invocation `engine.py:210`, implementation begins `engine.py:698`
- Phase 9 `_combat_resolution_tick` — invocation `engine.py:211`, implementation begins `engine.py:739`
- `FleetState` — `models.py:620`
- `CombatState` — `models.py:651`
- `EventType.FLEET_MOVEMENT` — `models.py:115`
- `EventType.FLEET_BATTLE` — `models.py:116`
- `calc_combat_outcome` — `formulas.py:415`
- `CombatResolver.resolve_battle` — `combat.py:69`
- `get_terrain_modifiers` — `combat.py:39`

The recovered package manifest identifies itself as `GUMAS L2 Multi-Agent Galactic Simulation Package v2.0` with anchor `GUMAS-PACKAGE-V2`.

## Archive execution evidence

Both historical witnesses contain matching compiled bytecode entries:

- `combat.cpython-310.pyc` — 9,442 bytes, CRC32 `b8e3d494`
- `topology.cpython-310.pyc` — 13,627 bytes, CRC32 `d2d52879`

These are retained as provenance evidence that those modules were imported under CPython 3.10. No decompilation was required.

## Important recovered defects — archival source remains untouched

Independent static inspection found two combat integration defects in the recovered authoring revision.

### 1. Phase 9 passes `combat=None`

`GUMASEngine._combat_resolution_tick()` calls:

`self._combat_resolver.resolve_battle(combat=None, attacker_fleets=..., defender_fleets=..., topology_manager=...)`

However `CombatResolver.resolve_battle()` dereferences `combat.condition` when obtaining terrain modifiers and later `combat.location` when generating battle events. Therefore a real contested-location Phase 9 execution would raise before completing combat unless another revision supplied a non-null `CombatState` or changed the resolver contract.

This means the recovered Phase 9 path is **not considered validated executable combat as-is**.

### 2. Explicit `FLEET_BATTLE` handler calls undefined method

`GUMASEngine._handle_fleet_battle()` calls:

`self._combat_resolver.resolve_combat(...)`

The recovered `CombatResolver` defines `resolve_battle()` but no `resolve_combat()` method. Static method/call inventory confirms `resolve_combat` is the only engine call to a missing `CombatResolver` method.

No archival repair has been made.

## Interpretation

The recovery proves that the historical tactical subsystem genuinely existed and that its core design/source identity is recoverable. It does **not** prove that this exact authoring revision can be used unchanged for the flash-rebellion control run.

The correct next stage is controlled restoration/integration:

1. preserve the recovered source byte-for-byte as immutable historical evidence;
2. retain both archive witnesses and their hashes;
3. search further for the later 2026-02-16 validated `engine.py` / `models.py` / `scenarios.py` revision if desired;
4. design the smallest explicit compatibility/restoration patch required to make the recovered tactical contract internally coherent;
5. version that restored implementation separately from the archive source;
6. validate deterministic replay, combat path execution, and fixture adapter behavior before Run 0.

## Control-run status

`BLOCKED_PENDING_TACTICAL_RESTORATION_AND_FIXTURE_INTEGRATION`

The source-recovery blocker itself is closed. Remaining blockers are implementation/validation blockers, not provenance blockers.
