# GUMAS Deterministic Factual Reporter and Evidence Export Contract

**Contract ID:** `GUMAS_DETERMINISTIC_FACTUAL_REPORTER_EVIDENCE_EXPORT_v1_0`  
**Version:** `1.0.0`  
**Date:** `2026-08-15`  
**Status:** normative Phase-10 implementation contract  
**Scenario admission:** accepted Phase-9 artifacts for `GUMAS_FLASH_REBELLION_P17_EQUAL_FLEETS`  
**Historical canon status:** `non_canon_simulation_instance`

## 1. Purpose

Phase 10 converts already committed and validated Phase-9 artifacts into:

1. a normalized machine-readable factual event stream;
2. a statement-to-artifact evidence index;
3. a deterministic fixed-template human-readable report;
4. an exporter receipt binding the input ledger head and every output hash.

The reporter is not a simulator, observer, commander, adjudicator, narrator, canon authority, or LLM. It is a pure projection. It cannot execute a macrostep, request a macrostep, mutate state, reinterpret a Phase-8 outcome, or feed any result back into the transition path.

This contract exists to make accepted simulation truth usable as reproducible evaluation and training material without allowing presentation code to become state authority.

## 2. Authority order

The reporter consumes authority in this order:

1. a caller-supplied accepted `run_identity_sha256` trust anchor;
2. a caller-supplied accepted Phase-9 ledger-head SHA-256 trust anchor;
3. the self-hashed Phase-9 run context;
4. an ordered, gap-free Phase-9 artifact sequence beginning at genesis;
5. the source hashes and cross-artifact links embedded in each accepted artifact;
6. this reporter's fixed projection vocabulary and templates.

The reporter's own output is evidence about accepted artifacts. It is never authority over those artifacts.

## 3. Layer and canon boundary

- The reporter operates at the L2 simulation evidence boundary.
- It does not read or mutate CanonRec.
- CanonRec-derived values may appear only when already present in an accepted artifact field.
- `historical_canon_status` is always copied as `non_canon_simulation_instance`.
- `run0_executed` is copied from the ledger and must be `false` for Phase-10 acceptance.
- No report or export promotes simulation output into canon.
- Public release policy is distinct from simulation truth and cannot change the truth export.

## 4. Pure-projection prohibition

Authoritative Phase-10 modules must not import or call:

- `simulation.runtime.gumas_battle_orchestrator.orchestrator`;
- `execute_macrostep`;
- any Phase-4 through Phase-9 transition function;
- `simulation.runtime.gumas_acceptance_fixture`;
- network, wall-clock, environment, subprocess, random, secrets, LLM, or text-generation authority.

The separate real-source smoke may use the acceptance fixture and may produce exactly one already-authorized one-step witness for reporting tests. The authoritative reporter must receive the resulting artifact packet as data and must not execute the step itself.

## 5. Canonical encoding and hashes

All machine-readable identities use UTF-8 JSON with:

- mapping keys sorted lexicographically;
- separators `,` and `:` with no optional whitespace;
- Unicode emitted directly;
- non-finite numbers rejected;
- no floating-point values;
- arrays retained in their contract-defined order.

The profile identifier is `aurora-canonical-json-v1`.

`sha256_canonical(value)` is SHA-256 over those canonical bytes.

For any object containing its own hash field, `hash_without_field(object, field)` hashes the complete object after removing only that field.

Rendered text is UTF-8, uses `\n` line endings, contains no trailing spaces, and ends with exactly one newline. `rendered_report_sha256` is SHA-256 over those exact bytes.

## 6. Versioned schemas

Phase 10 defines these identifiers:

| Object | Schema |
|---|---|
| input packet | `aurora://simulation/gumas/phase10_report_input/v1.0` |
| macrostep artifact packet | `aurora://simulation/gumas/phase10_macrostep_artifacts/v1.0` |
| normalized factual report | `aurora://simulation/gumas/phase10_normalized_factual_report/v1.0` |
| factual event | `aurora://simulation/gumas/phase10_factual_event/v1.0` |
| evidence index | `aurora://simulation/gumas/phase10_evidence_index/v1.0` |
| rendered report envelope | `aurora://simulation/gumas/phase10_rendered_report/v1.0` |
| exporter receipt | `aurora://simulation/gumas/phase10_export_receipt/v1.0` |

Unknown, partial, or extra top-level fields in input packet and macrostep artifact packets are rejected. Projection output has a closed, versioned shape.

## 7. Input packet

The authoritative entry point accepts one mapping with exactly:

```json
{
  "schema": "aurora://simulation/gumas/phase10_report_input/v1.0",
  "expected_run_identity_sha256": "...",
  "expected_ledger_head_sha256": "...",
  "run_context": {},
  "macrosteps": []
}
```

