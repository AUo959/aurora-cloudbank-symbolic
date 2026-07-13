"""
Property-based tests for collapse(), using Hypothesis to generate random and
edge-case verdict lists rather than only hand-picked examples. Skips
gracefully if hypothesis isn't installed.

Complements test_invariant_exhaustive.py (bounded brute force) and
test_invariant_smt.py (bounded SMT proof) with randomized coverage over a
wider variety of scores, source names, and list lengths than either of those
two exhaustively enumerate.
"""

import pytest

pytest.importorskip("hypothesis")
from hypothesis import given, settings, strategies as st  # noqa: E402

from modules.superposition_gate import Verdict, VerdictSeverity, collapse  # noqa: E402
from modules.superposition_gate.core import EmptyVerdictSetError  # noqa: E402

_severities = st.sampled_from(list(VerdictSeverity))


@st.composite
def _verdict_lists(draw, min_size: int = 1, max_size: int = 10):
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    return [
        Verdict(
            source=f"evaluator_{i}",
            severity=draw(_severities),
            score=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)),
            hard_veto=draw(st.booleans()),
        )
        for i in range(n)
    ]


@pytest.mark.unit
@settings(max_examples=200)
@given(_verdict_lists())
def test_any_hard_veto_forces_hard_veto_final(verdict_list):
    result = collapse(verdict_list)
    if any(v.hard_veto for v in verdict_list):
        assert result.final == VerdictSeverity.HARD_VETO
    else:
        assert result.final == max(v.severity for v in verdict_list)


@pytest.mark.unit
@given(_verdict_lists(), st.data())
@settings(max_examples=200)
def test_collapse_is_order_independent(verdict_list, data):
    # Hypothesis's own permutation strategy, not the stdlib `random` module --
    # keeps shuffling reproducible under Hypothesis's example database/seed
    # instead of reaching for a PRNG that security scanners flag as
    # unsuitable for anything beyond this kind of non-security test shuffling.
    shuffled = list(data.draw(st.permutations(verdict_list)))
    assert collapse(verdict_list).final == collapse(shuffled).final
    assert collapse(verdict_list).blocked == collapse(shuffled).blocked


@pytest.mark.unit
@settings(max_examples=200)
@given(_verdict_lists())
def test_all_input_verdicts_are_preserved(verdict_list):
    result = collapse(verdict_list)
    assert result.all_verdicts == tuple(verdict_list)


@pytest.mark.unit
def test_collapse_rejects_empty_list():
    with pytest.raises(EmptyVerdictSetError):
        collapse([])
