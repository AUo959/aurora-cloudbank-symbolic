# Recovered Protocol Promotion Plan

**Issue:** #993  
**Status:** Planning artifact  
**Runtime posture:** Documentation/schema review only; no enforcement wiring.

## 1. Objective

Promote recovered Sherlock / Watson / Moriarty / Tribunal / SHADOWFAX ethics-layer materials through a controlled review path before runtime integration.

This plan exists to prevent three failure modes:

1. treating recovered artifacts as sealed runtime canon without custody review,
2. collapsing investigation, context, containment, and judgment into one self-justifying lane,
3. wiring symbolic/anomaly doctrine into runtime behavior before tests and rollback paths exist.

## 2. Evidence classification model

Each recovered artifact must be classified before promotion.

| Classification | Meaning | Runtime use |
|---|---|---|
| Current repo canon | Already committed to CloudBank or control-plane Git | May be cited as committed source |
| Control-plane report lineage | Present in committed control-plane reports or docs | May inform planning; verify before CloudBank runtime use |
| Uploaded recovered candidate | Available as user-provided artifact with custody/hash notes | May be inventoried; not runtime canon |
| Sealed-bundle reference | Referenced by index/manifest/checksum material but payload not fully verified in repo | Requires payload verification before use |
| Missing dependency | Referenced but not available | Must be tracked as blocked |

## 3. Initial recovered protocol inventory

| Protocol | Proposed role | Initial status | Required next evidence |
|---|---|---|---|
| Sherlock | Investigation, traceability, causal mapping, transparency reporting, doctrine verification | Recovered candidate / sealed-bundle lineage | Confirm exact source files, version, checksum, schema |
| Watson | Context retention, rigidity moderation, evidence correlation, operator-readable briefs | Recovered candidate / sealed-bundle lineage | Confirm exact source files, version, checksum, schema |
| Moriarty | Anomaly containment, quarantine, review-only translation, ethics audit, anchor check, rollback | Recovered candidate / runtime recovery lineage | Confirm exact source files, version, checksum, schema, test boundaries |
| Tribunal | Dispute and appeal adjudication for memory, narrative integrity, drift, containment | Recovered candidate / sealed-bundle lineage | Confirm exact source files, version, checksum, schema, quorum/appeal semantics |
| SHADOWFAX | Stillness, supervisory review, paradox escalation, containment oversight | Referenced supervisory lane / partially recovered lineage | Locate standalone bundle or mark dependency blocked |

## 4. Required custody fields

Every promoted protocol artifact should include or be accompanied by:

- source package name,
- source package SHA-256,
- internal file path,
- internal file SHA-256,
- observed version,
- observed status,
- source classification,
- verification date,
- reviewer or agent surface,
- unresolved blockers,
- promotion decision.

## 5. Proposed schema families

Protocol schemas should be created before runtime use.

### 5.1 Common protocol schema

Required fields:

- `protocol_id`
- `version`
- `status`
- `role`
- `allowed_actions`
- `forbidden_actions`
- `required_evidence`
- `handoff_targets`
- `audit_requirements`
- `layer_boundaries`
- `rollback_requirements`
- `appeal_requirements`

### 5.2 Sherlock schema

Additional fields:

- `investigation_scope`
- `traceability_log_requirements`
- `causal_mapping_requirements`
- `transparency_report_requirements`
- `containment_referral_rules`

Sherlock must not contain, adjudicate, or mutate subject state.

### 5.3 Watson schema

Additional fields:

- `context_sources`
- `rigidity_moderation_rules`
- `brief_generation_rules`
- `evidence_correlation_rules`
- `audit_log_integrity_rules`

Watson must not alter Sherlock logs, contain anomalies, or adjudicate appeals.

### 5.4 Moriarty schema

Additional fields:

- `anomaly_detection_inputs`
- `quarantine_rules`
- `review_only_translation_rules`
- `anchor_validation_rules`
- `rollback_rules`
- `crew_or_operator_rights`

Moriarty must not treat containment as narrative escalation and must not adjudicate its own containment decisions.

### 5.5 Tribunal schema

Additional fields:

- `jurisdiction`
- `minimum_evidence_bundle`
- `conflict_of_interest_rules`
- `ruling_record_requirements`
- `appeal_rules`
- `reopen_rules`

Tribunal must not perform primary investigation or secretly enforce containment.

### 5.6 SHADOWFAX schema

Additional fields:

- `stillness_triggers`
- `paradox_escalation_rules`
- `boundary_instability_thresholds`
- `supervisory_review_requirements`
- `override_constraints`

SHADOWFAX must not bypass evidence, erase review paths, or convert instability into proof.

## 6. Runtime integration boundaries

Any runtime integration proposal must explicitly map to existing CloudBank surfaces:

| Surface | Current role | Integration question |
|---|---|---|
| `src/monitoring/ethics_engine.py` | Rule engine and violation persistence | Which protocol rules become `EthicsRule`s, if any? |
| `src/monitoring/ethics_gate.py` | Caller-facing ethics gate | Which protocol failures block actions? |
| `src/subroutines/ethics_compliance_monitor.py` | Compliance scoring and block-record separation | How are protocol verdicts recorded versus enforced? |
| `modules/ethics_field/geometric_ethics.py` | Ethical formation scoring | Should protocols inform dimensions, thresholds, or warnings? |
| `modules/symbolic_core/model_validation.py` | Model-agnostic validator contract | Should model outputs reference protocol lanes as receipt metadata? |
| CASK #780 / PR #941 | Recursive ethics/cultural cognition work | Does CASK overlap or only consume protocol decisions? |

## 7. Required test plan before runtime wiring

Runtime integration must not proceed until tests cover:

- no planned L2-to-L1 bleed,
- anomaly quarantine before interpretation,
- review-only translation until cleared,
- rollback over compromise,
- containment appeal path exists,
- Sherlock cannot enforce or mutate,
- Watson cannot alter Sherlock logs or enforce,
- Moriarty cannot adjudicate its own actions,
- Tribunal requires evidence before ruling,
- SHADOWFAX stillness cannot bypass audit,
- no direct device/environment control,
- no crew/operator impersonation,
- failure state is explicit and auditable.

## 8. Recommended follow-up issues

Create follow-up implementation issues only after this promotion plan is accepted.

1. **Protocol custody inventory** — add machine-readable manifest of recovered package/file hashes and blockers.
2. **Protocol JSON schemas** — add schema files and validation tests.
3. **Protocol fixture intake** — add sanitized canonical examples for Sherlock, Watson, Moriarty, Tribunal, and SHADOWFAX.
4. **Runtime mapping design** — decide how protocol decisions map to `EthicsEngine`, `ethics_gate`, compliance monitor, and geometric ethics.
5. **Moriarty containment tests** — test anomaly quarantine/review-only/rollback rules without enabling active L2-to-L1 behavior.
6. **Tribunal appeal tests** — test dispute/appeal record requirements without runtime enforcement.

## 9. Non-goals

This PR and plan must not:

- wire recovered protocols into runtime enforcement,
- add active anomaly containment behavior,
- promote uploaded artifacts as sealed canon without verification,
- bypass existing `EthicsEngine` or `ethics_gate`,
- duplicate #780, #991, #992, or #994,
- weaken L1/L2/L3 boundaries,
- create cross-tenant cache or memory leakage.

## 10. Merge criteria for this planning PR

A planning PR for #993 is ready when it:

- creates a clear recovered-protocol intake location,
- records canon/custody warnings,
- defines separation of duties,
- proposes schema families,
- lists runtime integration boundaries,
- lists required tests before runtime wiring,
- leaves runtime behavior unchanged.
