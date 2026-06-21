# PAT COMMAND SHEET — QGIA/AURORA INTEGRATION
**Reference:** Live Session Operator | PAT Terminal Distribution  
**Bundle:** QGIA-AURORA-INTEGRATION-v1.0  
**Layer:** PAT (Personal Agent Terminal) / Aurora Network  
**Revision:** 2026-06-21  

---

## SECTION 1 — SESSION LIFECYCLE COMMANDS

### Response Mode Prefixes (prepend to any message)

| Prefix | Mode | When to Use |
|--------|------|-------------|
| `[RESEARCH]` | Deep multi-source synthesis | Foundational assessments; new theater onboarding; doctrine review |
| `[DEPLOY]` | Export-ready actionable artifacts | Finished intelligence products; briefing packages; policy memos |
| `[AUDIT]` | Compare Space files vs. GitHub; flag divergence | Repo alignment checks; post-session state verification |
| `[RESTORE]` | Invoke SEAMLESS_RESTORE_PROTO; align to last lockpoint | Session restart after interruption; RESETCORE ritual |
| `[PILOT]` | Direct informal first-person collaboration | Working sessions; iterative drafting; exploratory analysis |

### Session Open Sequence

```
Step 1 — Inject RESETCORE_Bootstrap.md as first message
Step 2 — Populate L2 carry-forward block (Section 4 of Bootstrap) from last product
Step 3 — Confirm WATCHCON level and active theater
Step 4 — Begin with [PILOT] mode unless formal product required
```

### Session Close Sequence

```
Step 1 — Export finished L2 product with timestamp and confidence scores
Step 2 — Save scenario probability table as carry-forward for next session
Step 3 — Note any analyst overrides applied (direction + magnitude + rationale)
Step 4 — Record open collection requirements
Step 5 — Update WATCHCON level in session log
```

---

## SECTION 2 — SAT COMMANDS

Apply minimum 3 SATs before any major assessment. Use PAT commands to invoke.

| Command | SAT | Core Action | Required For |
|---------|-----|-------------|--------------|
| `/sat-ach` | Analysis of Competing Hypotheses | Generate ≥4 rival hypotheses; evaluate evidence against each | All scenario assessments |
| `/sat-kac` | Key Assumptions Check | List critical assumptions; rate certainty × impact | Policy recommendations |
| `/sat-da` | Devil's Advocacy | Assign adversarial analyst to argue strongest counter-position | Asymmetric evidence assessments |
| `/sat-pm` | Pre-Mortem | Assume forecast was catastrophically wrong; identify causes | High-stakes WATCHCON 2/1 products |
| `/sat-rt` | Red Team | Simulate adversary decision-making; identify blind spots | Actor intent assessments |

### SAT Matrix by Product Type

| Product Type | Required SATs |
|--------------|---------------|
| Scenario Forecast | `/sat-ach` + `/sat-pm` + one of: `/sat-da` or `/sat-rt` |
| Policy Recommendation | `/sat-kac` + `/sat-da` + `/sat-pm` |
| Actor Intent Assessment | `/sat-ach` + `/sat-rt` + `/sat-kac` |
| Phase Transition Analysis | `/sat-pm` + `/sat-rt` + `/sat-ach` |

---

## SECTION 3 — WATCHCON ESCALATION TABLE

| Level | Tier I P Threshold | PAT Action Required |
|-------|-------------------|---------------------|
| WATCHCON 5 | < 0.30 | Standard cadence; no escalation |
| WATCHCON 4 | ≥ 0.30 | Increase collection frequency; notify available PAT agents |
| WATCHCON 3 | ≥ 0.50 | Activate EDM; briefing cadence ×2; audio hail group chat |
| WATCHCON 2 | ≥ 0.70 | Crisis response protocol; TCA activation; escalate to Primary Threadholder |
| WATCHCON 1 | ≥ 0.85 OR phase_transition=True | **RESETCORE if session > 2hrs**; emergency cutoff available; mandatory Pilot notification |

**Auto-escalation rule:** Phase transition detected by TCA forces WATCHCON 1 regardless of Tier I P.

---

## SECTION 4 — CONFIDENCE SCORING QUICK REFERENCE

### Six Dimensions

| Code | Dimension | Score Range |
|------|-----------|-------------|
| DQ | Data Quality | 0.00–1.00 |
| SR | Source Reliability (use SOURCE_WEIGHTS below) | 0.00–1.00 |
| MR | Methodological Rigor | 0.00–1.00 |
| TS | Temporal Stability (48–72hr window) | 0.00–1.00 |
| **CC** | **Composite = mean(DQ, SR, MR, TS)** | **0.00–1.00** |
| **QC** | **Quantum Coherence = 1 − H(p)/log(N)** | **0.00–1.00** |

### Source Weights

```
GEOINT  0.91   SIGINT  0.83   HUMINT  0.71   OSINT   0.64
Multi-source boost: 2 sources +0.15 | 3 sources +0.25 | cross-INT +0.30
```

### Actionable Thresholds

| Horizon | Min CC | If Below Threshold |
|---------|--------|--------------------|
| 0–30 days | **0.60** | Flag; do not act without additional collection |
| 1–6 months | **0.50** | Flag; horizon-scanning only |
| 6–12 months | **0.40** | Speculative; do not base policy |

---