`macrosteps` must be a non-empty ordered array containing the complete accepted sequence from macrostep `1` through the anchored ledger head.

Each macrostep packet has exactly:

```json
{
  "schema": "aurora://simulation/gumas/phase10_macrostep_artifacts/v1.0",
  "ledger_entry": {},
  "observation_receipts_by_side": {},
  "decisions_by_fleet": {},
  "movement_receipt": {},
  "phase6_receipt": {},
  "phase7_receipt": {},
  "phase8_resolution_state": {},
  "phase8_receipt": {}
}
```

No raw prior, intermediate, enemy-private, or committed vessel-state object is accepted. The reporter may only project fields deliberately committed into receipts, resolution state, run context, and the Phase-9 ledger.

## 8. Mandatory input validation

Validation occurs before projection and fails closed.

### 8.1 Run context

The reporter must prove:

- schema is the Phase-9 run-context v1.0 schema;
- `run_identity_sha256` recomputes exactly;
- `run_identity_sha256` equals the caller trust anchor;
- `historical_canon_status = non_canon_simulation_instance`;
- canonical JSON profile is accepted;
- roster records are complete, unique, and sorted by `ship_id` after normalization;
- `t0_roster_sha256` equals the hash of those normalized records;
- accepted Phase-4 through Phase-9 source identities exist;
- the two-side frozen roster partitions are non-empty.

### 8.2 Ledger chain

For sequence position `n`, the reporter must prove:

- `macrostep_index = n`;
- every ledger-entry hash recomputes exactly;
- macrostep 1 has `previous_ledger_entry_sha256 = GENESIS`;
- later entries point to the immediately prior entry hash;
- start/end elapsed times are non-negative and strictly advance;
- each later `start_elapsed_ms` equals the prior `end_elapsed_ms`;
- each later `previous_committed_state_sha256` equals the prior `phase8_next_state_sha256`;
- run identity, roster identity, Phase-9 contract/version, canonical profile, canon status, and accepted source identities are constant;
- `reporter_invoked = false` in the transition ledger;
- `run0_executed = false` for the Phase-10 acceptance witness;
- the last entry hash equals `expected_ledger_head_sha256`.

A reordering, gap, duplicate, fork, truncated sequence, or previous-hash mutation fails.

### 8.3 Artifact hashes and cross-links

For every macrostep the reporter recomputes and validates:

- each live-observation receipt and its embedded observation hash;
- each command decision receipt;
- movement receipt;
- Phase-6 receipt;
- each Phase-7 target-damage receipt and the Phase-7 receipt;
- Phase-8 resolution state;
- Phase-8 receipt;
- Phase-9 ledger entry.

It then proves the ledger's maps and hashes equal the supplied artifacts and proves the state chain:

```text
ledger.previous_committed_state_sha256
  = movement.prior_state_sha256

movement.next_state_sha256
  = phase6.prior_state_sha256
  = ledger.phase5_state_sha256

phase6.next_state_sha256
  = phase7.prior_state_sha256
  = ledger.phase6_state_sha256

phase7.next_state_sha256
  = phase8.prior_state_sha256
  = ledger.phase7_state_sha256

phase8.next_state_sha256
  = ledger.phase8_next_state_sha256
```

Receipt hashes, resolution hash, observation hashes, observation-receipt hashes, and decision hashes must equal their ledger references. Phase-8 terminal outcome must be byte-for-byte equivalent in the resolution state, Phase-8 receipt, and ledger entry.

No caller may repair, normalize, or rehash a mutated input inside the reporter.

## 9. Projection profiles

Two fixed profiles exist and are never inferred:

### 9.1 `simulation_truth_v1`

The normalized factual event stream contains the complete allowed receipt projection described in section 10. It may include stable ship, side, and fleet identifiers because those identifiers are already committed simulation facts.

### 9.2 `public_summary_v1`

The public profile is a deterministic whitelist projection derived from the already-built `simulation_truth_v1` report. It may contain:

- run and ledger identities;
- macrostep/time boundaries;
- aggregate counts;
- collision and withdrawal-boundary counts;
- side-level resolution aggregates;
- Phase-8 terminal outcome verbatim;
- evidence hashes.

It excludes per-vessel vectors, weapon-attempt details, per-target damage values, command-team numeric inputs, and contact evidence. Redaction removes fields; it never replaces them with guesses or prose.

The truth report hash remains present in the public exporter receipt, so publication filtering cannot masquerade as simulation truth.

## 10. Fixed factual vocabulary

Every normalized event has:

```json
{
  "schema": "aurora://simulation/gumas/phase10_factual_event/v1.0",
  "event_id": "m00000001:p05:0001:movement_vessel:SHIP",
  "macrostep_index": 1,
  "phase": "phase5",
  "sequence": 1,
  "fact_type": "movement_vessel",
  "fact_basis": "committed_field",
  "subject_id": "SHIP",
  "object_id": null,
  "fields": {},
  "evidence_ref_ids": []
}
```

