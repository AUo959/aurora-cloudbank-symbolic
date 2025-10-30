"""
Tests for Aurora Synergy Dashboard - Component Registry
"""

import pytest
from src.synergy import (
    ComponentRegistry,
    ComponentDependency,
    ComponentStatus,
    DependencyType,
    get_registry,
    reset_registry
)


@pytest.mark.unit
@pytest.mark.synergy
def test_component_registration():
    """Test basic component registration"""
    registry = ComponentRegistry()
    
    component = registry.register_component(
        name="test-component",
        version="1.0.0",
        description="Test component for unit tests"
    )
    
    assert component.name == "test-component"
    assert component.version == "1.0.0"
    assert component.status == ComponentStatus.ACTIVE
    assert component.registered_at > 0


@pytest.mark.unit
@pytest.mark.synergy
def test_component_with_dependencies():
    """Test component registration with dependencies"""
    registry = ComponentRegistry()
    
    deps = [
        ComponentDependency(name="core-lib", version="2.0.0"),
        ComponentDependency(name="utils", version="1.5.0", dependency_type=DependencyType.RUNTIME)
    ]
    
    component = registry.register_component(
        name="dependent-component",
        version="1.0.0",
        description="Component with dependencies",
        dependencies=deps
    )
    
    assert len(component.dependencies) == 2
    assert component.dependencies[0].name == "core-lib"


@pytest.mark.unit
@pytest.mark.synergy
def test_get_component():
    """Test retrieving component metadata"""
    registry = ComponentRegistry()
    
    registry.register_component(
        name="fetchable",
        version="1.0.0",
        description="Component to fetch"
    )
    
    component = registry.get_component("fetchable")
    assert component is not None
    assert component.name == "fetchable"
    
    missing = registry.get_component("nonexistent")
    assert missing is None


@pytest.mark.unit
@pytest.mark.synergy
def test_list_components():
    """Test listing all components"""
    registry = ComponentRegistry()
    
    registry.register_component("comp1", "1.0.0", "First")
    registry.register_component("comp2", "2.0.0", "Second", status=ComponentStatus.INACTIVE)
    registry.register_component("comp3", "3.0.0", "Third")
    
    all_components = registry.list_components()
    assert len(all_components) == 3
    
    active_only = registry.list_components(status=ComponentStatus.ACTIVE)
    assert len(active_only) == 2


@pytest.mark.unit
@pytest.mark.synergy
def test_dependency_graph():
    """Test dependency graph construction"""
    registry = ComponentRegistry()
    
    # Register components with dependency chain
    registry.register_component("base", "1.0.0", "Base component")
    
    registry.register_component(
        "middle",
        "1.0.0",
        "Middle layer",
        dependencies=[ComponentDependency("base")]
    )
    
    registry.register_component(
        "top",
        "1.0.0",
        "Top layer",
        dependencies=[ComponentDependency("middle")]
    )
    
    # Check direct dependencies
    deps = registry.get_dependencies("top")
    assert "middle" in deps
    assert "base" not in deps  # Not direct dependency
    
    # Check transitive dependencies
    all_deps = registry.get_dependencies("top", recursive=True)
    assert "middle" in all_deps
    assert "base" in all_deps


@pytest.mark.unit
@pytest.mark.synergy
def test_reverse_dependencies():
    """Test finding components that depend on a component"""
    registry = ComponentRegistry()
    
    registry.register_component("library", "1.0.0", "Shared library")
    
    registry.register_component(
        "app1",
        "1.0.0",
        "Application 1",
        dependencies=[ComponentDependency("library")]
    )
    
    registry.register_component(
        "app2",
        "1.0.0",
        "Application 2",
        dependencies=[ComponentDependency("library")]
    )
    
    dependents = registry.get_dependents("library")
    assert len(dependents) == 2
    assert "app1" in dependents
    assert "app2" in dependents


@pytest.mark.unit
@pytest.mark.synergy
def test_circular_dependency_detection():
    """Test detection of circular dependencies"""
    registry = ComponentRegistry()
    
    registry.register_component("a", "1.0.0", "Component A")
    registry.register_component("b", "1.0.0", "Component B", dependencies=[ComponentDependency("a")])
    # Create circular: a -> b -> c -> a
    registry.register_component("c", "1.0.0", "Component C", dependencies=[ComponentDependency("b")])
    registry.register_component("a", "1.0.0", "Component A", dependencies=[ComponentDependency("c")])
    
    conflicts = registry.detect_conflicts()
    circular_conflicts = [c for c in conflicts if c["type"] == "circular_dependency"]
    assert len(circular_conflicts) > 0


