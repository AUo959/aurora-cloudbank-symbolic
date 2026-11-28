# GUMAS Unified — P6 Validation and Maintainability Contract

**Artifact:** `GUMAS__SPEC__UNIFIED_CAUSAL_ENGINE__v0.8__2026-11-23`  
**Version:** 0.8  
**Date:** 2026-11-23  
**Status:** DRAFT / SYNTHETIC L2 ONLY / RESEARCH  
**Supersedes:** `GUMAS__SPEC__UNIFIED_CAUSAL_ENGINE__v0.7__2026-11-16.md`  
**Provenance:** remediation PR #1712, stacked on P6 #1710, then P5 #1706.

## Purpose

P6 established non-territorial, two-member association formation through
delivered reciprocal consent and mandate-specific resource custody.
This revision refactors the verification and dispatch API without expanding
the simulation's authority or changing any social or physical law.

## Typed proposal contract

`MandateRequest` is now an immutable, P6-scoped value object with exactly:

- `cargo_route_id: str`
- `notice_route_id: str`
- `commodity: str`
- `amount: int`
- `expires_s: int`

Call `CausalEngine.propose_mandate(association_id, proposer_id, request,
cause=...)` with that object; the P6 package exports `MandateRequest`.
Direct dictionaries and unknown types are rejected atomically. Validation
of commodity, quantity, source custody, expiry, directed communications,
energy, route capacity and consent still occurs on the P0 copy-commit path.
Changing the mutable outer world cannot mutate the request object.

The earlier P6 prototype used nine parameters across the kernel and
`federated_actions.py`. That P6-only *draft* API has changed; no
production callers, existing P3/P4/P5 message shapes or canonical API
were migrated or called. A future owner-approved integration must
target the explicitly versioned request signature.

## Isolated verification units

The P6 validators are decomposed into named checks for:

1. Charter actor identity, physical directed notice, status, explicitly
   sent intent, actual delivered decision, and terminal formation.
2. Association proof of reciprocal foundation, physical confirmation
   transmission, and remote member knowledge.
3. Mandate participants and material custody, typed terms, delivery
   and actual receipt of the remote vote, authorization and expiry.
4. Fully separate shipment departure, cargo metadata, timing, in-flight
   records and P0 scheduled arrival.
5. Named scheduled-event receipt checks for charter, mandate and
   association confirmation.

The top-level `validate_federated_world` still executes these
checks in the same logical order before committing a new P0 state.
Refactoring the functions does **not** waive any predicate or promote
an operator's knowledge into an actor's private state.

The charter and mandate scheduler event handlers now delegate their
specific side effects (offer arrival, response receipt, expiry) to
small named functions. Existing event `kind`, `effect`, scheduled
arrival, status and hash logic remain unchanged for the same
synthetic source history.

## Regression and authority boundaries

Reproduce the scoped acceptance suite:

```sh
python -m unittest discover -s tests -p 'test_gumas_unified*.py' -v
python -m simulation.runtime.gumas_unified.scenario
python -m simulation.runtime.gumas_unified.political_scenario
python -m simulation.runtime.gumas_unified.governance_scenario
python -m simulation.runtime.gumas_unified.distributed_scenario
python -m simulation.runtime.gumas_unified.federated_scenario
```

This revision adds three typed-API tests and one parameterized
malformed-input regression covering seven invalid numeric/time fields.
Each mutation must raise a controlled validation error rather than
silently authorizing state or surfacing an unintended Python TypeError. All prior 175 tests must remain passing; accepted total
**179 tests**. The fixed baseline P0 state digest must match its
historical SHA256 fixture.

This is an isolated synthetic L2 specification. It does not create
L1 crew authority, L3 promotion, CanonRec writes, authenticated
ACE identity or tactical Run 0 permission. The original P0 kernel's
receipt-linked deterministic event ownership and physics remain.

## Audit history and quality gates

Original P6's one High ErrorProne issue was a Pyflakes F401
unused import, corrected on commit `b34ee452`; this rewrite
is not a substitute for that correction. Historic P6 audit
files v1.0, v1.1, and v1.2 received **whitespace-only** lint
normalization (table separators, a doubled blank line, and a final
newline). Their prior byte states remain recoverable from Git history;
no recorded audit conclusions or source evidence changed.

The Codacy zero-new-issues gate and complementary root/CloudBank
source review must both be satisfied for any merge. Report Codacy
findings against the **entire P6+remediation change compared with
P5**, not only the narrow #1712 diff against #1710. A passing
synthetic regression run is not a substitute for that review.
