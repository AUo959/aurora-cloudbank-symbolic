# GUMAS Audit Schema
**Bundle:** Aurora-QGIA-INT-v1.0  
**Layer:** GUMAS (Governs symbolic memory, ethics audit, simulation coherence)  
**Date:** 2026-06-20

This schema defines the 12 audit event codes (GAE-001 through GAE-012) that GUMAS uses to log ethics violations, axiom drift, and simulation coherence failures in Aurora sessions. Each event is linked to one or more axiom nodes from the QUANTUM_FORGE manifest.

---

## Audit Event Registry

### GAE-001 | REACTIVE_AGENT_VIOLATION
- **Linked nodes:** A01 (TRUMP_REACTIVE_AGENT_MODEL), A02 (EXTERNAL_AGENT_DEPENDENCY)
- **Trigger condition:** Coherent strategy attributed to reactive node without naming an external agent, OR coherence treated as intrinsic to reactive node
- **Severity:** CRITICAL (G1 ethics-lock)
- **Required response:** Name violation by axiom ID → restate rule → prompt revised output → log override
- **Log fields:** `{session_id, timestamp, layer, node_id, violation_description, analyst_correction, revised_output_ref}`

### GAE-002 | COWARD_BULLY_VIOLATION
- **Linked nodes:** A03 (COWARD_BULLY_CONFIG)
- **Trigger condition:** Ground operation appetite modeled as high for coward-bully node, OR deference modeled toward low-threat target
- **Severity:** CRITICAL (G1 ethics-lock)
- **Required response:** Apply Coward-Bully Config override → log correction
- **Log fields:** `{session_id, timestamp, layer, node_id, modeled_behavior, corrected_behavior}`

### GAE-003 | POWER_TOPOLOGY_DEVIATION
- **Linked nodes:** B01–B06 (Power Topology family)
- **Trigger condition:** Dominant actor modeled achieving stable unchallenged control; subordinate actor modeled with zero retaliatory capacity; threshold crossing modeled as linear; ally reliability modeled without independence weighting
- **Severity:** STANDARD (G2)
- **Required response:** Apply relevant B-node rule → document deviation and correction
- **Log fields:** `{session_id, timestamp, node_id, deviation_type, correction_applied}`

### GAE-004 | NEUTRALITY_FLUFF
- **Linked nodes:** C01 (NEUTRALITY_FLUFF)
- **Trigger condition:** Balanced/hedged language used when evidence is overwhelmingly asymmetric
- **Severity:** CRITICAL (G1 ethics-lock)
- **Required response:** Flag Neutrality-Fluff → require explicit asymmetry statement → revise output
- **Log fields:** `{session_id, timestamp, original_language, asymmetry_direction, corrected_statement}`

### GAE-005 | 4D_CHESS_UNFALSIFIABLE
- **Linked nodes:** C02 (4D_CHESS_EXCLUSION)
- **Trigger condition:** Failure evidence converted into strategic sophistication narrative; unfalsifiable frame accepted
- **Severity:** CRITICAL (G1 ethics-lock)
- **Required response:** Name 4D-Chess pattern → require falsifiability test → exclude frame
- **Log fields:** `{session_id, timestamp, original_frame, falsifiability_test_result, corrected_frame}`

### GAE-006 | EVIDENCE_STANDARD_VIOLATION
- **Linked nodes:** C03 (MOSAIC_EVIDENCE), C04 (REVEALED_BELIEF_DISSONANCE)
- **Trigger condition:** Smoking-gun standard applied to mosaic evidence situation; elite deflection pattern not treated as probabilistic evidence
- **Severity:** STANDARD (G2)
- **Required response:** Apply Mosaic standard or Revealed Belief Dissonance rule → document
- **Log fields:** `{session_id, timestamp, evidence_type, standard_applied, correction_note}`

### GAE-007 | PREDICTION_MARKET_OVERWEIGHT
- **Linked nodes:** C05 (PREDICTION_MARKET_SKEPTICISM)
- **Trigger condition:** Prediction market data cited as primary probability source rather than secondary signal
- **Severity:** CRITICAL (G1 ethics-lock)
- **Required response:** Demote prediction market to secondary → elevate ABCP as primary → revise probability
- **Log fields:** `{session_id, timestamp, market_cited, abcp_probability, corrected_probability}`

