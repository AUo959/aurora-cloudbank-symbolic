import pytest

from src.agents.crew.lin import get_lin


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collaboration_success_path():
    # Use two distinct instances of the same agent to ensure shared task support
    lin_primary = get_lin()
    lin_secondary = get_lin()  # Separate instance, same capabilities
    start_collabs = lin_primary.stats["collaborations"]
    task = {"task_type": "simulation_operations", "context": {"scope": "test"}, "priority": "low"}

    result = await lin_primary.collaborate_with(lin_secondary, task)

    assert result["success"] is True
    assert result["synergy_achieved"] is True
    # Contributions contain per-agent task execution payload
    assert result["my_contribution"]["task_type"] == task["task_type"]
    assert result["their_contribution"]["task_type"] == task["task_type"]
    # DLP placeholders present
    assert "context_tag" in result["my_contribution"]
    assert "symbolic_hash" in result["my_contribution"]
    assert "t1_state" in result["my_contribution"]
    assert "srb_resolution" in result["my_contribution"]
    # Collaboration metrics updated
    assert lin_primary.stats["collaborations"] == start_collabs + 1
    assert len(lin_primary.collaboration_history) >= 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collaboration_failure_propagation():
    lin_a = get_lin()
    lin_b = get_lin()
    start_collabs = lin_a.stats["collaborations"]
    invalid_task = {"task_type": "__invalid__", "context": {}, "priority": "low"}

    result = await lin_a.collaborate_with(lin_b, invalid_task)

    assert result["success"] is False
    assert result["synergy_achieved"] is True  # Synergy flag currently static True in implementation
    # Each contribution should reflect failure
    assert result["my_contribution"]["success"] is False
    assert result["their_contribution"]["success"] is False
    assert lin_a.stats["collaborations"] == start_collabs + 1
    assert len(lin_a.collaboration_history) >= 1
    # Ensure errors mention invalid token
    assert "__invalid__" in result["my_contribution"].get("error", "")
    assert "__invalid__" in result["their_contribution"].get("error", "")
