# QGIA-CORPUS Bulk Ingestion — Design Decision Record

**Status:** DECIDED — designated, implementation deferred
**Decision date:** 2026-07-18 (L1, issue #1062)
**Classification:** Architectural Canon | Constellation Contracts
**Relates to:** `constellation-contracts/manifests/zipwiz-engine.manifest.json`, `constellation-contracts/manifests/qgia-corpus.manifest.json`, `AUo959/qgia-knowledge-library`, `AUo959/zip_wizard`

---

## Decision

**ZIPWIZ-ENGINE is the designated bulk-ingestion mechanism for QGIA-CORPUS**, effective when a concrete bulk historical dataset actually needs ingesting. No pipeline is wired today, deliberately.

This resolves the final open question of issue #1062 (the other four were answered by pre-existing constellation-contract canon — see that issue's 2026-07-13 comment).

## Binding design constraint — the curation gate

QGIA-CORPUS's canonical property is **curated** (`stack: ["markdown"]`, "curated intelligence documents"). It is the ground truth that makes QGIA-SPINE retrieval and QSFE forecast evidence trustworthy. Therefore, when the ZIPWIZ ingestion path is built, it **must propose, never commit**:

```
archive → ZIPWIZ-ENGINE extraction/analysis → staged candidate documents
       → human/Aurora curation gate → corpus merge → knowledge-index regeneration
```

Direct writes from any automated ingestion into corpus domain directories are prohibited. This is the same automation-proposes/authority-disposes discipline used by the work-queue pipelines (`queue-issue-ingestion`, `queue-decision-escalation`).

## Why deferred, and what stays truthful meanwhile

- **No demand yet:** the corpus is ~700 KB of actively hand-curated markdown; no bulk datasets are pending anywhere in the constellation. Building the cross-repo pipeline now would be speculative plumbing.
- **Manifests stay honest:** `zipwiz-engine.manifest.json` keeps `downstream: []` and `published: []` until the pipeline is actually wired — no phantom contract claims for unbuilt paths (manifest-truth discipline, cf. the Phase 10 reconciliation on #1067/#1264).

## Activation checklist (open a scoped implementation issue when triggered)

A concrete bulk dataset arriving triggers implementation. That issue must cover:

1. `bulk-ingest` contract published by ZIPWIZ-ENGINE; `downstream` link to `s.tag::qgia.corpus` added **in the same change** that wires it
2. Staging area + curation workflow in `qgia-knowledge-library` (PR-based; curator sign-off required before merge)
3. Domain classification of staged candidates against the 9 canonical domains
4. `Provenance` binding (caelion_anchor / charter / l3_compliance) carried from ingestion through to indexed documents
5. knowledge-index regeneration as part of the corpus-merge change, so SPINE never serves an index that disagrees with the corpus

---

*Recorded by Claude Code from the L1 decision on issue #1062; verification details in that issue's 2026-07-18 decision brief.*
