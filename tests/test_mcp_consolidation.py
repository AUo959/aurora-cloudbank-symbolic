"""
Tests for MCP Bridge Core consolidation.

Tests verify that all MCP bridge logic reads from the centralized mcp_bridge_core.json
configuration and that there is a single source of truth for capsules, security, and routing.
"""

import pytest
from modules.symbolic_core import (
    load_mcp_configuration,
    get_mcp_bridge_core,
    validate_security_layer,
    get_capsule,
)
from modules.symbolic_core.mcp_security import MCPSecurity
from modules.symbolic_core.mcp_command_router import MCPCommandRouter


class TestMCPConfigurationLoading:
    """Test configuration loading and caching."""

    def test_load_mcp_configuration(self):
        """Test that configuration loads successfully."""
        config = load_mcp_configuration()
        assert config is not None
        assert isinstance(config, dict)

    def test_configuration_has_required_fields(self):
        """Test that configuration contains all required fields."""
        config = load_mcp_configuration()

        # Core fields
        assert "module_id" in config
        assert "version" in config
        assert "anchor_seed" in config
        assert "ethics_protocol" in config
        assert "governance_layer" in config

        # Security fields
        assert "security_layers" in config
        assert "security_validation_rules" in config

        # Capsule fields
        assert "capsules" in config

        # Additional fields
        assert "anchor_validation" in config
        assert "ethics_enforcement" in config
        assert "health_check" in config

    def test_get_mcp_bridge_core_caching(self):
        """Test that configuration is cached properly."""
        config1 = get_mcp_bridge_core()
        config2 = get_mcp_bridge_core()
        assert config1 is config2  # Should be the same object (cached)


class TestSecurityValidation:
    """Test security layer validation from configuration."""

    def test_validate_drift_lock(self):
        """Test drift_lock validation against config rules."""
        # Valid state
        assert validate_security_layer("drift_lock", "ACTIVE") is True

        # Invalid state
        assert validate_security_layer("drift_lock", "INACTIVE") is False

    def test_validate_guardian_ring(self):
        """Test guardian_ring validation with multiple allowed states."""
        # Valid states
        assert validate_security_layer("guardian_ring", "ACTIVE") is True
        assert validate_security_layer("guardian_ring", "STAGED_ACTIVE") is True

        # Invalid state
        assert validate_security_layer("guardian_ring", "INACTIVE") is False

    def test_validate_ethics_lock(self):
        """Test ethics_lock validation."""
        # Valid state
        assert validate_security_layer("ethics_lock", "ENFORCED") is True

        # Invalid states
        assert validate_security_layer("ethics_lock", "STAGED") is False
        assert validate_security_layer("ethics_lock", "DISABLED") is False

    def test_validate_unknown_layer(self):
        """Test validation of layer not defined in config."""
        # Unknown layers should pass (no rules to validate against)
        assert validate_security_layer("unknown_layer", "ANY_VALUE") is True


class TestMCPSecurity:
    """Test MCPSecurity class reads from configuration."""

    def test_mcp_security_initialization(self):
        """Test that MCPSecurity initializes with config data."""
        security = MCPSecurity()

        assert security.mcp is not None
        assert security.security_layers is not None
        assert security.ethics_protocol is not None
        assert security.validation_rules is not None
        assert security.anchor_validation_config is not None
        assert security.ethics_enforcement_config is not None

    def test_enforce_security_valid(self):
        """Test security enforcement with valid configuration."""
        security = MCPSecurity()
        # Should not raise exception if all layers are valid
        try:
            security.enforce_security()
            # If we get here, security is valid
            assert True
        except Exception as e:
            # Check if the exception is due to actual invalid config
            pytest.fail(f"Security enforcement failed unexpectedly: {e}")

    def test_validate_anchor_valid(self):
        """Test anchor validation with correct seed."""
        security = MCPSecurity()
        config = get_mcp_bridge_core()
        anchor_seed = config.get("anchor_seed")

        # Valid anchor should not raise
        try:
            security.validate_anchor(anchor_seed)
            assert True
        except Exception as e:
            pytest.fail(f"Anchor validation failed unexpectedly: {e}")

    def test_validate_anchor_invalid(self):
        """Test anchor validation with incorrect seed."""
        from fastapi import HTTPException

        security = MCPSecurity()

        # Invalid anchor should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            security.validate_anchor("INVALID_SEED")

        assert exc_info.value.status_code == 401

    def test_get_capsule_security_level(self):
        """Test getting capsule security level from config."""
        security = MCPSecurity()

        # Test with known capsule
        level = security.get_capsule_security_level("OPPY")
        assert level in ["HIGH", "MEDIUM", "LOW", "UNKNOWN"]

        # Test with unknown capsule
        level = security.get_capsule_security_level("NONEXISTENT")
        assert level == "UNKNOWN"

    def test_get_security_summary(self):
        """Test security summary contains config data."""
        security = MCPSecurity()
        summary = security.get_security_summary()

        assert "security_layers" in summary
        assert "validation_rules" in summary
        assert "anchor_validation" in summary
        assert "ethics_enforcement" in summary
        assert "ethics_protocol" in summary
        assert "anchor_seed" in summary


