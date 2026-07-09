"""Unit tests for modules.superposition_gate.core.collapse()."""

import pytest

from modules.superposition_gate import CollapsedVerdict, Verdict, VerdictSeverity, collapse
from modules.superposition_gate.core import EmptyVerdictSetError


def _v(source: str, severity: VerdictSeverity, score: float = 0.5, hard_veto: bool = False) -> Verdict:
    return Verdict(source=source, severity=severity, score=score, hard_veto=hard_veto)


@pytest.mark.unit
def test_single_allow_verdict():
    result = collapse([_v("rule_engine", VerdictSeverity.ALLOW)])
    assert result.final == VerdictSeverity.ALLOW
    assert not result.blocked


@pytest.mark.unit
def test_hard_veto_overrides_lower_severity_verdicts():
    verdicts = [
        _v("rule_engine", VerdictSeverity.ALLOW, score=0.9),
        _v("gate_intervention", VerdictSeverity.WARN, score=0.7),
        _v("ethics_field_hard_veto", VerdictSeverity.HARD_VETO, score=0.2, hard_veto=True),
    ]
    result = collapse(verdicts)
    assert result.final == VerdictSeverity.HARD_VETO
    assert result.blocked
    assert result.binding_verdict.source == "ethics_field_hard_veto"


@pytest.mark.unit
def test_hard_veto_overrides_even_when_others_strongly_disagree():
    # A hard veto must win even if every other evaluator says ALLOW with high confidence.
    verdicts = [_v(f"evaluator_{i}", VerdictSeverity.ALLOW, score=0.99) for i in range(5)]
    verdicts.append(_v("hard_veto_source", VerdictSeverity.HARD_VETO, score=0.01, hard_veto=True))
    result = collapse(verdicts)
    assert result.final == VerdictSeverity.HARD_VETO
    assert result.binding_verdict.source == "hard_veto_source"


@pytest.mark.unit
def test_most_severe_non_veto_verdict_wins():
    verdicts = [
        _v("rule_engine", VerdictSeverity.ALLOW),
        _v("gate_intervention", VerdictSeverity.THROTTLE),
        _v("other", VerdictSeverity.WARN),
    ]
    result = collapse(verdicts)
    assert result.final == VerdictSeverity.THROTTLE
    assert result.binding_verdict.source == "gate_intervention"


@pytest.mark.unit
def test_multiple_hard_vetoes_binds_to_lowest_score():
    verdicts = [
        _v("veto_a", VerdictSeverity.HARD_VETO, score=0.4, hard_veto=True),
        _v("veto_b", VerdictSeverity.HARD_VETO, score=0.1, hard_veto=True),
    ]
    result = collapse(verdicts)
    assert result.final == VerdictSeverity.HARD_VETO
    assert result.binding_verdict.source == "veto_b"


@pytest.mark.unit
def test_empty_verdict_list_raises():
    with pytest.raises(EmptyVerdictSetError):
        collapse([])


@pytest.mark.unit
def test_empty_generator_raises_empty_verdict_set_error():
    # A generator has no __len__/__bool__, so `not verdicts` on the raw
    # generator would never be True even when it yields nothing. collapse()
    # must snapshot to a tuple before checking emptiness, or this raises a
    # raw ValueError from max() instead of the documented EmptyVerdictSetError.
    with pytest.raises(EmptyVerdictSetError):
        collapse(v for v in [])


@pytest.mark.unit
def test_all_verdicts_preserved_in_result():
    verdicts = [_v("a", VerdictSeverity.ALLOW), _v("b", VerdictSeverity.WARN)]
    result = collapse(verdicts)
    assert result.all_verdicts == tuple(verdicts)


@pytest.mark.unit
def test_collapsed_verdict_is_frozen():
    result = collapse([_v("a", VerdictSeverity.ALLOW)])
    assert isinstance(result, CollapsedVerdict)
    with pytest.raises(Exception):
        result.final = VerdictSeverity.BLOCK  # type: ignore[misc]
