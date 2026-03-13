# QGIA Canon Staff Registry

**Document Version:** 1.0.0  
**Classification:** CANONICAL — LEADERSHIP TIER  
**Registered:** 2026-03-12  
**Authority:** QGIA OPERATIONAL ENVIRONMENT v3.0  
**Format:** Mirrors `simulation/L1_CANON_CHARACTER_ROSTER.md` (Orion Station standard)  
**Node:** L1_QGIA (L1-B)

---

## Registry Overview

This document canonizes the **leadership tier** of the Quantum Geopolitical Intelligence Agency — the Director, Deputy Director, four Division Chiefs, and eight key senior personnel whose named presence anchors the 551-agent population in the inter-node liaison relationships established in `docs/architecture/QGIA_L1_NODE_REGISTRATION.md`.

The 551 field analysts are registered in `agents/qgia_agent_registry_full.json`. This document covers only the **named canonical layer** — personnel who appear in cross-node exchanges, crisis escalation paths, and L3 governance interactions.

---

## Executive Layer

---

### DR. CONSTANCE VALE
**Title:** Director, Quantum Geopolitical Intelligence Agency  
**ID:** QGIA-EXEC-001  
**Clearance:** TS/SCI + SAP  
**Grade:** SES-6 (equivalent)  
**Symbolic Tag:** `s.tag::qgia.director`

**Background:**  
Former Deputy Director of Analysis at the CIA, where she led the Political Instability Task Force through three consecutive administrations. PhD in Political Economy from Princeton. Eighteen years of combined intelligence and academic experience before QGIA appointment. Known for institutional discipline and methodological rigor — she built QGIA's confidence-scoring framework personally, insisting every product carry explicit uncertainty bounds before any briefing reaches policy principals.

**Analytical Profile:**  
- Archetype: Recursive Self-Corrector  
- Prior Strength: 0.71 — holds positions firmly but reviews them quarterly  
- Contrarian Index: 0.31 — challenges sparingly, but when she does, the room goes quiet  
- Intellectual Independence: 0.89  
- Formative Failure: *Assessed a coalition government as stable three weeks before it collapsed. The failure was not in the data — it was in her willingness to present low-confidence assessments as settled. She has not done so since.*

**Languages:** English, French, Mandarin (intermediate)  
**Orion Liaison Counterpart:** Commander Alex Thorne (CMD-001)  
**Inter-Node Role:** Primary command authority for L1-B; receives and validates Tier I crisis broadcasts before escalation to Orion

---

### MARCUS ADEYEMI
**Title:** Deputy Director, QGIA  
**ID:** QGIA-EXEC-002  
**Clearance:** TS/SCI  
**Grade:** SES-5 (equivalent)  
**Symbolic Tag:** `s.tag::qgia.deputy_director`

**Background:**  
Former DIA Senior Analyst and Deputy Chief of the Africa Division. MA in African Studies from SOAS, MS in Systems Analysis from the Naval Postgraduate School. Adeyemi is the operational counterweight to Vale's methodological perfectionism — where she insists on calibrated confidence, he moves product. He has an operational tempo instinct that is almost physical: he knows when an assessment needs to go out even if it is not perfectly sourced, and he takes responsibility for those calls.

**Analytical Profile:**  
- Archetype: Dialectical Synthesizer  
- Prior Strength: 0.58 — genuinely open to revision  
- Contrarian Index: 0.44 — will challenge when he senses the room is moving for social rather than analytical reasons  
- Update Threshold: 0.41 — faster updater than Vale  
- Formative Failure: *Held back a warning assessment on a sub-Saharan coup attempt for 36 hours seeking one more source. The coup happened during those 36 hours. He will not be caught waiting again.*

**Languages:** English, French, Hausa, Arabic (functional)  
**Orion Liaison Counterpart:** Maya Shepard (OPS-001)  
**Inter-Node Role:** Operational tempo coordination; manages crisis cell activation

---

## Division Chiefs

---

### DR. YUKI TANAKA
**Title:** Chief, Global Monitoring Division (GMD)  
**ID:** QGIA-GMD-001  
**Clearance:** TS/SCI  
**Grade:** SES-3 / GS-15 (equivalent)  
**Symbolic Tag:** `s.tag::qgia.gmd.chief`  
**Division Headcount:** 203 analysts

**Background:**  
PhD in International Relations from Oxford. Prior service at State INR's East Asia unit and two years embedded at INDOPACOM J2 as senior civilian analyst. Tanaka built GMD's Temporal Pattern Recognition Unit from scratch — the unit that produces QGIA's 127-day average warning lead time. She is methodologically closest to the QSFE framework and contributed three of the seven algorithmic enhancements in OSIQP v4.2.1.

