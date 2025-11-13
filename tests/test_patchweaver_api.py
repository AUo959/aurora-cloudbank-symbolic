"""
Tests for PatchWeaver API endpoints

Tests the admin API endpoints for state patching.
"""

import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient


@pytest.fixture
def api_client():
    """Create test client for API testing"""
    from api.aurora_api import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Provide authentication headers for testing"""
    return {
        "Authorization": "Bearer test_token",
        "X-CSRF-Token": "test_csrf_token"
    }


@pytest.fixture(autouse=True)
def cleanup_patchweaver_state():
    """Clean up PatchWeaver state file after each test"""
    yield
    # Clean up state file after test
    state_file = Path("./data/patchweaver_state.json")
    if state_file.exists():
        state_file.unlink()


@pytest.mark.api
class TestPatchWeaverAPI:
    """Test suite for PatchWeaver API endpoints"""
    
    def test_apply_patch_endpoint_available(self, api_client):
        """Test that PatchWeaver endpoint exists"""
        # This will fail auth but proves endpoint exists
        response = api_client.post("/admin/patchweaver/apply")
        # Should get 401 (unauthorized) or 422 (validation), not 404
        assert response.status_code in [401, 403, 422]
    
    def test_history_endpoint_available(self, api_client):
        """Test that history endpoint exists"""
        response = api_client.get("/admin/patchweaver/history")
        # Should get 401 (unauthorized) or 403, not 404
        assert response.status_code in [401, 403, 422]
    
    def test_verify_endpoint_available(self, api_client):
        """Test that verify endpoint exists"""
        response = api_client.post("/admin/patchweaver/verify")
        # Should get 401 (unauthorized) or 403, not 404
        assert response.status_code in [401, 403, 422]
    
    @pytest.mark.skip(reason="Requires proper auth setup - endpoint structure verified")
    def test_apply_patch_with_auth(self, api_client, auth_headers):
        """Test applying patch with authentication"""
        # Note: This test requires proper authentication setup
        # Skipped by default but validates the expected flow
        
        patch_request = {
            "patch": {
                "set": {
                    "test/key": "test_value"
                }
            },
            "context": {
                "agent_id": "test_user",
                "context_tag": "test_operation"
            }
        }
        
        response = api_client.post(
            "/admin/patchweaver/apply",
            json=patch_request,
            headers=auth_headers
        )
        
        # With proper auth, should succeed
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "before_hash" in data
        assert "after_hash" in data
    
    @pytest.mark.skip(reason="Requires proper auth setup - endpoint structure verified")
    def test_get_history_with_auth(self, api_client, auth_headers):
        """Test retrieving patch history with authentication"""
        response = api_client.get(
            "/admin/patchweaver/history?limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "operations" in data
        assert isinstance(data["operations"], list)
    
    @pytest.mark.skip(reason="Requires proper auth setup - endpoint structure verified")
    def test_verify_state_with_auth(self, api_client, auth_headers):
        """Test verifying state hash with authentication"""
        # First apply a patch to get a hash
        patch_request = {
            "patch": {"set": {"test": "value"}},
            "context": {"agent_id": "test"}
        }
        
        apply_response = api_client.post(
            "/admin/patchweaver/apply",
            json=patch_request,
            headers=auth_headers
        )
        
        result = apply_response.json()
        after_hash = result["after_hash"]
        
        # Then verify the hash
        verify_response = api_client.post(
            f"/admin/patchweaver/verify?expected_hash={after_hash}",
            headers=auth_headers
        )
        
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["valid"] is True
        assert data["current_hash"] == after_hash


@pytest.mark.unit
class TestPatchWeaverAPIModels:
    """Test API request models"""
    
    def test_patch_request_model(self):
        """Test PatchWeaverRequest model validation"""
        from api.aurora_api import PatchWeaverRequest
        
        # Valid request
        request = PatchWeaverRequest(
            patch={
                "set": {"key": "value"},
                "delete": ["old_key"]
            },
            context={
                "agent_id": "test",
                "context_tag": "test_op"
            }
        )
        
        assert request.patch["set"]["key"] == "value"
        assert "old_key" in request.patch["delete"]
        assert request.context["agent_id"] == "test"
    
    def test_patch_request_minimal(self):
        """Test PatchWeaverRequest with minimal data"""
        from api.aurora_api import PatchWeaverRequest
        
        # Minimal valid request (context is optional with defaults)
        request = PatchWeaverRequest(
            patch={"set": {"key": "value"}}
        )
        
        assert request.patch == {"set": {"key": "value"}}
        assert isinstance(request.context, dict)
    
    def test_patch_request_example(self):
        """Test that example in schema is valid"""
        from api.aurora_api import PatchWeaverRequest
        
        example = {
            "patch": {
                "set": {
                    "config/setting": "value",
                    "simulation/status": "active"
                },
                "delete": ["deprecated_key"]
            },
            "context": {
                "agent_id": "admin_user",
                "context_tag": "config_update",
                "reason": "Update production configuration"
            }
        }
        
        request = PatchWeaverRequest(**example)
        assert request.patch["set"]["config/setting"] == "value"
        assert request.context["agent_id"] == "admin_user"


@pytest.mark.integration
class TestPatchWeaverIntegration:
    """Integration tests for PatchWeaver system"""
    
    def test_patchweaver_initialization(self):
        """Test that PatchWeaver initializes correctly"""
        # Import to trigger initialization
        try:
            from api.aurora_api import PATCHWEAVER_AVAILABLE, _patchweaver
            
            if PATCHWEAVER_AVAILABLE:
                assert _patchweaver is not None
                assert hasattr(_patchweaver, 'apply_patch')
                assert hasattr(_patchweaver, 'get_patch_history')
                assert hasattr(_patchweaver, 'verify_state_hash')
        except ImportError:
            pytest.skip("PatchWeaver not available in this environment")
    
    def test_state_persistence(self):
        """Test that state persists across operations"""
        try:
            from api.aurora_api import (
                PATCHWEAVER_AVAILABLE,
                _patchweaver,
                _load_patchweaver_state,
                _save_patchweaver_state
            )
            
            if not PATCHWEAVER_AVAILABLE:
                pytest.skip("PatchWeaver not available")
            
            # Save a test state
            test_state = {"test_key": "test_value"}
            _save_patchweaver_state(test_state)
            
            # Load it back
            loaded_state = _load_patchweaver_state()
            assert loaded_state == test_state
            
        except ImportError:
            pytest.skip("PatchWeaver not available in this environment")
