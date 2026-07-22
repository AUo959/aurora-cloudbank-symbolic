"""
Smoke tests for Opal2 API route registration (issue #765).

Guards against malformed decorators — previously @app.post(# comment"/path")
silently broke route registration for /render and /generate.
"""

import ast
import importlib
import os
import re
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


OPAL2_API_PATH = os.path.join(
    os.path.dirname(__file__), "..", "modules", "opal2", "api", "opal2_api.py"
)


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_api_syntax_valid():
    """opal2_api.py must parse without syntax errors."""
    with open(OPAL2_API_PATH) as f:
        source = f.read()
    # ast.parse raises SyntaxError if the file is malformed
    tree = ast.parse(source, filename="opal2_api.py")
    assert tree is not None


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_api_render_decorator_correct():
    """The /render route decorator must not contain an inline comment."""
    with open(OPAL2_API_PATH) as f:
        source = f.read()
    # The malformed pattern was: @app.post(  # comment"/render")
    # This check fails if the broken form is re-introduced.
    assert re.search(r'@app\.post\(\s*"/render"(?:\s*,|\s*\))', source), (  # nosec B101 - pytest assertion
        "Opal2 /render decorator is missing or malformed in opal2_api.py"
    )
    assert '# verify_csrf inside"/render"' not in source, (
        "Malformed inline-comment decorator re-introduced for /render"
    )


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_api_generate_decorator_correct():
    """The /generate route decorator must not contain an inline comment."""
    with open(OPAL2_API_PATH) as f:
        source = f.read()
    assert '@app.post("/generate")' in source, (
        "Opal2 /generate decorator is missing or malformed in opal2_api.py"
    )
    assert '# verify_csrf inside"/generate"' not in source, (
        "Malformed inline-comment decorator re-introduced for /generate"
    )


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_api_routes_registered():
    """FastAPI app object must have /render and /generate routes registered.

    This test catches the runtime consequence of the broken decorators:
    if a decorator is malformed Python never registers the route, so the
    app.routes list won't contain the path.
    """
    module = importlib.import_module("modules.opal2.api.opal2_api")

    app = getattr(module, "app", None)
    assert app is not None, "opal2_api.py must define a FastAPI `app` object"

    # Collect all registered route paths
    registered_paths = {getattr(route, "path", "") for route in app.routes}

    assert "/render" in registered_paths, (
        f"/render not registered in Opal2 app. Registered paths: {sorted(registered_paths)}"
    )
    assert "/generate" in registered_paths, (
        f"/generate not registered in Opal2 app. Registered paths: {sorted(registered_paths)}"
    )
    assert "/tools" in registered_paths  # nosec B101 - pytest assertion
    assert "/tools/{tool_id}" in registered_paths  # nosec B101 - pytest assertion
    assert "/tools/{tool_id}/run" in registered_paths  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_plugin_system_is_full_implementation():
    """PluginSystem must be the full class, not one of the stub shadows.

    Resolves issue #1025: two simplified stubs were concatenated at the end of
    plugin_system.py and shadowed the complete implementation.  This test
    verifies that the class loaded by opal2_api.py has the expected interface
    and that the five built-in plugins are registered at instantiation time.
    """
    from modules.opal2.plugin_system import PluginSystem

    ps = PluginSystem()

    # The full class has list_plugins(); the stubs do not
    assert hasattr(ps, "list_plugins"), (
        "PluginSystem is missing list_plugins() — a stub class is still active"
    )

    plugins = ps.list_plugins()
    assert len(plugins) == 5, (
        f"Expected 5 built-in plugins, got {len(plugins)}: {list(plugins.keys())}"
    )

    expected_plugins = {
        "webgl_renderer",
        "canvas_renderer",
        "svg_renderer",
        "quantum_field_renderer",
        "geometric_algebra_processor",
    }
    assert set(plugins.keys()) == expected_plugins, (
        f"Built-in plugin names mismatch: {set(plugins.keys())} != {expected_plugins}"
    )

    # get_plugin() must return a live object for each built-in
    for name in expected_plugins:
        plugin = ps.get_plugin(name)
        assert plugin is not None, f"get_plugin('{name}') returned None"


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_opal2_compatibility_render_uses_foundry_registry():
    """The legacy /render implementation must execute the registered glyph tool."""

    module = importlib.import_module("modules.opal2.api.opal2_api")
    request = module.RenderRequest(
        glyph_data={
            "vertices": [[0, 0], [1, 1]],
            "indices": [0, 1],
            "dimensions": 2,
        },
        renderer_type="webgl",
        cache_key="opal2-foundry-route-test",
    )

    result = await module._render_glyph_impl(request)

    assert result["success"] is True  # nosec B101 - pytest assertion
    assert result["cached"] is False  # nosec B101 - pytest assertion
    assert result["result"]["format"] == "webgl"  # nosec B101 - pytest assertion
    assert result["tool_run"]["tool_id"] == "opal2.glyph.render"  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
