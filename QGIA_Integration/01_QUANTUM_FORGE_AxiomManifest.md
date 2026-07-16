# QUANTUM_FORGE Axiom Node Manifest

- **Bundle:** Aurora-QGIA-INT-v1.0
- **Manifest:** `QGIA-AURORA-AXIOM-MANIFEST-v1.0`
- **Engine descriptor:** `gpt-symbolic-memetic`
- **Ethics binding:** `GUMAS_Thermax`
- **Core binding:** `Aurora_Core_Flowstate`
- **Reconciliation date:** 2026-07-16
- **Certainty:** `STAGING`
- **Runtime activation:** `NOT_IMPLEMENTED`

## Scope and authority

This document is the human-readable registry for
`QGIA_integration/QUANTUM_FORGE_Axiom_Manifest.json`. The JSON manifest is the
detailed machine mirror for the 23 QGIA axiom definitions; it retains every
rule summary, corollary, violation signal, audit event, PAT command, and
advisory hook.

The reconciliation preserves all 23 implemented axiom definitions. It corrects
the former human registry, which listed 22 standalone records while claiming
23. `EXTERNAL_AGENT_DEPENDENCY` remains preserved as a corollary of `AN-001`,
as represented in the machine manifest; it is not a removed axiom node.
`AN-007 ASYMMETRY_RECOGNITION` and `AN-010 ANTI_SMOKING_GUN` are restored to
the human registry.

The manifest is staged integration material. `export_ready: true` means the
document package can be exported; it does not mean that Quantum Forge loads or
activates the axiom definitions. No loader or adapter for that purpose is
present in this repository.

## Node registry

The `gumas_tier` values below are QGIA doctrine classifications. They are not
Quantum Forge `EthicsLevel` values. The `ethics_lock` flag is declarative until
an explicit adapter invokes the runtime ethics gate.

