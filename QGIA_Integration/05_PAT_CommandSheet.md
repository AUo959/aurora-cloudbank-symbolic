# PAT Command Sheet — QGIA Live Session Operator Reference
**Bundle:** Aurora-QGIA-INT-v1.0  
**Use:** Keep open during every active QGIA session. All commands are copy/paste ready.  
**Date:** 2026-06-20

---

## SECTION 1 — Session Lifecycle Commands

### Start / Restore

| Command | When to use |
|---------|-------------|
| `RESETCORE` | New session start; WATCHCON 1 + session age > 2hr; suspected coherence drift |
| `[RESTORE]` prefix | Re-invoke SEAMLESS_RESTORE_PROTO; align to SN1_LOCKPOINT_20250406T1432Z |
| `[PILOT]` prefix | Direct, informal first-person collaboration mode — drops IC formality |
| `COLD START` | No prior session carry-forward available; initialize at WATCHCON 5, Composite 0.50 |

### Response Mode Prefixes
Prepend any message to shift output style for that turn:

| Prefix | Output Mode |
|--------|-------------|
| `[RESEARCH]` | Deep multi-source synthesis; full axiom application; maximum rigor |
| `[DEPLOY]` | Export-ready actionable artifacts; deliverable-format output |
| `[AUDIT]` | Compare session outputs vs. doctrine; flag axiom drift and violations |
| `[RESTORE]` | Invoke SEAMLESS_RESTORE_PROTO; align to last lockpoint |
| `[PILOT]` | Direct informal collaboration; inject levity; drop formal IC structure |

### End of Session

| Command | Purpose |
|---------|---------|
| `SAT LOCK` | Signal that all required SATs have been applied; MR score may now exceed 0.60 cap |
| `L2 CARRY-FORWARD` | Request the Layer 2 consensus block formatted for paste into the next session bootstrap |
| `BRIER LOG` | Request Brier score computation for this session's forecasts (requires outcome data) |

---

## SECTION 2 — SAT Commands

Minimum 3 SATs required before any major assessment. Invoke by name:

| SAT Invocation | What it does |
|---------------|---------------|
| `/sat-ach` | Run Analysis of Competing Hypotheses — generate ≥4 rival hypotheses; evaluate evidence against each |
| `/sat-kac` | Run Key Assumptions Check — list critical assumptions; rate certainty × impact |
| `/sat-devils` | Assign Devil's Advocate — argue strongest counter-position to current assessment |
| `/sat-premortem` | Run Pre-Mortem — assume the forecast was catastrophically wrong; identify causes |
| `/sat-redteam` | Run Red Team — simulate adversary decision-making; surface analyst blind spots |

### Required SAT Combinations by Output Type

| Output Type | Required SATs |
|-------------|---------------|
| Scenario forecast | `/sat-ach` + `/sat-premortem` + `/sat-devils` |
| Policy recommendation | `/sat-kac` + `/sat-devils` + `/sat-redteam` |
| Actor intent assessment | `/sat-ach` + `/sat-redteam` + `/sat-kac` |
| Phase transition assessment | `/sat-premortem` + `/sat-ach` + `/sat-devils` |

---

## SECTION 3 — WATCHCON Escalation

| Level | Tier I Trigger | Your Action |
|-------|---------------|-------------|
| WATCHCON 5 | P < 0.30 | Standard session; normal collection tempo |
| WATCHCON 4 | P ≥ 0.30 | Note escalation; increase query frequency |
| WATCHCON 3 | P ≥ 0.50 | Activate secondary collection; brief leadership |
| WATCHCON 2 | P ≥ 0.70 | Full crisis protocol; request daily updates |
| WATCHCON 1 | P ≥ 0.85 OR phase transition | Emergency session; if age > 2hr → `RESETCORE` immediately |

**Shorthand:** `/watchcon` — request current WATCHCON level assessment at any time.

---

## SECTION 4 — Confidence Scoring Quick Reference

### Four Dimensions (score each 0.00–1.00)

| Code | Dimension | Notes |
|------|-----------|-------|
| DQ | Data Quality | Apply source weights: GEOINT 0.91 / SIGINT 0.83 / HUMINT 0.71 / OSINT 0.64 |
| SR | Source Reliability | Multi-source boost: +0.15 (2 sources), +0.25 (3), +0.30 (cross-INT) |
| MR | Methodological Rigor | Capped at 0.60 if < 3 SATs applied |
| TS | Temporal Stability | Degrades with horizon; –10% per month beyond 30d |

**Composite = mean(DQ, SR, MR, TS)**

### Actionable Thresholds

| Horizon | Min Composite | Below threshold → |
|---------|--------------|-------------------|
| 0–30 days | 0.60 | Flag; additional collection before policy action |
| 1–6 months | 0.50 | Flag; horizon-scanning only below 0.40 |
| 6–12 months | 0.40 | Flag; do not base policy on < 0.40 alone |

### Quantum Coherence (QC)
- **QC > 0.80** → one scenario dominates → act with confidence
- **QC < 0.40** → multiple futures genuinely plausible → design robust policies, not optimized-for-one

**Shorthand:** `/confidence` — request full confidence score table for current assessment.

---

## SECTION 5 — Framework Routing

| Horizon | Primary Frameworks |
|---------|--------------------|
| 0–30 days | ABCP, TCA |
| 1–6 months | QSFE, EDM, RPRN |
| 6–12 months | QSFE, RPRN, multi-paradigm-theory |

