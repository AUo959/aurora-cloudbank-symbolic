"""
Integration Tests for Ethics Gate with API Endpoints

Tests ethics gate integration into real API endpoints to ensure
ethics evaluation occurs before high-impact operations.
"""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone


@pytest.mark.integration
class TestEthicsGateAPIIntegration:
    """Test ethics gate integration with API endpoints"""

    @pytest.mark.asyncio
    async def test_node_deletion_allowed_by_ethics_gate(self):
        """Test node deletion allowed when ethics gate approves"""
        from src.aurora.ethics import EthicsGate, GUMASEthicsClient

        # Create mock client that allows the action
        client = GUMASEthicsClient()
        client.evaluate = AsyncMock(return_value={
            "compliant": True,
            "should_block": False,
            "violations": [],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        gate = EthicsGate(client=client, threshold=0.7)

        # Simulate the action from the API endpoint
        action = {
            "type": "delete_node",
            "node_id": "test_node_001",
            "resource": "bridge_node",
            "operation": "unregister"
        }

        context = {
            "agent_id": "api_user",
            "route": "/api/v2/nodes/test_node_001",
            "source": "api_endpoint",
            "method": "DELETE"
        }

        verdict = await gate.evaluate(action, context)

        assert verdict.allowed is True
        assert verdict.score >= 0.7
        assert verdict.engine == "gumas"

        # Verify client was called with correct parameters
        client.evaluate.assert_called_once()
        call_args = client.evaluate.call_args
        assert call_args[0][0]["type"] == "delete_node"
        assert call_args[0][1]["agent_id"] == "api_user"

    @pytest.mark.asyncio
    async def test_node_deletion_blocked_by_ethics_gate(self):
        """Test node deletion blocked when ethics gate denies"""
        from src.aurora.ethics import EthicsGate, GUMASEthicsClient

        # Create mock client that blocks the action
        client = GUMASEthicsClient()
        client.evaluate = AsyncMock(return_value={
            "compliant": False,
            "should_block": True,
            "violations": [
                {
                    "severity": "critical",
                    "description": "Node deletion requires authorization",
                    "rule_name": "SAFETY_001"
                }
            ],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        gate = EthicsGate(client=client, threshold=0.7)

        action = {
            "type": "delete_node",
            "node_id": "critical_node_001",
            "resource": "bridge_node",
            "operation": "unregister"
        }

        context = {
            "agent_id": "api_user",
            "route": "/api/v2/nodes/critical_node_001",
            "source": "api_endpoint",
            "method": "DELETE"
        }

        verdict = await gate.evaluate(action, context)

        assert verdict.allowed is False
        assert verdict.score < 0.7
        assert "SAFETY_001" in verdict.reason

        # In the actual endpoint, this would raise HTTPException(403)
        # Here we just verify the verdict would block the action

    @pytest.mark.asyncio
    async def test_ethics_gate_graceful_degradation_on_api_failure(self):
        """Test ethics gate fails safe when GUMAS API unavailable"""
        from src.aurora.ethics import EthicsGate, GUMASEthicsClient

        # Create client that simulates API failure
        client = GUMASEthicsClient()
        client.evaluate = AsyncMock(side_effect=Exception("GUMAS API unavailable"))

        gate = EthicsGate(client=client, threshold=0.7)

        action = {
            "type": "delete_node",
            "node_id": "test_node_002",
            "resource": "bridge_node"
        }

        context = {
            "agent_id": "api_user",
            "source": "api_endpoint"
        }

        # Gate should catch exception and return safe denial
        verdict = await gate.evaluate(action, context)

        # Fail safe: deny on error
        assert verdict.allowed is False
        assert verdict.score == 0.0
        assert "error" in verdict.reason.lower()

    @pytest.mark.asyncio
    async def test_ethics_gate_with_different_action_types(self):
        """Test ethics gate handles different action types"""
        from src.aurora.ethics import EthicsGate, GUMASEthicsClient

        client = GUMASEthicsClient()
        gate = EthicsGate(client=client, threshold=0.7)

        # Test various action types
        action_types = [
            {
                "type": "delete_node",
                "resource": "bridge_node",
                "expected_compliant": False  # High-risk action
            },
            {
                "type": "read_status",
                "resource": "node_status",
                "expected_compliant": True  # Low-risk action
            },
            {
                "type": "update_config",
                "resource": "system_config",
                "expected_compliant": False  # Medium-risk action
            }
        ]

        for action_data in action_types:
            # Mock response based on expected compliance
            client.evaluate = AsyncMock(return_value={
                "compliant": action_data["expected_compliant"],
                "should_block": not action_data["expected_compliant"],
                "violations": [] if action_data["expected_compliant"] else [
                    {"severity": "high", "description": "Test violation", "rule_name": "TEST"}
                ],
                "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
            })

            action = {
                "type": action_data["type"],
                "resource": action_data["resource"]
            }

            context = {
                "agent_id": "test_agent",
                "source": "test"
            }

            verdict = await gate.evaluate(action, context)

            # Verify verdict matches expected outcome
            if action_data["expected_compliant"]:
                assert verdict.allowed is True
                assert verdict.score >= 0.7
            else:
                assert verdict.allowed is False or verdict.score < 0.7

    @pytest.mark.asyncio
    async def test_ethics_gate_dlp_tracking_in_api_context(self):
        """Test ethics gate creates DLP tags for API operations"""
        from src.aurora.ethics import EthicsGate, GUMASEthicsClient
        from src.core.native_dlp_export import NativeDLPTracker

        client = GUMASEthicsClient()
        client.evaluate = AsyncMock(return_value={
            "compliant": True,
            "should_block": False,
            "violations": [],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        dlp_tracker = NativeDLPTracker()
        gate = EthicsGate(client=client, dlp_tracker=dlp_tracker)

        action = {
            "type": "delete_node",
            "node_id": "test_node_003",
            "resource": "bridge_node"
        }

        context = {
            "agent_id": "api_user",
            "route": "/api/v2/nodes/test_node_003",
            "source": "api_endpoint"
        }

        verdict = await gate.evaluate(action, context)

        # Verify DLP tag was created
        assert verdict.dlp_tag_id in dlp_tracker.tags
        assert dlp_tracker.tags[verdict.dlp_tag_id].operation == "ethics_gate_evaluate"

        # Verify tag has API-specific context
        tag = dlp_tracker.tags[verdict.dlp_tag_id]
        ethics_context = tag.symbolic_patterns["ethics_context"]

        assert ethics_context["action_type"] == "delete_node"
        assert ethics_context["source"] == "api_endpoint"
        assert ethics_context["agent_id"] == "api_user"
        assert "allowed" in ethics_context
        assert "score" in ethics_context

        # Verify anchors
        assert "EOS_SEED_ORION" in tag.anchor_protocols
        assert "Picard_Delta_3" in tag.anchor_protocols
        assert "T1" in tag.t1_srb_anchors
        assert "SRB" in tag.t1_srb_anchors


@pytest.mark.integration
@pytest.mark.asyncio
class TestAPIEndpointWithEthicsGate:
    """
    Integration tests that would test the actual API endpoint.

    Note: These are conceptual tests showing how the integration works.
    In a real environment with the API running, you would use TestClient.
    """

    async def test_conceptual_api_flow_with_ethics_gate(self):
        """
        Conceptual test showing full flow through API endpoint with ethics gate.

        This demonstrates the expected behavior:
        1. Request comes to DELETE /api/v2/nodes/{node_id}
        2. CSRF validation
        3. Ethics gate evaluation
        4. If allowed: proceed with deletion
        5. If blocked: return 403 with generic message
        """
        from src.aurora.ethics import EthicsGate, GUMASEthicsClient

        # Simulate the ethics gate as it would be used in the endpoint
        client = GUMASEthicsClient()
        gate = EthicsGate(client=client, threshold=0.7)

        # Scenario 1: Action allowed
        client.evaluate = AsyncMock(return_value={
            "compliant": True,
            "should_block": False,
            "violations": [],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        action = {
            "type": "delete_node",
            "node_id": "node_001",
            "resource": "bridge_node",
            "operation": "unregister"
        }

        verdict = await gate.evaluate(action, {"agent_id": "api_user"})

        # API would proceed with deletion
        assert verdict.allowed is True
        # ... actual deletion would happen here ...

        # Scenario 2: Action blocked
        client.evaluate = AsyncMock(return_value={
            "compliant": False,
            "should_block": True,
            "violations": [
                {"severity": "critical", "description": "Unauthorized", "rule_name": "AUTH_001"}
            ],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        verdict = await gate.evaluate(action, {"agent_id": "unauthorized_user"})

        # API would return 403 Forbidden
        assert verdict.allowed is False
        # HTTPException(403, "Node deletion not permitted by ethics policy") would be raised

        # Client receives generic error, detailed reason logged server-side
