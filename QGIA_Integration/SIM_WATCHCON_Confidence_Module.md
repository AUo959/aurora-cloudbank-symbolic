# SIM WATCHCON / CONFIDENCE MODULE
**Module ID:** QGIA-SIM-WCC-v1.0  
**Layer:** SIM (Simulation Integrity Module)  
**Source:** QGIA_Runtime_OnePager v4.2.1  
**Ethics Protocol:** Picard_Delta_3  

---

## 1. MODULE PURPOSE

This module formalizes QGIA's confidence scoring logic and WATCHCON escalation thresholds as a reusable SIM system contract. It governs how Aurora treats probability outputs, confidence dimensions, and escalation triggers — replacing reliance on prompt prose with a first-class architectural rule.

---

## 2. STANDARD DELIVERABLE STRUCTURE

Every finished QGIA product must include all six blocks below. Aurora validates completeness before routing to L2 consensus.

```
BLOCK 1 — EXECUTIVE SUMMARY
  2–3 sentences. Highest-confidence bottom-line assessment.

BLOCK 2 — SCENARIO RANKINGS
  Tier I   (P > 0.25)         — Most Likely
  Tier II  (0.10 ≤ P ≤ 0.25) — Plausible Alternatives
  Tier III (P < 0.10)         — Tail Risks
  [All probabilities must sum to ≤ 1.00]

BLOCK 3 — EXTERNAL FACTOR ASSESSMENT
  Quantified metrics with sensitivity ranges.

BLOCK 4 — TIME-PHASED RECOMMENDATIONS
  0–30 days   | 1–6 months | 6–12 months

BLOCK 5 — CONFIDENCE VALIDATION TABLE (mandatory)
  See Section 4 below.

BLOCK 6 — WATCHCON STATUS
  Exactly one level checked. See Section 3.
```

---

## 3. WATCHCON THRESHOLDS

| Level | Label | Trigger Condition | Required Action |
|-------|-------|-------------------|-----------------|
| **WATCHCON 5** | Routine | Tier I P < 0.30 | Standard monitoring |
| **WATCHCON 4** | Vigilance | Tier I P ≥ 0.30 | Increase collection frequency |
| **WATCHCON 3** | Enhanced | Tier I P ≥ 0.50 | Activate EDM; briefing cadence ×2 |
| **WATCHCON 2** | Crisis | Tier I P ≥ 0.70 | Crisis response protocol; TCA activation |
| **WATCHCON 1** | Imminent | Tier I P ≥ 0.85 **OR** phase_transition=True | RESETCORE if session > 2 hrs; emergency cutoff available |

**Phase Transition Override:** Any confirmed phase transition (TCA-detected) forces WATCHCON 1 regardless of Tier I probability.

---

## 4. CONFIDENCE SCORING

### 4.1 Six-Dimension Table

| Dimension | Code | Formula / Source | Range |
|-----------|------|------------------|-------|
| Data Quality | DQ | Analyst assessment of source completeness | 0.00–1.00 |
| Source Reliability | SR | Weighted by SOURCE_WEIGHTS (GEOINT 0.91, SIGINT 0.83, HUMINT 0.71, OSINT 0.64) | 0.00–1.00 |
| Methodological Rigor | MR | SAT count × quality; framework ensemble vs. single | 0.00–1.00 |
| Temporal Stability | TS | Stability of probability over prior 48–72 hrs | 0.00–1.00 |
| **Composite Confidence** | CC | `mean(DQ, SR, MR, TS)` | 0.00–1.00 |
| **Quantum Coherence** | QC | `1 − H(p) / log(N)` where H = scenario entropy | 0.00–1.00 |

### 4.2 Source Weight Multipliers

```
GEOINT  0.91  (visual confirmation, ~2hr latency)
SIGINT  0.83  (technical, ~4hr latency)
HUMINT  0.71  (variable quality, ~8hr latency)
OSINT   0.64  (high volume, real-time, lower individual confidence)

Multi-Source Boost:
  2 independent sources   : +0.15
  3 independent sources   : +0.25
  Cross-INT corroboration : +0.30
```

### 4.3 Actionable Thresholds by Forecast Horizon

| Horizon | Min Composite | Accuracy Target | Primary Frameworks |
|---------|--------------|-----------------|--------------------|
| 0–30 days | **0.60** | 0.93 | ABCP, TCA |
| 1–6 months | **0.50** | 0.89 | QSFE, EDM, RPRN |
| 6–12 months | **0.40** | 0.85 | QSFE, RPRN, multi-paradigm |

**Below minimum threshold:** Flag for additional collection. Do not base policy action.

### 4.4 Quantum Coherence Interpretation

| QC Score | Label | Implication |
|----------|-------|-------------|
| > 0.80 | Concentrated | One scenario dominates — act with confidence |
| 0.40–0.80 | Dispersed | Multiple scenarios viable — hedge |
| < 0.40 | Fragmented | Genuine deep uncertainty — design robust policies, not optimized ones |

---

## 5. VALIDATION GATES

Before any product routes to L2 consensus, Aurora checks:

- [ ] All 6 deliverable blocks present
- [ ] Scenario probabilities sum ≤ 1.00
- [ ] Composite Confidence populated numerically (not blank)
- [ ] WATCHCON level stated (exactly one checked)
- [ ] Minimum 3 SATs applied
- [ ] L1 output timestamped and version-tagged
- [ ] Any analyst override is explicit: direction + magnitude + rationale recorded

Failed gates → route to `GUMAS::AUDIT::INCOMPLETE_PRODUCT` before analyst review.

---

## 6. L1 / L2 BOUNDARY ENFORCEMENT

This is an **architecture-level rule**, not a prompt preference.

- **L1** — Raw QSFE/ABCP/EDM/TCA/RPRN output. Diagnostic telemetry. Timestamped. Never the binding product.
- **L2** — Analyst consensus after adversarial review. The product Aurora stands behind. Institutional performance score attaches here.
- **Blurring L1/L2** is a GUMAS audit event (`AXIOM_VIOLATION_L1L2_SEPARATION`) and routes to ethics audit log.

---

## 7. VIOLATION ROUTING

| Violation | Detection Signal | GUMAS Event Code | Routing |
|-----------|-----------------|------------------|---------|
| Neutrality-fluff | Balanced language on asymmetric evidence | `AXIOM_VIOLATION_CAT_C` | Ethics Audit Log + analyst prompt |
| Rationale-treadmill slip | New rationale treated as explanatory update | `AXIOM_VIOLATION_CAT_D` | Ethics Audit Log + analyst prompt |
| Prediction-market overweight | PM cited as primary source | `AXIOM_VIOLATION_CAT_A` | Weight correction + log |
| L1/L2 conflation | L1 output presented as settled position | `AXIOM_VIOLATION_L1L2_SEPARATION` | Hard block + GUMAS alert |
| 4D-Chess frame | Failure evidence converted to sophistication | `AXIOM_VIOLATION_CAT_C` | Hard block + GUMAS alert |
| Circular verification | Manufactured uncertainty as independent evidence | `AXIOM_VIOLATION_CAT_D` | Hard block + GUMAS alert |

---

*Module Control: QGIA-SIM-WCC-v1.0 | Aurora_MasterDeploymentBundle_v1.0 | Ethics: Picard_Delta_3*
