---
applyTo: "**/capsule_linter*,**/threadcore_registry*,**/qgia*,**/drift*,**/anomaly*"
---

# 🔴 Critical: Drift Threshold Stratification

This codebase uses a **three-layer stratified drift threshold system**. These values are
**not arbitrary** — they encode intentional 10x sensitivity ratios across architectural layers.

## Quick Reference

| Layer | Threshold | Location | Trigger |
|-------|-----------|----------|---------|
| L1 Capsule / Governance | `0.002` | `capsule_linter.py` | Per-capsule symbolic drift; tightest layer |
| L2 Agent / QGIA | `0.02` | QGIA agent config | Per-agent session drift; mid-layer |
| L3 Macro / Network | `0.1` | `threadcore_registry.json` | Cross-network coherence; loosest layer |

## Before You Touch Any Threshold

1. Read the full rationale: [`docs/dev-notes/drift-threshold-stratification.md`](../../docs/dev-notes/drift-threshold-stratification.md)
2. Understand which layer you are modifying and why the ratio between layers matters
3. If you change one threshold, verify the others are still proportionally correct
4. Update the dev note to reflect any intentional changes

**Silent divergence between layers is the primary risk.** A value that looks correct in
isolation may break the coherence contract between layers.
