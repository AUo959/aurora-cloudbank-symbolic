"""
FastAPI Router for Synergy Dashboard API

Provides RESTful endpoints for component registry access:
- GET /synergy/components - List all components
- POST /synergy/components - Register new component
- GET /synergy/components/{name} - Get component details
- PUT /synergy/components/{name}/status - Update component status
- GET /synergy/dependencies/{name} - Get component dependencies
- GET /synergy/conflicts - Detect dependency conflicts
- GET /synergy/export - Export registry data
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

from src.synergy import (
    get_registry,
    ComponentStatus,
    DependencyType,
    ComponentDependency
)


router = APIRouter(prefix="/synergy", tags=["Synergy Dashboard"])


# Pydantic models for API
class DependencyTypeEnum(str, Enum):
    """API representation of dependency type"""
    RUNTIME = "runtime"
    BUILD = "build"
    OPTIONAL = "optional"
    DEV = "dev"


class ComponentStatusEnum(str, Enum):
    """API representation of component status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    ERROR = "error"
    UNKNOWN = "unknown"


class DependencyInput(BaseModel):
    """Input model for component dependency"""
    name: str = Field(..., description="Dependency component name")
    version: Optional[str] = Field(None, description="Required version")
    dependency_type: DependencyTypeEnum = Field(DependencyTypeEnum.RUNTIME, description="Type of dependency")
    required: bool = Field(True, description="Whether dependency is required")


class ComponentInput(BaseModel):
    """Input model for component registration"""
    name: str = Field(..., description="Unique component name")
    version: str = Field(..., description="Semantic version")
    description: str = Field(..., description="Component description")
    module_path: Optional[str] = Field(None, description="Python module path")
    dependencies: List[DependencyInput] = Field(default_factory=list, description="Component dependencies")
    api_endpoints: List[str] = Field(default_factory=list, description="FastAPI endpoint paths")
    status: ComponentStatusEnum = Field(ComponentStatusEnum.ACTIVE, description="Component status")
    context_tag: Optional[str] = Field(None, description="DLP context tag")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")


class ComponentResponse(BaseModel):
    """Response model for component data"""
    name: str
    version: str
    description: str
    module_path: Optional[str]
    dependencies: List[Dict[str, Any]]
    api_endpoints: List[str]
    status: str
    registered_at: float
    last_updated: float
    metadata: Dict[str, Any]
    context_tag: Optional[str]


class StatusUpdateInput(BaseModel):
    """Input model for status update"""
    status: ComponentStatusEnum


@router.get("/components", response_model=List[ComponentResponse])
async def list_components(
    status: Optional[ComponentStatusEnum] = Query(None, description="Filter by status")
):
    """
    List all registered components
    
    Returns list of components, optionally filtered by status.
    """
    registry = get_registry()
    
    status_filter = None
    if status:
        status_filter = ComponentStatus(status.value)
    
    components = registry.list_components(status=status_filter)
    return [comp.to_dict() for comp in components]


@router.post("/components", response_model=ComponentResponse, status_code=201)
async def register_component(component: ComponentInput):
    """
    Register a new component in the registry
    
    Creates or updates component registration with dependencies.
    """
    registry = get_registry()
    
    # Convert input dependencies to ComponentDependency objects
    deps = [
        ComponentDependency(
            name=dep.name,
            version=dep.version,
            dependency_type=DependencyType(dep.dependency_type.value),
            required=dep.required
        )
        for dep in component.dependencies
    ]
    
    registered = registry.register_component(
        name=component.name,
        version=component.version,
        description=component.description,
        module_path=component.module_path,
        dependencies=deps,
        api_endpoints=component.api_endpoints,
        status=ComponentStatus(component.status.value),
        context_tag=component.context_tag,
        metadata=component.metadata
    )
    
    return registered.to_dict()


@router.get("/components/{name}", response_model=ComponentResponse)
async def get_component(name: str):
    """
    Get details for a specific component
    
    Returns component metadata including dependencies and status.
    """
    registry = get_registry()
    component = registry.get_component(name)
    
    if component is None:
        raise HTTPException(status_code=404, detail=f"Component '{name}' not found")
    
    return component.to_dict()


@router.put("/components/{name}/status", response_model=Dict[str, Any])
async def update_component_status(name: str, status_update: StatusUpdateInput):
    """
    Update component health status
    
    Updates the operational status of a registered component.
    """
    registry = get_registry()
    
    success = registry.update_component_status(
        name,
        ComponentStatus(status_update.status.value)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Component '{name}' not found")
    
    return {
        "component": name,
        "status": status_update.status.value,
        "success": True
    }


@router.get("/dependencies/{name}", response_model=Dict[str, Any])
async def get_dependencies(
    name: str,
    recursive: bool = Query(False, description="Include transitive dependencies")
):
    """
    Get dependencies for a component
    
    Returns direct dependencies or full transitive dependency tree.
    """
    registry = get_registry()
    
    component = registry.get_component(name)
    if component is None:
        raise HTTPException(status_code=404, detail=f"Component '{name}' not found")
    
    deps = registry.get_dependencies(name, recursive=recursive)
    dependents = registry.get_dependents(name)
    
    return {
        "component": name,
        "dependencies": list(deps),
        "dependents": list(dependents),
        "recursive": recursive
    }


@router.get("/conflicts", response_model=List[Dict[str, Any]])
async def detect_conflicts():
    """
    Detect dependency conflicts in the registry
    
    Identifies circular dependencies, missing dependencies, and version conflicts.
    """
    registry = get_registry()
    conflicts = registry.detect_conflicts()
    
    return conflicts


@router.get("/export", response_model=Dict[str, Any])
async def export_registry(context_tag: Optional[str] = Query(None, description="DLP context tag")):
    """
    Export complete registry state
    
    Returns all registry data for backup, analysis, or integration.
    """
    registry = get_registry()
    export_data = registry.export_registry()
    
    if context_tag:
        export_data["context_tag"] = context_tag
    
    return export_data


@router.get("/health", response_model=Dict[str, Any])
async def registry_health():
    """
    Get registry health status
    
    Returns metrics about registry state and component health distribution.
    """
    registry = get_registry()
    
    all_components = registry.list_components()
    status_counts = {}
    
    for component in all_components:
        status_val = component.status.value
        status_counts[status_val] = status_counts.get(status_val, 0) + 1
    
    conflicts = registry.detect_conflicts()
    
    return {
        "total_components": len(all_components),
        "status_distribution": status_counts,
        "conflicts": len(conflicts),
        "healthy": len(conflicts) == 0
    }
