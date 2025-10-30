"""
Tests for Synergy Dashboard FastAPI Router
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.synergy.api import router
from src.synergy import reset_registry


@pytest.fixture
def app():
    """Create test FastAPI app"""
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    """Create test client"""
    reset_registry()
    return TestClient(app)


@pytest.mark.api
@pytest.mark.synergy
def test_list_components_empty(client):
    """Test listing components when registry is empty"""
    response = client.get("/synergy/components")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
@pytest.mark.synergy
def test_register_component_via_api(client):
    """Test component registration through API"""
    component_data = {
        "name": "test-api-component",
        "version": "1.0.0",
        "description": "Test component via API"
    }
    
    response = client.post("/synergy/components", json=component_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "test-api-component"
    assert data["version"] == "1.0.0"
    assert data["status"] == "active"


@pytest.mark.api
@pytest.mark.synergy
def test_register_component_with_dependencies(client):
    """Test registering component with dependencies"""
    component_data = {
        "name": "dependent-component",
        "version": "2.0.0",
        "description": "Has dependencies",
        "dependencies": [
            {
                "name": "base-lib",
                "version": "1.0.0",
                "dependency_type": "runtime",
                "required": True
            }
        ]
    }
    
    response = client.post("/synergy/components", json=component_data)
    assert response.status_code == 201
    
    data = response.json()
    assert len(data["dependencies"]) == 1
    assert data["dependencies"][0]["name"] == "base-lib"


@pytest.mark.api
@pytest.mark.synergy
def test_get_component_by_name(client):
    """Test retrieving specific component"""
    # Register first
    client.post("/synergy/components", json={
        "name": "fetchable",
        "version": "1.0.0",
        "description": "Can be fetched"
    })
    
    # Then fetch
    response = client.get("/synergy/components/fetchable")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "fetchable"


@pytest.mark.api
@pytest.mark.synergy
def test_get_nonexistent_component(client):
    """Test fetching component that doesn't exist"""
    response = client.get("/synergy/components/ghost")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.api
@pytest.mark.synergy
def test_update_component_status(client):
    """Test updating component status via API"""
    # Register component
    client.post("/synergy/components", json={
        "name": "changeable",
        "version": "1.0.0",
        "description": "Status can change"
    })
    
    # Update status
    response = client.put(
        "/synergy/components/changeable/status",
        json={"status": "degraded"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify change
    get_response = client.get("/synergy/components/changeable")
    assert get_response.json()["status"] == "degraded"


@pytest.mark.api
@pytest.mark.synergy
def test_get_dependencies(client):
    """Test getting component dependencies"""
    # Register components
    client.post("/synergy/components", json={
        "name": "base",
        "version": "1.0.0",
        "description": "Base"
    })
    
    client.post("/synergy/components", json={
        "name": "derived",
        "version": "1.0.0",
        "description": "Derived",
        "dependencies": [{"name": "base", "required": True}]
    })
    
    response = client.get("/synergy/dependencies/derived")
    assert response.status_code == 200
    
    data = response.json()
    assert "base" in data["dependencies"]
    assert data["component"] == "derived"


@pytest.mark.api
@pytest.mark.synergy
def test_detect_conflicts(client):
    """Test conflict detection endpoint"""
    # Register component with missing dependency
    client.post("/synergy/components", json={
        "name": "broken",
        "version": "1.0.0",
        "description": "Has missing dep",
        "dependencies": [{"name": "nonexistent", "required": True}]
    })
    
    response = client.get("/synergy/conflicts")
    assert response.status_code == 200
    
    conflicts = response.json()
    assert len(conflicts) > 0
    assert any(c["type"] == "missing_dependency" for c in conflicts)


@pytest.mark.api
@pytest.mark.synergy
def test_export_registry(client):
    """Test registry export endpoint"""
    # Register some components
    client.post("/synergy/components", json={
        "name": "export-test",
        "version": "1.0.0",
        "description": "For export"
    })
    
    response = client.get("/synergy/export")
    assert response.status_code == 200
    
    data = response.json()
    assert "components" in data
    assert "dependency_graph" in data
    assert "export_timestamp" in data
    assert "export-test" in data["components"]


@pytest.mark.api
@pytest.mark.synergy
def test_export_with_context_tag(client):
    """Test export with DLP context tag"""
    response = client.get("/synergy/export?context_tag=test_export_123")
    assert response.status_code == 200
    
    data = response.json()
    assert data["context_tag"] == "test_export_123"


@pytest.mark.api
@pytest.mark.synergy
def test_registry_health(client):
    """Test registry health endpoint"""
    # Register components with different statuses
    client.post("/synergy/components", json={
        "name": "healthy",
        "version": "1.0.0",
        "description": "Healthy",
        "status": "active"
    })
    
    client.post("/synergy/components", json={
        "name": "sick",
        "version": "1.0.0",
        "description": "Sick",
        "status": "error"
    })
    
    response = client.get("/synergy/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_components"] == 2
    assert "status_distribution" in data
    assert data["status_distribution"]["active"] == 1
    assert data["status_distribution"]["error"] == 1


@pytest.mark.api
@pytest.mark.synergy
def test_list_components_with_status_filter(client):
    """Test listing components filtered by status"""
    # Register components
    client.post("/synergy/components", json={
        "name": "active1",
        "version": "1.0.0",
        "description": "Active",
        "status": "active"
    })
    
    client.post("/synergy/components", json={
        "name": "inactive1",
        "version": "1.0.0",
        "description": "Inactive",
        "status": "inactive"
    })
    
    # Filter by active
    response = client.get("/synergy/components?status=active")
    assert response.status_code == 200
    
    components = response.json()
    assert len(components) == 1
    assert components[0]["name"] == "active1"


@pytest.mark.api
@pytest.mark.synergy
def test_transitive_dependencies(client):
    """Test recursive dependency resolution"""
    # Create dependency chain
    client.post("/synergy/components", json={
        "name": "level1",
        "version": "1.0.0",
        "description": "Level 1"
    })
    
    client.post("/synergy/components", json={
        "name": "level2",
        "version": "1.0.0",
        "description": "Level 2",
        "dependencies": [{"name": "level1", "required": True}]
    })
    
    client.post("/synergy/components", json={
        "name": "level3",
        "version": "1.0.0",
        "description": "Level 3",
        "dependencies": [{"name": "level2", "required": True}]
    })
    
    # Get transitive dependencies
    response = client.get("/synergy/dependencies/level3?recursive=true")
    assert response.status_code == 200
    
    data = response.json()
    assert "level2" in data["dependencies"]
    assert "level1" in data["dependencies"]  # Transitive