@pytest.mark.parametrize("error_name", ["ToolNotFoundError", "ToolOutputError"])
async def test_opal2_compatibility_render_handles_registry_failures(
    monkeypatch, error_name
):
    """The compatibility route must convert registry failures into controlled 500s."""

    module = importlib.import_module("modules.opal2.api.opal2_api")
    error_type = getattr(module, error_name)

    class FailingRegistry:
        async def run(self, *_args, **_kwargs):
            raise error_type("forced registry failure")

    monkeypatch.setattr(module, "tool_registry", FailingRegistry())
    monkeypatch.setattr(module.glyph_cache, "get_async", AsyncMock(return_value=None))
    request = module.RenderRequest(
        glyph_data={"vertices": [], "indices": [], "dimensions": 2},
        cache_key=f"opal2-{error_name}-route-test",
    )

    with pytest.raises(module.HTTPException) as exc_info:
        await module._render_glyph_impl(request)

    assert exc_info.value.status_code == 500  # nosec B101 - pytest assertion
    assert (  # nosec B101 - pytest assertion
        exc_info.value.detail == "glyph render tool execution failed"
    )


@pytest.mark.integration
@pytest.mark.opal2
def test_opal2_foundry_http_discovery_and_execution():
    """The standalone API must discover and execute its reference tool."""

    module = importlib.import_module("modules.opal2.api.opal2_api")
    from src.middleware.fastapi_security import generate_csrf_token

    client = TestClient(module.app)
    root_response = client.get("/")
    assert root_response.status_code == 200  # nosec B101 - pytest assertion
    assert root_response.json()["timestamp"].endswith("+00:00")  # nosec B101 - pytest assertion
    discovery = client.get("/tools")
    assert discovery.status_code == 200  # nosec B101 - pytest assertion
    tool_ids = {tool["tool_id"] for tool in discovery.json()["tools"]}
    assert "opal2.glyph.render" in tool_ids  # nosec B101 - pytest assertion
    assert "opal2.regex.workshop" in tool_ids  # nosec B101 - pytest assertion

    auth_headers = {"Authorization": f"Bearer {generate_csrf_token('opal2-test')}"}
    response = client.post(
        "/tools/opal2.glyph.render/run",
        headers=auth_headers,
        json={
            "payload": {
                "glyph_data": {
                    "vertices": [[0, 0], [1, 1]],
                    "indices": [0, 1],
                    "dimensions": 2,
                },
                "renderer": "svg",
            }
        },
    )

    assert response.status_code == 200  # nosec B101 - pytest assertion
    assert response.json()["tool_id"] == "opal2.glyph.render"  # nosec B101 - pytest assertion
    assert response.json()["output"]["format"] == "svg"  # nosec B101 - pytest assertion

    regex_response = client.post(
        "/tools/opal2.regex.workshop/run",
        headers=auth_headers,
        json={
            "payload": {
                "template": "word",
                "value": "anchor",
                "samples": [
                    {"text": "stable anchor", "expected_match": True},
                    {"text": "anchored", "expected_match": False},
                ],
            }
        },
    )
    assert regex_response.status_code == 200  # nosec B101 - pytest assertion
    assert regex_response.json()["tool_id"] == "opal2.regex.workshop"  # nosec B101 - pytest assertion
    assert regex_response.json()["output"]["all_expectations_met"] is True  # nosec B101 - pytest assertion

    invalid_dimensions = client.post(
        "/tools/opal2.glyph.render/run",
        headers=auth_headers,
        json={
            "payload": {
                "glyph_data": {"vertices": [], "indices": [], "dimensions": 2},
                "renderer": "svg",
                "dimensions": {"width": 320},
            }
        },
    )
    assert invalid_dimensions.status_code == 422  # nosec B101 - pytest assertion
    assert (
        "dimensions missing required field: height"
        in invalid_dimensions.json()["detail"]
    )  # nosec B101 - pytest assertion