class TestCapsuleConfiguration:
    """Test capsule definitions from configuration."""

    def test_get_capsule_exists(self):
        """Test retrieving existing capsule."""
        capsule = get_capsule("OPPY")
        assert capsule is not None
        assert capsule["id"] == "OPPY"
        assert "type" in capsule
        assert "status" in capsule
        assert "security_level" in capsule
        assert "capabilities" in capsule

    def test_get_capsule_not_exists(self):
        """Test retrieving non-existent capsule."""
        capsule = get_capsule("NONEXISTENT")
        assert capsule is None

    def test_all_capsules_have_required_fields(self):
        """Test that all capsules have required fields."""
        config = get_mcp_bridge_core()
        capsules = config.get("capsules", {})

        required_fields = ["id", "type", "status", "security_level", "capabilities"]

        for capsule_id, capsule_config in capsules.items():
            for field in required_fields:
                assert field in capsule_config, f"Capsule {capsule_id} missing {field}"

    def test_capsule_capabilities_are_lists(self):
        """Test that all capsule capabilities are lists."""
        config = get_mcp_bridge_core()
        capsules = config.get("capsules", {})

        for capsule_id, capsule_config in capsules.items():
            capabilities = capsule_config.get("capabilities", [])
            assert isinstance(capabilities, list), f"Capsule {capsule_id} capabilities not a list"


class TestMCPCommandRouter:
    """Test MCPCommandRouter reads from configuration."""

    def test_router_initialization(self):
        """Test that MCPCommandRouter initializes with config data."""
        router = MCPCommandRouter()

        assert router.mcp is not None
        assert router.governance_layer is not None
        assert router.routing_protocol is not None
        assert router.capsules is not None
        assert router.external_hooks is not None

    def test_route_command_basic(self):
        """Test basic command routing."""
        router = MCPCommandRouter()
        result = router.route("TEST_COMMAND")

        assert result["status"] == "ROUTED"
        assert "protocol" in result
        assert "routed_command" in result
        assert "governance_layer" in result

    def test_route_command_with_target_capsule(self):
        """Test command routing to specific capsule."""
        router = MCPCommandRouter()
        result = router.route("TEST_COMMAND", target_capsule="OPPY")

        assert result["status"] == "ROUTED"
        assert "target_capsule" in result
        assert "capsule_status" in result

    def test_route_command_with_invalid_capsule(self):
        """Test command routing to non-existent capsule."""
        router = MCPCommandRouter()
        result = router.route("TEST_COMMAND", target_capsule="NONEXISTENT")

        assert result["status"] == "ROUTED"
        assert result["target_capsule"] is None
        assert result["capsule_status"] == "NOT_FOUND"

    def test_get_available_capsules(self):
        """Test getting all available capsules."""
        router = MCPCommandRouter()
        capsules = router.get_available_capsules()

        assert isinstance(capsules, list)
        assert len(capsules) > 0

    def test_get_available_capsules_by_capability(self):
        """Test filtering capsules by capability."""
        router = MCPCommandRouter()
        capsules = router.get_available_capsules(capability="symbolic_routing")

        assert isinstance(capsules, list)
        # Each capsule should have the requested capability
        for capsule in capsules:
            assert "symbolic_routing" in capsule.get("capabilities", [])

    def test_get_capsule_capabilities(self):
        """Test getting capabilities for a capsule."""
        router = MCPCommandRouter()
        capabilities = router.get_capsule_capabilities("OPPY")

        assert isinstance(capabilities, list)
        assert len(capabilities) > 0

    def test_is_capsule_active(self):
        """Test checking if capsule is active."""
        router = MCPCommandRouter()

        # Test with existing active capsule
        is_active = router.is_capsule_active("OPPY")
        assert isinstance(is_active, bool)

        # Test with non-existent capsule
        is_active = router.is_capsule_active("NONEXISTENT")
        assert is_active is False

    def test_get_routing_summary(self):
        """Test getting routing summary."""
        router = MCPCommandRouter()
        summary = router.get_routing_summary()

        assert "governance_layer" in summary
        assert "core_functions" in summary
        assert "total_capsules" in summary
        assert "active_capsules" in summary
        assert "external_hooks" in summary
        assert "ethics_enforcement" in summary


