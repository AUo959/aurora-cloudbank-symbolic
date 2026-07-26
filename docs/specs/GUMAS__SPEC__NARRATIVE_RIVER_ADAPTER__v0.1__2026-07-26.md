---
artifact_id: GUMAS.NARRATIVE_RIVER_ADAPTER.SPEC
title: Narrative River Adapter
version: 0.1.0
status: draft_specification
domain: GUMAS_L2_NARRATIVE
date: 2026-07-26
anchor_seed: EOS_SEED_ORION
ethics_protocol: Picard_Delta_3
canon_authority: Git
authoring_authority: Human-led, AI-assisted
persistent_behavior_status: not_implemented
related_artifacts:
  - The Eleven Governing Narrative Axioms
  - Aurora RiverCycle + RiverThread808 + GUMAS Social Pressure Regulator v0.5.0-alpha
---

# Narrative River Adapter

## Complete Specification v0.1.0

**Target environment:** Aurora CloudBank Symbolic / GUMAS L2 narrative workflow  
**Primary function:** Translate persistent RiverCycle state into scene-level causal constraints for prose generation and revision.  
**Design signature:** Built for consistency, clarity, and care.

## 0. Executive Summary

The Narrative River Adapter is a proposed bridge between RiverCycle, GUMAS simulation state, narrative prose generation, and the Eleven Governing Narrative Axioms.

The adapter does not write the story by itself. It does not replace the simulation engine, the narrative author, CanonRec, or Git. It does not introduce a hidden narrator, enforce peace, decide canon, or turn RiverCycle metaphors into in-world language.

Its purpose is narrower:

> Preserve causal continuity between scenes by making active pressures, uncertainties, relationship residue, institutional constraints, and required downstream effects explicit before prose is generated.

The adapter produces a **Narrative River Frame** for a scene or chapter. The frame tells the prose layer:

- what pressures are entering the scene;
- where they came from;
- who interprets them differently;
- which relationships or institutions carry unresolved residue;
- what channels are available for response;
- what evidence is known, disputed, or provisional;
- what consequences must remain active;
- which shortcuts would violate continuity;
- what state must change before the scene can end.

```text
Narrative Axioms = how the prose must behave
Narrative River Frame = what causal state the prose must preserve
CanonRec = what has been promoted as authoritative truth
Git = final canon authority
```

### Current implementation truth

This specification defines intended behavior. It does not establish that the adapter is currently implemented, automatically invoked, or persistently connected to prose generation.

Until code, tests, and storage are added:

- RiverCycle may influence prose through deliberate reasoning;
- the Eleven Axioms may guide revision through project context;
- scene continuity still depends on human/assistant discipline;
- no software guarantee exists that pressure, sediment, or consequence will persist between scenes.

# 1. Goals

## 1.1 Primary goals

The adapter must:

1. Preserve scene-to-scene causal continuity.
2. Prevent narrative details from becoming inert exposition.
3. Track active uncertainty without collapsing it into fact.
4. Carry unresolved interpersonal and institutional consequences forward.
5. Keep simulation-derived constraints active in prose.
6. Prevent symbolic RiverCycle vocabulary from bleeding into ordinary L2 narration.
7. Make scene endings correspond to real state transitions.
8. Support deterministic, auditable, versioned narrative planning.
9. Remain advisory before any mutating or blocking behavior is introduced.
10. Preserve Git and CanonRec as the authorities for canon.

## 1.2 Non-goals

The adapter must not:

- generate canon automatically;
- commit files;
- override human editorial judgment;
- force a predetermined emotional response;
- force peace, reconciliation, escalation, or tragedy;
- convert every scene into a procedural briefing;
- require RiverCycle terms to appear in prose;
- dictate a fixed plot;
- replace character psychology with numeric pressure scores;
- treat a probability or score as objective truth;
- resolve ambiguity because the frame prefers a clean state;
- bypass CanonRec admission and reconciliation workflows;
- claim persistent memory unless frames are stored and reloaded;
- allow an L3 metaphor to become a literal L2 event without an explicit translation step.

# 2. System Position

```text
CanonRec / Git
     │
     │ authoritative canon snapshot
     ▼
GUMAS World State ────────────┐
                              │
RiverCycle State ─────────────┤
                              ▼
                    Narrative River Adapter
                              │
                              ├── Narrative River Frame
                              ├── Scene prompt contract
                              ├── Validation report
                              └── Post-scene delta
                                      │
                                      ▼
                              Prose generation
                                      │
                                      ▼
                              Human review
                                      │
                                      ▼
                              Canon reconciliation
```

