import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.resilience_sentinel import api as sentinel_api
from modules.resilience_sentinel.alert_manager import Alert, AlertManager, AlertRule, AlertSeverity
from src.middleware.fastapi_security import generate_csrf_token


def _auth_headers() -> dict[str, str]:
    token = generate_csrf_token("sentinel-test-session")
    return {"Authorization": f"Bearer {token}"}


class _FakeSentinelEngine:
    def __init__(self):
        self.alert_manager = AlertManager()
        self.alert_manager.alerts.append(
            Alert(
                id="alert-1",
                severity=AlertSeverity.WARNING,
                title="CPU warning",
                message="CPU crossed test threshold",
                metric_name="cpu.percent",
                metric_value=91.0,
                threshold=90.0,
            )
        )
        self.alert_manager.add_rule(
            AlertRule(
                name="existing-rule",
                metric_name="cpu.percent",
                condition=">",
                threshold=90.0,
                severity=AlertSeverity.WARNING,
                message_template="CPU {value} above {threshold}",
            )
        )

    def add_alert_rule(self, rule: AlertRule):
        self.alert_manager.add_rule(rule)


def _build_client(monkeypatch):
    engine = _FakeSentinelEngine()
    monkeypatch.setattr(sentinel_api, "get_monitoring_engine", lambda: engine)
    app = FastAPI()
    app.include_router(sentinel_api.router)
    return TestClient(app), engine


def _new_rule_payload() -> dict[str, object]:
    return {
        "name": "new-rule",
        "metric_name": "memory.percent",
        "condition": ">",
        "threshold": 80.0,
        "severity": "warning",
        "message_template": "Memory {value} above {threshold}",
    }


def test_acknowledge_alert_requires_auth_before_mutation(monkeypatch):
    checks = unittest.TestCase()
    client, engine = _build_client(monkeypatch)

    response = client.post(
        "/sentinel/alerts/acknowledge",
        json={"alert_id": "alert-1"},
    )

    checks.assertIn(response.status_code, (401, 403))
    checks.assertFalse(engine.alert_manager.alerts[0].acknowledged)


def test_acknowledge_alert_accepts_valid_auth_token(monkeypatch):
    checks = unittest.TestCase()
    client, engine = _build_client(monkeypatch)

    response = client.post(
        "/sentinel/alerts/acknowledge",
        json={"alert_id": "alert-1"},
        headers=_auth_headers(),
    )

    checks.assertEqual(response.status_code, 200)
    checks.assertTrue(engine.alert_manager.alerts[0].acknowledged)


def test_resolve_alert_requires_auth_before_mutation(monkeypatch):
    checks = unittest.TestCase()
    client, engine = _build_client(monkeypatch)

    response = client.post(
        "/sentinel/alerts/resolve",
        json={"alert_id": "alert-1"},
    )

    checks.assertIn(response.status_code, (401, 403))
    checks.assertFalse(engine.alert_manager.alerts[0].resolved)


def test_resolve_alert_accepts_valid_auth_token(monkeypatch):
    checks = unittest.TestCase()
    client, engine = _build_client(monkeypatch)

    response = client.post(
        "/sentinel/alerts/resolve",
        json={"alert_id": "alert-1"},
        headers=_auth_headers(),
    )

    checks.assertEqual(response.status_code, 200)
    checks.assertTrue(engine.alert_manager.alerts[0].resolved)


def test_create_alert_rule_requires_auth_before_mutation(monkeypatch):
    checks = unittest.TestCase()
    client, engine = _build_client(monkeypatch)

    response = client.post(
        "/sentinel/alerts/rules",
        json=_new_rule_payload(),
    )

    checks.assertIn(response.status_code, (401, 403))
    checks.assertIsNone(engine.alert_manager.get_rule("new-rule"))


def test_create_alert_rule_accepts_valid_auth_token(monkeypatch):
    checks = unittest.TestCase()
    client, engine = _build_client(monkeypatch)

    response = client.post(
        "/sentinel/alerts/rules",
        json=_new_rule_payload(),
        headers=_auth_headers(),
    )

    checks.assertEqual(response.status_code, 200)
    checks.assertIsNotNone(engine.alert_manager.get_rule("new-rule"))


def test_delete_alert_rule_requires_auth_before_mutation(monkeypatch):
    checks = unittest.TestCase()
    client, engine = _build_client(monkeypatch)

    response = client.delete("/sentinel/alerts/rules/existing-rule")

    checks.assertIn(response.status_code, (401, 403))
    checks.assertIsNotNone(engine.alert_manager.get_rule("existing-rule"))


def test_delete_alert_rule_accepts_valid_auth_token(monkeypatch):
    checks = unittest.TestCase()
    client, engine = _build_client(monkeypatch)

    response = client.delete(
        "/sentinel/alerts/rules/existing-rule",
        headers=_auth_headers(),
    )

    checks.assertEqual(response.status_code, 200)
    checks.assertIsNone(engine.alert_manager.get_rule("existing-rule"))
