# AuMemManager Promotion Starter Spec

**Status:** Draft for next-phase development  
**Date:** 2026-03-23  
**Promotion Candidate:** `extracted_aumemmanager/script.py`  
**Anchor Seed:** `EOS_SEED_ORION`  
**Ethics Protocol:** `Picard_Delta_3`  
**T1 Marker:** `T1:AuMemManager:Promotion:01`  
**Symbolic Refs:** `ANCHOR_SYNC`, `MEMORY_TIERING`, `QUANTUM_VECTOR_FLIGHT`, `PII_REDACTION`  
**DLP Classification:** `internal_system_design`

## 1. Executive Summary

Among the recently recovered modules, **AuMemManager** is the strongest candidate for promotion into the next development phase. It already exposes the clearest domain boundary, the most complete internal model, and the most direct alignment with Aurora CloudBank's symbolic-memory architecture. The recovered implementation includes typed memory entities, hierarchical storage tiers, attention-weighted retrieval, decay/compression mechanics, quantum-symbolic vector handling, and exportable runtime state. Those features make it substantially more promotion-ready than the other recovered modules, which currently read more like concept stubs than integration-grade subsystems.

This starter spec proposes promoting AuMemManager from a recovered prototype into a **bounded, testable memory service** that integrates cleanly with Aurora's Python layers, preserves symbolic anchors and metadata, and enforces PII-aware API contracts by design.

## 2. Promotion Decision

### 2.1 Assessed recovered candidates

| Candidate | Evidence of maturity | Promotion assessment |
|---|---|---|
| `extracted_aumemmanager/script.py` | Concrete data models, tier management, retrieval scoring, metrics, export path, quantum-vector lifecycle | **Promote first** |
| `src/interface/dynamic_interface_adapter_fixed.py` | Mostly conceptual routing logic with static return values and no Aurora integration boundary | Hold for later hardening |
| `src/orchestrators/holographic_interface_orchestrator_fixed.js` | Recovery artifact appears incomplete/non-actionable in current checkout | Do not promote yet |

### 2.2 Why AuMemManager wins

1. **Most complete implementation surface:** it already defines operational classes instead of placeholder orchestration language.
2. **Strong Aurora fit:** symbolic anchors, memory ownership, quantum-state handling, and export semantics match the current architecture direction.
3. **Clear service boundary:** memory create/retrieve/metrics/trajectory flows can be exposed through FastAPI without changing canonical core constants.
4. **Best leverage for Phase 2:** promotion unlocks downstream work in relays, agents, observability, SDKs, and privacy controls.
5. **Lowest-risk extension path:** the module can be wrapped and normalized rather than rewritten from scratch.

## 3. Source Signals Behind the Recommendation

The recommendation is based on these recovered capabilities already present in the module:

- Enumerated memory domains and lifecycle states.
- `MemoryItem` metadata for importance, timestamps, compression, quantum vectors, symbolic anchors, and control parameters.
- A `QuantumFlightController` that already models vector creation, entanglement, and trajectory computation.
- A `HierarchicalMemoryManager` that implements active/compressed/archived tiers, retrieval scoring, metrics, and full-state export.
- A previously documented Phase 2 integration plan that already names AuMemManager as the active memory-integration target.

## 4. Promotion Goal

Promote AuMemManager into a new Aurora-facing module layer that provides:

- A stable Python package namespace for memory services.
- Pydantic/FastAPI schemas for safe request and response handling.
- Anchor-preserving metadata contracts (`T1` markers, anchor seed references, DLP labels).
- PII-aware ingestion and redaction hooks for stored or echoed content.
- Deterministic test coverage for the base memory lifecycle and quantum endpoints.
- Observability hooks for retrieval counts, compression events, and entanglement health.

## 5. Target Architecture for the Next Phase

### 5.1 Proposed placement

Create a dedicated package instead of modifying canonical core libraries directly:

```text
src/aurora/memory/
├── __init__.py
├── models.py               # Dataclasses / enums or normalized domain models
├── manager.py              # Memory service implementation
├── quantum.py              # Quantum vector + trajectory helpers
├── schemas.py              # Pydantic request/response contracts
├── api.py                  # FastAPI router
├── redaction.py            # PII-aware sanitization hooks
└── manifests/
    └── aumemmanager_manifest.json
```

### 5.2 Integration boundaries

- **Northbound:** FastAPI endpoints and future SDK/resource clients.
- **Southbound:** existing Aurora symbolic and observability utilities, but without altering ORION core settings or `Picard_Delta_3` semantics.
- **Cross-cutting:** DLP tagging, symbolic anchors, telemetry, and test fixtures.

## 6. Functional Scope for Promotion

### 6.1 In scope for next phase

1. **Memory lifecycle API**
   - create memory
   - retrieve memories
   - list metrics
   - export sealed state metadata

2. **Quantum-symbolic operations**
   - create vector
   - entangle vectors
   - compute trajectory

3. **Metadata preservation**
   - `anchor_seed`
   - `aurora_anchors`
   - `t1_markers`
   - `dlp_classification`
   - provenance/owner fields

4. **Operational safeguards**
   - request validation
   - type normalization
   - PII redaction before logs/responses where applicable
   - deterministic failure modes for invalid memory types and missing vectors