## 2.1 Boundary rules

- **Canon boundary:** A frame may reference canon but cannot promote canon.
- **Simulation boundary:** A frame may represent simulation state but cannot mutate simulation state in phase 1.
- **Narrative boundary:** A frame may constrain prose generation but cannot claim that generated prose is canon.
- **Symbolic boundary:** RiverCycle terms are internal abstractions and must be translated into concrete L2 conditions.
- **Memory boundary:** A frame persists only when stored in a durable location and reloaded later.

# 3. Core Concepts

## 3.1 Flow

A flow is something moving between actors, institutions, locations, or scenes: information, authority, trust, suspicion, material supply, political pressure, grief, doctrine, evidence, fear, legitimacy, or responsibility.

A flow must have:

- a source;
- a target;
- a carrier or channel;
- a strength or significance;
- a provenance;
- a current state.

## 3.2 Pressure

Pressure narrows available choices. Examples include archive destruction, limited fuel, deteriorating shields, political scrutiny, witness instability, unclear jurisdiction, relationship strain, or enemy movement.

Pressure does not determine response directly. It is interpreted through role, responsibility, culture, memory, exhaustion, evidence confidence, and perceived agency.

## 3.3 Sediment

Sediment is unresolved residue from prior events:

- reduced trust after withheld information;
- an unresolved withdrawal dispute;
- rivalry between institutions;
- a mistranslation not yet corrected;
- conflicting testimony;
- an unexplained casualty.

Sediment may accumulate, resolve, harden into grievance, become institutional learning, or lose relevance.

## 3.4 Reservoir

A reservoir absorbs or delays pressure:

- a court order;
- command discipline;
- medical isolation;
- a classified review chamber;
- a logistics reserve;
- a diplomatic channel;
- a ritual or cultural practice;
- a trusted relationship.

A reservoir does not erase pressure. It changes when and how pressure is released.

## 3.5 Turbulence

Turbulence distorts a channel:

- translation error;
- interference;
- conflicting authority;
- propaganda;
- partial records;
- institutional rivalry;
- overloaded communications.

## 3.6 Nutrient

A nutrient is useful capacity produced by an event:

- a technical method;
- trust earned;
- revised doctrine;
- a legal precedent;
- a new contact;
- a successful contingency.

## 3.7 Salmon return

A salmon return is a downstream result that changes the originating system:

- a boarding action changes doctrine;
- a colonial failure changes policy at the capital;
- a translation error changes future translation standards;
- a field refit changes later ship design.

# 4. Narrative River Frame

## 4.1 Required top-level fields

```yaml
narrative_river_frame:
  frame_id: string
  schema_version: "0.1.0"
  scene_id: string
  chapter_id: string | null
  generated_at_utc: string

  canon_snapshot:
    repository: string | null
    commit_sha: string | null
    source_files: []
    authority_status: canon | staging | draft | mixed

  narrative_status:
    current_state: outline | draft | revised | canon_candidate | canon
    previous_scene_id: string | null
    next_scene_hint: string | null

  viewpoint:
    mode: close_third | limited_third | first_person | primary_source | mixed
    focal_character_ids: []
    prohibited_omniscience: true

  scene_objective:
    operational_goal: string
    dramatic_goal: string
    required_state_change: string

  incoming_flows: []
  active_pressures: {}
  sediment: []
  reservoirs: []
  channel_conditions: []
  evidence_state: []
  actor_interpretations: []
  relationship_state: []
  institutional_constraints: []
  equipment_state: []
  scarcity_state: []
  required_downstream_effects: []
  prohibited_shortcuts: []
  unresolved_questions: []
  exit_conditions: []
  axiom_checks: {}
```

# 5. Persistence Model

The adapter recognizes four persistence classes.

## Class 0 — Ephemeral

Exists only in the current generation context. Use for exploratory possibilities, temporary phrasing, rejected scene approaches, and non-persistent stylistic experiments.

## Class 1 — Draft-persistent

Stored with a narrative draft and carried into future revisions. Use for active pressures, relationship sediment, unresolved questions, evidence classifications, and planned downstream effects.

## Class 2 — Project-persistent

Stored in the project space or repository as an approved working artifact. Use for narrative axioms, voice profiles, continuing arc state, validated scene deltas, and adapter configuration.