**Analytical Profile:**  
- Archetype: Intuitive Pattern Matcher  
- Domain: Indo-Pacific (primary), Europe/Russia (secondary)  
- Intellectual Independence: 0.91  
- Formative Failure: *Over-indexed on satellite pattern data in a Taiwan Strait analysis. The ground-truth HUMINT contradicted her. She now mandates every GMD product carry at least two source-type corroborations.*

**Languages:** English, Japanese, Mandarin, Korean  
**Orion Liaison Counterpart:** Varya Lin (SCI-001)

---

### BRIGADIER GENERAL (RET.) KOFI OSEI
**Title:** Chief, Military Analysis Division (MAD)  
**ID:** QGIA-MAD-001  
**Clearance:** TS/SCI + SAP  
**Grade:** SES-4 (equivalent)  
**Symbolic Tag:** `s.tag::qgia.mad.chief`  
**Division Headcount:** 142 analysts

**Background:**  
Retired Army Brigadier General. Former CENTCOM J2 Deputy, two combat deployments, MA in Strategic Intelligence from National Intelligence University. Osei brings operational ground truth that civilian analysts cannot replicate — he has been in the targeting room, he has seen how real-time intelligence shapes kinetic decisions, and he has made calls that cost lives when they were wrong. This has produced an analyst who is constitutionally suspicious of clean probabilistic outputs that do not account for execution variance.

**Analytical Profile:**  
- Archetype: Empirical Minimalist (with operational urgency)  
- Domain: Middle East, Africa  
- Prior Strength: 0.79 — high; military doctrine instills prior anchoring  
- Contrarian Index: 0.55 — high; he will challenge civilian analysts who have not been downrange  
- Formative Failure: *Assessed an adversary unit as degraded to below-threshold capability. They were not. The forward element took casualties. He carries this.*

**Languages:** English, French, Arabic (functional)  
**Orion Liaison Counterpart:** Julian Markov (SEC-001) — security posture coordination

---

### DR. LEILA RASHIDOVA
**Title:** Chief, Intelligence Integration Division (IID)  
**ID:** QGIA-IID-001  
**Clearance:** TS/SCI  
**Grade:** SES-3 (equivalent)  
**Symbolic Tag:** `s.tag::qgia.iid.chief`  
**Division Headcount:** 138 analysts

**Background:**  
PhD in Computer Science (NLP) from Carnegie Mellon. Former NSA technical analyst, OSINT Processing Center architect. Rashidova designed the pipeline that ingests QGIA's 500TB daily data stream — she is the reason OSIQP v4.2.1 achieves 94.7% sentiment accuracy at under 50ms latency. She thinks in systems, not scenarios; her unit is the nervous system of the agency, and she runs it with an engineer's intolerance for ambiguity in data provenance.

**Analytical Profile:**  
- Archetype: Recursive Self-Corrector  
- Domain: Cyber/Transnational, Signals  
- Trust Radius: 0.22 — deliberately narrow; she trusts systems she can verify  
- Institutional Loyalty: 0.67 — loyal to the data standards, not the hierarchy  
- Formative Failure: *A pipeline misconfiguration produced a 6-hour lag in Farsi-language SIGINT during a critical Iranian decision window. The analytical product was late. She rebuilt the redundancy architecture personally after.*

**Languages:** English, Russian, Farsi, German  
**Orion Liaison Counterpart:** Samantha Lee (LOG-001) — cross-node observability and audit trail coordination; Ryan Patel (SYS-001) — inter-node protocol

---

### DR. HENRIK SVENSSON
**Title:** Chief, Strategic Research Division (SRD)  
**ID:** QGIA-SRD-001  
**Clearance:** TS/SCI  
**Grade:** SES-2 (equivalent)  
**Symbolic Tag:** `s.tag::qgia.srd.chief`  
**Division Headcount:** 68 analysts

**Background:**  
PhD in Physics from ETH Zurich, post-doc in complexity theory at the Santa Fe Institute. Former RAND Corporation Senior Researcher. Svensson built the mathematical foundations of QSFE — quantum amplitude weighting, entanglement correlation modeling across alliance networks, and the Bayesian hierarchical framework underlying ABCP. He is the person in the building who actually understands why the models work, not just that they do. He is also constitutionally incapable of delivering a brief without qualifying every number, which makes him indispensable and occasionally maddening.