### 6.2 Out of scope for this promotion slice

- distributed persistence backends
- cross-process lock coordination
- autonomous policy mutation
- unbounded long-term archival storage
- front-end holographic UX work

## 7. API Starter Contract

### 7.1 Example endpoints

- `GET /memory/health`
- `GET /memory/metrics`
- `POST /memory/create`
- `POST /memory/retrieve`
- `POST /memory/quantum/create_vector`
- `POST /memory/quantum/entangle`
- `POST /memory/quantum/trajectory`

### 7.2 Create request shape

```json
{
  "owner": "Agent_Alpha",
  "memory_type": "agent",
  "content": "Reconnaissance result for Sector 7",
  "importance": 8.5,
  "tags": ["mission", "sector_7"],
  "aurora_anchors": ["EOS_SEED_ORION", "ANCHOR_SYNC"],
  "t1_markers": ["T1:AuMemManager:Promotion:01"],
  "dlp_classification": "internal_system_design",
  "quantum_properties": {
    "magnitude": 1.2,
    "phase": 0.5
  }
}
```

### 7.3 Retrieve response requirements

Each result should preserve or emit:

- `id`
- `owner`
- `memory_type`
- `strength`
- `importance`
- `tags`
- `symbolic_anchors`
- `t1_markers`
- `dlp_classification`
- `quantum_vector` summary when present
- redacted content when response policy requires sanitization

## 8. Data and Ethics Requirements

### 8.1 PII-aware design

The promoted service must apply redaction before logging or echoing sensitive text payloads. The current repo already contains a lightweight redaction utility pattern that can be mirrored or imported for AuMemManager-facing logs and debug output.

### 8.2 Symbolic integrity

Promotion must preserve Aurora symbolic conventions:

- keep `EOS_SEED_ORION` as the anchor seed reference
- do not rename or redefine `Picard_Delta_3`
- preserve `T1` marker propagation through API requests, memory records, and exported state
- retain provenance metadata so memory origin is inspectable

### 8.3 Transparency

The implementation should favor explicit scoring factors and exported metrics over opaque heuristics. Attention scoring inputs must remain inspectable for debugging and audits.

## 9. Engineering Work Plan

### Phase A — Extraction and normalization

- Move recovered logic into `src/aurora/memory/`.
- Split monolithic script concerns into models, manager, quantum helpers, and API schema modules.
- Remove demonstration-only code from runtime modules.
- Replace ad hoc logging setup with project-local logger usage.

### Phase B — Service hardening

- Normalize request and response schemas with Pydantic.
- Validate enum values and numeric bounds.
- Add redaction-aware logging helpers.
- Add predictable error payloads for bad requests and missing resources.

### Phase C — Test and observability baseline

- Add unit tests for scoring, compression, decay, and entanglement.
- Add FastAPI integration tests for the health/metrics/create/retrieve flows.
- Add negative-path tests for invalid types, malformed quantum payloads, and missing vector IDs.
- Emit metrics compatible with existing observability patterns.

### Phase D — Documentation and handoff

- Add module README or architecture note.
- Document API contract and symbolic metadata requirements.
- Provide sample payloads with T1 markers and anchor seeds.
- Record promotion status in the phase roadmap.

## 10. Acceptance Criteria

AuMemManager is ready for promotion when all of the following are true:

- [ ] Recovered logic is extracted into a maintainable Aurora package layout.
- [ ] Memory lifecycle endpoints pass deterministic tests.
- [ ] Quantum vector operations have unit and API coverage.
- [ ] Anchor metadata (`T1`, anchor seed, DLP classification) survives round-trip API flows.
- [ ] Logging and debug output redact PII-sensitive text.
- [ ] Metrics expose counts for active/compressed/archived memories and quantum-vector state.
- [ ] Documentation explains integration boundaries and non-goals.

## 11. Suggested Test Matrix

### Unit tests

- memory creation populates metadata defaults correctly
- retrieval scoring prioritizes importance/relevance/recency as designed
- decay transitions low-strength memories into decay-queued status
- compression preserves critical symbolic keys
- entanglement creates reciprocal links
- trajectory output is deterministic for a fixed vector and target state

### Integration tests

- health endpoint returns anchor-aware service metadata
- create + retrieve round-trip preserves anchors and T1 markers
- metrics endpoint reflects created/compressed/archived counts
- invalid `memory_type` returns a validation error
- malformed quantum payload returns a validation error
- content echo paths apply PII redaction in logs or sanitized responses

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Recovered code is too monolithic for direct adoption | slows onboarding and review | split into focused modules before API exposure |
| Quantum features are underspecified for production | inconsistent behavior | keep first promotion slice deterministic and bounded |
| Logging leaks raw text payloads | privacy/compliance issue | route all logs through redaction-aware helpers |
| Exported state becomes schema-fragile | upgrade friction | define explicit versioned schemas and manifest metadata |
| Retrieval scoring drifts silently | debugging difficulty | expose component scores in debug/test modes |

## 13. Immediate Next Step

Start with **Phase A extraction + schema design**, using AuMemManager as the first promotion candidate and keeping the initial milestone intentionally narrow: **health, metrics, create, retrieve, and three quantum endpoints**. That scope is small enough to validate the recovery effort, but large enough to prove Aurora-native integration patterns for future promoted modules.