## Class 3 — Canon-linked

References committed CanonRec truth and includes a canon snapshot or source path. A Class 3 reference is not itself canon.

## Persistence requirements

A frame may claim persistence only if:

1. It has a stable ID.
2. It is stored durably.
3. It has a schema version.
4. Its canon snapshot is identified when relevant.
5. Its post-scene delta is saved.
6. Future frames explicitly import unresolved state.

## No false memory rule

The adapter must not claim that something is remembered, permanent, or automatically active in future prose unless durable storage and reload behavior prove it.

# 6. Scene Lifecycle

## 6.1 Pre-scene phase

Gather:

- canon snapshot;
- prior scene delta;
- character and institution state;
- equipment and scarcity state;
- unresolved questions;
- active relationships;
- mission objective;
- RiverCycle pressures.

Generate the Narrative River Frame.

## 6.2 Drafting phase

The prose generator receives:

1. the narrative request;
2. the Narrative River Frame;
3. the Eleven Axioms;
4. viewpoint limits;
5. canon evidence;
6. invention boundaries.

## 6.3 Validation phase

Evaluate for:

- causal continuity;
- knowledge-layer violations;
- hierarchy drift;
- procedural over-explanation;
- symbolic bleed;
- unearned resolution;
- scarcity violations;
- missing downstream effects;
- self-aware prose;
- repeated rhetorical templates.

## 6.4 Post-scene extraction phase

```yaml
scene_river_delta:
  scene_id: string
  completed_at_utc: string
  state_changes: []
  new_sediment: []
  resolved_sediment: []
  pressure_changes: {}
  relationship_changes: []
  evidence_changes: []
  new_questions: []
  closed_questions: []
  equipment_changes: []
  institutional_changes: []
  canon_candidates: []
  next_scene_requirements: []
```

# 7. Prose Integration Contract

## 7.1 Compact prompt contract

```text
NARRATIVE RIVER CONSTRAINTS

Incoming pressures:
- [concrete pressure]
- [concrete pressure]

Active residue:
- [unresolved relationship or institutional consequence]

Evidence boundaries:
- [confirmed fact]
- [testimony]
- [hypothesis]

Required state changes:
- [what must change by scene end]

Prohibited shortcuts:
- [convenient but invalid outcome]

Surface-language rule:
Do not use RiverCycle metaphors unless the in-world speaker would naturally do so.
```

## 7.2 Surface-language firewall

Internal term | Expected prose translation
---|---
pressure | deadline, scrutiny, shield loss, fear, legal exposure
sediment | unresolved distrust, grievance, conflicting testimony
reservoir | court order, command discipline, reserve capacity, ritual
turbulence | translation error, interference, conflicting authority
flow | transfer, report, order, supply route, rumor, evidence chain
nutrient | doctrine learned, trust earned, technical method, legal precedent
salmon return | later policy or doctrine changed by downstream events

# 8. Eleven-Axiom Validation

Each draft receives `PASS`, `WARN`, `FAIL`, or `NOT_APPLICABLE`, with exact passages cited.

## Axiom 1 — Independent world

Fail when an object appears only because the plot needs it, a character knows information without a channel, or a consequence stops at scene end despite wider implications.

## Axiom 2 — Remain inside the scene

Fail when narration comments on tone, banter, professionalism, adherence to instructions, or what the reader should understand.

## Axiom 3 — Institutional reality through behavior

Warn when characters recite procedure they already know, authority is explained rather than exercised, or evidence handling does not affect action.

## Axiom 4 — Voice answers the situation

Fail when dialogue becomes an aphorism, a reply mainly states theme, or a character speaks for the audience.

## Axiom 5 — Hierarchy shapes speech

Fail when junior officers negotiate casually with supreme authority, formal contact has no behavioral effect, or rank disappears from language and timing.

## Axiom 6 — Consequential detail

Warn when inventories do not alter choices, exposition supplies facts without changing action, or technical detail has no downstream effect.

## Axiom 7 — Knowledge layers

Fail when testimony becomes narration, hypotheses become confirmed without evidence, or translation output becomes omniscient truth.

## Axiom 8 — Constrained choices

Warn when tension depends mainly on ominous language instead of competing losses.

## Axiom 9 — Competence includes error

Fail when one character predicts the entire problem, preparation eliminates cost, or disagreement resolves automatically after success.

## Axiom 10 — Rhythm

