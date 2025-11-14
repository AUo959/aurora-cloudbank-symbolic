"""
Tests for Glyph Mesh Controller

Tests multi-agent symbolic coordination messaging with DLP tagging.
"""

import pytest
from src.aurora.agents.glyph_mesh_controller import (
    GlyphMeshController,
    MeshMessage,
    build_message,
    get_glyph_mesh_controller,
)


@pytest.mark.unit
@pytest.mark.aurora
def test_build_message():
    """Test message builder creates proper MeshMessage"""
    msg = build_message(
        sender="Glyphon",
        recipient="Caelion",
        performative="inform",
        content={"status": "ready"},
        layer_context="L1"
    )

    assert msg.sender == "Glyphon"
    assert msg.recipient == "Caelion"
    assert msg.performative == "inform"
    assert msg.content == {"status": "ready"}
    assert msg.layer_context == "L1"
    assert msg.timestamp.endswith("Z")  # ISO-8601 with Z suffix


@pytest.mark.unit
@pytest.mark.aurora
def test_build_message_default_layer():
    """Test message builder uses default layer context"""
    msg = build_message(
        sender="Glyphon",
        recipient="Caelion",
        performative="request",
        content={"action": "sync"}
    )

    assert msg.layer_context == "L1"


@pytest.mark.unit
@pytest.mark.aurora
def test_controller_initialization():
    """Test GlyphMeshController initializes properly"""
    controller = GlyphMeshController()

    stats = controller.get_stats()
    assert stats["subscriber_count"] == 0
    assert stats["total_handlers"] == 0
    assert stats["message_count"] == 0


@pytest.mark.unit
@pytest.mark.aurora
def test_subscribe_single_agent():
    """Test subscribing a single agent handler"""
    controller = GlyphMeshController()

    def handler(msg: MeshMessage):
        pass

    controller.subscribe("Glyphon", handler)

    stats = controller.get_stats()
    assert stats["subscriber_count"] == 1
    assert stats["total_handlers"] == 1
    assert "Glyphon" in stats["subscribers"]
    assert stats["subscribers"]["Glyphon"] == 1


@pytest.mark.unit
@pytest.mark.aurora
def test_subscribe_multiple_handlers():
    """Test subscribing multiple handlers for same agent"""
    controller = GlyphMeshController()

    def handler1(msg: MeshMessage):
        pass

    def handler2(msg: MeshMessage):
        pass

    controller.subscribe("Glyphon", handler1)
    controller.subscribe("Glyphon", handler2)

    stats = controller.get_stats()
    assert stats["subscriber_count"] == 1
    assert stats["total_handlers"] == 2
    assert stats["subscribers"]["Glyphon"] == 2


@pytest.mark.unit
@pytest.mark.aurora
def test_subscribe_duplicate_handler():
    """Test subscribing same handler twice doesn't duplicate"""
    controller = GlyphMeshController()

    def handler(msg: MeshMessage):
        pass

    controller.subscribe("Glyphon", handler)
    controller.subscribe("Glyphon", handler)  # Duplicate

    stats = controller.get_stats()
    assert stats["total_handlers"] == 1  # Should still be 1


@pytest.mark.unit
@pytest.mark.aurora
def test_unsubscribe():
    """Test unsubscribing a handler"""
    controller = GlyphMeshController()

    def handler(msg: MeshMessage):
        pass

    controller.subscribe("Glyphon", handler)
    assert controller.get_stats()["total_handlers"] == 1

    controller.unsubscribe("Glyphon", handler)
    assert controller.get_stats()["total_handlers"] == 0
    assert controller.get_stats()["subscriber_count"] == 0


@pytest.mark.integration
@pytest.mark.aurora
@pytest.mark.critical
def test_direct_message_delivery():
    """Test direct message is delivered only to addressed agent"""
    controller = GlyphMeshController()

    # Track received messages
    glyphon_messages = []
    caelion_messages = []

    def glyphon_handler(msg: MeshMessage):
        glyphon_messages.append(msg)

    def caelion_handler(msg: MeshMessage):
        caelion_messages.append(msg)

    # Subscribe both agents
    controller.subscribe("Glyphon", glyphon_handler)
    controller.subscribe("Caelion", caelion_handler)

    # Send direct message to Glyphon
    msg = build_message(
        sender="System",
        recipient="Glyphon",
        performative="inform",
        content={"data": "test"}
    )
    controller.publish(msg)

    # Only Glyphon should receive it
    assert len(glyphon_messages) == 1
    assert len(caelion_messages) == 0
    assert glyphon_messages[0].sender == "System"
    assert glyphon_messages[0].content == {"data": "test"}


