"""
Unit tests for src/utils/persist_redact.py

Covers:
- Email, phone, SSN redaction from flat dict
- Recursive redaction in nested dicts
- Graceful degradation when data_guardian is not importable
- Empty dict edge case
- Non-string scalar values pass through unchanged
- List values are redacted recursively
- context_tag parameter is accepted without error
- redact_list_for_persistence helper
- Original dict is not mutated

Anchor: T1-EDG-001-PERSIST
"""

import importlib
import sys
from typing import Any, Dict
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reimport_module():
    """Force a fresh import of persist_redact (needed after monkeypatching sys.modules)."""
    mod_name = "src.utils.persist_redact"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return importlib.import_module(mod_name)


# ---------------------------------------------------------------------------
# Basic redaction tests (data_guardian available)
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.security
def test_redact_email_in_flat_dict():
    """Email addresses in string values are masked."""
    from src.utils.persist_redact import redact_for_persistence

    data = {"user": "alice@example.com", "action": "login"}
    result = redact_for_persistence(data)

    assert "alice@example.com" not in result["user"], "Email should be redacted"
    assert result["action"] == "login", "Non-PII field should be unchanged"


@pytest.mark.unit
@pytest.mark.security
def test_redact_ssn_in_flat_dict():
    """US Social Security Numbers are masked."""
    from src.utils.persist_redact import redact_for_persistence

    data = {"ssn": "123-45-6789", "category": "medical"}
    result = redact_for_persistence(data)

    assert "123-45-6789" not in result["ssn"], "SSN should be redacted"
    assert result["category"] == "medical"


@pytest.mark.unit
@pytest.mark.security
def test_redact_phone_in_flat_dict():
    """US phone numbers are masked."""
    from src.utils.persist_redact import redact_for_persistence

    data = {"contact": "Call me at 555-867-5309", "priority": "high"}
    result = redact_for_persistence(data)

    assert "555-867-5309" not in result["contact"], "Phone number should be redacted"
    assert result["priority"] == "high"


@pytest.mark.unit
@pytest.mark.security
def test_redact_nested_dict_recursively():
    """PII inside nested dicts is redacted recursively."""
    from src.utils.persist_redact import redact_for_persistence

    data = {
        "outer": "ok",
        "inner": {
            "email": "bob@domain.org",
            "deep": {
                "ssn": "987-65-4321"
            }
        }
    }
    result = redact_for_persistence(data)

    assert "bob@domain.org" not in result["inner"]["email"]
    assert "987-65-4321" not in result["inner"]["deep"]["ssn"]
    assert result["outer"] == "ok"


@pytest.mark.unit
@pytest.mark.security
def test_non_string_values_pass_through_unchanged():
    """Integers, booleans, and None are returned unchanged."""
    from src.utils.persist_redact import redact_for_persistence

    data = {
        "count": 42,
        "active": True,
        "ratio": 3.14,
        "missing": None,
    }
    result = redact_for_persistence(data)

    assert result["count"] == 42
    assert result["active"] is True
    assert result["ratio"] == 3.14
    assert result["missing"] is None


@pytest.mark.unit
@pytest.mark.security
def test_empty_dict_returns_empty_dict():
    """Empty input yields an empty output dict."""
    from src.utils.persist_redact import redact_for_persistence

    result = redact_for_persistence({})
    assert result == {}


@pytest.mark.unit
@pytest.mark.security
def test_original_dict_not_mutated():
    """redact_for_persistence must not mutate the input dict."""
    from src.utils.persist_redact import redact_for_persistence

    data = {"email": "carol@test.com", "score": 99}
    original_email = data["email"]
    redact_for_persistence(data)

    assert data["email"] == original_email, "Input dict should not be mutated"


@pytest.mark.unit
@pytest.mark.security
def test_context_tag_accepted():
    """context_tag keyword argument is accepted without raising."""
    from src.utils.persist_redact import redact_for_persistence

    data = {"note": "no pii here"}
    result = redact_for_persistence(data, context_tag="test-tag-001")
    assert result["note"] == "no pii here"


@pytest.mark.unit
@pytest.mark.security
def test_redact_list_for_persistence():
    """redact_list_for_persistence applies redaction to each item in a list."""
    from src.utils.persist_redact import redact_list_for_persistence

    records = [
        {"email": "dave@example.com", "action": "read"},
        {"note": "clean record", "value": 7},
    ]
    results = redact_list_for_persistence(records, context_tag="batch-001")

    assert "dave@example.com" not in results[0]["email"]
    assert results[0]["action"] == "read"
    assert results[1]["note"] == "clean record"
    assert results[1]["value"] == 7


@pytest.mark.unit
@pytest.mark.security
def test_graceful_degradation_when_data_guardian_unavailable(monkeypatch):
    """When data_guardian is not importable, data is returned unchanged."""
    # Remove any cached import of data_guardian components
    to_remove = [k for k in sys.modules if "data_guardian" in k]
    for key in to_remove:
        monkeypatch.delitem(sys.modules, key, raising=False)

    # Also remove cached persist_redact so it re-executes the import block
    monkeypatch.delitem(sys.modules, "src.utils.persist_redact", raising=False)

    # Patch the data_guardian detection_rules import to raise ImportError
    import builtins
    real_import = builtins.__import__

    def failing_import(name, *args, **kwargs):
        if "data_guardian" in name:
            raise ImportError(f"Simulated missing data_guardian: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", failing_import)

    module = _reimport_module()

    data = {"email": "eve@example.com", "value": 5}
    result = module.redact_for_persistence(data)

    # Without data_guardian the data must come back intact (graceful degradation)
    assert result["email"] == "eve@example.com"
    assert result["value"] == 5


@pytest.mark.unit
@pytest.mark.security
def test_string_list_values_are_redacted():
    """PII in string list items is redacted."""
    from src.utils.persist_redact import redact_for_persistence

    data = {"contacts": ["frank@corp.io", "plain text", "555-321-0987"]}
    result = redact_for_persistence(data)

    assert "frank@corp.io" not in result["contacts"][0]
    assert result["contacts"][1] == "plain text"
    assert "555-321-0987" not in result["contacts"][2]
