"""Tests for the model catalog validator's comparison logic (#1329).

The live API path needs ANTHROPIC_API_KEY and is not exercised here. The
comparison logic is a pure function precisely so it can be tested offline —
that is the part which decides pass or fail, and it is the part that would have
caught the retired `claude-3-5-sonnet-20241022`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_model_catalog import anthropic_entries, compare_entry, main  # noqa: E402

from modules.ai_core.unified_ai_interface import AIModel, UnifiedAIInterface  # noqa: E402


def test_unresolvable_model_is_a_finding():
    """The #1329 defect: a retired identifier must fail, not pass quietly."""
    findings = compare_entry("claude-3-5-sonnet-20241022", 200_000, 8192, None)
    assert len(findings) == 1
    assert findings[0].kind == "unresolvable"
    assert "retired" in findings[0].detail


def test_matching_entry_produces_no_findings():
    findings = compare_entry(
        "claude-opus-5", 1_000_000, 128_000,
        {"max_input_tokens": 1_000_000, "max_tokens": 128_000},
    )
    assert findings == []


def test_context_window_drift_is_caught():
    findings = compare_entry(
        "claude-opus-5", 200_000, 128_000,
        {"max_input_tokens": 1_000_000, "max_tokens": 128_000},
    )
    assert [f.kind for f in findings] == ["context_window"]
    assert "200,000" in findings[0].detail, "message should quote the catalog value"
    assert "1,000,000" in findings[0].detail, "message should quote the provider value"


def test_max_output_drift_is_caught():
    findings = compare_entry(
        "claude-opus-5", 1_000_000, 8192,
        {"max_input_tokens": 1_000_000, "max_tokens": 128_000},
    )
    assert [f.kind for f in findings] == ["max_output_tokens"]


def test_both_drifts_reported_together():
    findings = compare_entry(
        "claude-opus-5", 1, 2,
        {"max_input_tokens": 1_000_000, "max_tokens": 128_000},
    )
    assert {f.kind for f in findings} == {"context_window", "max_output_tokens"}


def test_absent_remote_fields_are_not_treated_as_mismatch():
    """OpenAI-shaped records carry no capability data; absence is not drift."""
    findings = compare_entry(
        "some-model", 1_000_000, 128_000, {"max_input_tokens": None, "max_tokens": None}
    )
    assert findings == []


def test_missing_api_key_fails_closed(monkeypatch, capsys):
    """A live validator that cannot run must not produce a green check."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert main() == 2
    err = capsys.readouterr().err
    assert "ERROR" in err
    assert "could not be checked" in err


def test_missing_anthropic_dependency_fails_closed(monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-only-not-a-real-key")
    monkeypatch.setitem(sys.modules, "anthropic", None)

    assert main() == 2
    assert "not installed" in capsys.readouterr().err


def test_disabled_available_entry_still_gets_live_validation(monkeypatch):
    """Routing policy must not hide a provider-existence claim from validation."""
    cap = UnifiedAIInterface.CAPABILITIES[AIModel.CLAUDE_OPUS_5]
    monkeypatch.setattr(cap, "enabled", False)

    assert cap.available
    assert cap in anthropic_entries()