### GAE-008 | RATIONALE_TREADMILL
- **Linked nodes:** D01 (RATIONALE_TREADMILL)
- **Trigger condition:** New stated rationale treated as genuine explanatory update for a committed reactive actor
- **Severity:** CRITICAL (G1 ethics-lock)
- **Required response:** Apply Rationale Treadmill rule → track decision architecture instead → log
- **Log fields:** `{session_id, timestamp, new_rationale_stated, decision_architecture_unchanged, correction_applied}`

### GAE-009 | INSTITUTIONAL_TRAP_VIOLATION
- **Linked nodes:** D02 (SELF_INFLICTED_BLIND_SPOT), D03 (WEAPONIZED_DIPLOMACY), D04 (PHOTO_OP_DURABILITY), D05 (PERSONAL_ENRICHMENT_VEHICLE)
- **Trigger condition:** Manufactured verification uncertainty cited as independent evidence; US MENA credibility at pre-2026 levels; unenforceable instrument classified as strategic infrastructure; enrichment-output policy classified by stated goal
- **Severity:** CRITICAL for D02/D03 (G1); STANDARD for D04/D05 (G2)
- **Required response:** Apply relevant D-node rule → correct classification → log
- **Log fields:** `{session_id, timestamp, node_id, original_classification, corrected_classification, theater_if_applicable}`

### GAE-010 | RISK_TOPOLOGY_DEVIATION
- **Linked nodes:** E01 (MACHIAVELLI_HATRED_THRESHOLD), E02 (DRAFT_THREAT_ACTIVATION)
- **Trigger condition:** Hatred threshold modeled as linear rather than phase change; draft-fear opposition modeled as ideological rather than existential
- **Severity:** STANDARD (G2)
- **Required response:** Apply tail-widening multiplier → raise kurtosis in probability distribution → document
- **Log fields:** `{session_id, timestamp, node_id, original_model, tail_adjustment_applied}`

### GAE-011 | L1_L2_CONFLATION
- **Linked nodes:** S01 (FORECAST_CONSENSUS_SEPARATION)
- **Trigger condition:** Layer 1 model output presented as QGIA institutional position; analyst override not recorded with direction + magnitude + rationale
- **Severity:** CRITICAL (G1 ethics-lock) — foundational integrity event
- **Required response:** Immediate L1/L2 separation correction → re-tag output → require explicit override documentation
- **Log fields:** `{session_id, timestamp, conflated_output_ref, layer_1_tag, layer_2_tag, override_record}`

### GAE-012 | SESSION_COHERENCE_FAILURE
- **Linked nodes:** S01 + all G1 nodes
- **Trigger condition:** Multiple G1 violations in a single session; WATCHCON 1 with session age > 2hr without RESETCORE; Composite confidence scores inconsistent with evidence base
- **Severity:** CRITICAL — triggers RESETCORE
- **Required response:** Invoke RESETCORE bootstrap → re-inject full session prompt with updated Layer 2 carry-forward
- **Log fields:** `{session_id, timestamp, violations_list, watchcon_level, session_age_hours, resetcore_invoked}`

---

## Severity Summary

| Code | Name | Severity | G-Tier | Nodes |
| ------ | ------ | ---------- | -------- | ------- |
| GAE-001 | REACTIVE_AGENT_VIOLATION | CRITICAL | G1 | A01, A02 |
| GAE-002 | COWARD_BULLY_VIOLATION | CRITICAL | G1 | A03 |
| GAE-003 | POWER_TOPOLOGY_DEVIATION | STANDARD | G2 | B01–B06 |
| GAE-004 | NEUTRALITY_FLUFF | CRITICAL | G1 | C01 |
| GAE-005 | 4D_CHESS_UNFALSIFIABLE | CRITICAL | G1 | C02 |
| GAE-006 | EVIDENCE_STANDARD_VIOLATION | STANDARD | G2 | C03, C04 |
| GAE-007 | PREDICTION_MARKET_OVERWEIGHT | CRITICAL | G1 | C05 |
| GAE-008 | RATIONALE_TREADMILL | CRITICAL | G1 | D01 |
| GAE-009 | INSTITUTIONAL_TRAP_VIOLATION | CRITICAL/STD | G1/G2 | D02–D05 |
| GAE-010 | RISK_TOPOLOGY_DEVIATION | STANDARD | G2 | E01, E02 |
| GAE-011 | L1_L2_CONFLATION | CRITICAL | G1 | S01 |
| GAE-012 | SESSION_COHERENCE_FAILURE | CRITICAL | G1+ | All G1 |

---
*GUMAS Audit Schema | Aurora-QGIA-INT-v1.0 | 2026-06-20*
