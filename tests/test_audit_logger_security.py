"""
Security regression tests for the audit logger signing key.
"""

import json
import unittest

import pytest

from src.monitoring.audit_logger import AuditLogger


def test_audit_logger_requires_startup_signing_key(monkeypatch):
    """Audit logging must not silently generate a runtime-only signing key."""
    monkeypatch.delenv("MONITORING_SIGNING_KEY", raising=False)

    with pytest.raises(ValueError, match="MONITORING_SIGNING_KEY environment variable must be set"):
        AuditLogger()


def test_audit_logger_does_not_persist_signing_key(tmp_path):
    """The audit storage file must never contain the HMAC signing key."""
    checks = unittest.TestCase()
    storage_path = tmp_path / "audit_log.json"
    audit_logger = AuditLogger(storage_path=storage_path, signing_key="test-audit-signing-key")

    audit_logger.log_manual_override(
        agent_id="test-agent",
        operator="test-operator",
        action="approve",
        justification="security regression coverage",
    )

    persisted = json.loads(storage_path.read_text())
    checks.assertNotIn("signing_key", persisted)
    checks.assertEqual(persisted["next_id"], 2)
    checks.assertEqual(len(persisted["entries"]), 1)


def test_audit_logger_ignores_legacy_persisted_signing_key(tmp_path, monkeypatch):
    """Legacy storage keys must not override the startup signing key."""
    checks = unittest.TestCase()
    storage_path = tmp_path / "audit_log.json"
    storage_path.write_text(
        json.dumps(
            {
                "entries": [],
                "signing_key": "legacy-persisted-key",
                "next_id": 7,
            }
        )
    )
    monkeypatch.setenv("MONITORING_SIGNING_KEY", "env-signing-key")

    audit_logger = AuditLogger(storage_path=storage_path)

    checks.assertEqual(audit_logger.signing_key, "env-signing-key")
    checks.assertEqual(audit_logger._next_id, 7)
