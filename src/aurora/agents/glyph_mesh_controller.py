"""
Glyph Mesh Controller - Multi-Agent Symbolic Coordination

Provides an internal event bus and message schema for glyph-like agents
(e.g., Glyphon, Caelion, Velatrix, Harmion) to communicate in a structured,
observable, and DLP-tagged way.

Features:
- Standardized message format with sender, recipient, performative, content
- Subscribe/unsubscribe mechanism for agent handlers
- Broadcast messaging (recipient="ALL")
- DLP tagging and structured logging for every message
- Exception handling to prevent handler failures from affecting other agents

Anchors: T1, SRB, EOS_SEED_ORION
DLP: glyph_mesh_controller_core_v1
Symbolic Tags: GLYPH_MESH_CORE, MULTI_AGENT_COORDINATION, SYNERGY_BACKPLANE
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

from src.core.native_dlp_export import NativeDLPTag, NativeDLPTracker
from src.core.logging_security import sanitize_for_logging

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class MeshMessage:
    """
    Structured message for glyph mesh communication.

    Attributes:
        sender: Name of the sending agent
        recipient: Name of the receiving agent or "ALL" for broadcast
        performative: Message type (e.g., "inform", "request", "propose", "confirm")
        content: Message payload as a dictionary
        layer_context: Layer context (e.g., "L1", "L2", "L3", or combined like "L1/L2")
        timestamp: ISO-8601 timestamp of message creation
    """
    sender: str
    recipient: str
    performative: str
    content: dict
    layer_context: str
    timestamp: str


def build_message(
    sender: str,
    recipient: str,
    performative: str,
    content: dict,
    layer_context: str = "L1"
) -> MeshMessage:
    """
    Build a standardized MeshMessage with automatic timestamping.

    Args:
        sender: Name of the sending agent
        recipient: Name of the receiving agent or "ALL" for broadcast
        performative: Message type (e.g., "inform", "request", "propose")
        content: Message payload as a dictionary
        layer_context: Layer context (default: "L1")

    Returns:
        MeshMessage with ISO-8601 timestamp

    Example:
        >>> msg = build_message("Glyphon", "Caelion", "inform", {"status": "ready"})
        >>> msg.sender
        'Glyphon'
    """
    return MeshMessage(
        sender=sender,
        recipient=recipient,
        performative=performative,
        content=content,
        layer_context=layer_context,
        timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    )


class GlyphMeshController:
    """
    Controller for multi-agent symbolic coordination via structured messaging.

    Provides:
    - Agent subscription management
    - Message publishing with DLP tagging
    - Broadcast and direct message routing
    - Exception handling for robust delivery
    - Structured logging with security sanitization

    Example:
        >>> controller = GlyphMeshController()
        >>>
        >>> def handle_message(msg: MeshMessage):
        ...     print(f"Received: {msg.content}")
        >>>
        >>> controller.subscribe("Glyphon", handle_message)
        >>> msg = build_message("Caelion", "Glyphon", "inform", {"data": "test"})
        >>> controller.publish(msg)
    """

    def __init__(self):
        """Initialize the Glyph Mesh Controller."""
        self._subscribers: Dict[str, List[Callable[[MeshMessage], None]]] = {}
        self._dlp_tracker = NativeDLPTracker()
        self._message_counter = 0

        logger.info(
            "Glyph Mesh Controller initialized",
            extra={
                "component": "glyph_mesh_controller",
                "action": "initialize",
                "anchors": ["T1", "SRB", "EOS_SEED_ORION"]
            }
        )

    def subscribe(self, agent_name: str, handler: Callable[[MeshMessage], None]) -> None:
        """
        Subscribe an agent handler to receive messages.

        Args:
            agent_name: Name of the agent subscribing
            handler: Callable that accepts a MeshMessage

        Example:
            >>> controller = GlyphMeshController()
            >>> def my_handler(msg): pass
            >>> controller.subscribe("Glyphon", my_handler)
        """
        if agent_name not in self._subscribers:
            self._subscribers[agent_name] = []

        if handler not in self._subscribers[agent_name]:
            self._subscribers[agent_name].append(handler)

            logger.info(
                f"Agent subscribed to mesh: {sanitize_for_logging(agent_name)}",
                extra={
                    "component": "glyph_mesh_controller",
                    "action": "subscribe",
                    "agent_name": sanitize_for_logging(agent_name),
                    "handler_count": len(self._subscribers[agent_name])
                }
            )

    def unsubscribe(self, agent_name: str, handler: Callable[[MeshMessage], None]) -> None:
        """
        Unsubscribe an agent handler from receiving messages.

        Args:
            agent_name: Name of the agent unsubscribing
            handler: The handler callable to remove

        Example:
            >>> controller = GlyphMeshController()
            >>> def my_handler(msg): pass
            >>> controller.subscribe("Glyphon", my_handler)
            >>> controller.unsubscribe("Glyphon", my_handler)
        """
        if agent_name in self._subscribers:
            if handler in self._subscribers[agent_name]:
                self._subscribers[agent_name].remove(handler)

                logger.info(
                    f"Agent unsubscribed from mesh: {sanitize_for_logging(agent_name)}",
                    extra={
                        "component": "glyph_mesh_controller",
                        "action": "unsubscribe",
                        "agent_name": sanitize_for_logging(agent_name),
                        "handler_count": len(self._subscribers[agent_name])
                    }
                )

                # Clean up empty subscriber lists
                if not self._subscribers[agent_name]:
                    del self._subscribers[agent_name]

    def publish(self, message: MeshMessage) -> None:
        """
        Publish a message to the mesh with DLP tagging and structured logging.

        Messages are delivered to:
        - All subscribers if recipient == "ALL" (broadcast)
        - Only the named recipient's handlers otherwise

        Handler exceptions are caught and logged without failing the entire publish.

        Args:
            message: MeshMessage to publish

        Example:
            >>> controller = GlyphMeshController()
            >>> msg = build_message("Glyphon", "ALL", "inform", {"status": "online"})
            >>> controller.publish(msg)
        """
        self._message_counter += 1

        # Create DLP tag for this message
        dlp_tag = self._create_dlp_tag(message)

        # Log the message with DLP tag
        self._log_message(message, dlp_tag)

        # Determine recipients
        if message.recipient == "ALL":
            # Broadcast to all subscribers
            recipients = list(self._subscribers.keys())
        elif message.recipient in self._subscribers:
            # Direct message to specific agent
            recipients = [message.recipient]
        else:
            # No subscribers for this recipient
            logger.warning(
                f"No subscribers found for recipient: {sanitize_for_logging(message.recipient)}",
                extra={
                    "component": "glyph_mesh_controller",
                    "action": "publish_no_recipient",
                    "sender": sanitize_for_logging(message.sender),
                    "recipient": sanitize_for_logging(message.recipient),
                    "dlp_tag_id": dlp_tag.tag_id
                }
            )
            recipients = []

        # Deliver to all relevant handlers
        delivery_count = 0
        error_count = 0

        for recipient_name in recipients:
            handlers = self._subscribers.get(recipient_name, [])

            for handler in handlers:
                try:
                    handler(message)
                    delivery_count += 1
                except Exception as e:
                    error_count += 1
                    logger.error(
                        f"Handler exception for agent {sanitize_for_logging(recipient_name)}: {e}",
                        extra={
                            "component": "glyph_mesh_controller",
                            "action": "handler_exception",
                            "recipient": sanitize_for_logging(recipient_name),
                            "sender": sanitize_for_logging(message.sender),
                            "error": str(e),
                            "dlp_tag_id": dlp_tag.tag_id
                        },
                        exc_info=True
                    )

        logger.info(
            f"Message published: {delivery_count} deliveries, {error_count} errors",
            extra={
                "component": "glyph_mesh_controller",
                "action": "publish_complete",
                "delivery_count": delivery_count,
                "error_count": error_count,
                "dlp_tag_id": dlp_tag.tag_id
            }
        )

    def _create_dlp_tag(self, message: MeshMessage) -> NativeDLPTag:
        """
        Create a DLP tag for a glyph mesh message.

        Args:
            message: MeshMessage to tag

        Returns:
            NativeDLPTag with proper anchors and symbolic patterns
        """
        # Create tag ID
        tag_id = f"glyph::{message.sender}->{message.recipient}::{self._message_counter}"

        # Create data hash
        message_str = json.dumps(asdict(message), sort_keys=True)
        data_hash = hashlib.sha256(message_str.encode()).hexdigest()

        # Create DLP tag
        dlp_tag = NativeDLPTag(
            tag_id=tag_id,
            operation="glyph_mesh_message",
            data_hash=data_hash,
            timestamp=time.time()
        )

        # Add anchor protocols
        dlp_tag.add_anchor_protocol("EOS_SEED_ORION")

        # Add T1/SRB anchors
        dlp_tag.add_t1_srb_anchor("T1")
        dlp_tag.add_t1_srb_anchor("SRB")

        # Add symbolic patterns
        dlp_tag.set_symbolic_pattern("glyph_message", {
            "sender": message.sender,
            "recipient": message.recipient,
            "performative": message.performative,
            "layer_context": message.layer_context,
            "timestamp": message.timestamp
        })

        # Store in tracker
        self._dlp_tracker.tags[tag_id] = dlp_tag

        return dlp_tag

    def _log_message(self, message: MeshMessage, dlp_tag: NativeDLPTag) -> None:
        """
        Log a message with structured fields and DLP tag.

        Args:
            message: MeshMessage to log
            dlp_tag: Associated DLP tag
        """
        logger.info(
            f"Glyph mesh message: {sanitize_for_logging(message.sender)} -> "
            f"{sanitize_for_logging(message.recipient)} [{message.performative}]",
            extra={
                "component": "glyph_mesh_controller",
                "action": "publish",
                "sender": sanitize_for_logging(message.sender),
                "recipient": sanitize_for_logging(message.recipient),
                "performative": sanitize_for_logging(message.performative),
                "layer_context": sanitize_for_logging(message.layer_context),
                "timestamp": message.timestamp,
                "dlp_tag_id": dlp_tag.tag_id,
                "dlp_tag": dlp_tag.to_dict(),
                "message_counter": self._message_counter
            }
        )

    def get_stats(self) -> Dict:
        """
        Get statistics about the mesh controller.

        Returns:
            Dictionary with subscriber counts and message statistics

        Example:
            >>> controller = GlyphMeshController()
            >>> stats = controller.get_stats()
            >>> stats['message_count']
            0
        """
        return {
            "subscriber_count": len(self._subscribers),
            "total_handlers": sum(len(handlers) for handlers in self._subscribers.values()),
            "message_count": self._message_counter,
            "subscribers": {
                agent: len(handlers)
                for agent, handlers in self._subscribers.items()
            }
        }

    def get_dlp_manifest(self) -> Dict:
        """
        Get DLP manifest for all mesh messages.

        Returns:
            DLP export manifest with all message tags

        Example:
            >>> controller = GlyphMeshController()
            >>> manifest = controller.get_dlp_manifest()
            >>> manifest['manifest_name']
            'glyph_mesh_messages'
        """
        return self._dlp_tracker.create_export_manifest("glyph_mesh_messages")


# Singleton instance for global use
_global_controller: Optional[GlyphMeshController] = None


def get_glyph_mesh_controller() -> GlyphMeshController:
    """
    Get or create the global GlyphMeshController singleton.

    Returns:
        Global GlyphMeshController instance

    Example:
        >>> controller1 = get_glyph_mesh_controller()
        >>> controller2 = get_glyph_mesh_controller()
        >>> controller1 is controller2
        True
    """
    global _global_controller
    if _global_controller is None:
        _global_controller = GlyphMeshController()
    return _global_controller
