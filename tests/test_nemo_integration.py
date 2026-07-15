"""
Tests for the NEMO ↔ Aurora integration (issue #1061).

Covers all four integration points' happy paths AND their graceful
fallbacks — the issue's cross-cutting requirement is that every call site
degrades cleanly when the NEMO pod is unavailable:

 1. MCPCommandRouter NEMO_GENERATE routing (+ NEMO_CAPSULE_004, + the
    frozen 3-capsule legacy contract staying intact)
 2. qf_create_agent NLU intent helper
 3. oppy_plan_maneuver ASR transcription helper
 4. HR narrative helper

NEMO is never contacted: httpx.MockTransport plays the service, including
its "model not loaded" mock payloads, which must also count as fallback
(they carry no usable intent/transcript).
"""

import os

import httpx
import pytest

from tests._slowapi_stub import install_slowapi_stub

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-nemo-integration")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-nemo-integration")
install_slowapi_stub()

from services.nemo_service.client import NemoClient  # noqa: E402
from modules.symbolic_core import mcp_command_router as router_mod  # noqa: E402
from modules.symbolic_core.mcp_command_router import MCPCommandRouter  # noqa: E402


# ---------------------------------------------------------------------------
# Mock NEMO transports
# ---------------------------------------------------------------------------

def _healthy_nemo_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/nemo/generate":
            return httpx.Response(200, json={
                "generated_text": "NEMO says hello",
                "tokens_generated": 4,
                "anchor_context": {"anchor_seed": "EOS_SEED_ORION", "t1_counter": 7},
                "entropy": 0.1,
                "latency_ms": 12.5,
            })
        if request.url.path == "/nemo/infer":
            body = request.read().decode()
            if '"nlu"' in body:
                result = {"intent": ["deploy_navigation_agent"]}
            else:
                result = {"transcript": ["orbital transfer burn"]}
            return httpx.Response(200, json={
                "result": result,
                "model_type": "nlu" if '"nlu"' in body else "asr",
                "anchor_context": {"anchor_seed": "EOS_SEED_ORION"},
                "drift_flagged": False,
                "latency_ms": 8.0,
            })
        return httpx.Response(404)
    return httpx.MockTransport(handler)


def _down_nemo_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)
    return httpx.MockTransport(handler)


