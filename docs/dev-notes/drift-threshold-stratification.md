# Dev Note: Drift Threshold Stratification

**Status:** Needs formal architecture doc entry  
**Priority:** Medium — debugging hazard for new contributors  
**Filed:** 2026-05-26  
**Relates to:** `capsule_linter.py`, `threadcore_registry.json`, QGIA operational layer  

---

## Context

Aurora uses **three distinct symbolic drift thresholds** across three different system layers. These values are currently implicit — they live in code constants, registry config, and the QGIA model layer, but are **not documented together anywhere**. Anyone debugging a drift-related issue without this map will have a hard time.

---

## The Three Thresholds

| Layer | Threshold | Where Defined | What Triggers |
|---|---|---|---|
| **Capsule / ThreadCore** | `0.002` | `threadcore_registry.json` → `validation_rules.max_drift_threshold`; also hardcoded as `DEFAULT_MAX_DRIFT` in `capsule_linter.py` | `symbolic_drift_high` warning finding → `review_drift` correction action planned |
| **QGIA Agent Network** | `0.02` | QGIA operational layer (agent-level drift monitoring) | Agent flagged for drift review by Velatrix; escalation to human if unresolved |
| **System / Macro** | `0.1` | QGIA macro-level / NexusEnhancementHub `DriftAwareAgent` | Hard alert; constellation coherence at risk; potential LOOMFIELD breach |

---

## Why Three Separate Thresholds?

The stratification is intentional, not accidental:

- **0.002 (capsule layer)** — the tightest because capsule payloads are structural governance artifacts. A ThreadCore payload with drift above 0.002 is potentially misaligned with the anchor seed, which is a *governance* problem, not just a performance one.
- **0.02 (agent layer)** — agents naturally have more variability than static capsules. A single agent drifting up to 2% is within acceptable operating range for the SBM network; above that, Velatrix should be notified.
- **0.1 (system layer)** — macro drift is measured across the full 551-agent QGIA network. Aggregate drift at 10% indicates systemic misalignment. Hard alert threshold — not a soft warning.

**The 10x ratio between layers is deliberate**: each layer is an order of magnitude more tolerant than the layer below it because it operates over a larger, noisier population.

---

## Risk if Left Undocumented

- A contributor seeing `0.002` in `capsule_linter.py` may assume it applies universally and be confused when agent-level drift at `0.015` does not trigger a linter warning.
- A contributor tuning the QGIA agent thresholds may not realize the capsule linter has a separate, independent threshold with different semantics.
- Debugging a `symbolic_drift_high` warning at the capsule layer while also seeing Velatrix quiet at the agent layer (because `0.015 < 0.02`) will look inconsistent without this map.

---

## Action Items for Future Dev

- [ ] Add a **Drift Threshold Reference** section to the main `ARCHITECTURE.md` (or create one if it doesn't exist) with this three-layer table
- [ ] Add inline comments in `capsule_linter.py` and `threadcore_registry.json` cross-referencing the other two thresholds, so the values are not read in isolation
- [ ] Consider a single `drift_thresholds.yaml` config file that all three layers import from, eliminating the risk of the values diverging silently over time
- [ ] Confirm the `0.02` and `0.1` thresholds are hardcoded or configurable in the QGIA layer — if hardcoded, add them to the same config consolidation

---

## Related Files

- `modules/reflective_autonomy/capsule_linter.py` — `DEFAULT_MAX_DRIFT = 0.002`
- `threadcore_registry.json` — `validation_rules.max_drift_threshold`
- `src/nexus_enhancement_hub.js` — `DriftAwareAgent` (system-level threshold)
- QGIA operational model (agent-level threshold)
- `modules/reflective_autonomy/autonomic_correction_engine.py` — `symbolic_drift_high` → `review_drift` action mapping

---

*Filed during architecture review session, 2026-05-26. The system remembers because we chose to align.*
