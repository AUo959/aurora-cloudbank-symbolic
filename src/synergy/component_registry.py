"""
Aurora Synergy Dashboard - Component Registry

Provides centralized tracking and discovery of Aurora components:
- Component registration (manual and auto-discovery)
- Dependency mapping and conflict detection
- Version tracking and changelog management
- Integration with OpenTelemetry for usage metrics
- DLP-compliant audit trails

Architecture: Organic field dynamics with distributed discovery
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
from pathlib import Path
import importlib.util

from src.core.logging_security import safe_str, safe_path, safe_error

logger = logging.getLogger(__name__)


class ComponentStatus(str, Enum):
    """Component health status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    ERROR = "error"
    UNKNOWN = "unknown"


class DependencyType(str, Enum):
    """Type of component dependency"""
    RUNTIME = "runtime"
    BUILD = "build"
    OPTIONAL = "optional"
    DEV = "dev"


@dataclass
class ComponentDependency:
    """Represents a dependency relationship"""
    name: str
    version: Optional[str] = None
    dependency_type: DependencyType = DependencyType.RUNTIME
    required: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "dependency_type": self.dependency_type.value,
            "required": self.required
        }


@dataclass
class ComponentMetadata:
    """Complete metadata for a registered component"""
    name: str
    version: str
    description: str
    module_path: Optional[str] = None
    dependencies: List[ComponentDependency] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    status: ComponentStatus = ComponentStatus.UNKNOWN
    registered_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # DLP tracking
    context_tag: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "module_path": self.module_path,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "api_endpoints": self.api_endpoints,
            "status": self.status.value,
            "registered_at": self.registered_at,
            "last_updated": self.last_updated,
            "metadata": self.metadata,
            "context_tag": self.context_tag
        }


