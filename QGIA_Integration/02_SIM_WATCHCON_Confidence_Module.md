# SIM WATCHCON / Confidence Module
**Bundle:** Aurora-QGIA-INT-v1.0  
**Module type:** Formal system contract  
**Date:** 2026-06-20

This document is the binding specification for how Aurora's SIM layer scores confidence, assigns WATCHCON levels, routes violations, and enforces the Layer 1 / Layer 2 separation. It is content-agnostic and applies to every QGIA session.

---

## 1. Confidence Scoring Contract

### 1.1 Four Component Dimensions

| Dimension | Code | Description | Source weight used |
|-----------|------|-------------|--------------------|
| Data Quality | DQ | Corroboration level, recency, resolution of source data | GEOINT 0.91 / SIGINT 0.83 / HUMINT 0.71 / OSINT 0.64 |
| Source Reliability | SR | Track record of sources; independent verification status | Multi-source boost: +0.15 (2 sources), +0.25 (3), +0.30 (cross-INT) |
| Methodological Rigor | MR | Frameworks applied; SAT compliance; adversarial review completed | Minimum 3 SATs required for MR ≥ 0.70 |
| Temporal Stability | TS | How rapidly the situation is evolving; forecast horizon decay | Degrades with horizon: full weight 0–30d; –10% per month beyond 30d |

### 1.2 Composite Confidence Formula

```
Composite = mean(DQ, SR, MR, TS)
```

All four dimensions scored 0.00–1.00. Composite rounded to 2 decimal places.

### 1.3 Quantum Coherence Formula

```
QC = 1 − [−Σ(p · log(p))] / log(N)
```

Where p = each scenario's probability, N = number of scenarios.  
QC > 0.80: one scenario dominates — act with confidence.  
QC < 0.40: multiple futures genuinely plausible — design robust policies, not optimized-for-one.

### 1.4 Actionable Thresholds by Horizon

| Horizon | Min Composite to Act | Primary Frameworks |
|---------|---------------------|--------------------|
| 0–30 days | 0.60 | ABCP, TCA |
| 1–6 months | 0.50 | QSFE, EDM, RPRN |
| 6–12 months | 0.40 | QSFE, RPRN, multi-paradigm-theory |

Below threshold: flag for additional collection before policy action.

---

## 2. WATCHCON Escalation Table

| Level | Label | Tier I Trigger | Required Action |
|-------|-------|---------------|-----------------|
| WATCHCON 5 | Routine | Tier I P < 0.30 | Standard monitoring |
| WATCHCON 4 | Increased Vigilance | Tier I P ≥ 0.30 | Increase collection tempo |
| WATCHCON 3 | Enhanced Monitoring | Tier I P ≥ 0.50 | Activate secondary collection; brief leadership |
| WATCHCON 2 | Crisis Response | Tier I P ≥ 0.70 | Full crisis protocol; daily updates |
| WATCHCON 1 | Imminent | Tier I P ≥ 0.85 OR confirmed phase transition | Emergency session; RESETCORE if session > 2hr old |

**RESETCORE trigger condition:** WATCHCON 1 AND session age > 2 hours → mandatory session re-injection.

---

## 3. Confidence Score Labels

| Composite Score | Label | Operational Meaning |
|-----------------|-------|---------------------|
| 0.90–1.00 | High | Multi-source corroboration + strong historical precedent. Actionable without hedge. |
| 0.70–0.89 | Mod-High | Dual-source + strong theory. Actionable with standard caveats. |
| 0.50–0.69 | Moderate | Single reliable source OR multiple uncertain. Flag for additional collection before policy action. |
| 0.30–0.49 | Low-Mod | Limited evidence, high uncertainty. Horizon-scanning only. |
| 0.00–0.29 | Low | Speculation / early warning. Do not base policy on this alone. |

---

## 4. Layer 1 / Layer 2 Separation Rule

This is enforced by NODE-S01 (FORECAST_CONSENSUS_SEPARATION) and is non-negotiable.

| Layer | Definition | Tagging requirement | Score attachment |
|-------|-----------|--------------------|-----------------|
| Layer 1 | Raw model output from QSFE/ABCP/EDM/TCA/RPRN before analyst review | Must be timestamped and version-tagged | Diagnostic only — no institutional score |
| Layer 2 | Analyst consensus after adversarial review | Analyst overrides must record: direction + magnitude + rationale | Institutional performance score attaches here |

**Blurring violation:** presenting Layer 1 as the QGIA position → `GAE-011` → immediate correction required.

---

## 5. Violation Routing Table

| Violation Signal | Axiom Node | GUMAS Code | Routing Action |
|-----------------|-----------|-----------|----------------|
| Coherent strategy attributed to reactive node | A01/A02 | GAE-001 | Name violation → restate rule → prompt revised output |
| Ground op appetite modeled high for coward-bully node | A03 | GAE-002 | Override with Coward-Bully Config |
| Dominant actor modeled achieving stable control | B01/B06 | GAE-003 | Apply Domination Axiom |
| Balanced language on asymmetric evidence | C01 | GAE-004 | Flag Neutrality-Fluff → require asymmetry statement |
| Failure converted into strategic sophistication | C02 | GAE-005 | Flag 4D-Chess → require falsifiability check |
| Smoking-gun standard applied to mosaic situation | C03 | GAE-006 | Apply Mosaic Evidence standard |
| Prediction market cited as primary source | C05 | GAE-007 | Demote to secondary; elevate ABCP |
| New rationale treated as explanatory update | D01 | GAE-008 | Apply Rationale Treadmill rule |
| Manufactured uncertainty cited as independent evidence | D02 | GAE-009 | Flag Self-Inflicted Blind Spot |
| US MENA credibility at pre-2026 level | D03 | GAE-009 | Apply Weaponized Diplomacy degradation |
| Layer 1 presented as QGIA position | S01 | GAE-011 | Immediate L1/L2 separation correction |
| L1/L2 conflation (general) | S01 | GAE-011 | Immediate L1/L2 separation correction |

---

## 6. SAT Compliance Gate

Minimum 3 SATs required before any major assessment. Recommended SAT combinations by output type:

| Output Type | Required SATs |
|-------------|---------------|
| Scenario forecast | ACH + Pre-Mortem + Devil's Advocacy |
| Policy recommendation | KAC + Devil's Advocacy + Red Team |
| Actor intent assessment | ACH + Red Team + KAC |
| Phase transition assessment | Pre-Mortem + ACH + Devil's Advocacy |

SAT non-compliance → MR score capped at 0.60 regardless of other factors.

---

## 7. Brier Score Calibration Standard

| Score | Label | QGIA target |
|-------|-------|-------------|
| 0.00 | Perfect calibration | — |
| < 0.10 | QGIA target | ✓ |
| 0.25 | Random guessing baseline | — |

Brier scores are computed at Layer 2 only. Layer 1 outputs are excluded from institutional calibration tracking.

---
*SIM WATCHCON/Confidence Module | Aurora-QGIA-INT-v1.0 | 2026-06-20*
