"""
test_symbolic_solver_plugin.py
Unit tests for SymbolicSolverPlugin and PluginRegistry.
"""

from modules.symbolic_core.symbolic_solver_plugin import (
    PluginRegistry,
    SymbolicSolverPlugin,
)

class DummyPlugin(SymbolicSolverPlugin):
    def name(self):
        return "dummy"

    def solve(self, problem):
        return f"solved: {problem}"

def test_plugin_registry():
    registry = PluginRegistry()
    plugin = DummyPlugin()
    registry.register(plugin)
    assert registry.get("dummy") is plugin
    assert "dummy" in registry.list_plugins()
    assert plugin.solve("test") == "solved: test"