class ComponentRegistry:
    """
    Centralized registry for Aurora components
    
    Features:
    - Manual and automatic component registration
    - Dependency graph tracking
    - Conflict detection
    - Health status monitoring
    - OpenTelemetry integration
    """
    
    def __init__(self):
        self._components: Dict[str, ComponentMetadata] = {}
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._reverse_dependencies: Dict[str, Set[str]] = {}
        
    def register_component(
        self,
        name: str,
        version: str,
        description: str,
        module_path: Optional[str] = None,
        dependencies: Optional[List[ComponentDependency]] = None,
        api_endpoints: Optional[List[str]] = None,
        status: ComponentStatus = ComponentStatus.ACTIVE,
        context_tag: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ComponentMetadata:
        """
        Register a component in the registry
        
        Args:
            name: Unique component identifier
            version: Semantic version string
            description: Human-readable description
            module_path: Python module path (for auto-discovery)
            dependencies: List of component dependencies
            api_endpoints: FastAPI endpoint paths
            status: Component health status
            context_tag: DLP context tag for audit
            metadata: Additional custom metadata
        
        Returns:
            ComponentMetadata for the registered component
        """
        dependencies = dependencies or []
        api_endpoints = api_endpoints or []
        metadata = metadata or {}
        
        component = ComponentMetadata(
            name=name,
            version=version,
            description=description,
            module_path=module_path,
            dependencies=dependencies,
            api_endpoints=api_endpoints,
            status=status,
            context_tag=context_tag,
            metadata=metadata
        )
        
        # Update registry
        if name in self._components:
            component.registered_at = self._components[name].registered_at
        component.last_updated = time.time()
        
        self._components[name] = component
        
        # Update dependency graphs
        self._update_dependency_graph(name, dependencies)
        
        logger.info("Component registered: %s v%s", safe_str(name), safe_str(version))
        return component
    
    def _update_dependency_graph(
        self,
        component_name: str,
        dependencies: List[ComponentDependency]
    ):
        """Update dependency tracking graphs"""
        # Forward dependencies (what this component depends on)
        self._dependency_graph[component_name] = {
            dep.name for dep in dependencies if dep.required
        }
        
        # Reverse dependencies (what depends on this component)
        for dep in dependencies:
            if dep.required:
                if dep.name not in self._reverse_dependencies:
                    self._reverse_dependencies[dep.name] = set()
                self._reverse_dependencies[dep.name].add(component_name)
    
    def get_component(self, name: str) -> Optional[ComponentMetadata]:
        """Get component metadata by name"""
        return self._components.get(name)
    
    def list_components(
        self,
        status: Optional[ComponentStatus] = None
    ) -> List[ComponentMetadata]:
        """
        List all registered components, optionally filtered by status
        
        Args:
            status: Filter by component status
        
        Returns:
            List of component metadata
        """
        components = list(self._components.values())
        if status:
            components = [c for c in components if c.status == status]
        return sorted(components, key=lambda c: c.name)
    
    def get_dependencies(
        self,
        component_name: str,
        recursive: bool = False
    ) -> Set[str]:
        """
        Get dependencies for a component
        
        Args:
            component_name: Name of component to check
            recursive: Include transitive dependencies
        
        Returns:
            Set of dependency names
        """
        if component_name not in self._dependency_graph:
            return set()
        
        deps = self._dependency_graph[component_name].copy()
        
        if recursive:
            # Breadth-first traversal for transitive dependencies
            visited = set()
            queue = list(deps)
            
            while queue:
                dep = queue.pop(0)
                if dep in visited:
                    continue
                visited.add(dep)
                
                if dep in self._dependency_graph:
                    for transitive_dep in self._dependency_graph[dep]:
                        if transitive_dep not in visited:
                            queue.append(transitive_dep)
                            deps.add(transitive_dep)
        
        return deps
    
    def get_dependents(self, component_name: str) -> Set[str]:
        """
        Get components that depend on this component
        
        Args:
            component_name: Name of component
        
        Returns:
            Set of dependent component names
        """
        return self._reverse_dependencies.get(component_name, set()).copy()
    
    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        Detect dependency conflicts in the registry
        
        Returns:
            List of conflict descriptions
        """
        conflicts = []
        
        # Check for circular dependencies
        for component in self._components:
            if self._has_circular_dependency(component):
                conflicts.append({
                    "type": "circular_dependency",
                    "component": component,
                    "description": f"Circular dependency detected involving {component}"
                })
        
        # Check for missing dependencies
        for component_name, deps in self._dependency_graph.items():
            for dep in deps:
                if dep not in self._components:
                    conflicts.append({
                        "type": "missing_dependency",
                        "component": component_name,
                        "missing": dep,
                        "description": f"{component_name} depends on unregistered component {dep}"
                    })
        
        # Check for version conflicts (simplified - would need version parsing)
        # This is a placeholder for more sophisticated version conflict detection
        
        return conflicts
    
    def _has_circular_dependency(
        self,
        component: str,
        visited: Optional[Set[str]] = None,
        rec_stack: Optional[Set[str]] = None
    ) -> bool:
        """Detect circular dependencies using DFS"""
        if visited is None:
            visited = set()
        if rec_stack is None:
            rec_stack = set()
        
        visited.add(component)
        rec_stack.add(component)
        
        if component in self._dependency_graph:
            for dep in self._dependency_graph[component]:
                if dep not in visited:
                    if self._has_circular_dependency(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
        
        rec_stack.remove(component)
        return False
    
    def auto_discover_components(
        self,
        scan_paths: Optional[List[Path]] = None
    ) -> List[ComponentMetadata]:
        """
        Auto-discover components by scanning module directories
        
        Args:
            scan_paths: Directories to scan (default: src/, modules/)
        
        Returns:
            List of newly discovered components
        """
        if scan_paths is None:
            scan_paths = [Path("src"), Path("modules")]
        
        discovered = []
        
        for base_path in scan_paths:
            if not base_path.exists():
                continue
            
            for module_path in base_path.rglob("*.py"):
                if module_path.name.startswith("_"):
                    continue
                
                # Try to extract component metadata from module
                metadata = self._extract_component_metadata(module_path)
                if metadata:
                    component = self.register_component(**metadata)
                    discovered.append(component)
        
        logger.info("Auto-discovered %d components", len(discovered))
        return discovered
    
    def _extract_component_metadata(self, module_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract component metadata from Python module
        
        Looks for:
        - __component_name__
        - __version__
        - __description__
        - __dependencies__
        """
        try:
            spec = importlib.util.spec_from_file_location("temp_module", module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if module has component metadata
                if hasattr(module, "__component_name__"):
                    return {
                        "name": getattr(module, "__component_name__"),
                        "version": getattr(module, "__version__", "0.0.0"),
                        "description": getattr(module, "__description__", ""),
                        "module_path": str(module_path),
                        "status": ComponentStatus.ACTIVE
                    }
        except Exception as e:
            logger.debug("Could not extract metadata from %s: %s", safe_path(module_path), safe_error(e))
        
        return None
    
    def update_component_status(
        self,
        name: str,
        status: ComponentStatus
    ) -> bool:
        """
        Update component health status
        
        Args:
            name: Component name
            status: New status
        
        Returns:
            True if updated, False if component not found
        """
        if name not in self._components:
            return False
        
        self._components[name].status = status
        self._components[name].last_updated = time.time()
        logger.info("Component %s status updated to %s", safe_str(name), safe_str(status.value))
        return True
    
    def export_registry(self) -> Dict[str, Any]:
        """
        Export complete registry state for persistence/export
        
        Returns:
            Dictionary with all registry data
        """
        return {
            "components": {
                name: component.to_dict()
                for name, component in self._components.items()
            },
            "dependency_graph": {
                name: list(deps)
                for name, deps in self._dependency_graph.items()
            },
            "export_timestamp": time.time()
        }


# Global registry instance
_global_registry: Optional[ComponentRegistry] = None


def get_registry() -> ComponentRegistry:
    """Get or create global component registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ComponentRegistry()
    return _global_registry


def reset_registry():
    """Reset global registry (useful for testing)"""
    global _global_registry
    _global_registry = None
