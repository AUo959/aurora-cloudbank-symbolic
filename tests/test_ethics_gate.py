"""
Tests for Aurora Ethics Gate Module

Covers:
- EthicsVerdict dataclass
- GUMASEthicsClient adapter
- EthicsGate core evaluation logic
- Relay Manager integration
- DLP tag generation
- Threshold behavior
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from src.aurora.ethics.ethics_gate import (
    EthicsVerdict,
    GUMASEthicsClient,
    EthicsGate,
    EthicsViolation
)
from src.aurora.relays.relay_manager import RelayManager, RelayMessage
from src.core.native_dlp_export import NativeDLPTracker


class TestEthicsVerdict:
    """Test EthicsVerdict dataclass"""

    def test_verdict_creation(self):
        """Test creating ethics verdict"""
        verdict = EthicsVerdict(
            allowed=True,
            score=0.85,
            reason="Action complies with all rules",
            engine="gumas"
        )

        assert verdict.allowed is True
        assert verdict.score == 0.85
        assert verdict.reason == "Action complies with all rules"
        assert verdict.engine == "gumas"
        assert datetime.fromisoformat(verdict.timestamp).isoformat() == verdict.timestamp
        assert verdict.dlp_tag_id is None

    def test_verdict_to_dict(self):
        """Test verdict serialization"""
        verdict = EthicsVerdict(
            allowed=False,
            score=0.3,
            reason="High severity violation",
            engine="gumas",
            dlp_tag_id="dlp_001"
        )

        data = verdict.to_dict()
        assert data["allowed"] is False
        assert data["score"] == 0.3
        assert data["reason"] == "High severity violation"
        assert data["engine"] == "gumas"
        assert data["dlp_tag_id"] == "dlp_001"
        assert "timestamp" in data


class TestGUMASEthicsClient:
    """Test GUMAS client adapter"""

    @pytest.mark.asyncio
    async def test_client_evaluation_success(self):
        """Test successful GUMAS API call"""
        client = GUMASEthicsClient(base_url="http://localhost:8000")

        # Mock httpx response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compliant": True,
            "should_block": False,
            "violations": [],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await client.evaluate(
                action={"type": "read_data", "resource": "public"},
                context={"agent_id": "test_agent"}
            )

        assert result["compliant"] is True
        assert result["should_block"] is False
        assert result["violations"] == []

    @pytest.mark.asyncio
    async def test_client_evaluation_with_violations(self):
        """Test GUMAS API call with violations"""
        client = GUMASEthicsClient()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "compliant": False,
            "should_block": True,
            "violations": [
                {
                    "severity": "critical",
                    "description": "Unauthorized access attempt",
                    "rule_name": "SAFETY_001"
                }
            ],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await client.evaluate(
                action={"type": "delete_node", "node_id": "critical_001"},
                context={"agent_id": "test_agent"}
            )

        assert result["compliant"] is False
        assert result["should_block"] is True
        assert len(result["violations"]) == 1

    @pytest.mark.asyncio
    async def test_client_evaluation_api_failure(self):
        """Test graceful degradation on API failure"""
        client = GUMASEthicsClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(side_effect=Exception("Connection failed"))
            mock_client_class.return_value = mock_client

            result = await client.evaluate(
                action={"type": "test_action"},
                context={}
            )

        # Should return safe default (deny)
        assert result["compliant"] is False
        assert result["should_block"] is True
        assert len(result["violations"]) > 0


class TestEthicsGate:
    """Test EthicsGate core logic"""

    @pytest.mark.asyncio
    async def test_gate_allows_compliant_action(self):
        """Test gate allows action with high score"""
        # Create mock client
        client = GUMASEthicsClient()
        client.evaluate = AsyncMock(return_value={
            "compliant": True,
            "should_block": False,
            "violations": [],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Create gate with threshold 0.7
        gate = EthicsGate(client=client, threshold=0.7)

        verdict = await gate.evaluate(
            action={"type": "read_data", "resource": "public"},
            context={"agent_id": "test_agent"}
        )

        assert verdict.allowed is True
        assert verdict.score >= 0.7
        assert verdict.engine == "gumas"
        assert verdict.dlp_tag_id in gate.dlp_tracker.tags
        assert gate.dlp_tracker.tags[verdict.dlp_tag_id].operation == "ethics_gate_evaluate"

    @pytest.mark.asyncio
    async def test_gate_blocks_non_compliant_action(self):
        """Test gate blocks action with low score"""
        client = GUMASEthicsClient()
        client.evaluate = AsyncMock(return_value={
            "compliant": False,
            "should_block": True,
            "violations": [
                {
                    "severity": "critical",
                    "description": "Safety violation",
                    "rule_name": "SAFETY_001"
                }
            ],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        gate = EthicsGate(client=client, threshold=0.7)

        verdict = await gate.evaluate(
            action={"type": "delete_critical_data", "resource": "system"},
            context={"agent_id": "test_agent"}
        )

        assert verdict.allowed is False
        assert verdict.score < 0.7
        assert "SAFETY_001" in verdict.reason

    @pytest.mark.asyncio
    async def test_gate_threshold_boundary(self):
        """Test gate behavior at threshold boundary"""
        client = GUMASEthicsClient()

        # Test at exactly threshold (0.7)
        client.evaluate = AsyncMock(return_value={
            "compliant": True,
            "should_block": False,
            "violations": [
                {
                    "severity": "low",
                    "description": "Minor warning",
                    "rule_name": "WARNING_001"
                }
            ],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        gate = EthicsGate(client=client, threshold=0.7)

        verdict = await gate.evaluate(
            action={"type": "moderate_action"},
            context={}
        )

        # Low severity = 0.7, exactly at threshold
        assert verdict.score == 0.7
        assert verdict.allowed is True  # >= threshold

    @pytest.mark.asyncio
    async def test_gate_creates_dlp_tags(self):
        """Test gate creates DLP tags with anchors"""
        client = GUMASEthicsClient()
        client.evaluate = AsyncMock(return_value={
            "compliant": True,
            "should_block": False,
            "violations": [],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        dlp_tracker = NativeDLPTracker()
        gate = EthicsGate(client=client, dlp_tracker=dlp_tracker)

        verdict = await gate.evaluate(
            action={"type": "test_action"},
            context={"agent_id": "test"}
        )

        # Check DLP tag was created
        assert verdict.dlp_tag_id in dlp_tracker.tags
        assert dlp_tracker.tags[verdict.dlp_tag_id].operation == "ethics_gate_evaluate"

        # Check tag has required anchors
        tag = dlp_tracker.tags[verdict.dlp_tag_id]
        assert "EOS_SEED_ORION" in tag.anchor_protocols
        assert "Picard_Delta_3" in tag.anchor_protocols
        assert "T1" in tag.t1_srb_anchors
        assert "SRB" in tag.t1_srb_anchors

        # Check symbolic patterns
        assert "ethics_context" in tag.symbolic_patterns
        ethics_context = tag.symbolic_patterns["ethics_context"]
        assert ethics_context["action_type"] == "test_action"
        assert "allowed" in ethics_context

    @pytest.mark.asyncio
    async def test_gate_score_calculation(self):
        """Test gate calculates score based on violation severity"""
        client = GUMASEthicsClient()
        gate = EthicsGate(client=client, threshold=0.7)

        # Test critical violation -> score 0.0
        client.evaluate = AsyncMock(return_value={
            "compliant": False,
            "should_block": True,
            "violations": [{"severity": "critical", "description": "Critical", "rule_name": "CRIT"}],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })
        verdict = await gate.evaluate({"type": "test"}, {})
        assert verdict.score == 0.0

        # Test high violation -> score 0.3
        client.evaluate = AsyncMock(return_value={
            "compliant": False,
            "should_block": False,
            "violations": [{"severity": "high", "description": "High", "rule_name": "HIGH"}],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })
        verdict = await gate.evaluate({"type": "test"}, {})
        assert verdict.score == 0.3

        # Test medium violation -> score 0.5
        client.evaluate = AsyncMock(return_value={
            "compliant": False,
            "should_block": False,
            "violations": [{"severity": "medium", "description": "Medium", "rule_name": "MED"}],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })
        verdict = await gate.evaluate({"type": "test"}, {})
        assert verdict.score == 0.5


class TestRelayManagerIntegration:
    """Test RelayManager with EthicsGate integration"""

    @pytest.mark.asyncio
    async def test_relay_allows_compliant_message(self):
        """Test relay allows message that passes ethics check"""
        # Create mock client
        client = GUMASEthicsClient()
        client.evaluate = AsyncMock(return_value={
            "compliant": True,
            "should_block": False,
            "violations": [],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        gate = EthicsGate(client=client, threshold=0.7)
        manager = RelayManager(ethics_gate=gate)

        message = RelayMessage(
            message_id="msg_001",
            source_layer="L1",
            target_layer="L2",
            message_type="query",
            payload={"query": "status"},
            requires_ethics_check=True
        )

        result = await manager.send_message(message)

        assert result["success"] is True
        assert result["message_id"] == "msg_001"
        assert manager.messages_processed == 1
        assert manager.messages_blocked == 0

    @pytest.mark.asyncio
    async def test_relay_blocks_non_compliant_message(self):
        """Test relay blocks message that fails ethics check"""
        client = GUMASEthicsClient()
        client.evaluate = AsyncMock(return_value={
            "compliant": False,
            "should_block": True,
            "violations": [
                {
                    "severity": "critical",
                    "description": "Unauthorized state change",
                    "rule_name": "SAFETY_001"
                }
            ],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        gate = EthicsGate(client=client, threshold=0.7)
        manager = RelayManager(ethics_gate=gate)

        message = RelayMessage(
            message_id="msg_002",
            source_layer="L1",
            target_layer="L2",
            message_type="state_change",
            payload={"action": "delete_all"},
            requires_ethics_check=True
        )

        with pytest.raises(EthicsViolation) as exc_info:
            await manager.send_message(message)

        assert "blocked" in str(exc_info.value).lower()
        assert manager.messages_processed == 1
        assert manager.messages_blocked == 1

    @pytest.mark.asyncio
    async def test_relay_skips_ethics_check_when_not_required(self):
        """Test relay skips ethics check for messages that don't require it"""
        manager = RelayManager()

        message = RelayMessage(
            message_id="msg_003",
            source_layer="L1",
            target_layer="L2",
            message_type="notification",
            payload={"notification": "status update"},
            requires_ethics_check=False  # No ethics check
        )

        result = await manager.send_message(message)

        assert result["success"] is True
        assert manager.messages_processed == 1
        assert manager.messages_blocked == 0

    @pytest.mark.asyncio
    async def test_relay_stats(self):
        """Test relay manager statistics"""
        client = GUMASEthicsClient()
        gate = EthicsGate(client=client, threshold=0.7)
        manager = RelayManager(ethics_gate=gate)

        # Send allowed message
        client.evaluate = AsyncMock(return_value={
            "compliant": True,
            "should_block": False,
            "violations": [],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        message1 = RelayMessage(
            message_id="msg_004",
            source_layer="L1",
            target_layer="L2",
            message_type="query",
            payload={},
            requires_ethics_check=True
        )
        await manager.send_message(message1)

        # Send blocked message
        client.evaluate = AsyncMock(return_value={
            "compliant": False,
            "should_block": True,
            "violations": [{"severity": "critical", "description": "Test", "rule_name": "TEST"}],
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        })

        message2 = RelayMessage(
            message_id="msg_005",
            source_layer="L1",
            target_layer="L2",
            message_type="state_change",
            payload={},
            requires_ethics_check=True
        )

        try:
            await manager.send_message(message2)
        except EthicsViolation:
            pass  # Expected

        stats = manager.get_stats()
        assert stats["messages_processed"] == 2
        assert stats["messages_blocked"] == 1
        assert stats["block_rate"] == 0.5


class TestEthicsViolationException:
    """Test EthicsViolation exception"""

    def test_violation_exception_creation(self):
        """Test creating ethics violation exception"""
        verdict = EthicsVerdict(
            allowed=False,
            score=0.2,
            reason="Critical safety violation",
            engine="gumas"
        )

        exc = EthicsViolation("Action blocked", verdict)

        assert str(exc) == "Action blocked"
        assert exc.verdict == verdict
        assert exc.verdict.score == 0.2
