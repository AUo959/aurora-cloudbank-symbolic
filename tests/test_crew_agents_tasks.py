import pytest

from src.agents.crew.lin import get_lin
from src.agents.crew.noor import get_noor
from src.agents.crew.qin import get_qin
from src.agents.crew.sorensen import get_sorensen
from src.agents.crew.vasquez import get_vasquez
from src.agents.crew.lee import get_lee
from src.agents.crew.suresh import get_suresh
from src.agents.crew.koss import get_koss


# Mapping each agent factory to one representative valid task_type it supports
AGENT_TASK_MAP = [
    (get_lin, "simulation_operations"),
    (get_noor, "reflexivity_analysis"),
    (get_qin, "nli_compilation"),
    (get_sorensen, "narrative_causality_audit"),
    (get_vasquez, "flight_operations"),
    # Lee task example
    (get_lee, "observability_framework"),
    # Suresh task example
    (get_suresh, "symbolic_visualization"),
    # Koss task example
    (get_koss, "drift_detection"),
]


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("getter,task_type", AGENT_TASK_MAP)
async def test_agent_valid_task_execution(getter, task_type):
    agent = getter()
    start_completed = agent.stats["tasks_completed"]
    result = await agent.process_request({"task_type": task_type, "context": {}, "priority": "low"})

    assert result["success"] is True
    # Top-level echoes task_type, nested result carries detailed payload with 'task'
    assert result["task_type"] == task_type
    assert "result" in result and result["result"].get("task") == task_type
    assert agent.stats["tasks_completed"] == start_completed + 1
    assert agent.status == "ready"


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("getter,task_type", AGENT_TASK_MAP)
async def test_agent_invalid_task_fails(getter, task_type):  # noqa: ARG001 (task_type unused intentionally)
    agent = getter()
    start_failed = agent.stats["tasks_failed"]
    invalid_type = "__invalid_task__"
    result = await agent.process_request({"task_type": invalid_type, "context": {}, "priority": "low"})

    assert result["success"] is False
    assert "error" in result
    # Error message should mention the invalid task type
    assert invalid_type in result["error"]
    assert agent.stats["tasks_failed"] == start_failed + 1
    assert agent.status == "ready"
    # Active task list cleaned up
    assert len(agent.active_tasks) == 0
