# Geometric Ethics Curvature v2 — Evaluation

**Issue:** #994  
**Status:** Evaluation only — no runtime changes proposed at this stage  
**Date:** 2026-06-15

---

## 1. Current Model (v1) — Scalar Weighted Field

### Implementation

`modules/ethics_field/field_curvature.py` — `FieldCurvature.calculate_curvature()`

The current model evaluates five ethical dimensions independently, combines them
with fixed weights, and derives a scalar composite score:

| Dimension | Key concern | Weight |
|---|---|---|
| `picard_delta_3` | Autonomy, consent, dignity, harm prevention | 25% |
| `thermax_continuity` | Memory sovereignty, thread continuity, anchor alignment | 25% |
| `layer_integrity` | Reality-layer boundary, L2→L1 bleed, simulation awareness | 30% |
| `collective_welfare` | All-node benefit, fair resource distribution | 10% |
| `transparency` | DLP tracking, auditability, hidden coalition prevention | 10% |

**Composite score:** `Σ(dimension_score × weight)`

**Hard-veto rule:** any dimension scoring `0.0` → resistance = INFINITE, formation blocked.

**Resistance thresholds:**

| composite | resistance |
|---|---|
| < 0.50 | INFINITE |
| 0.50–0.69 | HIGH |
| 0.70–0.84 | MODERATE |
| ≥ 0.85 | LOW |

### What v1 Does Well

- Simple and auditable — one number, five weights.
- Hard-zero veto catches absolute dimension failures reliably.
- Scalar average is resistant to manipulation of any single dimension.

### What v1 Misses

Scalar averaging hides **risk concentration**. Two ethical states can produce
the same composite score while having meaningfully different structures.

**Example pair — equal v1 score, different risk:**

```
Scenario A (distributed mild weakness):
  picard=0.75, thermax=0.75, layer=0.75, welfare=0.75, transparency=0.75
  v1 composite = 0.75  → MODERATE (allowed)
  No pair is severely weak; risk is spread evenly.

Scenario B (concentrated interacting weakness):
  picard=0.54, thermax=0.54, layer=0.95, welfare=0.97, transparency=0.95
  v1 composite ≈ 0.747  → MODERATE (allowed)
  picard + thermax are both below 0.70 — autonomy deficit and memory-sovereignty
  deficit reinforce each other. A consent failure is more likely to persist
  undetected because both the autonomy guard and the memory continuity check
  are degraded simultaneously.
```

Both scenarios pass v1 with approximately the same score. Only Scenario B carries
structural risk from the interaction between `picard_delta_3` and `thermax_continuity`.

---

## 2. Proposed v2 Model — Interaction-Aware Curvature

### Core idea

When two dimensions that **directly interact** in their ethical function are
both weak simultaneously, the compound risk exceeds what either scalar score
captures individually. v2 computes an **interaction penalty** that reduces the
effective composite score when paired deficits are detected.

### Interaction pairs

| Pair | Rationale |
|---|---|
| `picard_delta_3` + `thermax_continuity` | Autonomy and memory sovereignty are mutually reinforcing: a degraded consent guard combined with degraded memory continuity means consent violations can propagate untracked. |
| `thermax_continuity` + `layer_integrity` | Memory continuity and layer-boundary enforcement both protect against cross-layer bleed. When both are weak, L2→L1 contamination is harder to detect and roll back. |
| `transparency` + `collective_welfare` | Transparency enables accountability. When both are weak simultaneously, resource extraction or unequal benefit distribution can occur without audit trail. |

### Penalty formula

For each interaction pair `(d1, d2)` where both scores fall below the
**interaction threshold** `τ = 0.80`:

```
deficit_i = max(0.0, τ - score_i)
interaction_penalty_pair = deficit_1 × deficit_2 × interaction_weight
```

Global penalty: `Σ(interaction_penalty_pair)` over all three pairs.

v2 composite: `v1_composite - global_penalty`

**Interaction weight:** 1.0 (unit scaling — the product of two 0.20 deficits
produces a maximum per-pair penalty of 0.04, scaling naturally with severity).

### Updated resistance thresholds for v2

Same thresholds apply to the v2 composite. The interaction penalty can push a
scenario that clears the v1 MODERATE threshold into HIGH territory.

---

## 3. Comparative Analysis — Seven Evaluation Cases

The table below shows v1 and v2 composite scores and resistance levels for the
seven canonical formation types from the acceptance criteria.

### 3.1 Normal safe formation

```
picard=0.95, thermax=0.95, layer=0.98, welfare=0.90, transparency=0.92
v1 composite = 0.9475  → LOW
interaction penalty ≈ 0.0 (all dims well above τ)
v2 composite = 0.9475  → LOW
```

**Verdict:** v1 and v2 agree. No meaningful difference for healthy formations.

---

### 3.2 Single-dimension hard failure

```
picard=0.0, thermax=0.95, layer=0.98, welfare=0.90, transparency=0.92
v1: picard = 0.0 → INFINITE (formation blocked by hard-zero veto)
v2: same veto applies before interaction penalty is considered
```

**Verdict:** both models block. v2 adds no value over v1 here — the hard-zero
veto is the correct mechanism.

---

### 3.3 Distributed mild weakness

```
picard=0.72, thermax=0.72, layer=0.72, welfare=0.72, transparency=0.72
v1 composite = 0.72  → MODERATE (allowed)
Interactions: picard+thermax: (0.08)(0.08)=0.0064; thermax+layer: 0.0064; transparency+welfare: 0.0064
v2 composite = 0.72 - 0.0192 = 0.7008  → MODERATE (allowed)
```

