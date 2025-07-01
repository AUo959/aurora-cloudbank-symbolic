# plugin.py
"""
Abstract base class and registry for SymbolicSolverPlugin system.
"""
from abc import ABC, abstractmethod


class SymbolicSolverPlugin(ABC):
    @abstractmethod
    def solve(self, problem):
        pass


class PluginRegistry:
    def __init__(self):
        self.plugins = {}

    def register(self, name, plugin):
        self.plugins[name] = plugin

    def get(self, name):
        return self.plugins.get(name)

    def all_plugins(self):
        return self.plugins