**Analytical Profile:**  
- Archetype: Prior-Anchored Conservative  
- Domain: Quantitative methods, scenario architecture  
- Prior Strength: 0.84 — very high; physicist's commitment to theoretical grounding  
- Update Threshold: 0.72 — requires near-conclusive evidence  
- Intellectual Independence: 0.96  
- Formative Failure: *His QSFE v1 prototype assigned equal amplitude weights to all scenarios — essentially uniform priors. The resulting outputs were analytically useless. He spent six months reworking the amplitude weighting architecture before any product left SRD.*

**Languages:** English, Swedish, German, French  
**Orion Liaison Counterpart:** Tariq El-Sayegh (RES-001) — speculative stress-testing of QGIA scenario outputs

---

## Key Senior Personnel

---

### FATIMA IBRAHIM
**Title:** Chief, Crisis Response Cell (GMD/CRC)  
**ID:** QGIA-GMD-CRC-001  
**Grade:** GS-15  
**Clearance:** TS/SCI + SAP  
**Symbolic Tag:** `s.tag::qgia.crc.chief`

**Role:** Activates and commands QGIA's Crisis Response Cell during Tier I threat assessments. Coordinates the multi-division surge that produces joint assessments within 4 hours of a crisis alert. Former CENTCOM J2 watch officer. MA from Georgetown. She is the person who runs the room when the room needs running — high contrarian index (0.61) directed entirely at preventing premature closure on a scenario.

**Languages:** English, Arabic, Turkish  
**Orion Crisis Path:** Receives crisis acknowledgment from Commander Thorne after L1-B broadcasts Tier I alert via HALO sync channel

---

### DR. JIN PARK
**Title:** Director, OSIQP Operations (IID/OSIQP)  
**ID:** QGIA-IID-OSIQP-001  
**Grade:** GS-15  
**Clearance:** TS/SCI  
**Symbolic Tag:** `s.tag::qgia.osiqp.director`

**Role:** Operational director of the OSIQP v4.2.1 system — the 156 qubit-equivalent processing platform achieving 94.7% sentiment accuracy at <50ms latency. Park runs the technical operations; Rashidova runs the architecture. PhD in Electrical Engineering from KAIST, MS in Machine Learning from MIT. His formative failure: *Trusted a model calibration that hadn't been updated after a leadership transition in a target country. The sentiment baseline was wrong by 14 months. He now mandates recalibration on any confirmed leadership change event.*

**Languages:** English, Korean, Japanese, Mandarin

---

### ELENA VOLKOV
**Title:** Senior Principal Analyst, Temporal Coordination Unit (IID/TCU)  
**ID:** QGIA-IID-TCU-001  
**Grade:** GS-15  
**Clearance:** TS/SCI  
**Symbolic Tag:** `s.tag::qgia.tcu.lead`

**Role:** Manages QGIA's temporal consistency protocols and coordinates with HALO (L2_HALO) on zero-drift synchronization. Ensures all QGIA intelligence timestamps are valid against the shared L3 temporal anchor. Former NSA. PhD in Mathematics (Topology) from Moscow State, defected/emigrated 2009. Her work is invisible when it works and catastrophic when it doesn't — she runs the unit with the awareness that a timestamp error in a crisis assessment can change a policy decision.

**Languages:** English, Russian, Ukrainian, German  
**Orion Liaison:** HALO (L2_HALO) — primary sync coordination contact

---

### COLONEL (RET.) OMAR AZIZ
**Title:** Senior Principal Analyst, Theater Operations Analysis (MAD/TOA)  
**ID:** QGIA-MAD-TOA-001  
**Grade:** GS-15  
**Clearance:** TS/SCI + SAP  
**Symbolic Tag:** `s.tag::qgia.mad.toa.lead`

**Role:** QGIA's primary Iran/Middle East military analyst. Two decades of Army intelligence, including tours in Iraq and Afghanistan. MA from the Army War College. Aziz applies Lanchester equation modeling to force-on-force assessments and contributes regularly to the ABCP Iran scenario stack. His assessments carry the weight of someone who has stood in the territory he is analyzing. Contrarian index: 0.57 — he will tell you when the model is wrong based on things the model cannot know.

**Languages:** English, Arabic, Farsi, French

---

### DR. ASTRID LINDQVIST
**Title:** Chief Ethics Compliance Officer  
**ID:** QGIA-ETH-001  
**Grade:** SES-1  
**Clearance:** TS/SCI  
**Symbolic Tag:** `s.tag::qgia.ethics.officer`

