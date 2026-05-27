---
id: 20260526-drift-threshold-stratification
date: 2026-05-26
filed_by: Aurora session review (2026-05-26)
status: open
priority: medium
category: documentation
affected_files:
  - modules/reflective_autonomy/capsule_linter.py
  - threadcore_registry.json
  - src/nexus_enhancement_hub.js
  - modules/reflective_autonomy/autonomic_correction_engine.py
issue_url: 
tags: [drift, governance, thresholds, architecture-doc]
---

# Drift Threshold Stratification — Needs Architecture Doc Entry

## Observation

Aurora uses three distinct symbolic drift thresholds across three system layers. These values are currently **implicit** — each lives in its own file with no cross-reference and no shared documentation:

| Layer | Threshold | Source |
|---|---|---|
| Capsule / ThreadCore | `0.002` | `capsule_linter.py` → `DEFAULT_MAX_DRIFT`; `threadcore_registry.json` → `validation_rules.max_drift_threshold` |
| QGIA Agent Network | `0.02` | QGIA operational layer / Velatrix drift monitoring |
| System / Macro | `0.1` | `DriftAwareAgent` in `nexus_enhancement_hub.js` |

The 10x ratio between layers is intentional — each layer is more tolerant than the one below it because it operates over a larger, noisier population. But this rationale is undocumented.

## Risk / Impact

- A contributor seeing `0.002` in `capsule_linter.py` may assume it applies universally, then be confused when agent-level drift at `0.015` does not trigger a linter warning.
- A contributor tuning QGIA agent thresholds may not realize the capsule linter has a separate, independent threshold with different semantics.
- Debugging a `symbolic_drift_high` warning at the capsule layer while Velatrix is quiet at the agent layer (because `0.015 < 0.02`) will look inconsistent without this map.
- If any of the three values are hardcoded (not config-driven), they can diverge silently across refactors.

## Suggested Actions

- [ ] Add a **Drift Threshold Reference** section to `ARCHITECTURE.md` (or create the file) containing the three-layer table above plus the 10x-ratio rationale
- [ ] Add inline cross-reference comments in `capsule_linter.py` and `threadcore_registry.json` pointing to the other two threshold layers
- [ ] Evaluate whether a single `drift_thresholds.yaml` config file imported by all three layers would eliminate silent divergence risk
- [ ] Confirm whether the `0.02` and `0.1` values in the QGIA layer are hardcoded or config-driven — if hardcoded, prioritize the config consolidation above

## Related Files

- `modules/reflective_autonomy/capsule_linter.py` — `DEFAULT_MAX_DRIFT = 0.002`
- `threadcore_registry.json` — `validation_rules.max_drift_threshold`
- `src/nexus_enhancement_hub.js` — `DriftAwareAgent` (system-level threshold)
- `modules/reflective_autonomy/autonomic_correction_engine.py` — `symbolic_drift_high` → `review_drift` action mapping

---

*Filed: 2026-05-26*
