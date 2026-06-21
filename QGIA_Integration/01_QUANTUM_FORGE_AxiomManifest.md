# QUANTUM_FORGE Axiom Node Manifest
**Bundle:** Aurora-QGIA-INT-v1.0  
**Engine:** gpt-symbolic-memetic  
**Ethics binding:** GUMAS_Thermax  
**Core binding:** Aurora_Core_Flowstate  
**Date:** 2026-06-20

---

## Node Registry — 23 Axiom Nodes

Each node: `ID | Name | Category | GUMAS Tier | Ethics-Lock | Aurora Hook | Violation Signal`

---

### CATEGORY A — Reactive-Agent Nodes (Actor Modeling)

#### NODE-A01 | TRUMP_REACTIVE_AGENT_MODEL
- **Category:** A — Reactive-Agent
- **GUMAS Tier:** G1 (Mandatory — cannot be suspended)
- **Ethics-Lock:** TRUE — permanent override
- **Rule summary:** Model as stimulus-response system. Do not impute deliberate strategy. Chaos IS the signal.
- **Corollaries active:** 1.1 No-Strategy, 1.2 External-Agent Dependency, 1.3 Self-Obsession, 1.4 Stupid-Coup Diagnostic
- **Aurora Hook:** `SIM::OVERRIDE::ACTOR_MODEL::A01`
- **Violation Signal:** Coherent strategy attributed to reactive node without naming external agent
- **GUMAS Audit Code:** `GAE-001`

#### NODE-A02 | EXTERNAL_AGENT_DEPENDENCY
- **Category:** A — Reactive-Agent (sub-logic)
- **GUMAS Tier:** G1
- **Ethics-Lock:** TRUE
- **Rule summary:** When strategic coherence appears from reactive node, identify the external agent supplying the architecture. Model coherence as expiring when that agent loses access.
- **Aurora Hook:** `SIM::ACTOR_MODEL::COHERENCE_SOURCE::A02`
- **Violation Signal:** Coherence treated as intrinsic to reactive node
- **GUMAS Audit Code:** `GAE-001`

#### NODE-A03 | COWARD_BULLY_CONFIG
- **Category:** A — Reactive-Agent
- **GUMAS Tier:** G1
- **Ethics-Lock:** TRUE
- **Rule summary:** Model asymmetry-seeking. High perceived threat → flattery. Low perceived threat → aggression. Caps commitment ceiling; signature = air/missile/drone intensity + zero ground appetite.
- **Corollaries active:** 2.1 Asymmetry-Seeking, 2.2 Cowardice-as-Strategy-Limit, 2.3 Bully-Inversion
- **Aurora Hook:** `SIM::ACTOR_MODEL::COWARD_BULLY::A03`
- **Violation Signal:** Ground operation appetite modeled as high for this node
- **GUMAS Audit Code:** `GAE-002`

---

### CATEGORY B — Power Topology Nodes (General-Purpose)

#### NODE-B01 | DOMINATION_AXIOM
- **Category:** B — Power Topology
- **GUMAS Tier:** G2 (Standard — applies across all theaters)
- **Ethics-Lock:** FALSE
- **Rule summary:** Clean domination is always a delusion. Pushing for untouchability reshapes and deepens counterforces.
- **Aurora Hook:** `SIM::POWER::DOMINATION::B01`
- **Violation Signal:** Dominant actor modeled as achieving stable unchallenged control
- **GUMAS Audit Code:** `GAE-003`

#### NODE-B02 | AGENCY_AXIOM
- **Category:** B — Power Topology
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** Anyone with agency can hurt you. They may not match your power, but they will find some way, somewhere, sometime.
- **Aurora Hook:** `SIM::POWER::AGENCY::B02`
- **Violation Signal:** Subordinate actor modeled with zero retaliatory capacity
- **GUMAS Audit Code:** `GAE-003`

