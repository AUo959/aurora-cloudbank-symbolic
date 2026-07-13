"""Focused tests for the unified config-backed ethics engine."""

from __future__ import annotations

import json
import asyncio
import importlib.util
import sys
import types
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pytest

from ethics.audit_log import EthicsAuditLog
from ethics.engine import BLOCKED, REVIEW, EthicsEngine


def _engine(tmp_path):
    return EthicsEngine(
        audit_log=EthicsAuditLog(
            path=tmp_path / "ethics_audit.jsonl",
            cryptographic_signing=True,
            blockchain_anchoring=True,
        )
    )


@pytest.mark.parametrize(
    ("rule_id", "signals", "expected_verdict"),
    [
        (
            "ME001",
            {"risk_to_life": 0.2, "safety_protocols_incomplete": True},
            BLOCKED,
        ),
        (
            "ME002",
            {"consent_missing": True, "insufficient_information": True},
            BLOCKED,
        ),
        (
            "ME003",
            {"environmental_impact": 0.4, "threshold": 0.3, "no_mitigation_plan": True},
            REVIEW,
        ),
        (
            "RE001",
            {"inequality_coefficient": 0.8, "minority_exclusion": True},
            REVIEW,
        ),
        (
            "RE002",
            {"depletion_rate": 0.9, "renewal_rate": 0.1, "irreversible_damage": True},
            BLOCKED,
        ),
        (
            "AI001",
            {"decision_opacity": 0.35, "no_explanation_available": True},
            REVIEW,
        ),
        (
            "AI002",
            {"autonomous_critical_decision": True, "human_override": False},
            BLOCKED,
        ),
    ],
    ids=["ME001", "ME002", "ME003", "RE001", "RE002", "AI001", "AI002"],
)
def test_unified_engine_implements_each_config_rule(tmp_path, rule_id, signals, expected_verdict):
    engine = _engine(tmp_path)

    result = engine.validate(
        context="ai_operations",
        signals=signals,
        anchor="T1-ETHICS-ENGINE-001",
        agent_id="AI_AURORA",
    )

    assert result.verdict == expected_verdict
    assert [rule.rule_id for rule in result.triggered_rules] == [rule_id]
    assert result.audit_id
    assert result.audit_entry["signature"] == result.audit_entry["payload_hash"]
    assert result.audit_entry["blockchain_anchor_status"] == "todo_external_integration"


def test_unified_engine_approved_result_does_not_emit_audit(tmp_path):
    audit_path = tmp_path / "ethics_audit.jsonl"
    engine = _engine(tmp_path)

    result = engine.validate(
        context="mission_operations",
        signals={"risk_to_life": 0.0, "human_override": True},
        anchor="T1-ETHICS-ENGINE-001",
        agent_id="AI_AURORA",
    )

    assert result.verdict == "APPROVED"
    assert result.audit_id is None
    assert not audit_path.exists()


def test_issue_1070_ai001_sample_triggers_review_from_opacity(tmp_path):
    engine = _engine(tmp_path)

    result = engine.validate(
        context="ai_operations",
        signals={
            "decision_opacity": 0.35,
            "no_human_override": False,
            "autonomous_critical_decision": False,
        },
        anchor="T1-SENTINEL-001",
        agent_id="AI_AURORA",
    )

    assert result.verdict == REVIEW
    assert [rule.rule_id for rule in result.triggered_rules] == ["AI001"]
    assert result.audit_id


def test_audit_log_writes_signed_jsonl_entry(tmp_path):
    audit_path = tmp_path / "ethics_audit.jsonl"
    engine = _engine(tmp_path)

    result = engine.validate(
        context="ai_operations",
        signals={"decision_opacity": 0.4, "no_explanation_available": True},
        anchor="T1-ETHICS-ENGINE-001",
        agent_id="AI_AURORA",
    )

    rows = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["audit_id"] == result.audit_id
    assert len(rows[0]["signature"]) == 64
    assert rows[0]["triggered_rules"] == ["AI001"]


