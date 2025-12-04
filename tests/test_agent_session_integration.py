"""Integration coverage for agent session creation, run flow, and share/fork paths.

Anchor: T1-SESSION-FLOW-START
Context: session_integration_gallery
Ethics: Picard_Delta_3
"""

import asyncio

from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration


def test_agent_session_end_to_end_flow():
    """Create a session, execute a run, and verify share/fork redaction paths."""

    async def _run_flow():
        agent = ChatGPTAgentModeIntegration()

        create_response = await agent.execute_tool(
            "session_management",
            {
                "action": "create",
                "state_data": {
                    "full_name": "Ada Lovelace",
                    "preference": "quantum_memory_trace",
                    "metadata": {"anchor_seed": "T1-SESSION-FLOW-START"},
                },
            },
        )

        assert create_response["success"] is True
        session_id = create_response["result"]["session_id"]
        session_state = create_response["result"]["state"]["state"]
        assert session_state["pii_redaction"]["enabled"] is True
        assert session_state["metadata_anchor"]["anchor_seed"] == "T1-SESSION-FLOW-START"

        run_response = await agent.execute_tool(
            "symbolic_processing",
            {
                "operation": "quantum-thread-bridge",
                "data": {"qubits": 4, "thread": "bridge_v2", "decision_gate": "safe"},
                "anchor_context": "T1-SESSION-FLOW-START",
            },
            session_id=session_id,
        )

        assert run_response["success"] is True
        assert run_response["result"]["operation"] == "quantum-thread-bridge"

        share_response = await agent.execute_tool(
            "session_management",
            {"action": "share", "session_id": session_id},
        )

        assert share_response["success"] is True
        share_token = share_response["result"]["share_token"]
        shared_state = share_response["result"]["shared_state"]["state"]
        assert shared_state["full_name"] == "***"
        assert shared_state["pii_redaction"]["strategy"] == "mask"

        fork_response = await agent.execute_tool(
            "session_management",
            {"action": "fork", "session_id": session_id, "share_token": share_token},
        )

        assert fork_response["success"] is True
        new_state = fork_response["result"]["state"]["state"]
        assert fork_response["result"]["session_id"] != session_id
        assert new_state["forked_from"] == session_id
        assert new_state["share_token"] == share_token
        assert new_state["pii_redaction"]["enabled"] is True

    asyncio.run(_run_flow())
