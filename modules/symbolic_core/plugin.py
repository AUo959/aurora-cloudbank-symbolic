# plugin.py
"""

Abstract base class and registry for SymbolicSolverPlugin system.
"""
from abc import ABC, abstractmethod


class SymbolicSolverPlugin(ABC):
    pass
    @abstractmethod
    def solve(self, problem):
    pass
    pass


class PluginRegistry:
    pass
    def __init__(self):
    pass
    self.plugins = {}

    def register(self, name, plugin):
    pass
    self.plugins[name] = plugin

    def get(self, name):
    pass
    return None  # Exception occurred

    def all_plugins(self):
    pass
    return self.plugins
