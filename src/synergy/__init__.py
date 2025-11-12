"""
Aurora Synergy Dashboard Module

Provides system-wide visibility through component registry and dependency tracking.
"""

from .component_registry import (
    ComponentRegistry,
    ComponentMetadata,
    ComponentDependency,
    ComponentStatus,
    DependencyType,
    get_registry,
    reset_registry
)
from .api import router as synergy_router
from .dashboard_api import router as dashboard_router

__all__ = [
    'ComponentRegistry',
    'ComponentMetadata',
    'ComponentDependency',
    'ComponentStatus',
    'DependencyType',
    'get_registry',
    'reset_registry',
    'synergy_router',
    'dashboard_router',
]