Warn when three-word answers dominate, setup/reversal dialogue repeats, “not X, but Y” clusters, or the ending relies on a trailer line.

## Axiom 11 — Simulation produces drama

Fail when scarce assets are spent casually, new capability appears without precedent, an opponent behaves irrationally only to lose, or success arrives without material or institutional cost.

# 9. Additional Validation Rules

## 9.1 Anti-exposition

A procedural detail is permitted only when it grants or denies authority, preserves evidence, creates delay, causes conflict, changes risk, or limits action.

## 9.2 Anti-corny-dialogue

Flag dialogue built from abstract symmetry, generic wisdom, polished reversals, portable quotations, thematic summary, or trailer phrasing.

## 9.3 Anti-self-awareness

Flag narration that announces the absence of banter, rhetoric, confrontation, or stylistic error.

## 9.4 Three-word rhythm

Short responses are valid for command, shock, acknowledgment, interruption, or danger. Flag more than three consecutive dialogue turns of five words or fewer without situational reason.

## 9.5 Evidence provenance

Every consequential claim should resolve to direct observation, instrument output, testimony, inference, canon record, rumor, or unknown source.

## 9.6 Scarcity integrity

Track munitions, fuel, fatigue, Sentinel availability, damage, political capital, time, evidence access, and trust.

# 10. Character Interpretation Profiles

The adapter should not reduce characters to personality labels.

```yaml
character_interpretation_profile:
  character_id: string
  role: string
  responsibility: string
  preferred_control_method: string
  primary_attention: []
  known_blind_spots: []
  authority_limits: []
  speech_registers:
    peer: string
    superior: string
    subordinate: string
    hostile: string
    witness: string
  stress_changes:
    - condition: string
      effect: string
```

## Dark Star Ranger examples

### Tessa Korr

- Responsibility: mission outcome and crew command.
- Attention: timing, initiative, escape geometry, decisive opportunity.
- Blind spot: disappearing opportunity may feel more dangerous than poorly bounded commitment.
- Stress speech: more direct, not more theatrical.
- Superior register: concise and formal.

### Iven Raal

- Responsibility: evidence integrity, legal defensibility, false-pattern resistance.
- Attention: missing information, suspicious certainty, provenance.
- Blind spot: may withhold useful preparation until he considers it verified.
- Stress speech: qualified, concrete, occasionally delayed.
- Superior register: asks only necessary clarifications.

### Maelin Saye

- Responsibility: technical control, logistics, remote field manipulation, isolation.
- Attention: interfaces, reversibility, redundancy, exposure paths.
- Blind spot: may overvalue technical containment where human intent remains decisive.
- Stress speech: specific about capability and limits.
- Superior register: frames concerns as operational conditions.

# 11. Institutional Profiles

```yaml
institution_profile:
  institution_id: string
  mandate: string
  authority_channels: []
  protected_interests: []
  failure_modes: []
  typical_evidence_behavior: string
  typical_delay_behavior: string
  external_conflicts: []
  narrative_signals:
    - action: string
      meaning: string
```

Example:

```yaml
institution_id: FIELD_COURT_JUDICATOR
mandate: Preserve and exercise Union judicial authority in remote operations.
authority_channels:
  - preservation_order
  - warrant
  - custody_ruling
protected_interests:
  - admissibility
  - due process
  - independent record
failure_modes:
  - over-caution
  - jurisdictional friction
narrative_signals:
  - action: duplicate evidence hash
    meaning: no single institution can erase the record
```

# 12. Implementation Data Models

