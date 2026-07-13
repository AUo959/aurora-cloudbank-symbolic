"""
Exhaustive proof (bounded N) that collapse()'s hard-veto invariant holds:

    for all non-empty verdict lists V,
    if any v in V has v.hard_veto == True,
    then collapse(V).final == VerdictSeverity.HARD_VETO

This brute-forces every (severity, hard_veto) combination for verdict lists
of length 1..MAX_N. Score is held constant across generated verdicts because
the invariant does not depend on score -- only on severity and hard_veto --
so varying it would only inflate the search space without testing anything
new. No extra dependencies; this always runs.

See test_invariant_smt.py for a bounded-N proof that reaches larger N via an
SMT solver instead of brute force, and test_invariant_properties.py for
randomized property-based coverage.
"""

import itertools

import pytest

from modules.superposition_gate import Verdict, VerdictSeverity, collapse

MAX_N = 4  # 10 possible (severity, hard_veto) pairs per slot; 10**4 = 10,000 combinations at the deepest level.


def _all_verdict_combinations(n: int):
    """Yield every combination of (severity, hard_veto) assignments for n verdicts."""
    per_slot_options = list(itertools.product(list(VerdictSeverity), [False, True]))
    for assignment in itertools.product(per_slot_options, repeat=n):
        yield [
            Verdict(source=f"evaluator_{i}", severity=severity, score=0.5, hard_veto=hard_veto)
            for i, (severity, hard_veto) in enumerate(assignment)
        ]


@pytest.mark.unit
@pytest.mark.parametrize("n", range(1, MAX_N + 1))
def test_hard_veto_invariant_exhaustive(n):
    checked = 0
    for verdicts in _all_verdict_combinations(n):
        result = collapse(verdicts)
        checked += 1
        if any(v.hard_veto for v in verdicts):
            assert (
                result.final == VerdictSeverity.HARD_VETO
            ), f"Invariant violated for n={n}: {[(v.severity, v.hard_veto) for v in verdicts]}"
        else:
            assert result.final == max(v.severity for v in verdicts)
    assert checked == 10**n