@pytest.mark.integration
@pytest.mark.aurora
@pytest.mark.critical
def test_broadcast_message_delivery():
    """Test broadcast message is delivered to all subscribers"""
    controller = GlyphMeshController()

    # Track received messages
    glyphon_messages = []
    caelion_messages = []
    velatrix_messages = []

    def glyphon_handler(msg: MeshMessage):
        glyphon_messages.append(msg)

    def caelion_handler(msg: MeshMessage):
        caelion_messages.append(msg)

    def velatrix_handler(msg: MeshMessage):
        velatrix_messages.append(msg)

    # Subscribe three agents
    controller.subscribe("Glyphon", glyphon_handler)
    controller.subscribe("Caelion", caelion_handler)
    controller.subscribe("Velatrix", velatrix_handler)

    # Send broadcast message
    msg = build_message(
        sender="System",
        recipient="ALL",
        performative="inform",
        content={"announcement": "system_update"}
    )
    controller.publish(msg)

    # All three should receive it
    assert len(glyphon_messages) == 1
    assert len(caelion_messages) == 1
    assert len(velatrix_messages) == 1

    # All should have same content
    for messages in [glyphon_messages, caelion_messages, velatrix_messages]:
        assert messages[0].recipient == "ALL"
        assert messages[0].content == {"announcement": "system_update"}


@pytest.mark.integration
@pytest.mark.aurora
def test_handler_exception_handling():
    """Test that handler exceptions don't prevent delivery to other handlers"""
    controller = GlyphMeshController()

    # Track received messages
    good_messages = []

    def failing_handler(msg: MeshMessage):
        raise ValueError("Handler error")

    def good_handler(msg: MeshMessage):
        good_messages.append(msg)

    # Subscribe both handlers to same agent
    controller.subscribe("Glyphon", failing_handler)
    controller.subscribe("Glyphon", good_handler)

    # Publish message
    msg = build_message(
        sender="System",
        recipient="Glyphon",
        performative="inform",
        content={"data": "test"}
    )
    controller.publish(msg)

    # Good handler should still receive the message despite failing handler
    assert len(good_messages) == 1
    assert good_messages[0].content == {"data": "test"}


@pytest.mark.integration
@pytest.mark.aurora
def test_handler_exception_with_multiple_agents():
    """Test exceptions in one agent's handler don't affect others"""
    controller = GlyphMeshController()

    # Track received messages
    caelion_messages = []

    def failing_handler(msg: MeshMessage):
        raise RuntimeError("Glyphon handler failed")

    def caelion_handler(msg: MeshMessage):
        caelion_messages.append(msg)

    # Subscribe both agents
    controller.subscribe("Glyphon", failing_handler)
    controller.subscribe("Caelion", caelion_handler)

    # Broadcast message
    msg = build_message(
        sender="System",
        recipient="ALL",
        performative="inform",
        content={"data": "test"}
    )
    controller.publish(msg)

    # Caelion should receive message despite Glyphon's failure
    assert len(caelion_messages) == 1


@pytest.mark.unit
@pytest.mark.aurora
def test_message_counter_increments():
    """Test message counter increments with each publish"""
    controller = GlyphMeshController()

    def handler(msg: MeshMessage):
        pass

    controller.subscribe("Glyphon", handler)

    # Initial state
    assert controller.get_stats()["message_count"] == 0

    # Publish first message
    msg1 = build_message("System", "Glyphon", "inform", {})
    controller.publish(msg1)
    assert controller.get_stats()["message_count"] == 1

    # Publish second message
    msg2 = build_message("System", "Glyphon", "inform", {})
    controller.publish(msg2)
    assert controller.get_stats()["message_count"] == 2


@pytest.mark.unit
@pytest.mark.aurora
def test_dlp_tag_creation():
    """Test that DLP tags are created for messages"""
    controller = GlyphMeshController()

    def handler(msg: MeshMessage):
        pass

    controller.subscribe("Glyphon", handler)

    # Publish message
    msg = build_message("System", "Glyphon", "inform", {"test": "data"})
    controller.publish(msg)

    # Get DLP manifest
    manifest = controller.get_dlp_manifest()

    assert manifest["manifest_name"] == "glyph_mesh_messages"
    assert manifest["total_tags"] >= 1
    assert len(manifest["tags"]) >= 1

    # Check first tag
    tag = manifest["tags"][0]
    assert tag["operation"] == "glyph_mesh_message"
    assert "EOS_SEED_ORION" in tag["anchor_protocols"]
    assert "T1" in tag["t1_srb_anchors"]
    assert "SRB" in tag["t1_srb_anchors"]
    assert "glyph_message" in tag["symbolic_patterns"]


@pytest.mark.unit
@pytest.mark.aurora
def test_dlp_tag_contains_message_details():
    """Test DLP tag includes message sender, recipient, performative"""
    controller = GlyphMeshController()

    def handler(msg: MeshMessage):
        pass

    controller.subscribe("Caelion", handler)

    # Publish message
    msg = build_message(
        sender="Glyphon",
        recipient="Caelion",
        performative="request",
        content={"action": "sync"},
        layer_context="L2"
    )
    controller.publish(msg)

    # Get DLP manifest
    manifest = controller.get_dlp_manifest()
    tag = manifest["tags"][0]

    # Check symbolic patterns
    glyph_msg = tag["symbolic_patterns"]["glyph_message"]
    assert glyph_msg["sender"] == "Glyphon"
    assert glyph_msg["recipient"] == "Caelion"
    assert glyph_msg["performative"] == "request"
    assert glyph_msg["layer_context"] == "L2"


