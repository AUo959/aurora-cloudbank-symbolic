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
    storage_path = tmp_path / "audit_log.jsonl"
    audit_logger = AuditLogger(storage_path=storage_path, signing_key="test-audit-signing-key")

    audit_logger.log_manual_override(
        agent_id="test-agent",
        operator="test-operator",
        action="approve",
        justification="security regression coverage",
    )

    persisted_entries = [
        json.loads(line)
        for line in storage_path.read_text(encoding="utf-8").splitlines()
    ]
    checks.assertEqual(audit_logger._next_id, 2)
    checks.assertEqual(len(persisted_entries), 1)
    persisted = persisted_entries[0]
    checks.assertNotIn("signing_key", persisted)
    checks.assertEqual(persisted["id"], "AUDIT-00000001")


def test_audit_logger_appends_jsonl_entries(tmp_path):
    """Audit writes append one JSON object per line and reload cleanly."""
    checks = unittest.TestCase()
    storage_path = tmp_path / "audit_log.jsonl"
    audit_logger = AuditLogger(storage_path=storage_path, signing_key="test-audit-signing-key")

    audit_logger.log_manual_override(
        agent_id="test-agent",
        operator="test-operator",
        action="approve",
        justification="first entry",
    )
    first_line = storage_path.read_text(encoding="utf-8").splitlines()[0]

    audit_logger.log_manual_override(
        agent_id="test-agent",
        operator="test-operator",
        action="deny",
        justification="second entry",
    )
    lines = storage_path.read_text(encoding="utf-8").splitlines()

    checks.assertEqual(lines[0], first_line)
    checks.assertEqual(len(lines), 2)
    checks.assertEqual(json.loads(lines[1])["previous_hash"], audit_logger.entries[0].compute_hash())

    reloaded = AuditLogger(storage_path=storage_path, signing_key="test-audit-signing-key")
    checks.assertEqual(len(reloaded.entries), 2)
    checks.assertEqual(reloaded._next_id, 3)
    checks.assertTrue(reloaded.verify_chain())


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