```python
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal, Optional


EvidenceStatus = Literal[
    "confirmed",
    "observed",
    "instrument_output",
    "testimony",
    "hypothesis",
    "rumor",
    "contradicted",
    "unknown",
]


@dataclass(frozen=True)
class ProvenanceRef:
    source_type: str
    source_id: str
    authority_status: str
    commit_sha: Optional[str] = None
    confidence: float = 1.0


@dataclass
class IncomingFlow:
    flow_id: str
    flow_type: str
    source_id: str
    target_id: str
    carrier: str
    strength: float
    provenance: list[ProvenanceRef] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class NarrativeSediment:
    sediment_id: str
    source_event_id: str
    description: str
    affected_actor_ids: list[str] = field(default_factory=list)
    current_effect: str = ""
    resolution_status: str = "active"


@dataclass
class NarrativeReservoir:
    reservoir_id: str
    reservoir_type: str
    capacity: float
    absorbs: list[str] = field(default_factory=list)
    failure_condition: str = ""


@dataclass
class EvidenceClaim:
    claim_id: str
    claim: str
    status: EvidenceStatus
    support: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    provenance: list[ProvenanceRef] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ActorInterpretation:
    actor_id: str
    interpretation: str
    preferred_response: str
    blind_spot: str
    authority_limit: str = ""


@dataclass
class RelationshipState:
    relation_id: str
    actor_ids: list[str]
    trust: float
    operational_reliance: float
    current_strain: float
    required_change: str = ""


@dataclass
class NarrativeRiverFrame:
    frame_id: str
    schema_version: str
    scene_id: str
    chapter_id: Optional[str]
    generated_at_utc: str

    canon_snapshot: dict[str, Any]
    narrative_status: dict[str, Any]
    viewpoint: dict[str, Any]
    scene_objective: dict[str, str]

    incoming_flows: list[IncomingFlow] = field(default_factory=list)
    active_pressures: dict[str, float] = field(default_factory=dict)
    sediment: list[NarrativeSediment] = field(default_factory=list)
    reservoirs: list[NarrativeReservoir] = field(default_factory=list)
    channel_conditions: list[dict[str, Any]] = field(default_factory=list)
    evidence_state: list[EvidenceClaim] = field(default_factory=list)
    actor_interpretations: list[ActorInterpretation] = field(default_factory=list)
    relationship_state: list[RelationshipState] = field(default_factory=list)
    institutional_constraints: list[dict[str, Any]] = field(default_factory=list)
    equipment_state: list[dict[str, Any]] = field(default_factory=list)
    scarcity_state: list[dict[str, Any]] = field(default_factory=list)
    required_downstream_effects: list[str] = field(default_factory=list)
    prohibited_shortcuts: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    exit_conditions: list[str] = field(default_factory=list)
    axiom_checks: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class NarrativeRiverAdapter:
    def build_frame(
        self,
        *,
        canon_snapshot: dict[str, Any],
        prior_delta: Optional[dict[str, Any]],
        scene_request: dict[str, Any],
        actor_states: list[dict[str, Any]],
        institution_states: list[dict[str, Any]],
        simulation_state: Optional[dict[str, Any]] = None,
    ) -> NarrativeRiverFrame:
        raise NotImplementedError

    def render_prompt_contract(
        self,
        frame: NarrativeRiverFrame,
        axioms_text: str,
    ) -> str:
        raise NotImplementedError

    def validate_draft(
        self,
        frame: NarrativeRiverFrame,
        draft_text: str,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def extract_delta(
        self,
        frame: NarrativeRiverFrame,
        approved_draft_text: str,
    ) -> dict[str, Any]:
        raise NotImplementedError
```

# 13. Determinism

Given the same canon snapshot, prior delta, scene request, actor profiles, and configuration, the adapter should produce the same frame ordering, IDs, and computed pressure values.

Some fields remain qualitative and should not be generated solely by formula:

- required state change;
- prohibited shortcuts;
- blind spots;
- dramatic goal;
- unresolved questions;
- cultural interpretation.

Numeric scores are advisory. They rank attention and expose imbalance; they do not claim psychological precision.

# 14. Storage Layout

```text
narrative/
  river/
    schemas/
      narrative_river_frame.schema.json
      scene_river_delta.schema.json
    frames/
      dark_star/
    deltas/
      dark_star/
    profiles/
      characters/
      institutions/
    config/
      narrative_axioms.md
      adapter_rules.yaml
    examples/
      dark_star_quiet_lane.md

src/
  narrative_river/
    __init__.py
    models.py
    adapter.py
    prompt_contract.py
    validator.py
    delta_extractor.py
    persistence.py
    provenance.py

tests/
  test_narrative_river_models.py
  test_narrative_river_determinism.py
  test_narrative_river_persistence.py
  test_narrative_axiom_validator.py
  test_symbolic_bleed_filter.py
  test_dark_star_quiet_lane_frame.py
```

# 15. Phase Plan

## Phase 1 — Passive planning artifact

Deliver schema, serialization, manual frame creation, prompt rendering, and no mutation or canon writes.

## Phase 2 — Advisory validation

Add axiom checks, evidence checks, symbolic bleed warnings, rhythm heuristics, hierarchy warnings, and missing-consequence warnings.

## Phase 3 — Persistent scene chain

Add frame storage, delta storage, prior-delta import, stable IDs, canon snapshot references, and branch-aware persistence.

