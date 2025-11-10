"""Integration test for Fleet Bridge Python-JS sync.

Validates that Python fleet registry can be accessed via FastAPI
and synced to JavaScript station state structure.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.api
def test_fleet_bridge_api_availability():
    """Test that fleet bridge API endpoints are available."""
    from api.aurora_api import app
    
    client = TestClient(app)
    
    # Check /api/fleet/craft endpoint
    response = client.get("/api/fleet/craft")
    
    # Should either return 200 with craft list or 503 if registry unavailable
    assert response.status_code in [200, 503], \
        f"Unexpected status {response.status_code}"
    
    if response.status_code == 200:
        craft_list = response.json()
        assert isinstance(craft_list, list), "Craft list should be array"
        
        # If we have craft, validate schema
        if len(craft_list) > 0:
            craft = craft_list[0]
            required_fields = [
                "id", "craft_class", "dimensions", "mass_kg",
                "port_type", "fuel_type", "max_rcs", "capabilities", "status"
            ]
            for field in required_fields:
                assert field in craft, f"Missing required field: {field}"


@pytest.mark.integration
@pytest.mark.api
def test_fleet_bridge_craft_schema_mapping():
    """Test Python-to-JS schema mapping is correct."""
    from api.aurora_api import app
    
    client = TestClient(app)
    response = client.get("/api/fleet/craft")
    
    if response.status_code != 200:
        pytest.skip("Fleet registry unavailable")
    
    craft_list = response.json()
    if len(craft_list) == 0:
        pytest.skip("No craft in registry")
    
    craft = craft_list[0]
    
    # Validate JS-compatible schema
    assert "craft_class" in craft, "Should use craft_class (not class)"
    assert "mass_kg" in craft, "Should use mass_kg (snake_case)"
    assert "port_type" in craft, "Should use port_type (snake_case)"
    assert "fuel_type" in craft, "Should use fuel_type (snake_case)"
    assert "max_rcs" in craft, "Should use max_rcs (snake_case)"
    
    # Validate dimensions structure
    assert isinstance(craft["dimensions"], dict)
    assert "length" in craft["dimensions"]
    assert "width" in craft["dimensions"]
    assert "height" in craft["dimensions"]
    
    # Validate capabilities is array
    assert isinstance(craft["capabilities"], list)


@pytest.mark.integration
@pytest.mark.api
def test_fleet_bridge_specific_craft():
    """Test fetching specific craft by ID."""
    from api.aurora_api import app
    
    client = TestClient(app)
    
    # Try known vessel ID
    response = client.get("/api/fleet/craft/ORF-01")
    
    # Should return 200 (found), 404 (not in registry), or 503 (unavailable)
    assert response.status_code in [200, 404, 503]
    
    if response.status_code == 200:
        craft = response.json()
        assert craft["id"] == "ORF-01"
        assert "craft_class" in craft


@pytest.mark.integration
@pytest.mark.api
def test_fleet_bridge_status_endpoint():
    """Test fleet status summary endpoint."""
    from api.aurora_api import app
    
    client = TestClient(app)
    response = client.get("/api/fleet/status")
    
    if response.status_code != 200:
        pytest.skip("Fleet registry unavailable")
    
    status = response.json()
    
    # Validate status structure
    assert "total_craft" in status
    assert "active_vessels" in status
    assert "available_for_ops" in status
    assert "in_maintenance" in status
    assert "timestamp" in status
    
    # Validate types
    assert isinstance(status["total_craft"], int)
    assert isinstance(status["active_vessels"], int)
    assert isinstance(status["available_for_ops"], int)
    assert isinstance(status["in_maintenance"], int)
    assert isinstance(status["timestamp"], str)
