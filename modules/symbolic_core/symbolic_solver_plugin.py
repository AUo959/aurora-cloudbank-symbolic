"""
symbolic_solver_plugin.py

Abstract base class and registry for symbolic solver plugins.
"""

from abc import ABC, abstractmethod


class SymbolicSolverPlugin(ABC):
    """Abstract base class for symbolic solver plugins."""

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def solve(self, problem):
        pass


class PluginRegistry:
    """Registry for symbolic solver plugins."""

    def __init__(self):
        self._plugins = {}

    def register(self, plugin: SymbolicSolverPlugin):
        self._plugins[plugin.name()] = plugin

    def get(self, name):
        return self._plugins.get(name)

    def list_plugins(self):
        return list(self._plugins.keys())
