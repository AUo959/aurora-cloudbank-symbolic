"""Regression coverage for the public-review CodeQL backlog."""

from __future__ import annotations

import json
import logging
import time

import pytest


def test_improvement_engine_logs_do_not_expose_request_data(tmp_path, caplog) -> None:
    """Analysis failures retain an error class without logging request-derived data."""

    from src.improvement.engine import (
        CodeImprovementEngine,
        ImprovementCategory,
        ImprovementPattern,
        ImprovementSeverity,
    )

    class FailingPattern(ImprovementPattern):
        def __init__(self) -> None:
            super().__init__(
                "customer-secret-pattern",
                ImprovementCategory.SECURITY,
                ImprovementSeverity.HIGH,
            )

        def detect(self, file_path, content):
            raise RuntimeError("customer-secret-pattern-detail")

    engine = CodeImprovementEngine()
    engine.register_pattern(FailingPattern())
    secret_directory = tmp_path / "customer-secret-directory"
    secret_directory.mkdir()
    secret_file = secret_directory / "customer-secret-file.py"
    secret_file.write_text("max_items = 9999\n")

    with caplog.at_level(logging.INFO, logger="src.improvement.engine"):
        engine.analyze_file(tmp_path / "missing-customer-secret-file.py")
        engine.analyze_file(secret_file)
        engine.analyze_directory(secret_directory)

    messages = "\n".join(record.getMessage() for record in caplog.records)
    assert "customer-secret" not in messages  # nosec B101 - pytest assertion
    assert "FileNotFoundError" in messages  # nosec B101 - pytest assertion
    assert "RuntimeError" in messages  # nosec B101 - pytest assertion


def test_personnel_attention_tag_rejection_is_linear_for_long_input() -> None:
    """A rejected, attacker-controlled terminal id must not trigger regex backtracking."""

    from src.mesh.terminals import is_personnel_attention_tag

    adversarial_terminal_id = "{{@" + ("z:::" * 20_000) + "!"
    started = time.perf_counter()
    assert is_personnel_attention_tag(adversarial_terminal_id) is False  # nosec B101 - pytest assertion
    elapsed = time.perf_counter() - started

    assert elapsed < 0.2  # nosec B101 - pytest assertion


@pytest.mark.asyncio
async def test_opal2_health_response_hides_probe_exception(monkeypatch, caplog) -> None:
    """Opal2 health output exposes status, not internal exception details."""

    from modules.opal2.api import opal2_api

    async def healthy_probe():
        return {"healthy": True}

    def failing_registry_probe():
        raise RuntimeError("opal2-customer-secret")

    monkeypatch.setattr(opal2_api, "test_glyph_core", healthy_probe)
    monkeypatch.setattr(opal2_api, "test_quantum_renderer", healthy_probe)
    monkeypatch.setattr(opal2_api, "test_plugin_system", healthy_probe)
    monkeypatch.setattr(opal2_api, "test_cache_system", healthy_probe)
    monkeypatch.setattr(
        opal2_api.tool_registry, "list_manifests", failing_registry_probe
    )

    with caplog.at_level(logging.ERROR, logger=opal2_api.__name__):
        result = await opal2_api.health_check()

    assert result["components"]["tool_registry"] == {  # nosec B101 - pytest assertion
        "healthy": False,
        "error": "internal error",
    }
    assert "opal2-customer-secret" not in json.dumps(result)  # nosec B101 - pytest assertion
    assert "opal2-customer-secret" not in caplog.text  # nosec B101 - pytest assertion
    assert "RuntimeError" in caplog.text  # nosec B101 - pytest assertion


def test_cloudhub_health_response_hides_config_exception(monkeypatch, caplog) -> None:
    """CloudHub health failures return a stable public error contract."""

    from api import aurora_gui_cloudhub_fastapi as cloudhub

    def failing_config_load():
        raise RuntimeError("cloudhub-customer-secret")

    monkeypatch.setattr(cloudhub, "get_mcp_bridge_core", failing_config_load)

    with caplog.at_level(logging.ERROR, logger=cloudhub.__name__):
        response = cloudhub.mcp_bridge_health_check()

    payload = json.loads(response.body)
    assert payload["status"] == "unhealthy"  # nosec B101 - pytest assertion
    assert payload["error"] == "internal error"  # nosec B101 - pytest assertion
    assert "cloudhub-customer-secret" not in response.body.decode()  # nosec B101 - pytest assertion
    assert "cloudhub-customer-secret" not in caplog.text  # nosec B101 - pytest assertion
    assert "RuntimeError" in caplog.text  # nosec B101 - pytest assertion


@pytest.mark.asyncio
async def test_aumem_health_response_hides_metrics_exception(
    monkeypatch, caplog
) -> None:
    """AuMemManager health failures do not reflect exception messages."""

    from modules.aumemmanager import api_integration

    def failing_metrics_load():
        raise RuntimeError("aumem-customer-secret")

    monkeypatch.setattr(
        api_integration.memory_manager, "get_metrics", failing_metrics_load
    )

    with caplog.at_level(logging.ERROR, logger=api_integration.__name__):
        result = await api_integration.health_check()

    assert result["status"] == "unhealthy"  # nosec B101 - pytest assertion
    assert result["error"] == "internal error"  # nosec B101 - pytest assertion
    assert "aumem-customer-secret" not in json.dumps(result)  # nosec B101 - pytest assertion
    assert "aumem-customer-secret" not in caplog.text  # nosec B101 - pytest assertion
    assert "RuntimeError" in caplog.text  # nosec B101 - pytest assertion