| ID | Name | Category | Doctrine tier | Ethics lock | Status | Advisory hook |
| --- | --- | --- | --- | --- | --- | --- |
| AN-001 | TRUMP_REACTIVE_AGENT_MODEL | A | OVERRIDE | true | PERMANENT_OVERRIDE | `SIM::ACTOR_MODEL::REACTIVE_NODE` |
| AN-002 | COWARD_BULLY_CONFIG | A | OVERRIDE | true | PERMANENT_OVERRIDE | `SIM::ACTOR_MODEL::ASYMMETRY_CONFIG` |
| AN-003 | PREDICTION_MARKET_WEIGHT | A | WEIGHT_CONSTRAINT | false | LOW_WEIGHT_SECONDARY_SIGNAL | `SIM::SOURCE_WEIGHT::PREDICTION_MARKET` |
| AN-004 | RATIONALE_TREADMILL | D | STANDARD | false | ACTIVE | `SIM::INSTITUTIONAL::RATIONALE_TRACKER` |
| AN-005 | WEAPONIZED_DIPLOMACY | D | THEATER_SPECIFIC | false | ACTIVE | `SIM::THEATER::GULF_MENA_CREDIBILITY` |
| AN-006 | NEUTRALITY_FLUFF | C | STANDARD | false | ACTIVE | `SIM::EPISTEMIC::NEUTRALITY_CHECK` |
| AN-007 | ASYMMETRY_RECOGNITION | C | STANDARD | false | ACTIVE | `SIM::EPISTEMIC::ASYMMETRY_FLAG` |
| AN-008 | 4D_CHESS_EXCLUSION | C | STANDARD | true | ACTIVE | `SIM::EPISTEMIC::FALSIFIABILITY_GATE` |
| AN-009 | MOSAIC_EVIDENCE | C | STANDARD | false | ACTIVE | `SIM::EPISTEMIC::MOSAIC_STANDARD` |
| AN-010 | ANTI_SMOKING_GUN | C | STANDARD | false | ACTIVE | `SIM::EPISTEMIC::ABSENCE_WEIGHT` |
| AN-011 | REVEALED_BELIEF_DISSONANCE | C | STANDARD | false | ACTIVE | `SIM::EPISTEMIC::BELIEF_SIGNAL` |
| AN-012 | SELF_INFLICTED_BLIND_SPOT | D | STANDARD | true | ACTIVE | `SIM::INSTITUTIONAL::CIRCULAR_VERIFICATION` |
| AN-013 | PHOTO_OP_DURABILITY | D | STANDARD | false | ACTIVE | `SIM::INSTITUTIONAL::DURABILITY_TEST` |
| AN-014 | PERSONAL_ENRICHMENT_VEHICLE | D | STANDARD | false | ACTIVE | `SIM::INSTITUTIONAL::OUTPUT_CLASSIFICATION` |
| AN-015 | DOMINATION_AXIOM | B | STANDARD | false | ACTIVE | `SIM::POWER::DOMINATION_TRAP` |
| AN-016 | AGENCY_AXIOM | B | STANDARD | false | ACTIVE | `SIM::POWER::AGENCY_FLOOR` |
| AN-017 | THRESHOLD_AXIOM | B | STANDARD | false | ACTIVE | `SIM::POWER::THRESHOLD_TRACKER` |
| AN-018 | PERCEPTION_AXIOM | B | STANDARD | false | ACTIVE | `SIM::POWER::PERCEPTION_LAYER` |
| AN-019 | ALLIANCE_AXIOM | B | STANDARD | false | ACTIVE | `SIM::POWER::ALLIANCE_QUALITY` |
| AN-020 | RATIONAL_POWER | B | STANDARD | false | ACTIVE | `SIM::POWER::DURABILITY_MODEL` |
| AN-021 | FORECAST_CONSENSUS_SEPARATION | C | ARCHITECTURE | true | ACTIVE | `SIM::ARCHITECTURE::L1_L2_BOUNDARY` |
| AN-022 | MACHIAVELLI_HATRED_THRESHOLD | E | STANDARD | false | ACTIVE | `SIM::RISK::HATRED_THRESHOLD` |
| AN-023 | DRAFT_THREAT_ACTIVATION | E | STANDARD | false | ACTIVE | `SIM::RISK::DRAFT_ACTIVATION` |

## Quantum Forge binding crosswalk

| Manifest declaration | Verified repository seam | Reconciled meaning |
| --- | --- | --- |
| `GUMAS_Thermax` | `modules.quantum_forge.quantum_forge_v2.GUMAS_Thermax` | The declared runtime class exists. Manifest locks remain declarative until an adapter submits operations through `EthicsAwareQuantumGate`. |
| `Aurora_Core_Flowstate` | `modules.quantum_forge.quantum_forge_v2.Aurora_Core_Flowstate` | Runtime flow-state class exists. Quantum Forge v3 orchestration is coordinated by `SystemFlowOrchestrator`; the manifest is not registered with it. |
| `gpt-symbolic-memetic` | No runtime target verified | External/package descriptor only; it is not a verified Quantum Forge class or loader. |
| `SIM::...` hooks | QGIA L1 signal architecture | Advisory destinations only. L1 crew or relay-agent judgment must mediate any L2 simulation effect. |

## Layer and activation constraints

- QGIA is an L1 analytical institution. These axiom definitions may inform L1
  analysis and decision support.
- L2 has no interpretive authority and must not self-task from QGIA signals.
  L1 crew or relay agents must translate an advisory hook into L2 parameters.
- The `AN-*` identifiers are QGIA doctrine identifiers, not Quantum Forge
  `SymbolicMemoryNode` identifiers.
- A future activation change requires a reviewed loader/adapter contract,
  explicit tier-to-runtime semantics, ethics-gate enforcement, tests, and owner
  approval. Documentation alignment alone does not activate the manifest.

## Promotion assessment

Current recommendation: remain `STAGING`. The node registry is internally
reconciled, but activation semantics and a reviewed runtime adapter do not yet
exist. This is a readiness boundary, not a decision to exclude the axiom work.
Promotion or activation requires explicit owner review.