## Phase 4 — GUMAS integration

Add simulation-state import, equipment and scarcity import, RiverCycle pressure import, event provenance, and deterministic pressure calculation.

## Phase 5 — CanonRec integration

Add canon-reference validation, canon-candidate extraction, conflict reporting, and optional PR-ready packaging. No automatic promotion.

# 16. Test Plan

## Model tests

- frame serializes to JSON and YAML;
- IDs remain stable;
- confidence and pressure values stay in range;
- missing required fields fail validation;
- unknown schema versions fail closed.

## Persistence tests

- stored frame reloads without loss;
- scene delta imports into the next frame;
- unresolved sediment persists;
- resolved sediment does not reappear unless reintroduced;
- canon references preserve commit SHA.

## Narrative validation fixtures

1. self-aware narration;
2. corny aphoristic dialogue;
3. hierarchy drift;
4. procedural over-explanation;
5. unsupported omniscience;
6. evidence-layer collapse;
7. scarcity violation;
8. trailer-line ending;
9. repeated three-word dialogue;
10. symbolic RiverCycle metaphor bleed.

## Dark Star acceptance test

A compliant Quiet Lane draft must:

- show Iven’s suspicion before confirmation;
- allow several minutes where he may appear wrong;
- reveal a layered ambush;
- use his credential preparation as a limited advantage;
- preserve tension between useful preparation and withheld disclosure;
- consume scarce equipment;
- extract a witness with incomplete knowledge;
- preserve the artifact as uncertain;
- avoid RiverCycle terminology in prose;
- end on a material state change.

# 17. Failure Modes

## Frame becomes an outline

Contain by requiring state transitions rather than exact choreography.

## Numeric pseudo-psychology

Contain by treating scores as advisory and preserving qualitative interpretation.

## Symbolic bleed

Contain with the surface-language firewall and concrete translation.

## Procedural inflation

Contain by including process only when it changes action.

## False persistence

Contain by requiring storage receipts and explicit persistence class.

## Canon contamination

Contain by labeling evidence status and separating canon-candidate extraction.

## Validation becomes stylistic policing

Contain by starting with warnings, citing passages, and preserving human override.

# 18. Worked Dark Star Frame — Quiet Lane