@pytest.mark.unit
@pytest.mark.aurora
def test_publish_to_nonexistent_recipient():
    """Test publishing to non-subscribed recipient logs warning but doesn't fail"""
    controller = GlyphMeshController()

    # No subscribers
    msg = build_message(
        sender="System",
        recipient="NonExistent",
        performative="inform",
        content={"data": "test"}
    )

    # Should not raise exception
    controller.publish(msg)

    # Message counter should still increment
    assert controller.get_stats()["message_count"] == 1


@pytest.mark.unit
@pytest.mark.aurora
def test_singleton_controller():
    """Test that get_glyph_mesh_controller returns same instance"""
    controller1 = get_glyph_mesh_controller()
    controller2 = get_glyph_mesh_controller()

    assert controller1 is controller2

    # Verify they share state
    def handler(msg: MeshMessage):
        pass

    controller1.subscribe("Glyphon", handler)

    stats2 = controller2.get_stats()
    assert stats2["subscriber_count"] == 1


@pytest.mark.integration
@pytest.mark.aurora
def test_multiple_performatives():
    """Test different performative types work correctly"""
    controller = GlyphMeshController()

    received = []

    def handler(msg: MeshMessage):
        received.append(msg.performative)

    controller.subscribe("Glyphon", handler)

    # Test various performatives
    performatives = ["inform", "request", "propose", "confirm", "reject", "query"]

    for perf in performatives:
        msg = build_message("System", "Glyphon", perf, {})
        controller.publish(msg)

    assert received == performatives


@pytest.mark.integration
@pytest.mark.aurora
def test_layer_contexts():
    """Test different layer contexts are preserved"""
    controller = GlyphMeshController()

    received = []

    def handler(msg: MeshMessage):
        received.append(msg.layer_context)

    controller.subscribe("Glyphon", handler)

    # Test various layer contexts
    layers = ["L1", "L2", "L3", "L1/L2", "L2/L3", "L1/L2/L3"]

    for layer in layers:
        msg = build_message("System", "Glyphon", "inform", {}, layer_context=layer)
        controller.publish(msg)

    assert received == layers


@pytest.mark.unit
@pytest.mark.aurora
def test_stats_accuracy():
    """Test that stats accurately reflect controller state"""
    controller = GlyphMeshController()

    def handler1(msg: MeshMessage):
        pass

    def handler2(msg: MeshMessage):
        pass

    # Add subscribers
    controller.subscribe("Glyphon", handler1)
    controller.subscribe("Glyphon", handler2)
    controller.subscribe("Caelion", handler1)

    stats = controller.get_stats()
    assert stats["subscriber_count"] == 2
    assert stats["total_handlers"] == 3
    assert stats["subscribers"]["Glyphon"] == 2
    assert stats["subscribers"]["Caelion"] == 1

    # Publish messages
    msg = build_message("System", "ALL", "inform", {})
    controller.publish(msg)
    controller.publish(msg)

    stats = controller.get_stats()
    assert stats["message_count"] == 2


@pytest.mark.integration
@pytest.mark.aurora
def test_complex_messaging_scenario():
    """Test complex multi-agent messaging scenario"""
    controller = GlyphMeshController()

    # Track messages for multiple agents
    agent_messages = {
        "Glyphon": [],
        "Caelion": [],
        "Velatrix": [],
        "Harmion": []
    }

    # Create handlers for each agent
    for agent_name in agent_messages.keys():
        def make_handler(name):
            def handler(msg: MeshMessage):
                agent_messages[name].append(msg)
            return handler

        controller.subscribe(agent_name, make_handler(agent_name))

    # 1. Broadcast announcement
    msg1 = build_message("System", "ALL", "inform", {"type": "announcement"})
    controller.publish(msg1)

    # 2. Direct message to Glyphon
    msg2 = build_message("Caelion", "Glyphon", "request", {"action": "status"})
    controller.publish(msg2)

    # 3. Direct message to Velatrix
    msg3 = build_message("Harmion", "Velatrix", "propose", {"plan": "sync"})
    controller.publish(msg3)

    # 4. Another broadcast
    msg4 = build_message("System", "ALL", "inform", {"type": "update"})
    controller.publish(msg4)

    # Verify message counts
    assert len(agent_messages["Glyphon"]) == 3  # 2 broadcasts + 1 direct
    assert len(agent_messages["Caelion"]) == 2  # 2 broadcasts
    assert len(agent_messages["Velatrix"]) == 3  # 2 broadcasts + 1 direct
    assert len(agent_messages["Harmion"]) == 2  # 2 broadcasts

    # Verify controller stats
    stats = controller.get_stats()
    assert stats["message_count"] == 4
    assert stats["subscriber_count"] == 4
