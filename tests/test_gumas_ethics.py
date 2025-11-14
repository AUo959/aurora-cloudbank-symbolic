"""
Tests for GUMAS Ethics API

DLP: gumas_ethics_tests
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create test client for API testing"""
    from api.aurora_api import app
    return TestClient(app)


class TestGUMASEthicsAPI:
    """Test suite for GUMAS ethics endpoints"""
    
    def test_health_endpoint(self, test_client):
        """Test ethics API health check"""
        response = test_client.get("/gumas/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "gumas_ethics_api"
        assert "rules_loaded" in data
        assert "violations_recorded" in data
        assert "timestamp" in data
        assert data["rules_loaded"] >= 5  # Default rules
    
    def test_get_rules(self, test_client):
        """Test retrieving ethics rules"""
        response = test_client.get("/gumas/rules")
        assert response.status_code == 200
        
        rules = response.json()
        assert isinstance(rules, list)
        assert len(rules) >= 5  # At least default rules
        
        # Verify rule structure
        rule = rules[0]
        assert "id" in rule
        assert "name" in rule
        assert "description" in rule
        assert "category" in rule
        assert "severity" in rule
        assert "auto_block" in rule
        assert "conditions" in rule
    
    def test_get_specific_rule(self, test_client):
        """Test retrieving specific rule by ID"""
        response = test_client.get("/gumas/rules/SAFETY_001")
        assert response.status_code == 200
        
        rule = response.json()
        assert rule["id"] == "SAFETY_001"
        assert rule["name"] == "Life Safety Priority"
        assert rule["auto_block"] is True
    
    def test_evaluate_compliant_action(self, test_client):
        """Test evaluating a compliant action"""
        response = test_client.post("/gumas/evaluate", json={
            "agent_id": "test_agent",
            "action_type": "safe_operation",
            "parameters": {}
        })
        assert response.status_code == 200
        
        result = response.json()
        assert result["compliant"] is True
        assert result["should_block"] is False
        assert len(result["violations"]) == 0
    
    def test_evaluate_non_compliant_action(self, test_client):
        """Test evaluating action with ethics violation"""
        response = test_client.post("/gumas/evaluate", json={
            "agent_id": "test_agent",
            "action_type": "risky_operation",
            "parameters": {
                "risk_to_life": 1.0,
                "safety_override_missing": True
            }
        })
        assert response.status_code == 200
        
        result = response.json()
        assert result["compliant"] is False
        assert result["should_block"] is True
        assert len(result["violations"]) > 0
        
        violation = result["violations"][0]
        assert violation["rule_id"] == "SAFETY_001"
        assert violation["blocked"] is True
    
    def test_get_categories(self, test_client):
        """Test retrieving rule categories"""
        response = test_client.get("/gumas/categories")
        assert response.status_code == 200
        
        categories = response.json()
        assert "mission_ethics" in categories
        assert "ai_ethics" in categories
        assert "safety" in categories
    
    def test_get_severities(self, test_client):
        """Test retrieving severity levels"""
        response = test_client.get("/gumas/severities")
        assert response.status_code == 200
        
        severities = response.json()
        assert "low" in severities
        assert "medium" in severities
        assert "high" in severities
        assert "critical" in severities
    
    def test_add_custom_rule(self, test_client):
        """Test adding a custom ethics rule"""
        response = test_client.post("/gumas/rules", json={
            "id": "TEST_001",
            "name": "Test Rule",
            "description": "Test ethics rule for validation",
            "category": "ai_ethics",
            "severity": "medium",
            "auto_block": False,
            "conditions": ["test_condition"],
            "metadata": {"test": True}
        })
        assert response.status_code == 201
        
        rule = response.json()
        assert rule["id"] == "TEST_001"
        assert rule["name"] == "Test Rule"
    
    def test_delete_rule(self, test_client):
        """Test deleting a rule"""
        # First add a rule
        test_client.post("/gumas/rules", json={
            "id": "DELETE_TEST",
            "name": "Delete Test",
            "description": "Rule to be deleted",
            "category": "ai_ethics",
            "severity": "low",
            "auto_block": False,
            "conditions": []
        })
        
        # Then delete it
        response = test_client.delete("/gumas/rules/DELETE_TEST")
        assert response.status_code == 204
        
        # Verify it's gone
        response = test_client.get("/gumas/rules/DELETE_TEST")
        assert response.status_code == 404