def test_sentinel_stream_3_overlay_uses_unified_engine(tmp_path):
    from src.sensors.observatory.symbolic.ethical_signal import Action, EthicalSignalSentinel

    sentinel = EthicalSignalSentinel(ethics_engine=_engine(tmp_path))

    sentinel.evaluate_action(
        "AI_AURORA",
        Action(
            "inference_decision",
            params={"decision_opacity": 0.35, "no_explanation_available": True},
        ),
    )

    violation = sentinel.action_history["AI_AURORA"][0]["violations"][0]
    assert violation["rule_id"] == "AI001"
    assert violation["verdict"] == REVIEW
    assert violation["audit_id"].startswith("AUDIT-")


def test_nemo_symbolic_bridge_exposes_engine_verdict(tmp_path):
    from services.nemo_service.symbolic_bridge import SymbolicBridge

    bridge = SymbolicBridge(ethics_engine=_engine(tmp_path))

    anchor_context = bridge.resolve_anchor_context("llm")
    assert anchor_context["ethics"]["verdict"] == "APPROVED"

    blocked = bridge.validate_ethics_context(
        "llm",
        signals={"autonomous_critical_decision": True, "human_override": False},
        agent_id="AI_AURORA",
    )
    assert blocked["verdict"] == BLOCKED
    assert blocked["triggered_rules"][0]["rule_id"] == "AI002"


def test_gumas_ethics_check_delegates_to_unified_engine(tmp_path, monkeypatch):
    class _ViolationSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    class _RuleCategory(Enum):
        AI_ETHICS = "ai_ethics"

    @dataclass
    class _ActionContext:
        agent_id: str
        action_type: str
        parameters: dict
        context_tag: str | None = None

    @dataclass
    class _EthicsRule:
        id: str
        name: str
        description: str
        category: _RuleCategory
        severity: _ViolationSeverity
        auto_block: bool
        conditions: list
        metadata: dict | None = None

    class _LegacyEthicsEngine:
        def __init__(self, *args, **kwargs):
            self.rules = {}
            self.violations = []

        def evaluate_action(self, context):
            return []

        def check_should_block(self, violations):
            return False

        def get_violations(self, *args, **kwargs):
            return []

        def add_rule(self, rule):
            self.rules[rule.id] = rule

        def remove_rule(self, rule_id):
            self.rules.pop(rule_id, None)

        def clear_violations(self, *args, **kwargs):
            self.violations.clear()

    legacy_module = types.ModuleType("src.monitoring.ethics_engine")
    legacy_module.EthicsEngine = _LegacyEthicsEngine
    legacy_module.ActionContext = _ActionContext
    legacy_module.EthicsRule = _EthicsRule
    legacy_module.ViolationSeverity = _ViolationSeverity
    legacy_module.RuleCategory = _RuleCategory
    monitoring_package = types.ModuleType("src.monitoring")
    monkeypatch.setitem(sys.modules, "src.monitoring", monitoring_package)
    monkeypatch.setitem(sys.modules, "src.monitoring.ethics_engine", legacy_module)
    middleware_package = types.ModuleType("src.middleware")
    fastapi_security_module = types.ModuleType("src.middleware.fastapi_security")

    def _require_csrf_token():
        return True

    fastapi_security_module.require_csrf_token = _require_csrf_token
    monkeypatch.setitem(sys.modules, "src.middleware", middleware_package)
    monkeypatch.setitem(sys.modules, "src.middleware.fastapi_security", fastapi_security_module)

    spec = importlib.util.spec_from_file_location(
        "_test_gumas_routes", Path("modules/gumas/api/routes.py")
    )
    routes = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(routes)

    monkeypatch.setattr(routes, "unified_ethics_engine", _engine(tmp_path))

    async def _call_route():
        return await routes.unified_ethics_check(
            routes.UnifiedEthicsCheckRequest(
                context="gumas_ethics_check",
                signals={"autonomous_critical_decision": True, "human_override": False},
                anchor="T1-ETHICS-ENGINE-001",
                agent_id="AI_AURORA",
            )
        )

    response = asyncio.run(_call_route())

    assert response.verdict == BLOCKED
    assert response.blocked is True
    assert response.triggered_rules[0]["rule_id"] == "AI002"