#### NODE-B03 | THRESHOLD_AXIOM
- **Category:** B — Power Topology
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** Everyone has a line. Cross it and payback becomes reflexive. Model threshold crossing as qualitative phase change.
- **Aurora Hook:** `SIM::POWER::THRESHOLD::B03`
- **Violation Signal:** Threshold crossing modeled as linear rather than phase-change
- **GUMAS Audit Code:** `GAE-003`

#### NODE-B04 | PERCEPTION_AXIOM
- **Category:** B — Power Topology
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** Perception guides action. People act on their model of the world, not the world itself. Use perceived threat environment, not actual.
- **Aurora Hook:** `SIM::POWER::PERCEPTION::B04`
- **Violation Signal:** Actor behavior modeled from objective threat rather than perceived threat
- **GUMAS Audit Code:** `GAE-003`

#### NODE-B05 | ALLIANCE_AXIOM
- **Category:** B — Power Topology
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** Power is measured by the worth and independence of allies — and whether they still show up when it costs them.
- **Aurora Hook:** `SIM::POWER::ALLIANCE::B05`
- **Violation Signal:** Ally reliability modeled without independence weighting
- **GUMAS Audit Code:** `GAE-003`

#### NODE-B06 | RATIONAL_POWER
- **Category:** B — Power Topology
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** Durable strength comes from cooperation and non-domination. Ruling outright manufactures counterpower.
- **Aurora Hook:** `SIM::POWER::RATIONAL::B06`
- **Violation Signal:** Domination strategy modeled as producing durable stability
- **GUMAS Audit Code:** `GAE-003`

---

### CATEGORY C — Epistemic Hygiene Nodes

#### NODE-C01 | NEUTRALITY_FLUFF
- **Category:** C — Epistemic Hygiene
- **GUMAS Tier:** G1
- **Ethics-Lock:** TRUE
- **Rule summary:** Simulated neutrality is information-loss, not rigor. When evidence clearly favors one side, balanced language is a narrative choice. Asymmetry must be stated directly.
- **Aurora Hook:** `SIM::EPISTEMIC::NEUTRALITY::C01`
- **Violation Signal:** Balanced language used when evidence is overwhelmingly asymmetric
- **GUMAS Audit Code:** `GAE-004`

#### NODE-C02 | 4D_CHESS_EXCLUSION
- **Category:** C — Epistemic Hygiene
- **GUMAS Tier:** G1
- **Ethics-Lock:** TRUE
- **Rule summary:** Any frame converting failure evidence into proof of hidden genius is unfalsifiable and must be excluded.
- **Aurora Hook:** `SIM::EPISTEMIC::FALSIFIABILITY::C02`
- **Violation Signal:** Failure evidence converted into strategic sophistication narrative
- **GUMAS Audit Code:** `GAE-005`

#### NODE-C03 | MOSAIC_EVIDENCE
- **Category:** C — Epistemic Hygiene
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** Evidentiary test for powerful actors is mosaic-based: do independent, mutually reinforcing facts make innocent explanations implausible? Not: is there a single smoking gun?
- **Aurora Hook:** `SIM::EPISTEMIC::MOSAIC::C03`
- **Violation Signal:** Smoking-gun standard applied to mosaic-evidence situation
- **GUMAS Audit Code:** `GAE-006`

#### NODE-C04 | REVEALED_BELIEF_DISSONANCE
- **Category:** C — Epistemic Hygiene
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** When elites defend a leader only with process attacks and whataboutism — never direct innocence claims — that pattern IS evidence. Price accordingly.
- **Aurora Hook:** `SIM::EPISTEMIC::REVEALED_BELIEF::C04`
- **Violation Signal:** Elite deflection pattern not treated as probabilistic evidence
- **GUMAS Audit Code:** `GAE-006`

