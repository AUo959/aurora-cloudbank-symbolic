"""Offline guardrails against AI model catalog drift (#1329).

Background: `claude-3-5-sonnet-20241022` was retired on 2025-10-28 but kept a
`# Verified live` comment while being the only selectable Anthropic entry, so
every Anthropic call 404'd and silently fell back to GPT-4o. A second entry,
`claude-4-5-opus-20250115`, named a release that never existed.

A comment is a *claim*; nothing can falsify it. These tests replace that
convention with checks that can fail. All of them are offline — no API key, no
network — so they run in ordinary CI.
"""

from __future__ import annotations

import re
from datetime import date, datetime

import pytest

from modules.ai_core.unified_ai_interface import (
    AIModel,
    AIProvider,
    UnifiedAIInterface,
)

# How long a verification claim stays trustworthy. Deliberately a hard failure
# rather than a warning: the whole point is that silent rot becomes a red build
# on a predictable cadence. See the fix instructions in the assertion message.
MAX_CLAIM_AGE_DAYS = 90

VALID_SOURCES = {"models-api", "pricing-docs", "manual", "unverified"}

# Current Anthropic identifiers carry no date suffix. `claude-4-5-opus-20250115`
# was mechanically detectable as fabricated at the moment it was written.
ANTHROPIC_DATE_SUFFIXED = re.compile(r"^claude-.*-\d{8}$")

CATALOG = UnifiedAIInterface.CAPABILITIES


def selectable_entries():
    return [(model, cap) for model, cap in CATALOG.items() if cap.available]


def test_catalog_is_not_empty():
    """Guards the rest of this file against silently testing nothing."""
    assert CATALOG, "model catalog is empty"
    assert selectable_entries(), "no selectable models — later assertions would be vacuous"


@pytest.mark.parametrize("model,cap", list(CATALOG.items()), ids=lambda x: getattr(x, "name", ""))
def test_verified_source_is_recognised(model, cap):
    assert cap.verified_source in VALID_SOURCES, (
        f"{model.name} claims verified_source={cap.verified_source!r}; "
        f"expected one of {sorted(VALID_SOURCES)}"
    )


def test_selectable_models_carry_a_dated_claim():
    """A model we will actually route to must say when it was last checked."""
    for model, cap in selectable_entries():
        assert cap.verified_on, (
            f"{model.name} is selectable (available=True) but carries no "
            f"verified_on date. An unverifiable claim is what #1329 removed."
        )
        datetime.strptime(cap.verified_on, "%Y-%m-%d")  # raises if malformed


def test_selectable_models_are_not_marked_unverified():
    """available=True and verified_source='unverified' is a contradiction."""
    for model, cap in selectable_entries():
        assert cap.verified_source != "unverified", (
            f"{model.name} is selectable but its source is 'unverified'. "
            f"Either verify it against the provider catalog or set available=False."
        )


def test_unverified_models_are_not_selectable():
    """The gate that kept the fabricated ID inert must stay closed."""
    for model, cap in CATALOG.items():
        if cap.verified_source == "unverified" or not cap.verified_on:
            assert not cap.available, (
                f"{model.name} has no verification claim but is selectable. "
                f"This is exactly the state that routed live traffic to a "
                f"retired model in #1329."
            )


def test_verification_claims_are_not_stale():
    """Fails on a predictable cadence so rot cannot stay silent.

    If this test is what failed your build: re-check each listed model against
    the provider's catalog, then update `verified_on` (and `verified_source`)
    in modules/ai_core/unified_ai_interface.py. Do not simply bump the date —
    the point is the re-check, and pricing in particular is not covered by any
    API, so it needs a human read of the pricing page.
    """
    today = date.today()
    stale = []
    for model, cap in selectable_entries():
        age = (today - datetime.strptime(cap.verified_on, "%Y-%m-%d").date()).days
        if age > MAX_CLAIM_AGE_DAYS:
            stale.append(f"{model.name} ({cap.model.value}): {age} days old")

    assert not stale, (
        f"Model catalog verification is older than {MAX_CLAIM_AGE_DAYS} days:\n  "
        + "\n  ".join(stale)
        + "\n\nRe-verify against the provider catalog, then update verified_on."
    )


def test_verification_claims_are_not_in_the_future():
    """A future date would silently disable the staleness clock."""
    today = date.today()
    for model, cap in CATALOG.items():
        if not cap.verified_on:
            continue
        claimed = datetime.strptime(cap.verified_on, "%Y-%m-%d").date()
        assert claimed <= today, f"{model.name} claims a verified_on in the future: {cap.verified_on}"


@pytest.mark.parametrize("model", list(AIModel), ids=lambda m: m.name)
def test_anthropic_ids_carry_no_date_suffix(model):
    """Eliminates the fabricated-ID class permanently.

    Current Anthropic model IDs are complete without a date suffix. Anything
    matching `claude-<...>-YYYYMMDD` is either legacy or invented; neither
    belongs in this catalog.
    """
    cap = CATALOG.get(model)
    if cap is not None and cap.provider is not AIProvider.ANTHROPIC:
        return
    if not model.value.startswith("claude-"):
        return
    assert not ANTHROPIC_DATE_SUFFIXED.match(model.value), (
        f"{model.name} = {model.value!r} carries a date suffix. Current "
        f"Anthropic identifiers take none; this shape is how "
        f"'claude-4-5-opus-20250115' was fabricated (#1329)."
    )


def test_format_rule_would_have_caught_the_known_bad_ids():
    """Non-vacuity: the rule must reject the two identifiers that caused #1329."""
    assert ANTHROPIC_DATE_SUFFIXED.match("claude-3-5-sonnet-20241022")
    assert ANTHROPIC_DATE_SUFFIXED.match("claude-4-5-opus-20250115")
    # ...and must accept the current, correct ones.
    assert not ANTHROPIC_DATE_SUFFIXED.match("claude-opus-5")
    assert not ANTHROPIC_DATE_SUFFIXED.match("claude-sonnet-5")
