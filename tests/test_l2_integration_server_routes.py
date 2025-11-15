"""Tests for L2 integration server route registration."""

import sys
import types

import pytest
from fastapi.routing import APIRoute


@pytest.fixture(autouse=True)
def stub_chatgpt_agent_mode(monkeypatch):
    """Provide a lightweight stub for the chatgpt_agent_mode integration if missing."""

    module_name = "src.integrations.chatgpt_agent_mode"

    class _StubBridge:
        """Minimal async-compatible stub for auroraCustomGptBridge."""

        def __init__(self):
            self.integrationActive = True

        async def initializeCommandNodeIntegration(self):
            self.integrationActive = True
            return {"success": True}

        async def routeCommandFromCustomGpt(self, command, context):
            return {"success": True, "command": command, "context": context}

        def getIntegrationStatus(self):
            return {"active": True}

        async def getConstellationStatus(self):
            return {"success": True, "constellation": []}

    try:
        module = __import__(module_name, fromlist=["AURORA_CUSTOM_GPT", "auroraCustomGptBridge"])
    except ImportError:
        stub_module = types.ModuleType(module_name)
        stub_module.AURORA_CUSTOM_GPT = object()
        stub_module.auroraCustomGptBridge = _StubBridge()
        monkeypatch.setitem(sys.modules, module_name, stub_module)
        try:
            yield
        finally:
            monkeypatch.delitem(sys.modules, module_name, raising=False)
    else:
        if not hasattr(module, "AURORA_CUSTOM_GPT"):
            monkeypatch.setattr(module, "AURORA_CUSTOM_GPT", object(), raising=False)
        if not hasattr(module, "auroraCustomGptBridge"):
            monkeypatch.setattr(module, "auroraCustomGptBridge", _StubBridge(), raising=False)
        yield


def _get_route(app, path: str, method: str):
    """Return the FastAPI route matching the given path and HTTP method."""
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path == path and method.upper() in route.methods:
            return route
    return None


def test_l2_integration_server_registers_expected_routes():
    """Ensure critical L2 integration routes are registered on the FastAPI app."""
    from src.servers.l2_integration_server import app

    expected_routes = [
        ("/api/aurora/command", "POST"),
        ("/api/aurora/initialize", "POST"),
        ("/api/bridge/gpt/connect/{agent_id}", "POST"),
        ("/api/bridge/gpt/message/{agent_id}", "POST"),
        ("/api/bridge/gpt/heartbeat/{agent_id}", "POST"),
        ("/api/bridge/gpt/disconnect/{agent_id}", "POST"),
    ]

    for path, method in expected_routes:
        route = _get_route(app, path, method)
        assert route is not None, f"Route {method} {path} is not registered on the app"