@pytest.mark.unit
@pytest.mark.synergy
def test_missing_dependency_detection():
    """Test detection of missing dependencies"""
    registry = ComponentRegistry()
    
    registry.register_component(
        "broken",
        "1.0.0",
        "Component with missing dep",
        dependencies=[ComponentDependency("nonexistent")]
    )
    
    conflicts = registry.detect_conflicts()
    missing_conflicts = [c for c in conflicts if c["type"] == "missing_dependency"]
    assert len(missing_conflicts) == 1
    assert missing_conflicts[0]["missing"] == "nonexistent"


@pytest.mark.unit
@pytest.mark.synergy
def test_component_status_update():
    """Test updating component status"""
    registry = ComponentRegistry()
    
    registry.register_component("changeable", "1.0.0", "Status test")
    
    success = registry.update_component_status("changeable", ComponentStatus.DEGRADED)
    assert success is True
    
    component = registry.get_component("changeable")
    assert component.status == ComponentStatus.DEGRADED
    
    # Try updating non-existent component
    failure = registry.update_component_status("ghost", ComponentStatus.ERROR)
    assert failure is False


@pytest.mark.unit
@pytest.mark.synergy
def test_component_metadata_serialization():
    """Test component metadata can be serialized"""
    registry = ComponentRegistry()
    
    registry.register_component(
        name="serializable",
        version="1.0.0",
        description="Test serialization",
        api_endpoints=["/api/test", "/api/status"],
        context_tag="test_context_123",
        metadata={"custom_field": "custom_value"}
    )
    
    export = registry.export_registry()
    assert "components" in export
    assert "serializable" in export["components"]
    
    component_data = export["components"]["serializable"]
    assert component_data["name"] == "serializable"
    assert component_data["context_tag"] == "test_context_123"
    assert len(component_data["api_endpoints"]) == 2


@pytest.mark.unit
@pytest.mark.synergy
def test_dependency_type_handling():
    """Test different dependency types"""
    registry = ComponentRegistry()
    
    deps = [
        ComponentDependency("runtime-dep", dependency_type=DependencyType.RUNTIME, required=True),
        ComponentDependency("optional-dep", dependency_type=DependencyType.OPTIONAL, required=False),
        ComponentDependency("dev-dep", dependency_type=DependencyType.DEV, required=False)
    ]
    
    registry.register_component(
        "complex",
        "1.0.0",
        "Component with mixed deps",
        dependencies=deps
    )
    
    component = registry.get_component("complex")
    assert len(component.dependencies) == 3
    
    # Only required dependencies should be in graph
    graph_deps = registry.get_dependencies("complex")
    assert "runtime-dep" in graph_deps
    assert "optional-dep" not in graph_deps  # Not required
    assert "dev-dep" not in graph_deps  # Not required


@pytest.mark.unit
@pytest.mark.synergy
def test_global_registry_singleton():
    """Test global registry singleton pattern"""
    reset_registry()
    
    registry1 = get_registry()
    registry1.register_component("singleton-test", "1.0.0", "Test")
    
    registry2 = get_registry()
    component = registry2.get_component("singleton-test")
    
    assert component is not None
    assert registry1 is registry2


@pytest.mark.integration
@pytest.mark.synergy
def test_component_update_preserves_registration_time():
    """Test that re-registering preserves original registration time"""
    registry = ComponentRegistry()
    
    component1 = registry.register_component("updatable", "1.0.0", "First version")
    original_time = component1.registered_at
    
    import time
    time.sleep(0.01)
    
    component2 = registry.register_component("updatable", "2.0.0", "Second version")
    
    assert component2.registered_at == original_time
    assert component2.last_updated > original_time
    assert component2.version == "2.0.0"


@pytest.mark.unit
@pytest.mark.synergy
def test_export_registry_structure():
    """Test registry export contains all necessary data"""
    registry = ComponentRegistry()
    
    registry.register_component("exp1", "1.0.0", "Export test 1")
    registry.register_component(
        "exp2",
        "1.0.0",
        "Export test 2",
        dependencies=[ComponentDependency("exp1")]
    )
    
    export = registry.export_registry()
    
    assert "components" in export
    assert "dependency_graph" in export
    assert "export_timestamp" in export
    assert len(export["components"]) == 2
    assert "exp2" in export["dependency_graph"]
    assert "exp1" in export["dependency_graph"]["exp2"]
