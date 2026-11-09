# GUMAS Tactical Source Deduplication Root Cause Analysis v1.0

**Date:** 2026-08-12  
**Layer:** L2  
**Status:** preservation root cause identified from local forensic evidence; recovered v2.0 bytes independently verified elsewhere in this branch  
**Severity:** high preservation risk

## Executive finding

The recovered GUMAS v2.0 tactical package was not deliberately retired or superseded. According to Addendum D of the local forensic recovery, a 2026-02-15 deduplication/reorganization pass classified files by **basename/format rather than content identity** and moved three load-bearing v2.0 package files into `_REDUNDANT_FILES_ARCHIVED/02_FORMAT_DUPLICATES/`, a location whose own reorganization documentation described as safe to delete.

The three affected files were:

- `engine.py` — v2.0 tactical engine, 64,942 bytes / 1,620 LOC
- `scenarios.py` — v2.0 scenario builder, 59,277 bytes / 1,837 LOC
- `__init__.py` — `GUMAS-PACKAGE-V2` package manifest, 1,412 bytes / 34 LOC

The deduplication record reportedly mapped them to unrelated or non-equivalent files solely because the basenames matched.

This explains why ten v2.0 subsystem modules survived under the development tree while the engine, scenario builder, and package manifest appeared only in a delete-recommended archive location.

## Evidence status

Two evidence classes must remain distinct.

### Independently verified in this ChatGPT/GitHub workstream

The reunited recovered v2.0 package and two historical witnesses were independently hash-checked. The recovered `modules/gumas` tree digest is:

`a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9`

The historical witness hashes are:

- Witness A: `1f9dae31d916e8d3815ca465177007f5359544bf9ade6e23a5bd8a123ff7ed23`
- Witness B: `606314440661ed9ddd17d0dc1b794595e9c2bdaccd12c4bbe61899a8a4d0166f`

All recovered GUMAS module hashes agree across both witnesses.

### Local forensic evidence from Addendum D

The following primary-source paths and deduplication records were reported from the owner device and are not present in the indexed GitHub repositories:

- `projects/GUMAS_SIM_2.0/07_INDICES/Getting_Started/REORGANIZATION_SUMMARY.txt`
- `projects/GUMAS_SIM_2.0/07_INDICES/Indices/_DEDUPLICATION_REPORT.json`
- `projects/GUMAS_SIM_2.0/07_INDICES/Indices/REORGANIZATION_MANIFEST.json`

The report states that `REORGANIZATION_SUMMARY.txt` described `_REDUNDANT_FILES_ARCHIVED/02_FORMAT_DUPLICATES/` as `Safe to delete` and recommended deleting all redundant files.

The deduplication report reportedly contains this representative mapping:

```text
duplicate_file: engine.py
duplicate_path: .../26_engine_2.0/modules/gumas/engine.py
duplicate_size_bytes: 64942
canonical_file: engine.py
canonical_path: 26_Engine_1.2/engine.py
canonical_size_bytes: 54786
reason: duplicate_format
```

The supposed canonical v1.2 `engine.py` contains no `CombatResolver`, `FLEET_BATTLE`, or `FleetState` surface and therefore is not semantically interchangeable with the recovered v2.0 engine.

The same report identifies analogous false mappings for `scenarios.py` and the package `__init__.py`, including a 1,412-byte manifest mapped against a zero-byte package marker.

## Causal chain

```text
2026-02-06  pre-tactical L2_GUMAS_ENGINE v1.0.0 authored
2026-02-07  GUMAS v2.0 tactical package authored
            - 13 modules / recovered complete package
            - CombatResolver / topology / fleets / Phase 8 / Phase 9
2026-02-12  architecture/forge documentation produced against v2.0
2026-02-13  corrected deep-dive documents a third combat API signature
2026-02-15  basename-based deduplication/reorganization
            - 10 tactical subsystem modules remain in development tree
            - engine.py / scenarios.py / package __init__.py moved to
              delete-recommended format-duplicate archive
2026-02-16  GUMAS_SIM_2.5 published from pre-tactical v1 lineage
2026-02-19  FORGE v3.0 wired to the v1-derived 2.5 base
2026-08-12  v2.0 package reunited and independently hash-verified
```

## Root cause

**Primary root cause:** deduplication based on filename/basename equivalence rather than cryptographic content identity and semantic/version lineage.

**Contributing controls failure:** the reorganization output asserted that format duplicates were identical and safely deletable without verifying byte equality.

**Preservation amplification:** `/projects/*` was reportedly excluded from Git tracking, leaving the misclassified local files dependent on local archive retention.

**Detection failure:** no automated integrity check compared the reorganization manifest's declared canonical file against the moved file by hash, size, package version, or exported symbols.

## Impact

The deduplication pass broke package integrity by separating the v2.0 engine/scenario/manifest from its tactical subsystem tree.

Had the documented cleanup recommendation been executed and the two historical archive witnesses not survived, the package could have become unrecoverable.

This failure also contributed to later lineage confusion: the surviving v1-derived `GUMAS_SIM_2.5` package was subsequently mistaken for the tactical successor because the true v2 engine had been administratively displaced.

## Preservation requirements

1. Preserve the recovered v2.0 package byte-for-byte and keep its tree digest pinned.
2. Preserve both historical witness ZIPs off-device as independent witnesses.
3. Never patch the archival recovery copy in place.
4. Track any executable restoration in Git under a non-ignored path.
5. Do not execute legacy cleanup Option 2/Option 3 against the historical GUMAS archive tree.
6. Future deduplication must use cryptographic content hashes as the minimum identity test; basename equality is never sufficient.
7. Before deleting a duplicate candidate, verify at least hash, size, package/version context, and semantic/export identity.
8. Treat the remaining 305 historical deduplication records as untrusted until audited against this failure mode.

## Relation to the control battle

This root cause changes provenance interpretation but not Run-0 safety gates.

- recovered v2.0 is the historical restoration base;
- the archival combat-contract defects remain real and unresolved;
- restoration must be separately versioned;
- the physically bounded per-vessel planetoid extension remains subordinate to restored v2.0 authority;
- no battle result may execute until restoration, adapter, deterministic T0 state, command policy, physical constraints, and replay validation all pass.

## Source note

This RCA records the findings supplied in `GUMAS_RECOVERY_ADDENDUM_D__ROOT_CAUSE__2026-08-12.md`. The local deduplication manifests and reorganization files themselves have not yet been imported into this GitHub workstream. If imported later, their hashes should be appended to a new version of this RCA rather than overwriting this record.