```yaml
frame_id: NRF-DARKSTAR-CH05-S02-001
schema_version: "0.1.0"
scene_id: DARKSTAR.CH05.QUIET_LANE.02
chapter_id: DARKSTAR.CH05

canon_snapshot:
  repository: AUo959/CanonRec
  commit_sha: null
  authority_status: mixed

viewpoint:
  mode: close_third
  focal_character_ids:
    - TESSA_KORR
  prohibited_omniscience: true

scene_objective:
  operational_goal: Reach Kallis Foundry before archive destruction completes.
  dramatic_goal: Show how Ranger planning, conflict, contacts, and equipment operate under pressure.
  required_state_change: The assumed safe approach becomes confirmed hostile space, and the crew gains a witness plus a dangerous artifact fragment.

incoming_flows:
  - flow_id: FLOW-KALLIS-PURGE
    type: evidence_loss
    source: KALLIS_FOUNDRY
    target: THIRD_MEASURE_CREW
    carrier: live_archive_telemetry
    strength: 0.86
    confidence: 0.91

  - flow_id: FLOW-IVEN-WITHHELD-CREDENTIAL
    type: trust_strain
    source: IVEN_RAAL
    target: THIRD_MEASURE_CREW
    carrier: mission_preparation
    strength: 0.43
    confidence: 1.0

active_pressures:
  tactical: 0.77
  evidentiary: 0.91
  interpersonal: 0.38
  political: 0.29
  technical: 0.62
  exhaustion: 0.34

sediment:
  - sediment_id: SED-LETHAN-WITHDRAWAL
    source_event: DARK_STAR_BOARDING
    description: The crew survived a disagreement about withdrawal without resolving the underlying decision model.
    current_effect: Each interprets uncertainty through a different responsibility.
    resolution_status: active

  - sediment_id: SED-IVEN-CREDENTIAL
    source_event: CURRENT_SCENE
    description: Iven obtained and carried a quarantined credential without informing the crew before launch.
    current_effect: His caution proves useful while reducing trust in his process.
    resolution_status: newly_created

reservoirs:
  - reservoir_id: RES-CREW-DISCIPLINE
    type: professional_discipline
    capacity: 0.74
    absorbs:
      - interpersonal_conflict
      - operational_fear
    failure_condition: A concealed action creates immediate danger without time for correction.

  - reservoir_id: RES-DRONE-DEPTH
    type: equipment_redundancy
    capacity: 0.63
    absorbs:
      - sensor_uncertainty
      - approach_risk
      - casualty_risk

evidence_state:
  - claim_id: CLAIM-CALDER-PRESENT
    claim: Calder Vey remains at Kallis Foundry.
    status: unconfirmed
    support:
      - active purge
      - restored station systems
    contradictions:
      - false departure record
    confidence: 0.24

  - claim_id: CLAIM-AMBUSH
    claim: The approach corridor is prepared as an ambush.
    status: hypothesis
    support:
      - unusually clean traffic picture
      - purge timing
      - known Calder counter-surveillance methods
    confidence: 0.58

actor_interpretations:
  - actor_id: TESSA_KORR
    interpretation: Delay destroys evidence; uncertainty should be reduced without surrendering initiative.
    preferred_response: controlled approach with limited deception
    blind_spot: May treat disappearing opportunity as justification for accepting poorly bounded risk.

  - actor_id: IVEN_RAAL
    interpretation: The clean traffic picture is itself evidence of preparation.
    preferred_response: expose the trap through a decoy and independent observation
    blind_spot: May withhold useful preparation until he considers it verified.

  - actor_id: MAELIN_SAYE
    interpretation: The field can be manipulated only if control systems remain segmented and observable.
    preferred_response: layered drones, isolated channels, reversible technical actions
    blind_spot: May overvalue technical containment where human intent remains decisive.

relationship_state:
  - relation_id: REL-TESSA-IVEN
    trust: 0.67
    operational_reliance: 0.81
    current_strain: 0.39
    required_change: Tessa recognizes the value of Iven's warning without treating concealment as acceptable.

institutional_constraints:
  - constraint_id: INST-FIELD-COURT-PRESERVATION
    authority: FIELD_COURT
    effect: Evidence enters Marshal and judicial custody simultaneously.
    appears_in_prose_as:
      - duplicate evidence routing
      - immediate hash receipt
    must_not_appear_as:
      - extended procedural explanation

scarcity_state:
  - scarce_asset: Javelin munitions
    current_quantity: 3
    consequence: Firing two during the ambush reduces later breaching and defense options.

required_downstream_effects:
  - Iven's warning is only partly correct; the trap contains a second layer.
  - Crew trust does not reset after survival.
  - Kallis evidence implicates a Union authority class without identifying a culprit.
  - The witness enters with an immediate survival objective.
  - The fragment creates a new containment problem.

prohibited_shortcuts:
  - Calder appears without prior evidence.
  - The administrative root solves the whole fight.
  - Tessa praises Iven in a way that resolves their conflict.
  - The witness explains the conspiracy in one speech.
  - The artifact is identified with certainty.
  - RiverCycle vocabulary appears in ordinary narration.

exit_conditions:
  - The ambush is exposed.
  - The crew survives through layered preparation, not luck.
  - A witness and artifact fragment are extracted.
  - Kallis becomes unrecoverable.
  - At least one evidentiary lead is preserved.
```

# 19. Worked Post-Scene Delta — Quiet Lane