Event IDs are fixed-format, contain no wall-clock value, and are unique within a report. `sequence` is a one-based global sequence within each macrostep after sorting by the ordering rules below.

Allowed fact types and sources are:

| Fact type | Phase | Source | Basis |
|---|---|---|---|
| `macrostep_boundary` | phase9 | ledger entry | committed field |
| `command_order` | phase4 | decision receipt `orders` | committed field |
| `movement_vessel` | phase5 | movement `per_vessel` | committed field |
| `movement_aggregate` | phase5 | fixed counts over `per_vessel` | deterministic aggregation |
| `sensor_contact` | phase6 | `contacts` | committed field |
| `target_selection` | phase6 | `selections` | committed field |
| `weapon_attempt` | phase6 | `weapon_attempts` | committed field |
| `delivered_effect` | phase6 | `effect_descriptors` | committed field |
| `sensing_fire_aggregate` | phase6 | fixed list counts | deterministic aggregation |
| `target_damage` | phase7 | `target_damage_receipts` | committed field |
| `damage_aggregate` | phase7 | fixed receipt counts | deterministic aggregation |
| `side_resolution` | phase8 | resolution side maps | committed field |
| `terminal_outcome` | phase8 | `terminal_outcome` | verbatim committed field |

No free-form event type, motive, dialogue, tactical explanation, winner label, moral judgment, causal speculation, or canon claim is allowed.

## 11. Event ordering

For each macrostep, events are ordered by:

1. `macrostep_boundary`;
2. `command_order`, sorted by `fleet_id`;
3. `movement_vessel`, sorted by `ship_id`;
4. `movement_aggregate`;
5. `sensor_contact`, sorted by `(observer_ship_id, target_ship_id)`;
6. `target_selection`, sorted by `shooter_ship_id`;
7. `weapon_attempt`, sorted by `(shooter_ship_id, target_ship_id or "")`;
8. `delivered_effect`, sorted by `effect_id`;
9. `sensing_fire_aggregate`;
10. `target_damage`, sorted by `target_ship_id`;
11. `damage_aggregate`;
12. `side_resolution`, sorted by `side_id`;
13. `terminal_outcome`.

Input mapping insertion order and semantically unordered receipt-array order are inert. The reporter validates receipt hashes first, then orders copies for projection without altering the input artifact identity.

## 12. Evidence references and index

Every event field must be justified by at least one evidence reference. Each reference has:

```json
{
  "evidence_ref_id": "m00000001:movement_receipt:/per_vessel/0",
  "macrostep_index": 1,
  "artifact_kind": "movement_receipt",
  "artifact_sha256": "...",
  "json_pointers": ["/per_vessel/0"],
  "ledger_entry_sha256": "..."
}
```

JSON pointers are RFC-6901 escaped. References are sorted by `evidence_ref_id` and deduplicated by exact canonical value.

The evidence index contains:

- all evidence-reference records;
- `event_to_evidence_ref_ids` for every normalized event;
- `rendered_statement_to_event_ids` for every factual rendered line;
- `evidence_index_sha256` over the closed object without that field.

Header and separator lines are structural, not factual statements, and are explicitly listed as such by the renderer. Every line containing a factual value maps to one or more event IDs.

## 13. Normalized report

The normalized report contains exactly:

- schema, contract ID, reporter version, canonical profile;
- reporter source identity;
- selected profile ID;
- historical canon status;
- `run0_executed`;
- run identity and T0 roster hash;
- macrostep count;
- first and final elapsed milliseconds;
- ledger head SHA-256;
- ordered factual events;
- `normalized_report_sha256`.

`simulation_truth_v1` is always built first. `public_summary_v1` is then projected from that immutable normalized truth object. The exporter receipt binds both hashes when public output is selected.

## 14. Fixed rendered report

The human-readable report is generated from a fixed English vocabulary and these line classes only:

```text
GUMAS FACTUAL REPORT v1
profile=<PROFILE> canon_status=non_canon_simulation_instance run0_executed=false
run=<RUN_SHA> roster=<ROSTER_SHA> ledger_head=<LEDGER_SHA>
macrosteps=<N> elapsed_ms=<START>..<END>

STEP <INDEX> elapsed_ms=<START>..<END> ledger=<LEDGER_SHA>
COMMAND side=<SIDE> fleet=<FLEET> posture=<POSTURE> intents=<ROLE=VALUE,...>
MOVEMENT vessels=<N> collisions=<N> boundary_crossings=<N>
SENSING contacts=<N> selections=<N> attempts=<N> effects=<N>
DAMAGE effects=<N> targets=<N>
RESOLUTION side=<SIDE> combat_capable=<N> degraded=<N> disabled=<N> destroyed=<N> morale_q1000=<N> cohesion_q1000=<N>
TERMINAL terminated=<true|false> mode=<PHASE8_VALUE> fields=<CANONICAL_JSON>
```