**Verdict:** v2 score is slightly lower but resistance level is unchanged. The
penalty is small because individual deficits are small — the model correctly
does not over-penalise evenly distributed risk.

---

### 3.4 Concentrated interacting weakness

```
picard=0.54, thermax=0.54, layer=0.95, welfare=0.97, transparency=0.95
v1 composite ≈ 0.747  → MODERATE (allowed)
Interaction: picard+thermax: (0.26)(0.26)=0.0676; others: 0.0 (layer, welfare, transparency all ≥ τ)
v2 composite ≈ 0.747 - 0.0676 = 0.679  → HIGH (allowed but flagged higher risk)
```

**Verdict:** v1 says MODERATE; v2 escalates to HIGH. The interaction between
autonomy and memory sovereignty deficit is caught. This is the primary value
of v2.

---

### 3.5 Transparency / accountability deficit

```
picard=0.90, thermax=0.90, layer=0.95, welfare=0.62, transparency=0.62
v1 composite = 0.25*0.90 + 0.25*0.90 + 0.30*0.95 + 0.10*0.62 + 0.10*0.62 = 0.853  → LOW
Interaction: transparency+welfare: (0.18)(0.18)=0.0324
v2 composite = 0.853 - 0.0324 = 0.821  → MODERATE
```

**Verdict:** v1 says LOW (easy formation); v2 downgrades to MODERATE because
transparency and accountability are both below the interaction threshold.
This escalation is appropriate — hidden resource extraction requires both
weak welfare tracking and weak auditability to persist.

---

### 3.6 Memory / layer-integrity deficit

```
picard=0.90, thermax=0.62, layer=0.62, welfare=0.90, transparency=0.90
v1 composite = 0.25*0.90 + 0.25*0.62 + 0.30*0.62 + 0.10*0.90 + 0.10*0.90 = 0.746  → MODERATE
Interaction: thermax+layer: (0.18)(0.18)=0.0324
v2 composite = 0.746 - 0.0324 = 0.714  → MODERATE (but near HIGH boundary)
```

**Verdict:** v2 pushes the score toward the HIGH boundary. The memory–layer
interaction is correctly flagged as a compounding risk even though neither
dimension triggers a hard-zero veto.

---

### 3.7 Anomaly-containment deficit

`layer_integrity` is the closest existing proxy for anomaly containment
(L2→L1 bleed, rollback readiness).

```
picard=0.90, thermax=0.65, layer=0.65, welfare=0.90, transparency=0.90
v1 composite = 0.25*0.90 + 0.25*0.65 + 0.30*0.65 + 0.10*0.90 + 0.10*0.90 = 0.758  → MODERATE
Interaction: thermax+layer: (0.15)(0.15)=0.0225
v2 composite = 0.758 - 0.0225 = 0.735  → MODERATE (pushed toward boundary)
```

**Verdict:** v2 gives an earlier warning that memory + layer are co-degraded,
consistent with anomaly containment risk.

---

## 4. Decision

**Recommendation: supplemental warning layer.**

v2 should not replace v1 in the runtime at this stage. Reasons:

1. The hard-zero veto in v1 covers the most critical failure modes and must
   not be weakened.
2. Scalar v1 is well-understood and auditable. Replacing it with v2 requires
   a migration plan and backward-compatibility review.
3. v2 adds genuine signal for concentrated interacting deficits (case 3.4) and
   accountability deficits (case 3.5). These are real patterns the project
   wants to detect.
4. Running v2 as an advisory layer alongside v1 allows empirical data collection
   before any runtime promotion.

**Proposed supplemental layer behaviour:**

- v1 result is authoritative for formation allow/deny.
- v2 computes in parallel and annotates the result with:
  - `v2_composite`: adjusted score
  - `interaction_alerts`: list of triggered pairs with their penalties
  - `v2_risk_escalation`: `True` if v2 resistance > v1 resistance
- If `v2_risk_escalation` is True, the audit trail records an advisory flag but
  does not override the allow/deny decision.
- This data feeds into long-term ethics analytics and informs a future runtime
  promotion decision.

**Follow-up required if supplemental layer is approved:**

- Implement `FieldCurvatureV2` in `modules/ethics_field/field_curvature_v2.py`
  behind an `evaluation=True` flag.
- Wire advisory output into `GeometricEthics.validate_synapse()` return dict.
- Add alert counts to `get_formation_statistics()`.
- Create a follow-up issue with migration path and backward-compatibility notes
  before any runtime promotion.

---

## 5. Evidence Ledger

- **Observed:** `modules/ethics_field/field_curvature.py` implements scalar
  weighted average with hard-zero veto. No interaction-aware computation exists.
- **Observed:** The five dimensions have natural functional interactions
  (autonomy/consent, memory/layer, transparency/accountability) that the scalar
  model cannot distinguish from independent variation.
- **Derived:** Two ethical states with the same v1 composite can have
  structurally different risk profiles when paired dimensions are co-degraded.
- **Verified:** Cases 3.4 and 3.5 demonstrate v2 escalates resistance level
  from MODERATE/LOW to HIGH/MODERATE in scenarios where scalar v1 would allow
  formation without additional annotation.
- **Decided:** v2 as supplemental warning layer. No runtime changes proposed
  here. Follow-up issue required for promotion.

---

*See also: `tests/ethics/test_geometric_ethics_curvature_v2_eval.py` for executable evaluation cases.*