```yaml
scene_river_delta:
  scene_id: DARKSTAR.CH05.QUIET_LANE.02

  state_changes:
    - The direct Kallis approach is confirmed as a layered ambush.
    - Calder's network demonstrates cloaked pursuit craft and converted industrial defenses.
    - A Kallis technician is recovered alive.
    - The foundry becomes unrecoverable as a physical site.
    - A fragment associated with the First Silence enters Third Measure custody.

  new_sediment:
    - sediment_id: SED-IVEN-CREDENTIAL
      description: Iven's preparation saved the crew, but he withheld the credential until en route.
      affected:
        - TESSA_KORR
        - MAELIN_SAYE
        - IVEN_RAAL

  pressure_changes:
    evidentiary: -0.18
    technical: +0.27
    political: +0.22
    interpersonal: +0.09
    containment: +0.41

  relationship_changes:
    - relation_id: REL-TESSA-IVEN
      trust_delta: -0.04
      operational_reliance_delta: +0.05
      note: The relationship becomes more complex rather than simply better or worse.

  evidence_changes:
    - claim_id: CLAIM-AMBUSH
      previous_status: hypothesis
      new_status: confirmed

    - claim_id: CLAIM-CALDER-PRESENT
      previous_status: unconfirmed
      new_status: contradicted_by_testimony
      confidence: 0.62

    - claim_id: CLAIM-FIRST-SILENCE-FRAGMENT
      previous_status: unknown
      new_status: testimony_plus_instrument_output
      confidence: 0.47

  new_questions:
    - Who authorized the false departure using Union strategic access?
    - Why did the fragment synchronize with the gunboat clock?
    - Why did the station architecture change after the case was isolated?
    - Did Calder leave the credential active intentionally?

  equipment_changes:
    - asset: Javelin
      delta: -2
    - asset: Porter
      delta: -1
      state: destroyed_decoy

  canon_candidates:
    - Calder's network uses multi-layer ambush doctrine.
    - Kallis Foundry functioned as part of a field assembly.
    - A surviving technician participated in production-level-three work.
    - A possible First Silence fragment was recovered.

  next_scene_requirements:
    - Medical and technical isolation compete for control of the survivor and case.
    - The crew must report a Union authority-class signature without naming a culprit.
    - The fragment remains instrumentally observed and conceptually unresolved.
    - Iven's concealment remains active in crew interaction.
```

# 20. Acceptance Criteria for v0.1 Implementation

## Models

- `NarrativeRiverFrame` exists.
- `SceneRiverDelta` exists.
- Frames serialize to JSON and YAML.
- Evidence claims preserve provenance and confidence.
- Persistence classes are explicit.

## Adapter

- A frame can be built from a manual scene request.
- A compact prompt contract can be rendered.
- A post-scene delta can be created manually or semi-automatically.
- No canon, memory, or simulation mutation occurs.

## Validation

- The Eleven Axioms are named checks.
- Symbolic bleed, evidence collapse, self-aware prose, and hierarchy drift can be flagged.
- Warnings cite exact passages.

## Example

- Quiet Lane has a complete example frame and post-scene delta.
- The example includes pressure, sediment, reservoirs, evidence, relationships, scarcity, and exit conditions.

# 21. Operational Use Before Code Exists

For each scene:

1. Identify the canon snapshot.
2. State viewpoint.
3. State operational and dramatic objectives.
4. List incoming pressures.
5. List active sediment.
6. Identify reservoirs.
7. Separate evidence from interpretation.
8. Describe how major actors interpret the same pressure.
9. State scarcity and equipment limits.
10. Define required downstream effects.
11. Define prohibited shortcuts.
12. Define the state transition that ends the scene.
13. Draft under the Eleven Axioms.
14. Extract a post-scene delta.
15. Carry the delta forward.

Manual use is genuine use of the framework, but it is not persistent automation unless frames and deltas are saved.

# 22. Final Design Principle

The Narrative River Adapter should not make prose sound like RiverCycle.

It should make the world behave as though information, pressure, memory, authority, scarcity, and consequence continue moving after the scene ends.

The strongest proof that the adapter is working will be prose in which:

- characters remember consequences without reciting them;
- institutions reveal themselves through action;
- evidence retains provenance;
- tension grows from constrained choices;
- success creates residue;
- mystery remains bounded by what is known;
- later scenes are altered by earlier ones;
- drama emerges from the system rather than authorial convenience.

## Appendix A — Minimal Frame Template

```yaml
frame_id:
scene_id:
chapter_id:
canon_snapshot:
viewpoint:
scene_objective:
  operational_goal:
  dramatic_goal:
  required_state_change:

incoming_flows: []
active_pressures: {}
sediment: []
reservoirs: []
evidence_state: []
actor_interpretations: []
relationship_state: []
institutional_constraints: []
equipment_state: []
scarcity_state: []
required_downstream_effects: []
prohibited_shortcuts: []
unresolved_questions: []
exit_conditions: []
```

## Appendix B — Minimal Delta Template

```yaml
scene_id:
state_changes: []
new_sediment: []
resolved_sediment: []
pressure_changes: {}
relationship_changes: []
evidence_changes: []
new_questions: []
closed_questions: []
equipment_changes: []
institutional_changes: []
canon_candidates: []
next_scene_requirements: []
```

## Appendix C — Status Declaration

```yaml
narrative_river_adapter:
  specification_complete: true
  code_implemented: false
  automatically_invoked: false
  persistent_storage_configured: false
  canon_authority: Git
  recommended_next_step: implement Phase 1 models, serialization, and manual prompt rendering
```