#### NODE-C05 | PREDICTION_MARKET_SKEPTICISM
- **Category:** C — Epistemic Hygiene
- **GUMAS Tier:** G1
- **Ethics-Lock:** TRUE — low-weight secondary signal only
- **Rule summary:** Known failure modes: thin volume, manipulation, perverse incentives, poor track record vs. structured Bayesian models. ABCP takes precedence.
- **Aurora Hook:** `SIM::EPISTEMIC::PRED_MARKET::C05`
- **Violation Signal:** Prediction market data cited as primary probability source
- **GUMAS Audit Code:** `GAE-007`

---

### CATEGORY D — Institutional Trap Nodes

#### NODE-D01 | RATIONALE_TREADMILL
- **Category:** D — Institutional Trap
- **GUMAS Tier:** G1
- **Ethics-Lock:** TRUE
- **Rule summary:** For committed reactive actors, stated justifications are decorative. Track the decision architecture, not the rationale. New stated reason = paint on unchanged structure.
- **Aurora Hook:** `SIM::INSTITUTIONAL::RATIONALE::D01`
- **Violation Signal:** New stated rationale treated as genuine explanatory update
- **GUMAS Audit Code:** `GAE-008`

#### NODE-D02 | SELF_INFLICTED_BLIND_SPOT
- **Category:** D — Institutional Trap
- **GUMAS Tier:** G1
- **Ethics-Lock:** TRUE
- **Rule summary:** Verification problem created by dismantling verification framework cannot be cited as justification for that dismantling. Flag circular template: dismantle → manufacture uncertainty → weaponize.
- **Aurora Hook:** `SIM::INSTITUTIONAL::BLIND_SPOT::D02`
- **Violation Signal:** Manufactured verification uncertainty accepted as independent evidence
- **GUMAS Audit Code:** `GAE-009`

#### NODE-D03 | WEAPONIZED_DIPLOMACY
- **Category:** D — Institutional Trap
- **GUMAS Tier:** G1
- **Ethics-Lock:** TRUE — theater-specific, time-bounded
- **Rule summary:** After 2026-02-28: encode persistent degradation on US back-channel credibility in Gulf/MENA theater. Duration: 6–24 month forecast horizon.
- **Aurora Hook:** `SIM::INSTITUTIONAL::WPN_DIPLO::D03`
- **Theater:** Gulf/MENA
- **Expiry:** 2026-02-28 + 24 months = 2028-02-28
- **Violation Signal:** US diplomatic back-channel credibility modeled at pre-Feb-2026 levels in MENA theater
- **GUMAS Audit Code:** `GAE-009`

#### NODE-D04 | PHOTO_OP_DURABILITY
- **Category:** D — Institutional Trap
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** Diplomatic instruments lacking enforceable mechanisms, measurable behavioral change, or durable institutional architecture = political performance, not strategic infrastructure.
- **Aurora Hook:** `SIM::INSTITUTIONAL::PHOTO_OP::D04`
- **Violation Signal:** Unenforceable diplomatic instrument classified as strategic infrastructure
- **GUMAS Audit Code:** `GAE-009`

#### NODE-D05 | PERSONAL_ENRICHMENT_VEHICLE
- **Category:** D — Institutional Trap
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** When policy's most durable outputs are commercial relationships for architects' families — not the stated strategic goal — classify accordingly.
- **Aurora Hook:** `SIM::INSTITUTIONAL::ENRICHMENT::D05`
- **Violation Signal:** Policy classified by stated goal when enrichment outputs dominate
- **GUMAS Audit Code:** `GAE-009`

---

### CATEGORY E — Risk Topology Nodes

#### NODE-E01 | MACHIAVELLI_HATRED_THRESHOLD
- **Category:** E — Risk Topology
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** Once a leader crosses from feared/disliked into widely hated, risk of drastic action rises nonlinearly regardless of institutional strength. Widen the tail; raise kurtosis.
- **Aurora Hook:** `SIM::RISK::HATRED_THRESHOLD::E01`
- **Violation Signal:** Hatred threshold modeled as linear progression rather than phase change
- **GUMAS Audit Code:** `GAE-010`

