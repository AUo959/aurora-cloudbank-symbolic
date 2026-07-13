"""
Superposition Gate - Collapse Function

Combines N independent Verdicts into one CollapsedVerdict using a
lexicographic, hard-veto-first rule: any Verdict with hard_veto=True is
unconditionally binding, regardless of what any other evaluator reports.
Among non-veto verdicts, the most severe ordinal level wins.

This function is intentionally a pure, stateless, order-independent
combinator. It does not call any source evaluator and has no knowledge of
GUMAS, the Ethics Field, or any specific quantum backend -- callers own that
integration. See README.md in this directory for the design rationale
(why a lexicographic rule instead of Dempster-Shafer/subjective logic, and
why this is deliberately not modeled on quantum-probability formalisms).

The hard-veto invariant this function must satisfy is:

    for all non-empty verdict lists V,
    if any v in V has v.hard_veto == True,
    then collapse(V).final == VerdictSeverity.HARD_VETO

That invariant is checked three ways in tests/modules/test_superposition_gate_*.py:
exhaustive enumeration over small bounded verdict-list lengths (no extra
dependencies), a bounded-N SMT proof via z3 (skipped if z3 isn't installed),
and Hypothesis property-based tests over randomly generated verdict lists.

DLP: context_tag=superposition_gate_core, symbolic_hash=SUPERPOSITION_GATE_v1
"""

from typing import Iterable

from .models import CollapsedVerdict, Verdict, VerdictSeverity


class EmptyVerdictSetError(ValueError):
    """Raised when collapse() is called with no verdicts to combine."""


def collapse(verdicts: Iterable[Verdict]) -> CollapsedVerdict:
    """Combine independent Verdicts into one CollapsedVerdict.

    Args:
        verdicts: Independent judgments from any number of evaluators, in any
            order or iterable form (list, tuple, generator, ...). Order must
            not affect the result -- see
            tests/modules/test_superposition_gate_invariant_properties.py::test_collapse_is_order_independent.

    Returns:
        CollapsedVerdict carrying the final severity and the verdict that
        bound the decision. Note that `binding_verdict.severity` is the
        vetoing evaluator's own reported severity, which is not required to
        equal `HARD_VETO` -- an evaluator may report a low general severity
        while still setting `hard_veto=True` on one specific judgment. Only
        `final` (and `blocked`) is the authoritative collapsed decision;
        don't assume `binding_verdict.severity == final`.

    Raises:
        EmptyVerdictSetError: if verdicts is empty. There is no safe default
            outcome for zero evaluators -- callers must supply at least one.
    """
    # Snapshot once, before the emptiness check: guards against a caller
    # mutating a mutable input sequence mid-call, avoids iterating the input
    # multiple times below, and ensures the emptiness check below is correct
    # for any iterable -- a generator has no __len__ and is always truthy
    # regardless of whether it yields anything, so `not verdicts` on a raw
    # generator would never be True even when empty. Checking before
    # snapshotting would silently skip the check and let max() raise a
    # different, undocumented error instead of EmptyVerdictSetError.
    verdicts = tuple(verdicts)

    if not verdicts:
        raise EmptyVerdictSetError("collapse() requires at least one Verdict")

    # Tie-break keys cover every field, not just (score, source): if two
    # verdicts somehow shared just those two (e.g. a caller bug emitting
    # duplicate verdicts for one evaluator), stopping the key there would let
    # min()/max() return whichever duplicate came first in the input,
    # making binding_verdict order-dependent even though `final` stays
    # stable. `context_tag` is Optional, so it's normalized to "" for
    # ordering purposes (None isn't orderable against str).
    hard_vetoes = [v for v in verdicts if v.hard_veto]
    if hard_vetoes:
        # Lowest score is the most concerning veto; remaining fields are a
        # final deterministic tie-break so the result never depends on list
        # order, only on the verdicts' own field values.
        binding = min(hard_vetoes, key=lambda v: (v.score, v.source, v.reason, v.context_tag or ""))
        return CollapsedVerdict(
            final=VerdictSeverity.HARD_VETO,
            binding_verdict=binding,
            all_verdicts=verdicts,
        )

    # No hard veto: the most severe ordinal verdict wins; ties broken by
    # lowest score (more concerning), then by the remaining fields for full
    # determinism.
    binding = max(verdicts, key=lambda v: (v.severity, -v.score, v.source, v.reason, v.context_tag or ""))
    return CollapsedVerdict(
        final=binding.severity,
        binding_verdict=binding,
        all_verdicts=verdicts,
    )