class TestConfigurationConsistency:
    """Test that configuration is consistent and complete."""

    def test_gpt_parallel_nodes_match_capsules(self):
        """Test that all GPT parallel nodes have capsule definitions."""
        config = get_mcp_bridge_core()

        gpt_nodes = config.get("external_hooks", {}).get("gpt_parallel_nodes", [])
        capsules = config.get("capsules", {})

        for node_id in gpt_nodes:
            assert node_id in capsules, f"GPT node {node_id} has no capsule definition"

    def test_security_layers_have_validation_rules(self):
        """Test that all security layers have validation rules."""
        config = get_mcp_bridge_core()

        security_layers = config.get("security_layers", {})
        validation_rules = config.get("security_validation_rules", {})

        for layer_name in security_layers.keys():
            assert layer_name in validation_rules, f"Security layer {layer_name} has no validation rules"

    def test_validation_rules_have_required_fields(self):
        """Test that validation rules have required fields."""
        config = get_mcp_bridge_core()
        validation_rules = config.get("security_validation_rules", {})

        for rule_name, rule_config in validation_rules.items():
            assert "valid_states" in rule_config, f"Rule {rule_name} missing valid_states"
            assert "description" in rule_config, f"Rule {rule_name} missing description"
            # Must have either required_state or required_states
            assert "required_state" in rule_config or "required_states" in rule_config, \
                f"Rule {rule_name} missing required_state or required_states"

    def test_ethics_protocol_consistency(self):
        """Test that ethics protocol is consistent across config."""
        config = get_mcp_bridge_core()

        top_level_protocol = config.get("ethics_protocol")
        enforcement_protocol = config.get("ethics_enforcement", {}).get("protocol")

        assert top_level_protocol == enforcement_protocol, \
            "Ethics protocol mismatch between top level and enforcement config"

    def test_anchor_seed_consistency(self):
        """Test that anchor seed is properly configured."""
        config = get_mcp_bridge_core()

        anchor_seed = config.get("anchor_seed")
        allowed_seeds = config.get("anchor_validation", {}).get("allowed_seeds", [])

        assert anchor_seed in allowed_seeds, \
            "Current anchor_seed not in allowed_seeds list"


class TestHealthEndpointIntegration:
    """Test health endpoint integration with consolidated config.

    Note: These tests verify the configuration structure that the health endpoint
    would use, rather than directly testing the endpoint (which has a pre-existing
    syntax error in the containing file).
    """

    def test_config_has_health_endpoint_fields(self):
        """Test that configuration has all fields needed by health endpoint."""
        config = get_mcp_bridge_core()

        # Basic fields
        assert "module_id" in config
        assert "version" in config
        assert "governance_layer" in config

        # Security fields
        assert "security_layers" in config
        assert "security_validation_rules" in config

        # Capsule fields
        assert "capsules" in config

        # Anchor and ethics fields
        assert "anchor_validation" in config
        assert "ethics_enforcement" in config

        # Health check config
        assert "health_check" in config

    def test_capsule_summary_generation(self):
        """Test that we can generate capsule summary from config."""
        config = get_mcp_bridge_core()
        capsules = config.get("capsules", {})

        # Generate summary like health endpoint does
        total = len(capsules)
        active = sum(1 for c in capsules.values() if c.get("status") == "ACTIVE")
        inactive = total - active

        assert total > 0
        assert active >= 0
        assert inactive >= 0
        assert total == active + inactive

    def test_validation_rules_structure(self):
        """Test that validation rules have proper structure for health endpoint."""
        config = get_mcp_bridge_core()
        validation_rules = config.get("security_validation_rules", {})

        assert len(validation_rules) > 0

        # Check that rules have proper structure
        for rule_name, rule_config in validation_rules.items():
            assert "valid_states" in rule_config
            assert "description" in rule_config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