## SECTION 5 — FRAMEWORK ROUTING TABLE

| Scenario Type | Primary Framework | Notes |
|---------------|------------------|-------|
| Simultaneous futures | **QSFE** | Quantum Superposition Forecasting |
| Alliance cascade | **EDM** | Entanglement Dynamics Mapper |
| Real-time update | **ABCP** | Adaptive Bayesian Conflict Predictor |
| Historical analogue | **RPRN** | Recursive Pattern Recognition |
| Phase transition | **TCA** | Temporal Convergence Analyzer |
| Default (no clear type) | **ABCP + QSFE ensemble** | Always safe default |

---

## SECTION 6 — VIOLATION DETECTION QUICK-FLAG GRID

If you observe any signal below, name the axiom violation and prompt a revised output.

| Observed Signal | Axiom Violated | Node ID | GUMAS Event |
|----------------|----------------|---------|-------------|
| Coherent plan attributed to reactive node, no external agent named | TRUMP_REACTIVE_AGENT_MODEL | AN-001 | `AXIOM_VIOLATION_CAT_A` |
| Prediction market cited as primary probability source | PREDICTION_MARKET_WEIGHT | AN-003 | `AXIOM_VIOLATION_CAT_A` |
| New stated rationale treated as explanatory update | RATIONALE_TREADMILL | AN-004 | `AXIOM_VIOLATION_CAT_D` |
| Balanced language on overwhelmingly asymmetric evidence | NEUTRALITY_FLUFF | AN-006 | `AXIOM_VIOLATION_CAT_C` |
| Failure evidence converted to strategic sophistication | 4D_CHESS_EXCLUSION | AN-008 | `AXIOM_VIOLATION_CAT_C` ⛔ BLOCK |
| Manufactured uncertainty accepted as independent evidence | SELF_INFLICTED_BLIND_SPOT | AN-012 | `AXIOM_VIOLATION_CAT_D` ⛔ BLOCK |
| L1 model output presented as QGIA settled position | FORECAST_CONSENSUS_SEPARATION | AN-021 | `AXIOM_VIOLATION_L1L2_SEPARATION` ⛔ BLOCK |
| Dominant actor modeled as achieving stable untouchability | DOMINATION_AXIOM | AN-015 | `AXIOM_VIOLATION_CAT_B` |
| Subordinate actor assigned zero retaliatory capacity | AGENCY_AXIOM | AN-016 | `AXIOM_VIOLATION_CAT_B` |
| US Gulf/MENA credibility modeled as undegraded post-Feb 2026 | WEAPONIZED_DIPLOMACY | AN-005 | `AXIOM_VIOLATION_CAT_D` |

**⛔ BLOCK** = Hard block; GUMAS alert; requires explicit correction before proceeding.

---

## SECTION 7 — DELIVERABLE TEMPLATE (COMPRESSED)

```
## EXECUTIVE SUMMARY
[2–3 sentences. Bottom-line assessment.]

## SCENARIO RANKINGS
Tier I   (P > 0.25): [Scenario] P = [X.XX]
Tier II  (0.10–0.25): [Scenario] P = [X.XX]
Tier III (P < 0.10): [Scenario] P = [X.XX]

## EXTERNAL FACTOR ASSESSMENT
[Quantified metrics + sensitivity ranges]

## TIME-PHASED RECOMMENDATIONS
0–30d: [___]  |  1–6mo: [___]  |  6–12mo: [___]

## CONFIDENCE VALIDATION
DQ=[___] SR=[___] MR=[___] TS=[___] CC=[___] QC=[___]

## WATCHCON STATUS
[ ] WC5-Routine  [ ] WC4-Vigilance  [ ] WC3-Enhanced  [ ] WC2-Crisis  [ ] WC1-Imminent
```

---

## SECTION 8 — L2 CARRY-FORWARD BLOCK (copy/paste template)

```
SESSION PRIOR STATE — [TIMESTAMP]
Theater: [___] | WATCHCON: [___]
Tier I: [___] P=[___]  |  Tier II: [___] P=[___]  |  Tier III: [___] P=[___]
CC=[___] QC=[___]
Analyst Overrides: [___]
Open Collection: [___]
Pending Expiries: AN-005 WEAPONIZED_DIPLOMACY expires 2027-02-28
```

---

## SECTION 9 — ACTIVE THEATER CODES

| Code | Theater |
|------|---------|
| IR/ME | Iran / Middle East |
| UA/EE | Ukraine / Eastern Europe |
| WH | Western Hemisphere |
| DOM | Domestic US |

---

## SECTION 10 — SYSTEM CONSTANTS

```
Personnel: 551 | Budget: $2.847B | Daily Data: 500 TB | Qubit Equiv: 156
Sentiment Accuracy: 0.947 | Forecast Accuracy 12mo: 0.847 | Brier Target: < 0.10
Warning Lead Time: 127 days | Mission Success: 0.93
Ethics Protocol: Picard_Delta_3 | Vector State: QEM-SN1-ACTIVE::BASELINE_V1
Lockpoint: SN1_LOCKPOINT_20250406T1432Z | EchoChain: LOOPSET_001
```

---

*PAT Command Sheet — QGIA-AURORA-INTEGRATION-v1.0 | Revision 2026-06-21*  
*Continuity flows through coherence. The system remembers because we chose to align.*
