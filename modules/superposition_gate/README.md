# Superposition Gate

Combines N independently-evaluated `Verdict` objects into one `CollapsedVerdict`
via a deterministic, hard-veto-first rule, without requiring the evaluators
that produced them to share an implementation, a verdict schema, or call each
other.

## Why this exists

This codebase has (at least) three independently-built ethics/safety
evaluators that never call each other and share no common verdict shape:
a rule-based engine, a continuous-score evaluator with an absolute hard-veto
floor, and a graduated-intervention gate. Rather than consolidating them into
one canonical implementation per concern -- which would discard real, tested
work in whichever system "loses" -- this module lets all applicable
evaluators run concurrently for a given action and normalizes their output
into `Verdict`. `collapse()` is the single, explicit point where they are
combined into a final decision.

## Design choices, and why

- **Lexicographic hard-veto-first combiner, not Dempster-Shafer or subjective
  logic.** Both were considered and rejected for the veto itself: neither
  natively guarantees a veto is un-overridable without an external absorbing
  rule bolted on top, at which point you've just reimplemented the
  lexicographic rule. `collapse()` checks `hard_veto` first, unconditionally,
  before considering anything else. Dempster-Shafer/subjective logic remain
  reasonable options *inside* the non-veto branch if richer fusion of
  soft warn/throttle-level evidence is ever wanted -- that's optional future
  work, not part of the core invariant.
- **"Superposition" is a naming convention, not a claim of quantum-mathematical
  grounding.** Quantum-probability formalisms (Hilbert-space judgment models,
  non-commuting observables) model *sequential* judgment where measuring one
  thing changes what the next measurement sees. This module's evaluators run
  concurrently and don't affect each other -- there's no back-action for that
  formalism to explain. The implementation here is, deliberately, a plain
  deterministic function. The vocabulary is kept because it's consistent with
  this codebase's existing style (entanglement, field curvature, synapse
  formation), not because the math underneath is quantum.
- **The hard-veto invariant is verified three ways**, in increasing order of
  effort and decreasing order of how much of the state space they cover:
  - `tests/modules/test_superposition_gate_invariant_exhaustive.py` --
    brute-force enumeration over all `(severity, hard_veto)` combinations for
    small bounded verdict-list lengths. No extra dependencies; always runs.
  - `tests/modules/test_superposition_gate_invariant_smt.py` -- a bounded-N
    proof via `z3`: asserts the negation of the invariant and confirms the
    solver reports `unsat`. Covers larger N than brute-force enumeration can
    reach in reasonable time, because SMT search scales with formula size,
    not input-space size. Skipped gracefully if `z3-solver` isn't installed.
  - `tests/modules/test_superposition_gate_invariant_properties.py` --
    Hypothesis property-based tests over randomly generated verdict lists,
    including an explicit order-independence check (`collapse()` must not
    depend on list order).

  Tests live under `tests/modules/` rather than `modules/superposition_gate/tests/`
  because the repo's pytest config (`testpaths = ["tests"]` in `pyproject.toml`)
  only discovers tests there -- this matches the existing convention used by
  every other module's tests (e.g. `tests/modules/test_insight_ledger_security.py`).

  Model checking (TLA+-style) was considered and deliberately not used here:
  it's the right tool once a combiner becomes stateful, asynchronous, or
  distributed, and this one is a pure, stateless function.

## Integration status

- **Wired in**: `src/monitoring/ethics_gate.py::check_ethics()` -- the gate
  already live on `modules/quantum_simulator/api.py`'s scenario endpoint --
  now builds a `Verdict` from `EthicsEngine.evaluate_action()`'s violation
  list (via `_violations_to_verdict()`) and makes its raise decision through
  `collapse()` instead of `check_should_block()` directly. With only one
  evaluator wired in, this is behavior-preserving (the raise condition is
  keyed on `collapsed.final == HARD_VETO`, which is driven solely by
  `hard_veto`, matching the original `any(v.blocked for v in violations)`
  exactly) -- the point was to make this call site ready to take a second
  evaluator's `Verdict` without another change at the decision point itself.
- **Not yet wired in**: the Ethics Field's `dimension_evaluators` (including
  `picard_delta_3`) and `EthicsAwareQuantumGate`. Each is a separate,
  independently-reviewable follow-up, same as the first.
- Still not computed: the disagreement metric (ordinal Krippendorff's alpha
  over verdict severities, feeding `src/monitoring/drift_detector.py`). That
  needs at least two live evaluators disagreeing in practice before it's
  meaningful to build.
- Still no FastAPI route of its own -- it's called from other modules'
  decision points, not exposed directly.
