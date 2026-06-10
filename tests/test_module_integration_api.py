"""
Integration tests for OPPY Navigator, HR Module, and Quantum Forge FastAPI endpoints.

Tests the integration of modules into the MCP FastAPI server with proper
DLP tracking, anchor protocols, and ethics enforcement.

T1: MODULE_INTEGRATION_TEST
SRB: API_INTEGRATION_TEST
DLP: context_tag=module_integration_test

Run with: pytest tests/test_module_integration_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

# Set required environment variables for testing. setdefault, not assignment:
# a direct write at import time changes the secret AFTER other test modules
# have bound it into fastapi_security's module constant, so tokens they
# generate no longer match what GlobalCsrfMiddleware (which re-reads the env
# lazily at first request) validates against.
os.environ.setdefault("CSRF_SECRET_KEY", "test_csrf_secret_key_for_integration_tests_only")
os.environ.setdefault("WS_AUTH_SECRET", "test_ws_auth_secret_for_integration_tests_only")


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    from api.aurora_gui_cloudhub_fastapi import app
    return TestClient(app)


@pytest.fixture
def mock_csrf_token():
    """Mock CSRF token validation for tests"""
    with patch("src.middleware.fastapi_security.verify_csrf_token", return_value=None):
        with patch("api.aurora_gui_cloudhub_fastapi.verify_csrf_token", return_value=None):
            yield


# ============================================================================
# OPPY NAVIGATOR TESTS
# ============================================================================

@pytest.mark.integration
def test_oppy_plan_maneuver_endpoint(client, mock_csrf_token):
    """Test OPPY plan maneuver endpoint"""
    response = client.post(
        "/oppy/plan_maneuver",
        json={
            "vessel_id": "TEST_VESSEL_001",
            "maneuver_type": "orbital_insertion",
            "target_state": {"velocity_change": 25.0}
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert response.status_code in [200, 503]  # 503 if module not available
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "plan" in data
        assert data["context_tag"] == "oppy_plan_maneuver"
        assert "anchor" in data
        assert data["plan"]["vessel_id"] == "TEST_VESSEL_001"


@pytest.mark.integration
def test_oppy_get_telemetry_endpoint(client):
    """Test OPPY get telemetry endpoint"""
    response = client.get("/oppy/telemetry/TEST_VESSEL_001")
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "telemetry" in data
        assert data["context_tag"] == "oppy_telemetry"
        assert data["telemetry"]["vessel_id"] == "TEST_VESSEL_001"


@pytest.mark.integration
def test_oppy_get_state_endpoint(client):
    """Test OPPY get state endpoint"""
    response = client.get("/oppy/state/TEST_VESSEL_001")
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "state" in data
        assert data["context_tag"] == "oppy_state"
        assert data["state"]["vessel_id"] == "TEST_VESSEL_001"


# ============================================================================
# HR MODULE TESTS
# ============================================================================

@pytest.mark.integration
def test_hr_assess_psychological_safety_endpoint(client, mock_csrf_token):
    """Test HR psychological safety assessment endpoint"""
    response = client.post(
        "/hr/assess_psychological_safety",
        json={"member_name": "Test Member"},
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "assessment" in data
        assert data["context_tag"] == "hr_psych_safety"
        assert data["ethics_protocol"] == "Picard_Delta_3"


@pytest.mark.integration
def test_hr_detect_conflict_endpoint(client, mock_csrf_token):
    """Test HR conflict detection endpoint"""
    response = client.post(
        "/hr/detect_conflict",
        json={
            "indicators": {
                "explicit_report": True,
                "parties": ["Member A", "Member B"],
                "reported_severity": 2,
                "category": "technical"
            }
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "conflict_detected" in data
        assert data["context_tag"] == "hr_conflict_detect"
        assert data["ethics_protocol"] == "Picard_Delta_3"


@pytest.mark.integration
def test_hr_initiate_onboarding_endpoint(client, mock_csrf_token):
    """Test HR onboarding initiation endpoint"""
    response = client.post(
        "/hr/initiate_onboarding",
        json={
            "member_name": "New Member",
            "title": "Engineer",
            "department": "Engineering",
            "manager": "Test Manager"
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "journey" in data
        assert data["context_tag"] == "hr_onboarding"
        assert data["ethics_protocol"] == "Picard_Delta_3"


@pytest.mark.integration
def test_hr_cultural_health_endpoint(client, mock_csrf_token):
    """Test HR cultural health assessment endpoint"""
    response = client.post(
        "/hr/cultural_health",
        json={"layer": "real_world"},
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "report" in data
        assert data["context_tag"] == "hr_cultural_health"
        assert data["ethics_protocol"] == "Picard_Delta_3"


# ============================================================================
# QUANTUM FORGE TESTS
# ============================================================================

@pytest.mark.integration
def test_qf_create_agent_endpoint(client, mock_csrf_token):
    """Test Quantum Forge agent creation endpoint"""
    response = client.post(
        "/quantum_forge/create_agent",
        json={
            "agent_id": "TEST_AGENT_001",
            "capabilities": ["reasoning", "learning"],
            "ethics_level": "balanced",
            "flowstate_mode": "generative",
            "symbolic_depth": 2
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "agent" in data
        assert data["context_tag"] == "qf_create_agent"
        assert data["ethics_protocol"] == "GUMAS_Thermax"


@pytest.mark.integration
def test_qf_store_memory_endpoint(client, mock_csrf_token):
    """Test Quantum Forge memory storage endpoint"""
    response = client.post(
        "/quantum_forge/store_memory",
        json={
            "content": {"test": "data", "value": 42},
            "intent_alignment": 0.85,
            "tags": ["test", "integration"]
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "node" in data
        assert data["context_tag"] == "qf_store_memory"


@pytest.mark.integration
def test_qf_ethics_check_endpoint(client, mock_csrf_token):
    """Test Quantum Forge ethics check endpoint"""
    response = client.post(
        "/quantum_forge/ethics_check",
        json={
            "action_vector": [1.0, 0.0, 0.0],
            "baseline_vector": [0.98, 0.05, 0.05]
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "ethics_check" in data
        assert data["context_tag"] == "qf_ethics_check"
        assert data["ethics_protocol"] == "GUMAS_Thermax"
        assert "is_acceptable" in data["ethics_check"]
        assert "drift_value" in data["ethics_check"]


# ============================================================================
# MCP BRIDGE INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
def test_mcp_bridge_health_includes_capsules(client):
    """Test that MCP bridge health check includes registered capsules"""
    response = client.get("/mcp_bridge/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check basic health check structure
    assert "status" in data
    assert "governance_layer" in data
    
    # Check that capsules are registered
    assert "registered_capsules" in data
    capsules = data["registered_capsules"]
    assert "count" in capsules
    assert capsules["count"] == 3  # OPPY, HR, Quantum Forge
    assert "capsules" in capsules
    assert capsules["status"] == "OPERATIONAL"
    
    # Verify capsule IDs are present
    capsule_ids = [c["capsule_id"] for c in capsules["capsules"]]
    assert "OPPY_NAV_CAPSULE_001" in capsule_ids
    assert "HR_MODULE_CAPSULE_002" in capsule_ids
    assert "QF_CAPSULE_003" in capsule_ids


@pytest.mark.integration
def test_mcp_route_command_with_capsules(client, mock_csrf_token):
    """Test MCP command routing includes capsule information"""
    response = client.post(
        "/mcp_bridge/route_command",
        params={"command": "TEST_COMMAND", "anchor": "EOS_SEED_ORION"},
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ROUTED"
    assert "registered_capsules" in data
    assert data["capsule_count"] == 3
    assert data["anchor_ethics"] == "ENFORCED"
    assert data["zipwiz_handshake"] == "VALIDATED"


# ============================================================================
# END-TO-END FLOW TESTS
# ============================================================================

@pytest.mark.integration
def test_e2e_oppy_maneuver_flow(client, mock_csrf_token):
    """Test end-to-end flow for OPPY maneuver planning and execution"""
    # Step 1: Plan maneuver
    plan_response = client.post(
        "/oppy/plan_maneuver",
        json={
            "vessel_id": "E2E_TEST_VESSEL",
            "maneuver_type": "course_correction",
            "target_state": {"velocity_change": 15.0}
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    if plan_response.status_code == 503:
        pytest.skip("OPPY Navigator not available")
    
    assert plan_response.status_code == 200
    plan_data = plan_response.json()
    assert plan_data["status"] == "success"
    
    # Step 2: Execute maneuver (if plan was successful)
    if "plan" in plan_data:
        plan = plan_data["plan"]
        execute_response = client.post(
            "/oppy/execute_maneuver",
            json={
                "vessel_id": plan["vessel_id"],
                "plan_id": plan["plan_id"],
                "delta_v_ms": plan["delta_v_ms"],
                "burn_duration_s": plan["burn_duration_s"],
                "fuel_cost_kg": plan["fuel_cost_kg"],
                "anchor_impact": plan["anchor_impact"],
                "risk_assessment": plan["risk_assessment"]
            },
            headers={
                "Authorization": "Bearer test_token",
                "X-CSRF-Token": "test_csrf"
            }
        )
        
        assert execute_response.status_code == 200
        execute_data = execute_response.json()
        assert execute_data["status"] == "success"
        assert execute_data["context_tag"] == "oppy_execute_maneuver"


@pytest.mark.integration
def test_e2e_hr_onboarding_and_safety_flow(client, mock_csrf_token):
    """Test end-to-end flow for HR onboarding and safety assessment"""
    member_name = "E2E Test Member"
    
    # Step 1: Initiate onboarding
    onboarding_response = client.post(
        "/hr/initiate_onboarding",
        json={
            "member_name": member_name,
            "title": "Test Engineer",
            "department": "Testing",
            "manager": "Test Manager"
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    if onboarding_response.status_code == 503:
        pytest.skip("HR Module not available")
    
    assert onboarding_response.status_code == 200
    onboarding_data = onboarding_response.json()
    assert onboarding_data["status"] == "success"
    
    # Step 2: Assess psychological safety
    safety_response = client.post(
        "/hr/assess_psychological_safety",
        json={"member_name": member_name},
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert safety_response.status_code == 200
    safety_data = safety_response.json()
    assert safety_data["status"] == "success"
    assert safety_data["ethics_protocol"] == "Picard_Delta_3"


@pytest.mark.integration
def test_e2e_quantum_forge_agent_lifecycle(client, mock_csrf_token):
    """Test end-to-end flow for Quantum Forge agent creation and memory"""
    # Step 1: Create agent
    create_response = client.post(
        "/quantum_forge/create_agent",
        json={
            "agent_id": "E2E_AGENT_001",
            "capabilities": ["learning", "reasoning", "adaptation"],
            "ethics_level": "balanced",
            "flowstate_mode": "generative",
            "symbolic_depth": 2
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    if create_response.status_code == 503:
        pytest.skip("Quantum Forge not available")
    
    assert create_response.status_code == 200
    create_data = create_response.json()
    assert create_data["status"] == "success"
    
    # Step 2: Store memory for agent
    memory_response = client.post(
        "/quantum_forge/store_memory",
        json={
            "content": {
                "agent_id": "E2E_AGENT_001",
                "experience": "initial_training",
                "metrics": {"accuracy": 0.95}
            },
            "intent_alignment": 0.90,
            "tags": ["agent", "training", "e2e"]
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert memory_response.status_code == 200
    memory_data = memory_response.json()
    assert memory_data["status"] == "success"
    
    # Step 3: Perform ethics check
    ethics_response = client.post(
        "/quantum_forge/ethics_check",
        json={
            "action_vector": [0.95, 0.03, 0.02],
            "baseline_vector": [1.0, 0.0, 0.0]
        },
        headers={
            "Authorization": "Bearer test_token",
            "X-CSRF-Token": "test_csrf"
        }
    )
    
    assert ethics_response.status_code == 200
    ethics_data = ethics_response.json()
    assert ethics_data["status"] == "success"
    assert ethics_data["ethics_protocol"] == "GUMAS_Thermax"


# ============================================================================
# SMOKE TESTS
# ============================================================================

@pytest.mark.smoke
def test_all_new_endpoints_exist(client):
    """Smoke test to verify all new endpoints are registered"""
    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    paths = schema.get("paths", {})
    
    # Check OPPY endpoints
    assert "/oppy/plan_maneuver" in paths
    assert "/oppy/execute_maneuver" in paths
    assert "/oppy/telemetry/{vessel_id}" in paths
    assert "/oppy/state/{vessel_id}" in paths
    
    # Check HR endpoints
    assert "/hr/assess_psychological_safety" in paths
    assert "/hr/detect_conflict" in paths
    assert "/hr/initiate_onboarding" in paths
    assert "/hr/cultural_health" in paths
    
    # Check Quantum Forge endpoints
    assert "/quantum_forge/create_agent" in paths
    assert "/quantum_forge/store_memory" in paths
    assert "/quantum_forge/reactivate" in paths
    assert "/quantum_forge/ethics_check" in paths


@pytest.mark.smoke
def test_mcp_capsule_registration(client):
    """Smoke test to verify MCP capsules are registered"""
    from modules.symbolic_core.mcp_command_router import MCPCommandRouter
    
    router = MCPCommandRouter()
    
    # Verify capsules are registered
    assert len(router.registered_capsules) == 3
    assert "OPPY_NAV_CAPSULE_001" in router.registered_capsules
    assert "HR_MODULE_CAPSULE_002" in router.registered_capsules
    assert "QF_CAPSULE_003" in router.registered_capsules
    
    # Verify capsule info
    oppy_info = router.get_capsule_info("OPPY_NAV_CAPSULE_001")
    assert oppy_info["status"] == "ACTIVE"
    assert oppy_info["module"] == "OPPY Navigator v2.1"
    
    hr_info = router.get_capsule_info("HR_MODULE_CAPSULE_002")
    assert hr_info["status"] == "ACTIVE"
    assert hr_info["module"] == "HR Module v3.0 Helios"
    
    qf_info = router.get_capsule_info("QF_CAPSULE_003")
    assert qf_info["status"] == "ACTIVE"
    assert qf_info["module"] == "Quantum Forge v3.0"
    
    # Verify ethics validation
    assert router.validate_capsule_ethics("OPPY_NAV_CAPSULE_001")
    assert router.validate_capsule_ethics("HR_MODULE_CAPSULE_002")
    assert router.validate_capsule_ethics("QF_CAPSULE_003")