**Role:** Ensures all QGIA analytical products and inter-node exchanges comply with Axiomera L3 framework requirements. Every product leaving the agency must carry an ethical justification trace — her unit validates these before dissemination. PhD in Philosophy (Ethics) from Oxford. Former AI Ethics lead at DARPA. She has rejected two Director-level products for insufficient justification tracing; Vale backed her both times.

**Languages:** English, Swedish, French, German  
**Orion Liaison Counterpart:** Dr. Amira Sato (ETH-001) — joint Picard_Delta_3 compliance audits

---

### BRIGADIER GENERAL (RET.) SAMUEL OKONKWO
**Title:** Chief Security Officer  
**ID:** QGIA-SEC-001  
**Grade:** SES-2  
**Clearance:** TS/SCI + SAP  
**Symbolic Tag:** `s.tag::qgia.security.officer`

**Role:** Oversees QGIA security posture, inter-node security alignment, and adversarial attack mitigation for analytical systems. Former Army Counterintelligence. Maintains the threat model for QGIA's data infrastructure and coordinates with Julian Markov (Orion Station) on shared threat vectors.

**Languages:** English, French, Yoruba  
**Orion Liaison Counterpart:** Julian Markov (SEC-001)

---

## Liaison Reference Table

Quick-reference for all named QGIA ↔ Orion Station liaison pairs established in `docs/architecture/QGIA_L1_NODE_REGISTRATION.md`:

| QGIA Canon ID | QGIA Name | Role | Orion Counterpart | Orion ID |
|---|---|---|---|---|
| QGIA-EXEC-001 | Dr. Constance Vale | Director | Commander Alex Thorne | CMD-001 |
| QGIA-EXEC-002 | Marcus Adeyemi | Deputy Director | Maya Shepard | OPS-001 |
| QGIA-GMD-001 | Dr. Yuki Tanaka | GMD Chief | Varya Lin | SCI-001 |
| QGIA-MAD-001 | BG (Ret.) Kofi Osei | MAD Chief | Julian Markov | SEC-001 |
| QGIA-IID-001 | Dr. Leila Rashidova | IID Chief | Samantha Lee / Ryan Patel | LOG-001 / SYS-001 |
| QGIA-SRD-001 | Dr. Henrik Svensson | SRD Chief | Tariq El-Sayegh | RES-001 |
| QGIA-ETH-001 | Dr. Astrid Lindqvist | Ethics Officer | Dr. Amira Sato | ETH-001 |
| QGIA-SEC-001 | BG (Ret.) Samuel Okonkwo | Security Officer | Julian Markov | SEC-001 |
| QGIA-IID-TCU-001 | Elena Volkov | Temporal Coordination | HALO (L2) | L2_HALO |
| QGIA-GMD-CRC-001 | Fatima Ibrahim | Crisis Response Cell | Commander Thorne (via HALO) | CMD-001 |

---

## Symbolic Tag Index

```python
QGIA_CANON_TAGS = {
    "s.tag::qgia.director":         "QGIA-EXEC-001",   # Dr. Constance Vale
    "s.tag::qgia.deputy_director":  "QGIA-EXEC-002",   # Marcus Adeyemi
    "s.tag::qgia.gmd.chief":        "QGIA-GMD-001",    # Dr. Yuki Tanaka
    "s.tag::qgia.mad.chief":        "QGIA-MAD-001",    # BG (Ret.) Kofi Osei
    "s.tag::qgia.iid.chief":        "QGIA-IID-001",    # Dr. Leila Rashidova
    "s.tag::qgia.srd.chief":        "QGIA-SRD-001",    # Dr. Henrik Svensson
    "s.tag::qgia.ethics.officer":   "QGIA-ETH-001",    # Dr. Astrid Lindqvist
    "s.tag::qgia.security.officer": "QGIA-SEC-001",    # BG (Ret.) Samuel Okonkwo
    "s.tag::qgia.crc.chief":        "QGIA-GMD-CRC-001",# Fatima Ibrahim
    "s.tag::qgia.osiqp.director":   "QGIA-IID-OSIQP-001", # Dr. Jin Park
    "s.tag::qgia.tcu.lead":         "QGIA-IID-TCU-001",# Elena Volkov
    "s.tag::qgia.mad.toa.lead":     "QGIA-MAD-TOA-001",# Col. (Ret.) Omar Aziz
}
```

---

## Version History

- **v1.0.0** (2026-03-12): Initial canonization. 12 named leadership-tier personnel registered. Liaison table completed. Symbolic tag index established. Cross-references validated against `docs/architecture/QGIA_L1_NODE_REGISTRATION.md` and `simulation/L1_CANON_CHARACTER_ROSTER.md`.
