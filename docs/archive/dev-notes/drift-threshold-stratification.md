# Drift Threshold Stratification Reference

**Status:** Active architecture reference  
**Origin:** [`docs/review-notes/entries/20260526-drift-threshold-stratification.md`](../review-notes/entries/20260526-drift-threshold-stratification.md)  
**Last updated:** 2026-05-28  
**Related roadmap lane:** [`docs/ROADMAP.md`](../ROADMAP.md#lane-d--review-note-intake-and-architecture-references)

Aurora uses a three-layer symbolic drift threshold model. The thresholds are intentionally stratified so lower-level capsule and governance checks remain more sensitive than larger, noisier agent or macro-system checks.

This document is the stable contributor reference. Review-note entries capture intake history and unresolved observations; this file captures durable guidance that PRs, instructions, and code comments can link to.

---

## Threshold model

| Layer | Current threshold | Intended scope | Notes |
|---|---:|---|---|
| L1 Capsule / Governance | `0.002` | Per-capsule or tight governance drift | Tightest layer; small symbolic changes matter |
| L2 Agent / QGIA | `0.02` | Per-agent or session-level drift | Mid-layer; tolerates more variation across active agents |
| L3 Macro / Network | `0.1` | Cross-network or macro-system coherence | Loosest layer; evaluates broader, noisier system behavior |

The rough 10x step between layers is intentional. A value that is safe at one layer may be too loose or too strict at another.

---

## Contributor rule

Before changing drift thresholds, anomaly logic, capsule validation, QGIA agent monitoring, or macro drift handling:

1. Identify which layer the change affects.
2. Check whether the other two layers remain semantically consistent.
3. Update this file if a threshold value or rationale changes.
4. Update the originating review note or related issue if the change resolves a tracked observation.
5. Add or update tests where threshold behavior is externally visible.

---

## Known references to keep aligned

- `modules/reflective_autonomy/capsule_linter.py`
- `threadcore_registry.json`
- `src/nexus_enhancement_hub.js`
- `modules/reflective_autonomy/autonomic_correction_engine.py`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/instructions/drift-thresholds.instructions.md`
- `connector/tools/get_drift.py`

If any of these files encode a drift value directly, prefer moving toward shared configuration or an explicit local constant with a comment linking here.

---

## Open follow-up

The review intake note remains open until the implementation surface is fully reconciled. The key unresolved question is whether all drift thresholds should be sourced from a shared `drift_thresholds.yaml` or similar configuration file.

---

*Built for consistency, clarity, and care.*
