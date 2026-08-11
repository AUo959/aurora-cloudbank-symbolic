# Orion Named-Human Count Erratum

**Document ID:** `AURORA__CANON_ERRATA__ORION_NAMED_HUMAN_COUNT`  
**Version:** v1.0  
**Date:** 2026-08-08  
**Status:** Current-facing canon/data erratum  
**Related issues:** #1449, #1452, #1454, #1455

## Ruling

The current evidence-supported named-human roster contains **35 identified human
records**.

The inherited **36-human** declaration is a bookkeeping error propagated from
Phase 1. It is **not evidence of a missing named person** and must not be used to
create, infer, or reserve an `UNRESOLVED_HUMAN_001` identity.

This erratum does not determine Orion Station's total current human crew
complement. Aggregate complement is a separate institutional population concept
and remains governed by the typed population work in #1452/#1455.

## Forensic arithmetic

The provenance review recorded the following sequence:

- roster v1.1 baseline: 11 humans plus Aurora Core AI;
- Phase 1 added three humans: Elira Noor, Elena Sorensen, Helena Vu;
- Alex Thorne and Maya Shepard were updates to existing humans;
- Aurora was an AI update;
- correct Phase-1 human total: `11 + 3 = 14`;
- Phase-1 milestone prose recorded 15 while the loader parsed 14;
- subsequent phase milestone totals inherited the +1 offset;
- Phase 5 therefore reached 35 actual named humans while metadata said 36;
- Phase 6 propagated that incorrect cumulative value into the later entity
  declaration.

The discrepancy is therefore explained by lineage. No additional person is
required to make the arithmetic coherent.

## Runtime rule

For live L1 initialization:

```text
identified_human_records = 35
missing_named_human_claim = false
```

Do not:

- fabricate a 36th named person;
- interpret 35 named records as proof that Orion has only 35 humans aboard;
- interpret the historical `81` aggregate as 81 fully authored personas;
- collapse humans, Aurora Core, relays, HALO, or L3 frameworks into one census.

## Historical preservation

Historical phase documents may retain their original milestone prose for
provenance. Current-facing loaders and runtime contracts must treat the 36-human
value as superseded count metadata rather than silently rewriting historical
artifacts.

The machine-readable current-facing rule is
`config/l1_runtime_baseline.json`.

## Follow-up boundary

Issue #1454 may remain open for mechanical regeneration/cleanup of every legacy
manifest surface if desired. That cleanup is not required to make the live
runtime safe, because the INIT path now rejects the false missing-human claim
and routes current-facing population semantics through the typed baseline.
