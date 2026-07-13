# Ethics Documentation Map

**Status:** Active navigation index
**Scope:** Current ethics runtime surfaces, geometric evaluation, and recovered-protocol promotion planning
**Tracked in:** [#1139](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1139)

This directory is a map, not a new ethics authority. Committed runtime code and its tests remain authoritative for behavior. Recovered artifacts, planning documents, examples, and archived philosophy remain explicitly non-runtime unless promoted through their existing gates.

## At a glance

| Area | Current surface | Status |
|---|---|---|
| Rule evaluation | [`src/monitoring/ethics_engine.py`](../../src/monitoring/ethics_engine.py) | Implemented rule engine with blocking violations and audit records |
| Inline action gate | [`src/monitoring/ethics_gate.py`](../../src/monitoring/ethics_gate.py) | Implemented fail-closed gate used by model validation and the quantum simulator API |
| GUMAS adapter and relay gate | [`src/aurora/ethics/ethics_gate.py`](../../src/aurora/ethics/ethics_gate.py) | Implemented normalized GUMAS verdict adapter used by relay and compliance surfaces |
| Compliance monitoring | [`src/subroutines/ethics_compliance_monitor.py`](../../src/subroutines/ethics_compliance_monitor.py) | Implemented operational subroutine with scoring, audit, alert, and caller-enforcement receipts |
| Geometric ethics | [`modules/ethics_field/`](../../modules/ethics_field/) | Implemented five-dimension synapse evaluation; v1 remains authoritative |
| Recovered protocols | [`recovered_protocols/`](./recovered_protocols/) | Planning, custody fixtures, schemas, and test plans only; no runtime wiring authorized |

The two gate implementations serve different call paths: `src/monitoring/ethics_gate.py` wraps the local `EthicsEngine`, while `src/aurora/ethics/ethics_gate.py` normalizes responses from the GUMAS HTTP API. Do not treat their shared name as proof that their policies or callers are interchangeable.

## Picard_Delta_3 location and status

The current machine-executable definition is the autonomy-and-respect dimension in [`modules/ethics_field/dimension_evaluators/picard_delta_3.py`](../../modules/ethics_field/dimension_evaluators/picard_delta_3.py), summarized by [`docs/GEOMETRIC_ETHICS_ARCHITECTURE.md`](../GEOMETRIC_ETHICS_ARCHITECTURE.md). It evaluates:

- autonomy preservation,
- informed and revocable consent,
- human dignity,
- prevention of physical, psychological, and social harm.

The evaluator's formation threshold is `0.70`; scores below its `0.50` critical threshold create infinite geometric resistance. [`modules/ethics_field/field_curvature.py`](../../modules/ethics_field/field_curvature.py) weights this dimension at 25 percent in the v1 composite.

The local rule engine implements overlapping safety, oversight, transparency, fairness, and informed-consent rules, but it does not import `PicardDelta3Evaluator`. References to `Picard_Delta_3` elsewhere therefore identify the governing protocol or anchor; they do not by themselves prove that this evaluator is on that call path.

[`docs/archive/philosophy/04_ETHICS_PROTOCOL.md`](../archive/philosophy/04_ETHICS_PROTOCOL.md) contains a fuller historical narrative, but it is archived and is not promoted here as current canon. No standalone current `docs/ethics/PICARD_DELTA_3_CHARTER.md` was found during the #1139 audit.

## Runtime and evaluation references

| Reference | Purpose | Authority note |
|---|---|---|
| [`docs/GEOMETRIC_ETHICS_ARCHITECTURE.md`](../GEOMETRIC_ETHICS_ARCHITECTURE.md) | Documents the five dimensions, weights, resistance mapping, and synapse contract | Current architecture reference for geometric v1 |
| [`modules/ethics/README.md`](../../modules/ethics/README.md) | Documents the GUMAS-backed `src/aurora/ethics` gate and relay integration | Runtime module documentation, outside this directory by design |
| [`tests/test_ethics_engine.py`](../../tests/test_ethics_engine.py) | Rule-engine behavior | Executable evidence |
| [`tests/test_monitoring_ethics_gate.py`](../../tests/test_monitoring_ethics_gate.py) | Local fail-closed gate behavior | Executable evidence |
| [`tests/test_ethics_field.py`](../../tests/test_ethics_field.py) | Geometric dimensions and v1 field behavior | Executable evidence |
| [`tests/test_subroutines_integration.py`](../../tests/test_subroutines_integration.py) | Compliance-monitor and subroutine integration | Executable evidence |

## Files in `docs/ethics/`

### Top level

| File | Description | Status |
|---|---|---|
| [`README.md`](./README.md) | This navigation and authority map | Active index; #1139 |
| [`geometric_curvature_v2_evaluation.md`](./geometric_curvature_v2_evaluation.md) | Compares scalar v1 curvature with an interaction-aware v2 model | Evaluation only; v1 remains authoritative; #994 and #1137 |
| [`recovered_protocols/`](./recovered_protocols/) | Controlled intake and promotion lane for Sherlock, Watson, Moriarty, Tribunal, and SHADOWFAX | Planning only; #993 and #1138 |

### Recovered-protocol core

| File | Description | Status |
|---|---|---|
| [`recovered_protocols/README.md`](./recovered_protocols/README.md) | Intake rules, separation of duties, and runtime boundary warning | Active planning guide; #993 |
| [`recovered_protocols/PROTOCOL_PROMOTION_PLAN.md`](./recovered_protocols/PROTOCOL_PROMOTION_PLAN.md) | Required evidence, gates, tests, rollback, and follow-up sequence | Planning artifact; #993 |
| [`recovered_protocols/recovered_protocol_manifest.json`](./recovered_protocols/recovered_protocol_manifest.json) | Live custody fixture and authoritative wiring-gate list for the recovered lane | `custody_fixture`; all protocol hashes remain `PENDING`; #1148 and #1138 |
| [`recovered_protocols/recovered_protocol_manifest.example.json`](./recovered_protocols/recovered_protocol_manifest.example.json) | Earlier example shape for schema/onboarding comparison | `draft_schema`; not the live manifest |
| [`recovered_protocols/runtime_mapping_design.md`](./recovered_protocols/runtime_mapping_design.md) | Conditional protocol-to-runtime mapping design | Documentation only; no wiring authorization; #1151 |

### Schemas

| File | Description | Status |
|---|---|---|
| [`recovered_protocols/schemas/custody_record.schema.json`](./recovered_protocols/schemas/custody_record.schema.json) | Draft 2020-12 schema for each custody record | Active validation schema; #1149 |
| [`recovered_protocols/schemas/recovered_protocol_manifest.schema.json`](./recovered_protocols/schemas/recovered_protocol_manifest.schema.json) | Schema for the live manifest, wiring gate, and protocol records | Active validation schema; #1149 |
| [`recovered_protocols/schemas/validate_manifest.test.json`](./recovered_protocols/schemas/validate_manifest.test.json) | Machine-readable positive and negative validation cases | Active schema test fixture; #1149 |

### Sanitized fixtures

| File | Description | Status |
|---|---|---|
| [`recovered_protocols/fixtures/README.md`](./recovered_protocols/fixtures/README.md) | Fixture contract and intake rules | Active fixture guide; #1150 |
| [`recovered_protocols/fixtures/sherlock.fixture.json`](./recovered_protocols/fixtures/sherlock.fixture.json) | Sanitized Sherlock reference shape | Example only; custody fields are not verified |
| [`recovered_protocols/fixtures/watson.fixture.json`](./recovered_protocols/fixtures/watson.fixture.json) | Sanitized Watson reference shape | Example only; custody fields are not verified |
| [`recovered_protocols/fixtures/moriarty.fixture.json`](./recovered_protocols/fixtures/moriarty.fixture.json) | Sanitized Moriarty reference shape | Example only; no containment authority |
| [`recovered_protocols/fixtures/tribunal.fixture.json`](./recovered_protocols/fixtures/tribunal.fixture.json) | Sanitized Tribunal reference shape | Example only; no adjudication authority |
| [`recovered_protocols/fixtures/shadowfax.fixture.json`](./recovered_protocols/fixtures/shadowfax.fixture.json) | Sanitized SHADOWFAX reference shape | Example only; standalone bundle remains a hard blocker |

### Test plans

| File | Description | Status |
|---|---|---|
| [`recovered_protocols/tests/moriarty_containment_tests.md`](./recovered_protocols/tests/moriarty_containment_tests.md) | Required recommendation, quarantine, appeal, rollback, and L2-to-L1 boundary cases | Planning artifact; no runtime containment; #1152 |
| [`recovered_protocols/tests/tribunal_appeal_tests.md`](./recovered_protocols/tests/tribunal_appeal_tests.md) | Required appeal-record, evidence, conflict, and reopen cases | Planning artifact; no runtime adjudication; #1153 |

## Promotion path

Recovered or proposed ethics behavior moves through this sequence:

1. **Evaluate and classify** the proposal or recovered artifact; do not call it runtime canon.
2. **Define schemas** and separation-of-duties boundaries.
3. **Verify custody** in the live manifest, including package and internal-file hashes.
4. **Validate sanitized fixtures** against the schemas.
5. **Pass protocol-specific tests**, including containment, appeal, rollback, and layer-boundary cases.
6. **Complete and sign `pentest_scope_v2.md`** when required by the manifest.
7. **Open and approve a scoped implementation issue and PR** for a named runtime adapter.
8. **Wire only the reviewed surface**, preserving existing enforcement authority and rollback paths.

At the current manifest state, step 3 is incomplete for every recovered protocol. SHADOWFAX is additionally blocked on locating and hash-verifying its standalone bundle.

## Related material outside this directory

- [`simulation/CODEX_PHASE1_COMMAND_ETHICS_COMPLETE.md`](../../simulation/CODEX_PHASE1_COMMAND_ETHICS_COMPLETE.md) is a simulation crew/character integration receipt. It remains in `simulation/`; it is not a runtime ethics specification.
- [`docs/archive/philosophy/04_ETHICS_PROTOCOL.md`](../archive/philosophy/04_ETHICS_PROTOCOL.md) is historical conceptual context. Its archive location is preserved.
- [`modules/hr/ETHICS_FRAMEWORK_CONNECTION_AS_CONSTANT.md`](../../modules/hr/ETHICS_FRAMEWORK_CONNECTION_AS_CONSTANT.md) is HR-module-specific material and remains with that module.

No files were moved into `docs/ethics/` by #1139. Cross-links preserve their existing authority and layer boundaries without promoting simulation, module, or archive material.

## Governing issues

| Issue | Scope |
|---|---|
| [#1139](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1139) | This directory index and Picard_Delta_3 location audit |
| [#994](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/994) / [#1137](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1137) | Geometric curvature v2 evaluation and supplemental implementation follow-up |
| [#993](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/993) / [#1138](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1138) | Recovered-protocol promotion plan and unresolved custody verification |
| [#1148](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1148) | Custody manifest fixture |
| [#1149](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1149) | Protocol schemas and validation cases |
| [#1150](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1150) | Sanitized fixtures |
| [#1151](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1151) | Conditional runtime mapping design |
| [#1152](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1152) / [#1153](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1153) | Moriarty containment and Tribunal appeal test plans |
