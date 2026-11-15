# GUMAS Unified — Read-Only Upstream Evidence Adapters (P1)

**Version:** 0.2 | **Date:** 2026-11-14
**Status:** PROPOSED / SYNTHETIC / L2 RESEARCH-ONLY
**Previous specification:** \`GUMAS__SPEC__UNIFIED_CAUSAL_ENGINE__v0.1__2026-11-14.md\`
**No canonical, L1, or upstream PR authority is changed.**

## Purpose

P0 proves a minimal causal field: actor choice, physical availability, information
latency, event ledger and cross-scale reconciled projections. P1 introduces a
bounded, **read-only intake** for two separate unmerged Aurora source branches,
without importing their Python runtime, materializing characters, executing a
tactical macrostep, synchronizing disjoint clocks, or promoting canon.

**Source pins reviewed for this contract:**

| Upstream | Branch | PR/head | Relevant contract |
|---|---|---|---|
| Root / ACE | \`codex/ace-persistent-continuity-20260906\` | #85 / \`7ffb7c94eb8bf539d9b3a5e99ef549bbaaab8c68\` | \`tools/ace/sandbox.py\` World.verify() and World._result() |
| CloudBank / tactical | \`agent/gumas-flash-rebellion-battle-baseline\` | #1506 / \`40b5866dba2d8ac3a0636736dcf069adaa451c8a\` | \`simulation/runtime/gumas_battle_orchestrator/orchestrator.py\` Phase-9 ledger |
| CloudBank / tactical | same | same | \`simulation/receipts/GUMAS__RECEIPT__LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_PHASE9__v1.0__2026-08-15.json\` |

These SHA values are *documentation pins*. Pure adapters accept caller-provided
objects; they do **not** fetch or attest that the caller actually used these
commits. Structural validation and self-contained SHA256 checks must never be
misrepresented as externally authenticated evidence.

## Adapter 1: ACE world-scoped identity (retrieve-only)

Input: a world-status packet and a character-response packet obtained from an
independently approved ACE read tool. Preconditions:

- World status is \`ready\`, \`isolated_aurora_world\`, and explicitly denies
  authority over the canonical workspace.
- Character response is a successful \`operation=retrieve\` with
  \`status=RETRIEVED_CANON\`, same world ID/scope, canonical entity ID consistent
  with returned character ID, determination ID and origin.
- World source pins for root, CanonRec and CloudBank, plus sandbox CanonRec head,
  are nonempty lower-case Git SHA-1 commit identifiers.
- \`create\`, \`preview\`, blocked retrieval, unresolved identities and world
  recovery-pending cases fail closed.
- Projection includes only an ID, name, world scope, origin, provenance pins,
  and non-authoritative flags. Narrated background, absolute filesystem paths,
  materialization metadata and internal receipts are not copied.

**Sandbox \`RETRIEVED_CANON\` is not Aurora source canon.** Inherited and
sandbox-created character identities remain evidence scoped to that isolated
world. Binding one to a synthetic L2 agent needs a separate explicit
identity-mapping contract; none is implemented in P1.

## Adapter 2: tactical Phase-9 immutable ledger

Input: an ordered genesis-to-tail sequence of **caller-supplied** Phase-9
ledger-entry objects. Preconditions:

- Exact \`aurora://simulation/gumas/phase9_ledger_entry/v1.0\` schema and
  \`GUMAS_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_v1_0\` contract.
- Lowercase SHA256 fields and canonical JSON (sorted keys, no NaN).
- Ledger-entry hash is computed over all entry fields except
  \`ledger_entry_sha256\`.
- First entry binds \`GENESIS\` and starts at 0 ms; successive entries advance
  indexes and relative milliseconds without gaps, bind previous entry hash and
  committed Phase-8 next-state hash, and retain the same run/roster identity.
- Any continuation after an outcome other than \`ongoing\` fails closed.
- \`run0_executed=false\`, \`reporter_invoked=false\`; no actor's hidden state,
  tactical inputs or authoritative battle results are imported.

**Important limitation:** Self-consistent hashes do not independently prove
that a runtime was executed or that the source commits match the expected
upstream. For that, independently verify pinned repository source, input hashes
and accepted CI receipts, and eventually perform full controlled replay under
the tactical owners' authorization. P1 explicitly does not do so.

The separate public Phase-9 acceptance receipt can also be summarized through
\`observe_phase9_acceptance\`. Its \`PASS\` is reported as a **recorded
upstream acceptance claim**, not as a newly run battle or a Phase-9 checkpoint.
The historical one-step integration witness is not Run 0; Run 0 remains blocked.

## Operator evidence frame

\`operator_evidence_frame(engine, *projections)\` is a pure, deterministic
review-only packet. It contains the P0 L2 state hash/time and a sorted list of
bounded external projection records. It verifies projection checksums, but:

- does NOT add identities to \`Universe.actors\`;
- does NOT create a \`CausalEngine\` transaction or alter its ledger;
- does NOT deliver observations to any simulated actor;
- does NOT map tactical relative milliseconds onto P0 absolute seconds;
- does NOT infer battle outcomes or political consequences;
- does NOT grant canon promotion, execution, network, persistence or L1 access.

Only an authorized operator can investigate the combined report. The local
L2 kernel remains the only writer of its synthetic in-memory state.

## Tests / reproduction

Run from CloudBank root:

\`\`\`sh
python -m unittest discover -s tests -p 'test_gumas_unified*.py' -v
python -m simulation.runtime.gumas_unified.scenario
\`\`\`

Acceptance includes original P0 tests and P1 negative/positive fixtures:
cross-world identity mismatch, create/preview/recovery rejection,
strict provenance shape, background redaction, input immutability,
one-/two-step ledger linkage, tampered hashes, time gaps, stopped-run
continuations, mistaken Run 0 claims and non-mutating combined context.

All P1 fixtures are synthetic and do not imply CanonRec initialization,
live ACE integration, tactical execution or accepted Run 0.

## Proposed next gate (P2; separate review)

1. Independently verify the source commit and receipt signatures/provenance
   outside the adapter. Do not trust caller-supplied Git pins without a resolved
   approved source.
2. Design an identity binding contract with exact world ID, entity ID,
   actor ID, validity period and origin authority, plus explicit scope
   to an isolated L2 run. Never infer faction/affiliation from character name.
3. Design a physical/time reference transformation between tactical relative ms
   and a specified L2 epoch, with units and allowed causal delays.
4. Only then connect domain-level political action proposals and event
   adjudication, repairing repeat \`CIVIL_WAR_ONSET\` semantics and calibrating
   hazards per elapsed time rather than copying Earth conflict rates.
5. Keep all PRs draft until repository-wide CI, branch protections and
   independent architectural review are complete. No cross-PR merge is implied.

**Safety note:** P1 has no tool to call ACE, execute Phase 9, read private
worlds, access L1, or mutate any canonical source. It is evidence-only.
