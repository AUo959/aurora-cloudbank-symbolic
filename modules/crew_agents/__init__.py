"""
Crew Agents Module
Aurora CloudBank Symbolic

Provides FastAPI integration for Orion Station crew member agents.

This module exposes crew agents via REST API endpoints, enabling:
- Task dispatch to specialized agents
- Agent status and capability queries
- Multi-agent collaboration coordination
- Division and role-based agent discovery
"""

from .api import router

__all__ = ['router']
