"""
Comprehensive Test Suite for GUMAS Ethics API Routes

Tests all API endpoints in modules/gumas/api/routes.py:
- Health check endpoint
- Action evaluation endpoint
- Violations query endpoint
- Rules management endpoints
- Error handling and validation

DLP: T1-GUMAS-API-TEST
Chain: #test/gumas/api/001
Target: 95%+ code coverage
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-gumas-api")

from api.aurora_api import app  # noqa: E402
from src.monitoring.ethics_engine import (
    EthicsEngine,
    EthicsRule,
    ViolationSeverity,
    RuleCategory
)
from src.middleware.fastapi_security import generate_csrf_token

# Create test client
client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    # GlobalCsrfMiddleware checks X-CSRF-Token on unsafe methods; the
    # require_csrf_token route dependency reads the bearer credentials.
    token = generate_csrf_token('gumas-test-session')
    return {"Authorization": f"Bearer {token}", "X-CSRF-Token": token}


@pytest.fixture
def clean_ethics_engine():
    """Fixture to provide a clean ethics engine for each test."""
    from modules.gumas.api.routes import ethics_engine
    # Clear existing violations and rules
    ethics_engine.violations.clear()
    original_rules = dict(ethics_engine.rules)
    yield ethics_engine
    # Restore original rules after test
    ethics_engine.rules = original_rules
    ethics_engine.violations.clear()


@pytest.mark.api
@pytest.mark.unit
class TestGumasHealthEndpoint:
    """Test GUMAS health check endpoint."""

    def test_health_check_success(self):
        """Test health check returns success."""
        response = client.get("/gumas/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "gumas_ethics_api"
        assert "rules_loaded" in data
        assert "violations_recorded" in data
        assert "timestamp" in data

    def test_health_check_response_structure(self):
        """Test health check response has correct structure."""
        response = client.get("/gumas/health")
        data = response.json()

        required_fields = ["status", "service", "rules_loaded", "violations_recorded", "timestamp"]
        for field in required_fields:
            assert field in data

    def test_health_check_timestamp_format(self):
        """Test health check timestamp is ISO format."""
        response = client.get("/gumas/health")
        data = response.json()

        # Should be parseable as ISO timestamp
        timestamp = datetime.fromisoformat(data["timestamp"])
        assert timestamp is not None


@pytest.mark.api
@pytest.mark.critical
class TestGumasEvaluateAction:
    """Test action evaluation endpoint."""

    def test_evaluate_action_success(self, clean_ethics_engine):
        """Test evaluating a compliant action."""
        request_data = {
            "agent_id": "test_agent",
            "action_type": "data_access",
            "parameters": {"resource": "public_data"},
            "context_tag": "test_evaluation"
        }

        response = client.post("/gumas/evaluate", json=request_data, headers=_auth_headers())

        assert response.status_code == 200
        data = response.json()

        assert "compliant" in data
        assert "should_block" in data
        assert "violations" in data
        assert "evaluation_timestamp" in data

    def test_evaluate_action_with_violation(self, clean_ethics_engine):
        """Test evaluating an action that triggers violation."""
        # Add a test rule that will be violated
        test_rule = EthicsRule(
            id="test_violation_rule",
            name="Test Violation Rule",
            description="Test rule for violations",
            category=RuleCategory.SAFETY,
            severity=ViolationSeverity.HIGH,
            auto_block=True,
            conditions=["action_type == 'forbidden_action'"],
            metadata={}
        )
        clean_ethics_engine.add_rule(test_rule)

        request_data = {
            "agent_id": "test_agent",
            "action_type": "forbidden_action",
            "parameters": {},
        }

        response = client.post("/gumas/evaluate", json=request_data, headers=_auth_headers())

        assert response.status_code == 200
        data = response.json()

        # Should detect violation
        assert data["compliant"] is False
        assert data["should_block"] is True
        assert len(data["violations"]) > 0

    def test_evaluate_action_missing_fields(self):
        """Test evaluation with missing required fields."""
        request_data = {
            "agent_id": "test_agent",
            # Missing action_type
        }

        response = client.post("/gumas/evaluate", json=request_data, headers=_auth_headers())

        assert response.status_code == 422  # Validation error

    def test_evaluate_action_empty_parameters(self, clean_ethics_engine):
        """Test evaluation with empty parameters."""
        request_data = {
            "agent_id": "test_agent",
            "action_type": "test_action",
            "parameters": {},
        }

        response = client.post("/gumas/evaluate", json=request_data, headers=_auth_headers())

        assert response.status_code == 200

    def test_evaluate_action_with_context_tag(self, clean_ethics_engine):
        """Test evaluation includes context tag in response."""
        request_data = {
            "agent_id": "test_agent",
            "action_type": "test_action",
            "parameters": {},
            "context_tag": "custom_context_123"
        }

        response = client.post("/gumas/evaluate", json=request_data, headers=_auth_headers())

        assert response.status_code == 200
        data = response.json()
        assert data["context_tag"] == "custom_context_123"


@pytest.mark.api
@pytest.mark.unit
class TestGumasViolationsQuery:
    """Test violations query endpoint."""

    def test_get_violations_empty(self, clean_ethics_engine):
        """Test getting violations when none exist."""
        request_data = {
            "limit": 100
        }

        response = client.post("/gumas/violations", json=request_data, headers=_auth_headers())

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_violations_with_limit(self, clean_ethics_engine):
        """Test violations query respects limit parameter."""
        request_data = {
            "limit": 5
        }

        response = client.post("/gumas/violations", json=request_data, headers=_auth_headers())

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_get_violations_invalid_severity(self):
        """Test violations query with invalid severity."""
        request_data = {
            "severity": "INVALID_SEVERITY"
        }

        response = client.post("/gumas/violations", json=request_data, headers=_auth_headers())

        # Should return 400 for invalid parameter
        assert response.status_code == 400
        assert "Invalid parameter" in response.json()["detail"]

    def test_get_violations_invalid_category(self):
        """Test violations query with invalid category."""
        request_data = {
            "category": "INVALID_CATEGORY"
        }

        response = client.post("/gumas/violations", json=request_data, headers=_auth_headers())

        assert response.status_code == 400

    def test_get_violations_with_agent_filter(self, clean_ethics_engine):
        """Test filtering violations by agent ID."""
        request_data = {
            "agent_id": "specific_agent",
            "limit": 100
        }

        response = client.post("/gumas/violations", json=request_data, headers=_auth_headers())

        assert response.status_code == 200

    def test_get_violations_limit_validation(self):
        """Test limit parameter validation."""
        # Test minimum limit
        request_data = {"limit": 1}
        response = client.post("/gumas/violations", json=request_data, headers=_auth_headers())
        assert response.status_code == 200

        # Test maximum limit
        request_data = {"limit": 1000}
        response = client.post("/gumas/violations", json=request_data, headers=_auth_headers())
        assert response.status_code == 200

        # Test exceeding maximum
        request_data = {"limit": 2000}
        response = client.post("/gumas/violations", json=request_data, headers=_auth_headers())
        assert response.status_code == 422  # Validation error


@pytest.mark.api
@pytest.mark.critical
class TestGumasRulesManagement:
    """Test rules management endpoints."""

    def test_get_all_rules(self, clean_ethics_engine):
        """Test getting all ethics rules."""
        response = client.get("/gumas/rules")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_rules_structure(self, clean_ethics_engine):
        """Test rules list response structure."""
        response = client.get("/gumas/rules")
        data = response.json()

        if len(data) > 0:
            rule = data[0]
            required_fields = ["id", "name", "description", "category", "severity", "auto_block", "conditions", "metadata"]
            for field in required_fields:
                assert field in rule

    def test_get_specific_rule(self, clean_ethics_engine):
        """Test getting a specific rule by ID."""
        # First, add a test rule
        test_rule = EthicsRule(
            id="test_rule_123",
            name="Test Rule",
            description="Test rule description",
            category=RuleCategory.SAFETY,
            severity=ViolationSeverity.MEDIUM,
            auto_block=False,
            conditions=["test_condition"],
            metadata={"test": "data"}
        )
        clean_ethics_engine.add_rule(test_rule)

        response = client.get("/gumas/rules/test_rule_123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_rule_123"
        assert data["name"] == "Test Rule"

    def test_get_nonexistent_rule(self, clean_ethics_engine):
        """Test getting a rule that doesn't exist."""
        response = client.get("/gumas/rules/nonexistent_rule_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_add_new_rule(self, clean_ethics_engine):
        """Test adding a new ethics rule."""
        new_rule = {
            "id": "new_test_rule",
            "name": "New Test Rule",
            "description": "A new rule for testing",
            "category": "safety",
            "severity": "medium",
            "auto_block": True,
            "conditions": ["test == true"],
            "metadata": {"created_by": "test"}
        }

        response = client.post("/gumas/rules", json=new_rule, headers=_auth_headers())

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "new_test_rule"
        assert data["name"] == "New Test Rule"

    def test_add_duplicate_rule(self, clean_ethics_engine):
        """Test adding a rule with duplicate ID."""
        rule_data = {
            "id": "duplicate_rule",
            "name": "Duplicate Rule",
            "description": "Test duplicate",
            "category": "safety",
            "severity": "low",
            "auto_block": False,
            "conditions": [],
            "metadata": {}
        }

        # Add rule first time
        response1 = client.post("/gumas/rules", json=rule_data, headers=_auth_headers())
        assert response1.status_code == 201

        # Try to add again
        response2 = client.post("/gumas/rules", json=rule_data, headers=_auth_headers())
        assert response2.status_code == 409  # Conflict
        assert "already exists" in response2.json()["detail"]

    def test_add_rule_invalid_category(self, clean_ethics_engine):
        """Test adding rule with invalid category."""
        rule_data = {
            "id": "invalid_category_rule",
            "name": "Invalid Category",
            "description": "Test",
            "category": "INVALID_CATEGORY",
            "severity": "low",
            "auto_block": False,
            "conditions": [],
            "metadata": {}
        }

        response = client.post("/gumas/rules", json=rule_data, headers=_auth_headers())

        assert response.status_code == 400
        assert "Invalid parameter" in response.json()["detail"]

    def test_add_rule_invalid_severity(self, clean_ethics_engine):
        """Test adding rule with invalid severity."""
        rule_data = {
            "id": "invalid_severity_rule",
            "name": "Invalid Severity",
            "description": "Test",
            "category": "safety",
            "severity": "INVALID_SEVERITY",
            "auto_block": False,
            "conditions": [],
            "metadata": {}
        }

        response = client.post("/gumas/rules", json=rule_data, headers=_auth_headers())

        assert response.status_code == 400

    def test_delete_rule(self, clean_ethics_engine):
        """Test deleting an ethics rule."""
        # Add a rule first
        test_rule = EthicsRule(
            id="rule_to_delete",
            name="Rule To Delete",
            description="This will be deleted",
            category=RuleCategory.SAFETY,
            severity=ViolationSeverity.LOW,
            auto_block=False,
            conditions=[],
            metadata={}
        )
        clean_ethics_engine.add_rule(test_rule)

        # Delete the rule
        response = client.delete("/gumas/rules/rule_to_delete", headers=_auth_headers())

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get("/gumas/rules/rule_to_delete")
        assert get_response.status_code == 404

    def test_delete_nonexistent_rule(self, clean_ethics_engine):
        """Test deleting a rule that doesn't exist."""
        response = client.delete("/gumas/rules/nonexistent_rule", headers=_auth_headers())

        assert response.status_code == 404


@pytest.mark.api
@pytest.mark.unit
class TestGumasUtilityEndpoints:
    """Test utility endpoints."""

    def test_get_categories(self):
        """Test getting all available rule categories."""
        response = client.get("/gumas/categories")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Should include standard categories
        categories = [cat.lower() for cat in data]
        assert "safety" in categories or any("safety" in cat.lower() for cat in data)

    def test_get_severities(self):
        """Test getting all available violation severity levels."""
        response = client.get("/gumas/severities")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Should include standard severities
        severities = [sev.lower() for sev in data]
        assert "low" in severities or any("low" in sev.lower() for sev in data)
        assert "medium" in severities or any("medium" in sev.lower() for sev in data)
        assert "high" in severities or any("high" in sev.lower() for sev in data)

    def test_clear_violations(self, clean_ethics_engine):
        """Test clearing old violations."""
        response = client.delete("/gumas/violations", headers=_auth_headers())

        assert response.status_code == 204

    def test_clear_violations_with_timestamp(self, clean_ethics_engine):
        """Test clearing violations before specific timestamp."""
        from urllib.parse import quote
        timestamp = datetime.now(timezone.utc).isoformat()
        # URL-encode the timestamp to handle the + in timezone offset
        encoded_timestamp = quote(timestamp, safe='')

        response = client.delete(f"/gumas/violations?before={encoded_timestamp}", headers=_auth_headers())

        assert response.status_code == 204

    def test_clear_violations_invalid_timestamp(self, clean_ethics_engine):
        """Test clearing violations with invalid timestamp."""
        response = client.delete("/gumas/violations?before=invalid_timestamp", headers=_auth_headers())

        assert response.status_code == 400
        assert "Invalid timestamp" in response.json()["detail"]

    def test_register_evaluator_not_implemented(self):
        """Test that custom evaluator registration returns 501."""
        response = client.post(
            "/gumas/rules/test_rule/register-evaluator?condition=test_condition",
            headers=_auth_headers(),
        )

        assert response.status_code == 501
        assert "must be registered programmatically" in response.json()["detail"]


@pytest.mark.integration
@pytest.mark.api
class TestGumasApiIntegration:
    """Integration tests for GUMAS API workflows."""

    def test_complete_rule_lifecycle(self, clean_ethics_engine):
        """Test complete workflow: add rule, use it, delete it."""
        # 1. Add a new rule
        new_rule = {
            "id": "lifecycle_test_rule",
            "name": "Lifecycle Test",
            "description": "Test full lifecycle",
            "category": "safety",
            "severity": "high",
            "auto_block": True,
            "conditions": ["action_type == 'blocked_action'"],
            "metadata": {"test": "lifecycle"}
        }

        add_response = client.post("/gumas/rules", json=new_rule, headers=_auth_headers())
        assert add_response.status_code == 201

        # 2. Verify rule exists
        get_response = client.get("/gumas/rules/lifecycle_test_rule")
        assert get_response.status_code == 200

        # 3. Use rule to evaluate an action
        eval_request = {
            "agent_id": "test_agent",
            "action_type": "blocked_action",
            "parameters": {}
        }

        eval_response = client.post("/gumas/evaluate", json=eval_request, headers=_auth_headers())
        assert eval_response.status_code == 200

        # 4. Delete the rule
        delete_response = client.delete("/gumas/rules/lifecycle_test_rule", headers=_auth_headers())
        assert delete_response.status_code == 204

        # 5. Verify rule is deleted
        get_after_delete = client.get("/gumas/rules/lifecycle_test_rule")
        assert get_after_delete.status_code == 404

    def test_multi_rule_evaluation(self, clean_ethics_engine):
        """Test evaluation with multiple rules."""
        # Add multiple rules
        rules = [
            {
                "id": f"multi_rule_{i}",
                "name": f"Multi Rule {i}",
                "description": f"Test rule {i}",
                "category": "safety",
                "severity": "medium",
                "auto_block": False,
                "conditions": [],
                "metadata": {}
            }
            for i in range(3)
        ]

        for rule in rules:
            response = client.post("/gumas/rules", json=rule, headers=_auth_headers())
            assert response.status_code == 201

        # Verify all rules are present
        all_rules = client.get("/gumas/rules")
        rule_ids = [r["id"] for r in all_rules.json()]

        for i in range(3):
            assert f"multi_rule_{i}" in rule_ids

        # Clean up
        for i in range(3):
            client.delete(f"/gumas/rules/multi_rule_{i}", headers=_auth_headers())


@pytest.mark.api
@pytest.mark.security
class TestGumasApiSecurity:
    """Test API security considerations."""

    def test_add_rule_requires_auth_before_mutation(self, clean_ethics_engine):
        """Unauthenticated callers cannot add ethics rules."""
        rule_data = {
            "id": "unauthenticated_rule",
            "name": "Unauthenticated Rule",
            "description": "Should not be added",
            "category": "safety",
            "severity": "low",
            "auto_block": False,
            "conditions": [],
            "metadata": {}
        }

        response = client.post("/gumas/rules", json=rule_data)

        assert response.status_code in (401, 403)
        assert "unauthenticated_rule" not in clean_ethics_engine.rules

    def test_delete_rule_requires_auth_before_mutation(self, clean_ethics_engine):
        """Unauthenticated callers cannot delete ethics rules."""
        clean_ethics_engine.add_rule(EthicsRule(
            id="protected_rule",
            name="Protected Rule",
            description="Should remain present",
            category=RuleCategory.SAFETY,
            severity=ViolationSeverity.LOW,
            auto_block=False,
            conditions=[],
            metadata={}
        ))

        response = client.delete("/gumas/rules/protected_rule")

        assert response.status_code in (401, 403)
        assert "protected_rule" in clean_ethics_engine.rules

    def test_clear_violations_requires_auth_before_mutation(self, clean_ethics_engine):
        """Unauthenticated callers cannot clear recorded violations."""
        violation_marker = object()
        clean_ethics_engine.violations.append(violation_marker)

        response = client.delete("/gumas/violations")

        assert response.status_code in (401, 403)
        assert clean_ethics_engine.violations == [violation_marker]

    def test_input_validation_prevents_injection(self, clean_ethics_engine):
        """Test that input validation prevents injection attacks."""
        malicious_rule = {
            "id": "'; DROP TABLE rules; --",
            "name": "<script>alert('xss')</script>",
            "description": "Test injection",
            "category": "safety",
            "severity": "low",
            "auto_block": False,
            "conditions": [],
            "metadata": {}
        }

        response = client.post("/gumas/rules", json=malicious_rule, headers=_auth_headers())

        # Should either succeed with sanitized input or fail validation
        # But should not cause server errors
        assert response.status_code in [201, 400, 422]

    def test_large_payload_handling(self, clean_ethics_engine):
        """Test handling of very large payloads."""
        large_metadata = {"data": "x" * 10000}

        rule_data = {
            "id": "large_payload_rule",
            "name": "Large Payload",
            "description": "Test large data",
            "category": "safety",
            "severity": "low",
            "auto_block": False,
            "conditions": [],
            "metadata": large_metadata
        }

        response = client.post("/gumas/rules", json=rule_data, headers=_auth_headers())

        # Should handle large payloads gracefully
        assert response.status_code in [201, 413, 422]
