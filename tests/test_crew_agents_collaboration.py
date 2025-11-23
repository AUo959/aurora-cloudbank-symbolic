import pytest

from src.agents.crew.thorne import get_thorne
from src.agents.crew.markov import get_markov


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collaboration_success_path():
    # Use two distinct instances of the same agent to ensure shared task support
    thorne_primary = get_thorne()
    thorne_secondary = get_thorne()  # Separate instance, same capabilities
    start_collabs = thorne_primary.stats["collaborations"]
    task = {"task_type": "strategic_planning", "context": {"phase": 1}, "priority": "low"}

    result = await thorne_primary.collaborate_with(thorne_secondary, task)

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
    assert thorne_primary.stats["collaborations"] == start_collabs + 1
    assert len(thorne_primary.collaboration_history) >= 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collaboration_failure_propagation():
    thorne = get_thorne()
    markov = get_markov()
    start_collabs = thorne.stats["collaborations"]
    invalid_task = {"task_type": "__invalid__", "context": {}, "priority": "low"}

    result = await thorne.collaborate_with(markov, invalid_task)

    assert result["success"] is False
    assert result["synergy_achieved"] is True  # Synergy flag currently static True in implementation
    # Each contribution should reflect failure
    assert result["my_contribution"]["success"] is False
    assert result["their_contribution"]["success"] is False
    assert thorne.stats["collaborations"] == start_collabs + 1
    assert len(thorne.collaboration_history) >= 1
    # Ensure errors mention invalid token
    assert "__invalid__" in result["my_contribution"].get("error", "")
    assert "__invalid__" in result["their_contribution"].get("error", "")
