"""
Test suite for Issue #325 - NoSQL/Dictionary Injection Prevention

Tests validation of AgentSessionRequest to ensure:
1. Action field is constrained to valid enum values
2. State data keys are whitelisted
3. Dangerous patterns are rejected
"""

import pytest
from pydantic import ValidationError

from api.aurora_api import AgentSessionRequest


class TestSessionActionValidation:
    """Test action field enum constraints"""
    
    def test_valid_actions(self):
        """Valid actions should be accepted"""
        for action in ["create", "update", "get", "delete"]:
            req = AgentSessionRequest(action=action)
            assert req.action == action
    
    def test_invalid_action_rejected(self):
        """Invalid actions should raise validation error"""
        with pytest.raises(ValidationError) as exc_info:
            AgentSessionRequest(action="malicious; DROP TABLE users;")
        
        assert "action" in str(exc_info.value).lower()
    
    def test_empty_action_rejected(self):
        """Empty action should be rejected"""
        with pytest.raises(ValidationError):
            AgentSessionRequest(action="")
    
    def test_sql_injection_action_rejected(self):
        """SQL injection attempts in action should be rejected"""
        malicious_actions = [
            "'; DROP TABLE sessions;--",
            "update; DELETE FROM users",
            "1' OR '1'='1",
        ]
        for malicious in malicious_actions:
            with pytest.raises(ValidationError):
                AgentSessionRequest(action=malicious)


class TestStateDataValidation:
    """Test state_data dictionary validation"""
    
    def test_valid_state_data_keys(self):
        """Valid state_data keys should be accepted"""
        valid_data = {
            "preference": "dark_mode",
            "theme": "blue",
            "context": "dashboard",
            "metadata": {"version": "1.0"},
            "settings": {"notifications": True},
            "config": {"timeout": 30},
            "options": {"verbose": False}
        }
        req = AgentSessionRequest(action="create", state_data=valid_data)
        assert req.state_data == valid_data
    
    def test_invalid_state_data_keys_rejected(self):
        """Invalid state_data keys should be rejected"""
        invalid_data = {"malicious_key": "value", "preference": "dark"}
        
        with pytest.raises(ValidationError) as exc_info:
            AgentSessionRequest(action="create", state_data=invalid_data)
        
        assert "malicious_key" in str(exc_info.value)
    
    def test_none_state_data_allowed(self):
        """None state_data should be allowed"""
        req = AgentSessionRequest(action="get", state_data=None)
        assert req.state_data is None
    
    def test_empty_state_data_allowed(self):
        """Empty state_data dict should be allowed"""
        req = AgentSessionRequest(action="get", state_data={})
        assert req.state_data == {}


class TestInjectionPatternDetection:
    """Test detection of dangerous injection patterns"""
    
    def test_nosql_injection_patterns_rejected(self):
        """NoSQL injection patterns should be rejected"""
        malicious_patterns = [
            {"$where": "function() { return true; }"},
            {"$regex": ".*"},
        ]
        
        for malicious in malicious_patterns:
            with pytest.raises(ValidationError) as exc_info:
                AgentSessionRequest(action="create", state_data=malicious)
            # Key whitelist catches malicious keys
            assert "invalid state_data keys" in str(exc_info.value).lower()
        
        # Pattern detection in values
        malicious_value = {"preference": "$where: malicious"}
        with pytest.raises(ValidationError) as exc_info:
            AgentSessionRequest(action="create", state_data=malicious_value)
        assert "pattern" in str(exc_info.value).lower()
    
    def test_prototype_pollution_rejected(self):
        """Prototype pollution attempts should be rejected"""
        malicious_patterns = [
            {"__proto__": {"isAdmin": True}},
            {"constructor": {"prototype": {"isAdmin": True}}},
            {"prototype": "malicious"},
        ]
        
        for malicious in malicious_patterns:
            with pytest.raises(ValidationError) as exc_info:
                AgentSessionRequest(action="update", state_data=malicious)
            # Key whitelist or pattern detection catches these
            error_msg = str(exc_info.value).lower()
            assert "invalid state_data keys" in error_msg or "pattern" in error_msg
    
    def test_dangerous_pattern_in_value(self):
        """Dangerous patterns in values should be detected"""
        malicious_data = {"preference": "__proto__.isAdmin = true"}
        
        with pytest.raises(ValidationError) as exc_info:
            AgentSessionRequest(action="create", state_data=malicious_data)
        assert "pattern" in str(exc_info.value).lower()


class TestIntegrationScenarios:
    """Test realistic usage scenarios"""
    
    def test_create_session_with_preferences(self):
        """Creating session with user preferences"""
        req = AgentSessionRequest(
            action="create",
            state_data={
                "theme": "dark",
                "preference": "compact_view",
                "settings": {"language": "en"}
            }
        )
        assert req.action == "create"
        assert "theme" in req.state_data
    
    def test_update_session_minimal(self):
        """Updating session with minimal data"""
        req = AgentSessionRequest(
            action="update",
            session_id="test-123",
            state_data={"context": "updated"}
        )
        assert req.session_id == "test-123"
    
    def test_get_session_no_state_data(self):
        """Getting session without state data"""
        req = AgentSessionRequest(
            action="get",
            session_id="test-456"
        )
        assert req.action == "get"
        assert req.state_data is None
    
    def test_delete_session(self):
        """Deleting session"""
        req = AgentSessionRequest(
            action="delete",
            session_id="test-789"
        )
        assert req.action == "delete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
