import pytest

from src.agents.crew.base_agent import (
    BaseCrewAgent,
    AgentRole,
    ClearanceLevel,
    CrewAgentCapability,
)


class TestCrewAgent(BaseCrewAgent):
    def __init__(self):
        super().__init__(
            agent_id="TEST_001",
            surname="Tester",
            full_name="Unit Tester",
            role=AgentRole.SYSTEMS,
            clearance=ClearanceLevel.L3_TECHNICAL,
            specializations=["unit_testing"],
            capabilities=[
                CrewAgentCapability(
                    name="Echo",
                    description="Echo back context",
                    tool_endpoint="/api/test/echo",
                    clearance_required="L3_TECHNICAL",
                    specialization_bonus=1.0,
                )
            ],
            location="Test Deck",
            division="Quality",
            symbolic_tag="s.tag::test.unit",
            model="claude-sonnet-4-5",
        )

    async def _execute_task(self, task_type: str, context):  # type: ignore[override]
        if task_type == "echo":
            return {"echo": context}
        raise ValueError("unsupported task type")


class FailingCrewAgent(TestCrewAgent):
    async def _execute_task(self, task_type: str, context):  # type: ignore[override]
        raise RuntimeError("forced failure")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_request_success():
    agent = TestCrewAgent()
    start_tasks_completed = agent.stats["tasks_completed"]
    request = {"task_type": "echo", "context": {"value": 42}, "priority": "high"}
    result = await agent.process_request(request)

    assert result["success"] is True
    assert result["result"]["echo"] == {"value": 42}
    assert agent.stats["tasks_completed"] == start_tasks_completed + 1
    # Active task list should be cleaned up after completion
    assert len(agent.active_tasks) == 0
    # Status reset to ready
    assert agent.status == "ready"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_request_failure():
    agent = FailingCrewAgent()
    start_failed = agent.stats["tasks_failed"]
    request = {"task_type": "echo", "context": {"value": "x"}}
    result = await agent.process_request(request)
    assert result["success"] is False
    assert agent.stats["tasks_failed"] == start_failed + 1
    assert len(agent.active_tasks) == 0
    assert agent.status == "ready"


@pytest.mark.unit
def test_get_capabilities_structure():
    agent = TestCrewAgent()
    caps = agent.get_capabilities()
    assert isinstance(caps, list)
    assert caps and {"name", "description", "endpoint", "clearance", "specialization_bonus"}.issubset(
        caps[0].keys()
    )


@pytest.mark.unit
def test_get_status_contains_basic_fields():
    agent = TestCrewAgent()
    status = agent.get_status()
    for key in [
        "agent_id",
        "surname",
        "role",
        "clearance",
        "division",
        "status",
        "capabilities_count",
        "statistics",
        "symbolic_tag",
        "model",
    ]:
        assert key in status
    assert status["surname"] == "Tester"
    assert status["capabilities_count"] == 1
    assert status["statistics"]["tasks_completed"] == 0
    # uptime should be numeric and small at test start
    assert status["statistics"]["uptime_seconds"] >= 0