def _model_not_loaded_transport() -> httpx.MockTransport:
    """NEMO answers, but with its own mock payload (no usable fields)."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "result": {"mock": True, "message": "NeMo model not loaded"},
            "model_type": "nlu",
            "anchor_context": {},
            "drift_flagged": False,
            "latency_ms": 1.0,
        })
    return httpx.MockTransport(handler)


@pytest.fixture()
def healthy_client():
    client = NemoClient(transport=_healthy_nemo_transport())
    yield client
    client.close()


@pytest.fixture()
def down_client():
    client = NemoClient(transport=_down_nemo_transport())
    yield client
    client.close()


# ---------------------------------------------------------------------------
# NemoClient contract
# ---------------------------------------------------------------------------

def test_client_generate_success(healthy_client):
    response = healthy_client.generate("hello", context={"anchor": "X"})
    assert response["generated_text"] == "NEMO says hello"
    assert response["anchor_context"]["anchor_seed"] == "EOS_SEED_ORION"


def test_client_returns_none_on_any_failure(down_client):
    assert down_client.generate("hello") is None
    assert down_client.infer(model_type="nlu", text="hello") is None


# ---------------------------------------------------------------------------
# Integration point 1: MCPCommandRouter NEMO_GENERATE
# ---------------------------------------------------------------------------

def test_router_routes_nemo_generate_and_merges_anchor_context(
    monkeypatch, healthy_client
):
    monkeypatch.setattr(router_mod, "get_nemo_client", lambda: healthy_client)
    monkeypatch.setattr(router_mod, "NEMO_CLIENT_AVAILABLE", True)

    router = MCPCommandRouter()
    result = router.route("NEMO_GENERATE plot a course home", anchor="EOS_SEED_ORION")

    assert result["status"] == "ROUTED"
    assert result["nemo"]["status"] == "OK"
    assert result["nemo"]["generated_text"] == "NEMO says hello"
    # Merged anchor context carries both services' lineage
    merged = result["anchor_context"]
    assert merged["cloudhub"]["anchor"] == "EOS_SEED_ORION"
    assert merged["cloudhub"]["capsule_id"] == "NEMO_CAPSULE_004"
    assert merged["nemo"]["anchor_seed"] == "EOS_SEED_ORION"


def test_router_nemo_fallback_when_service_down(monkeypatch, down_client):
    monkeypatch.setattr(router_mod, "get_nemo_client", lambda: down_client)
    monkeypatch.setattr(router_mod, "NEMO_CLIENT_AVAILABLE", True)

    router = MCPCommandRouter()
    result = router.route("NEMO_GENERATE anyone home?", anchor="EOS_SEED_ORION")

    assert result["status"] == "ROUTED"
    assert result["nemo"]["status"] == "FALLBACK"
    assert result["nemo"]["mock"] is True
    assert "anyone home?" in result["nemo"]["generated_text"]


def test_router_non_nemo_commands_unchanged(monkeypatch, down_client):
    """Legacy routing contract untouched: no nemo key, capsule_count == 3."""
    monkeypatch.setattr(router_mod, "get_nemo_client", lambda: down_client)

    router = MCPCommandRouter()
    result = router.route("SYNC_THREADCORE")

    assert result["status"] == "ROUTED"
    assert "nemo" not in result
    assert result["capsule_count"] == 3
    assert len(result["registered_capsules"]) == 3


def test_nemo_capsule_registered_but_not_in_legacy_alias_list():
    router = MCPCommandRouter()
    info = router.get_capsule_info("NEMO_CAPSULE_004")
    assert info["status"] == "ACTIVE"
    assert info["module"] == "Aurora NeMo Inference v1.0"
    assert info["ethics_protocol"] == "Picard_Delta_3"
    assert router.validate_capsule_ethics("NEMO_CAPSULE_004") is True
    # The 3-capsule alias list is a frozen test contract — NEMO must not
    # be appended to it (see tests/test_module_integration_api.py).
    assert "NEMO_CAPSULE_004" not in router.registered_capsules


def test_nemo_capsule_in_bridge_core_config():
    from modules.symbolic_core import get_capsule
    capsule = get_capsule("NEMO_CAPSULE_004")
    assert capsule is not None
    assert capsule["status"] == "ACTIVE"
    assert "llm_generate" in capsule["capabilities"]


# ---------------------------------------------------------------------------
# Integration points 2-4: CloudHub helpers (NLU / ASR / narrative)
# ---------------------------------------------------------------------------

apimod = pytest.importorskip(
    "api.aurora_gui_cloudhub_fastapi",
    reason="CloudHub app not importable in this environment",
)


def test_nlu_intent_helper(monkeypatch, healthy_client):
    monkeypatch.setattr(apimod, "get_nemo_client", lambda: healthy_client)
    monkeypatch.setattr(apimod, "NEMO_CLIENT_AVAILABLE", True)
    intent = apimod._nemo_nlu_intent("agent_x", ["navigation", "docking"])
    assert intent == "deploy_navigation_agent"


def test_nlu_intent_falls_back_when_down(monkeypatch, down_client):
    monkeypatch.setattr(apimod, "get_nemo_client", lambda: down_client)
    monkeypatch.setattr(apimod, "NEMO_CLIENT_AVAILABLE", True)
    assert apimod._nemo_nlu_intent("agent_x", ["navigation"]) is None


def test_nlu_intent_falls_back_on_model_not_loaded_mock(monkeypatch):
    client = NemoClient(transport=_model_not_loaded_transport())
    try:
        monkeypatch.setattr(apimod, "get_nemo_client", lambda: client)
        monkeypatch.setattr(apimod, "NEMO_CLIENT_AVAILABLE", True)
        assert apimod._nemo_nlu_intent("agent_x", ["navigation"]) is None
    finally:
        client.close()


def test_asr_transcribe_helper(monkeypatch, healthy_client):
    monkeypatch.setattr(apimod, "get_nemo_client", lambda: healthy_client)
    monkeypatch.setattr(apimod, "NEMO_CLIENT_AVAILABLE", True)
    assert apimod._nemo_transcribe("QUJD") == "orbital transfer burn"


def test_asr_transcribe_falls_back_when_down(monkeypatch, down_client):
    monkeypatch.setattr(apimod, "get_nemo_client", lambda: down_client)
    monkeypatch.setattr(apimod, "NEMO_CLIENT_AVAILABLE", True)
    assert apimod._nemo_transcribe("QUJD") is None


def test_narrative_helper(monkeypatch, healthy_client):
    monkeypatch.setattr(apimod, "get_nemo_client", lambda: healthy_client)
    monkeypatch.setattr(apimod, "NEMO_CLIENT_AVAILABLE", True)
    narrative = apimod._nemo_narrative("hr_psych_safety", {"overall_score": 3.4})
    assert narrative == "NEMO says hello"


def test_narrative_helper_falls_back_when_down(monkeypatch, down_client):
    monkeypatch.setattr(apimod, "get_nemo_client", lambda: down_client)
    monkeypatch.setattr(apimod, "NEMO_CLIENT_AVAILABLE", True)
    assert apimod._nemo_narrative("hr_psych_safety", {"overall_score": 3.4}) is None


def test_helpers_short_circuit_when_client_unavailable(monkeypatch):
    """No client import → helpers return None without any HTTP attempt."""
    monkeypatch.setattr(apimod, "NEMO_CLIENT_AVAILABLE", False)
    assert apimod._nemo_nlu_intent("agent_x", ["navigation"]) is None
    assert apimod._nemo_transcribe("QUJD") is None
    assert apimod._nemo_narrative("tag", {}) is None


def test_oppy_request_model_backward_compatible():
    """Text-only requests (no audio_bytes) still validate unchanged."""
    req = apimod.OPPYManeuverRequest(
        vessel_id="AUR-1",
        maneuver_type="hohmann_transfer",
        target_state={"altitude_km": 400.0},
    )
    assert req.audio_bytes is None
    audio_req = apimod.OPPYManeuverRequest(
        vessel_id="AUR-1",
        audio_bytes="QUJD",
        target_state={"altitude_km": 400.0},
    )
    assert audio_req.maneuver_type is None