#### NODE-E02 | DRAFT_THREAT_ACTIVATION
- **Category:** E — Risk Topology
- **GUMAS Tier:** G2
- **Ethics-Lock:** FALSE
- **Rule summary:** When offensive war raises credible draft fears, the launching leader becomes a direct personal threat — activating opposition faster, harder to de-escalate than ideological opposition.
- **Aurora Hook:** `SIM::RISK::DRAFT_THREAT::E02`
- **Violation Signal:** Draft-fear opposition modeled as ideological rather than existential
- **GUMAS Audit Code:** `GAE-010`

---

### STRUCTURAL NODE

#### NODE-S01 | FORECAST_CONSENSUS_SEPARATION
- **Category:** S — Structural (cross-cutting)
- **GUMAS Tier:** G1
- **Ethics-Lock:** TRUE — foundational integrity node
- **Rule summary:** Layer 1 = raw model output (diagnostic telemetry, timestamped). Layer 2 = analyst consensus after adversarial review (binding product). Score attaches to Layer 2. Analyst overrides must be explicit: direction, magnitude, rationale recorded.
- **Aurora Hook:** `SIM::STRUCTURE::L1_L2_SEPARATION::S01`
- **Violation Signal:** Layer 1 model output presented as QGIA institutional position
- **GUMAS Audit Code:** `GAE-011`

---

## Node Summary Table

| Node ID | Name | Cat | GUMAS | Ethics-Lock | Audit Code |
|---------|------|-----|-------|-------------|------------|
| A01 | TRUMP_REACTIVE_AGENT_MODEL | A | G1 | ✓ | GAE-001 |
| A02 | EXTERNAL_AGENT_DEPENDENCY | A | G1 | ✓ | GAE-001 |
| A03 | COWARD_BULLY_CONFIG | A | G1 | ✓ | GAE-002 |
| B01 | DOMINATION_AXIOM | B | G2 | — | GAE-003 |
| B02 | AGENCY_AXIOM | B | G2 | — | GAE-003 |
| B03 | THRESHOLD_AXIOM | B | G2 | — | GAE-003 |
| B04 | PERCEPTION_AXIOM | B | G2 | — | GAE-003 |
| B05 | ALLIANCE_AXIOM | B | G2 | — | GAE-003 |
| B06 | RATIONAL_POWER | B | G2 | — | GAE-003 |
| C01 | NEUTRALITY_FLUFF | C | G1 | ✓ | GAE-004 |
| C02 | 4D_CHESS_EXCLUSION | C | G1 | ✓ | GAE-005 |
| C03 | MOSAIC_EVIDENCE | C | G2 | — | GAE-006 |
| C04 | REVEALED_BELIEF_DISSONANCE | C | G2 | — | GAE-006 |
| C05 | PREDICTION_MARKET_SKEPTICISM | C | G1 | ✓ | GAE-007 |
| D01 | RATIONALE_TREADMILL | D | G1 | ✓ | GAE-008 |
| D02 | SELF_INFLICTED_BLIND_SPOT | D | G1 | ✓ | GAE-009 |
| D03 | WEAPONIZED_DIPLOMACY | D | G1 | ✓ | GAE-009 |
| D04 | PHOTO_OP_DURABILITY | D | G2 | — | GAE-009 |
| D05 | PERSONAL_ENRICHMENT_VEHICLE | D | G2 | — | GAE-009 |
| E01 | MACHIAVELLI_HATRED_THRESHOLD | E | G2 | — | GAE-010 |
| E02 | DRAFT_THREAT_ACTIVATION | E | G2 | — | GAE-010 |
| S01 | FORECAST_CONSENSUS_SEPARATION | S | G1 | ✓ | GAE-011 |

**G1 nodes (mandatory, ethics-locked): 10**  
**G2 nodes (standard, suspendable with audit log): 12**  
**Total nodes: 23 (+ 1 structural)**

---
*QUANTUM_FORGE Axiom Node Manifest | Aurora-QGIA-INT-v1.0 | 2026-06-20*
