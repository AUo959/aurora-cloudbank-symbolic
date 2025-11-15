"""Regression tests for relay tier constellation status."""

from datetime import datetime

import pytest

from src.bridges.l2_meta_agent_bridge import L2MetaAgentBridge


@pytest.fixture()
def bridge():
    """Provide a fresh bridge instance for each test."""
    return L2MetaAgentBridge()


def test_relay_constellation_structure(bridge):
    """Relay tier status should use the relay-specific naming."""
    status = bridge.get_constellation_status()

    relay_tier = status.get("relay_tier")
    assert relay_tier is not None
    assert relay_tier["constellation"] == "RELAY_TIER_CAPSULES"
    assert relay_tier["total_capsules"] == 5
    assert relay_tier["connected_capsules"] == 0
    assert len(relay_tier["capsules"]) == 5


def test_relay_capsule_entries_include_metadata(bridge):
    """Each relay capsule entry should expose descriptive metadata."""
    status = bridge.get_constellation_status()
    relay_tier = status["relay_tier"]

    for capsule in relay_tier["capsules"]:
        assert "agent_id" in capsule
        assert "status" in capsule
        assert capsule["status"] in {"connected", "disconnected"}
        assert "capabilities" in capsule
        assert isinstance(capsule["capabilities"], list)
        if capsule.get("connected"):
            # Connected timestamps must be ISO 8601
            datetime.fromisoformat(capsule["connected"])  # pragma: no branch