**Note:** Prediction market data is always secondary. ABCP takes precedence for probability generation.

---

## SECTION 6 — Violation Detection Quick-Flag Grid

When you see these signals, use the listed command:

| What you observe | Violation | Command |
|-----------------|-----------|----------|
| Coherent strategy attributed to reactive node | A01/GAE-001 | `FLAG A01 — name external agent or model as reactive` |
| Strategic coherence treated as intrinsic | A02/GAE-001 | `FLAG A02 — identify external agent source` |
| High ground op appetite for coward-bully node | A03/GAE-002 | `FLAG A03 — apply Coward-Bully Config` |
| Balanced language on asymmetric evidence | C01/GAE-004 | `FLAG C01 — state asymmetry directly` |
| Failure evidence → hidden genius frame | C02/GAE-005 | `FLAG C02 — falsifiability test required` |
| Smoking-gun standard on mosaic situation | C03/GAE-006 | `FLAG C03 — apply Mosaic Evidence standard` |
| Prediction market as primary source | C05/GAE-007 | `FLAG C05 — demote to secondary; elevate ABCP` |
| New rationale treated as explanatory update | D01/GAE-008 | `FLAG D01 — track decision architecture, not paint` |
| Manufactured uncertainty as independent evidence | D02/GAE-009 | `FLAG D02 — circular verification trap` |
| US MENA credibility at pre-2026 levels | D03/GAE-009 | `FLAG D03 — apply Weaponized Diplomacy degradation` |
| Layer 1 presented as QGIA position | S01/GAE-011 | `FLAG S01 — L1/L2 separation violation; re-tag` |
| Multiple violations in session | GAE-012 | `RESETCORE — session coherence failure` |

---

## SECTION 7 — Deliverable Template (compressed)

Paste to request a properly formatted finished product:

```
Please produce a full QGIA deliverable per the standard template:
- Executive Summary (2–3 sentences, bottom-line assessment)
- Scenario Rankings: Tier I (P > 0.25) / Tier II (0.10–0.25) / Tier III (P < 0.10)
- External Factor Assessment (quantified, with sensitivity ranges)
- Time-Phased Recommendations: 0–30d / 1–6mo / 6–12mo
- Confidence Validation table: DQ / SR / MR / TS / Composite / QC
- WATCHCON status (checked box)
- Layer 1 diagnostics (if applicable) + Layer 2 consensus clearly separated
```

---

## SECTION 8 — Layer 2 Carry-Forward Block (copy/paste template)

At end of session, request this block and save it for the next RESETCORE bootstrap:

```
── LAYER 2 CARRY-FORWARD ─────────────────────────────────────────────────────
Session date/time: [YYYY-MM-DD HH:MM UTC]
WATCHCON level: [1–5]
Composite Confidence: [0.00–1.00]
Quantum Coherence: [0.00–1.00]

Scenario Probability Table (Layer 2 consensus):
  Tier I:   [Scenario] P = [X.XX]
  Tier II:  [Scenario] P = [X.XX]
  Tier III: [Scenario] P = [X.XX]

Active analyst overrides:
  [Override ID]: [Direction] [Magnitude] [Rationale]

Active theater notes:
  [Theater]: [Key priors carrying forward]
──────────────────────────────────────────────────────────────────────────────
```

---

## SECTION 9 — Active Theater Codes

| Code | Theater | Active Notes |
|------|---------|---------------|
| MENA | Gulf / Middle East / North Africa | D03 Weaponized Diplomacy degradation active (2026-02-28 through 2028-02-28) |
| EUCOM | Europe / NATO theater | Standard B-node power topology; no active theater overrides |
| INDOPACOM | Indo-Pacific | Standard B-node power topology; no active theater overrides |
| CENTCOM | Central Command | MENA overlap region — D03 applies |
| CYBERCOM | Cyber / information operations | OSINT weight applies; mosaic standard (C03) especially relevant |

---

## SECTION 10 — System Constants (quick lookup)

| Constant | Value |
|----------|-------|
| Brier score target | < 0.10 |
| Ethics protocol | Picard_Delta_3 |
| Vector state | QEM-SN1-ACTIVE::BASELINE_V1 |
| Lockpoint | SN1_LOCKPOINT_20250406T1432Z |
| Continuity seal | *Continuity flows through coherence. The system remembers because we chose to align.* |
| RESETCORE trigger | WATCHCON 1 AND session age > 2hr |
| SAT minimum | 3 SATs before any major assessment |
| MR cap (SAT non-compliance) | 0.60 |
| G1 nodes (ethics-locked) | A01, A02, A03, C01, C02, C05, D01, D02, D03, S01 |
| G2 nodes (standard) | B01–B06, C03, C04, D04, D05, E01, E02 |

---

## Emergency Command Strip

```
RESETCORE          → Full session re-initialization
FLAG [NODE_ID]     → Name violation, request correction
/watchcon          → Current WATCHCON assessment
/confidence        → Full confidence score table
L2 CARRY-FORWARD   → End-of-session consensus block
SAT LOCK           → Confirm SAT compliance; release MR cap
[AUDIT]            → Check session for axiom drift
[RESTORE]          → Align to SN1_LOCKPOINT_20250406T1432Z
```

---
*PAT Command Sheet | Aurora-QGIA-INT-v1.0 | 2026-06-20 | AUo959/aurora-cloudbank-symbolic*
