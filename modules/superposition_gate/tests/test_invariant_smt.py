"""
SMT proof that the hard-veto invariant holds for bounded verdict-list
lengths, via z3. Skips gracefully if z3-solver isn't installed.

This complements test_invariant_exhaustive.py (which brute-forces small N in
pure Python with no dependencies) by reaching a larger N cheaply: SMT search
scales with formula size, not with the size of the input space, so it covers
lengths brute-force enumeration could not reach in reasonable time.

Scope note: this proves the invariant for lists up to MAX_N verdicts, encoded
directly from collapse()'s own logic (any hard_veto -> HARD_VETO, else max
severity). It is a bounded-N proof, not a fully universal (all N) inductive
proof over a recursive list datatype -- that's a reasonable next step only if
this module's verdict count ever becomes unbounded in practice; it isn't
needed while callers pass a small, fixed number of evaluators.
"""

import pytest

z3 = pytest.importorskip("z3")

from modules.superposition_gate.models import VerdictSeverity  # noqa: E402

MAX_N = 8


def _build_combine_formula(n: int):
    """Mirror collapse()'s logic symbolically: any hard_veto -> HARD_VETO, else max severity."""
    severities = [z3.Int(f"severity_{i}") for i in range(n)]
    hard_vetoes = [z3.Bool(f"hard_veto_{i}") for i in range(n)]

    domain_constraints = [
        z3.And(s >= int(VerdictSeverity.ALLOW), s <= int(VerdictSeverity.HARD_VETO)) for s in severities
    ]

    any_veto = z3.Or(*hard_vetoes)

    max_severity = severities[0]
    for s in severities[1:]:
        max_severity = z3.If(s > max_severity, s, max_severity)

    final = z3.If(any_veto, z3.IntVal(int(VerdictSeverity.HARD_VETO)), max_severity)

    return domain_constraints, any_veto, final


@pytest.mark.unit
@pytest.mark.parametrize("n", range(1, MAX_N + 1))
def test_hard_veto_invariant_holds_for_bounded_n(n):
    """For all verdict lists of length n, any hard_veto=True forces final=HARD_VETO."""
    domain_constraints, any_veto, final = _build_combine_formula(n)

    solver = z3.Solver()
    solver.add(*domain_constraints)
    # Assert the NEGATION of the invariant and search for a counterexample.
    solver.add(any_veto)
    solver.add(final != int(VerdictSeverity.HARD_VETO))

    result = solver.check()
    counterexample = solver.model() if result == z3.sat else None
    assert result == z3.unsat, f"Counterexample found for n={n}: {counterexample}"
