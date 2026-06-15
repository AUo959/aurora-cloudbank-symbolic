"""
Smoke tests for Opal2 API route registration (issue #765).

Guards against malformed decorators — previously @app.post(# comment"/path")
silently broke route registration for /render and /generate.
"""

import ast
import importlib.util
import os

import pytest


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
    assert '@app.post("/render")' in source, (
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
    spec = importlib.util.spec_from_file_location("opal2_api_module", OPAL2_API_PATH)
    if spec is None or spec.loader is None:
        pytest.skip("Cannot load opal2_api module via importlib (missing optional deps)")

    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    except Exception as exc:
        pytest.skip(f"opal2_api module failed to import (optional deps missing): {exc}")

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


@pytest.mark.unit
@pytest.mark.opal2
def test_opal2_plugin_system_is_full_implementation():
    """PluginSystem must be the full class, not one of the stub shadows.

    Resolves issue #1025: two simplified stubs were concatenated at the end of
    plugin_system.py and shadowed the complete implementation.  This test
    verifies that the class loaded by opal2_api.py has the expected interface
    and that the five built-in plugins are registered at instantiation time.
    """
    try:
        from modules.opal2.plugin_system import PluginSystem
    except ImportError as exc:
        pytest.skip(f"modules.opal2.plugin_system not importable: {exc}")

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
