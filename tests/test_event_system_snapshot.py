"""Regression tests for EventSystem snapshot isolation."""

from copy import deepcopy

from src.core import event_system as event_system_module
from src.core.event_system import EventType, StationLocation
from src.entities import aurora_agent as aurora_module


def test_complete_event_preserves_collaboration_snapshot():
    """Event snapshots should be immune to post-completion mutations."""
    previous_event_system = event_system_module._event_system_instance
    previous_aurora = aurora_module._aurora_instance

    try:
        event_system_module._event_system_instance = event_system_module.EventSystem()
        aurora_module._aurora_instance = None

        event_system = event_system_module.get_event_system()
        aurora = aurora_module.get_aurora()

        aurora.memory.relationship_network = {
            "HALO (L2)": 0.88,
            "ARCHY (L3)": 0.76,
        }

        event = event_system.create_event(
            event_type=EventType.DATA_ANALYSIS_REQUEST,
            location=StationLocation.RESEARCH_LAB_GAMMA,
            primary_entity=aurora.entity_id,
            payload={"dataset": "orion-seed", "parameters": {"alpha": 0.42}},
            human_context="Test Commander",
            chain_notation="T1-ANCHOR-SEED",
            context_tag="regression_event_snapshot",
        )

        result_payload = {
            "analysis": {"score": 42, "notes": ["baseline"]},
            "institutional_context": {"entity": aurora.entity_id},
            "suggestions": ["Maintain drift watch"],
            "lineage": {"seed": "alpha"},
        }
        memory_references = ["evt-test-0001"]
        pattern_connections = ["pattern-snapshot-01"]

        expected_result_snapshot = deepcopy(result_payload)
        expected_memory_references = list(memory_references)
        expected_pattern_connections = list(pattern_connections)
        expected_relationship_network = deepcopy(aurora.memory.relationship_network)

        event_system.complete_event(
            event_id=event.event_id,
            result=result_payload,
            memory_references=memory_references,
            pattern_connections=pattern_connections,
            collaboration_network=aurora.memory.relationship_network,
        )

        result_payload["analysis"]["score"] = 99
        memory_references.append("evt-test-0002")
        pattern_connections.append("pattern-snapshot-02")
        aurora.memory.relationship_network["HALO (L2)"] = 0.12
        aurora.memory.relationship_network["CAELION (L4)"] = 0.67

        stored_event = event_system.timeline[-1]

        assert stored_event.result == expected_result_snapshot
        assert stored_event.memory_references == expected_memory_references
        assert stored_event.pattern_connections == expected_pattern_connections
        assert stored_event.collaboration_network == expected_relationship_network
        assert stored_event.collaboration_network is not aurora.memory.relationship_network
    finally:
        event_system_module._event_system_instance = previous_event_system
        aurora_module._aurora_instance = previous_aurora