The renderer may omit a line only when the selected profile prohibits that line class. It may not paraphrase, add adjectives, infer a winner, choose a protagonist, introduce dialogue, or use a locale-sensitive format.

The `TERMINAL` line copies the complete Phase-8 terminal-outcome mapping as canonical JSON. It does not rename or reinterpret any field.

## 15. Exporter receipt

The receipt contains exactly:

- schema, contract ID, version, canonical profile;
- reporter source identity;
- profile ID;
- historical canon status and `run0_executed`;
- accepted run identity, T0 roster hash, and input ledger head;
- `report_input_sha256`;
- truth normalized-report hash;
- selected normalized-report hash;
- evidence-index hash;
- rendered-report hash;
- macrostep/event/rendered-statement counts;
- `transition_execution_imported = false`;
- `transition_execution_called = false`;
- `report_feedback_applied = false`;
- `wall_clock_used = false`;
- `network_used = false`;
- `llm_used = false`;
- `ambient_rng_used = false`;
- `export_receipt_sha256`.

The receipt contains no generated timestamp. Publication time belongs to a separate external delivery receipt and cannot affect report identity.

## 16. Determinism and mutation isolation

For identical accepted input bytes and profile ID, the reporter must regenerate byte-identical:

- normalized truth report;
- selected normalized report;
- evidence index;
- rendered report;
- exporter receipt.

Changing one committed factual field under a new, internally consistent test fixture may alter only:

1. the event(s) that project that field;
2. their evidence references and dependent indexes;
3. fixed aggregates that mathematically depend on the field;
4. the corresponding rendered line(s);
5. dependent output hashes and receipt.

It must not alter unrelated event content or order.

## 17. Terminal semantics

- Phase 8 is the sole termination authority.
- The reporter copies `terminal_outcome` verbatim.
- `terminated=false` is reported as ongoing only because the accepted Phase-8 field says so.
- A terminal entry must be the final ledger entry.
- A non-final terminal entry is rejected.
- The reporter never creates `winner`, `loser`, `victory`, or `defeat` unless a future Phase-8 contract adds one of those exact fields.

## 18. Required acceptance tests

Phase 10 is not accepted until tests prove:

1. exact replay and mapping-order invariance;
2. every event has valid evidence references and every factual rendered line maps to events;
3. input field mutation without the accepted trust anchor fails closed;
4. ledger reordering, gap, duplicate, fork, truncation, and previous-hash mutation fail closed;
5. run-context, receipt, nested target-damage, resolution, and ledger hash mutation fail closed;
6. cross-phase state/hash mismatch fails closed;
7. hidden raw state cannot be supplied or projected;
8. terminal outcome is copied byte-for-byte and never re-decided;
9. insertion order is inert and deterministic sorting is exact;
10. source identity covers every authoritative reporter module;
11. no transition, fixture, random, network, wall-clock, subprocess, environment, or LLM import exists in authoritative modules;
12. `simulation_truth_v1` and `public_summary_v1` have distinct deterministic field surfaces;
13. a local factual fixture mutation changes only the corresponding projection and dependent hashes;
14. a real pinned-CanonRec one-step smoke reports an already produced Phase-9 witness, replays byte-identically, and does not execute a second step;
15. focused and repository-wide CI pass on the same implementation head.

## 19. Phase-10 acceptance witness boundary

The real-source smoke may construct one Phase-9 witness using the existing separately scoped Phase-9 smoke path. It then serializes the minimum Phase-10 input packet and invokes the reporter twice on that immutable packet.

Acceptance requires:

- macrostep count `1`;
- prior ledger marker `GENESIS`;
- `historical_canon_status = non_canon_simulation_instance`;
- `run0_executed = false`;
- exact report replay;
- no second `execute_macrostep` call;
- no reporter import in the Phase-9 transition path;
- no report value used as a transition input.

This one-step witness is integration evidence only. It is not Run 0, a battle outcome, a control result, or authorization to continue the battle.

## 20. Stop conditions

Stop rather than improvise if reporting would require:

- an unvalidated or floating artifact;
- raw hidden state outside the closed input packet;
- another macrostep;
- reporter feedback into state;
- a narrative decision;
- a winner reinterpretation;
- class, polity, faction, side-name, or prose special casing;
- an LLM or network call;
- wall clock, locale, environment, or ambient randomness;
- canon promotion;
- Run-0 execution.

## 21. Admission consequence

Acceptance of this contract authorizes implementation and validation of the pure Phase-10 reporter only. It does not admit Control A/B/C, Phase 11, or Run 0.

**Run 0 remains blocked. No battle result is claimed.**
