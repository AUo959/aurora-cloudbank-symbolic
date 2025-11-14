# Glyph Mesh Controller

**Multi-Agent Symbolic Coordination Infrastructure**

## Overview

The Glyph Mesh Controller provides an internal event bus and message schema for glyph-like agents (e.g., Glyphon, Caelion, Velatrix, Harmion) to communicate in a structured, observable, and DLP-tagged way.

This controller enables:
- **Structured messaging** with standardized schema
- **Multi-agent coordination** through publish-subscribe pattern
- **DLP-tagged communication** for full traceability and audit
- **Broadcast and direct messaging** for flexible routing
- **Exception resilience** to prevent handler failures from cascading

## Key Features

### Standardized Message Format

Every message in the glyph mesh follows a consistent schema:

```python
@dataclass
class MeshMessage:
    sender: str          # Name of the sending agent
    recipient: str       # Name of receiving agent or "ALL" for broadcast
    performative: str    # Message type (e.g., "inform", "request", "propose")
    content: dict        # Message payload
    layer_context: str   # Layer context (e.g., "L1", "L2", "L3")
    timestamp: str       # ISO-8601 timestamp
```

### Subscribe/Unsubscribe Mechanism

Agents can dynamically join and leave the mesh:

```python
from src.aurora.agents import GlyphMeshController, MeshMessage

controller = GlyphMeshController()

def my_handler(msg: MeshMessage):
    print(f"Received: {msg.content} from {msg.sender}")

# Subscribe
controller.subscribe("Glyphon", my_handler)

# Unsubscribe when done
controller.unsubscribe("Glyphon", my_handler)
```

### Message Publishing

Agents can send direct or broadcast messages:

```python
from src.aurora.agents import build_message

# Direct message
msg = build_message(
    sender="Caelion",
    recipient="Glyphon",
    performative="request",
    content={"action": "status_check"},
    layer_context="L1"
)
controller.publish(msg)

# Broadcast message
broadcast = build_message(
    sender="System",
    recipient="ALL",
    performative="inform",
    content={"announcement": "system_update"}
)
controller.publish(broadcast)
```

## Message Performatives

The controller supports various message types (performatives):

| Performative | Description | Example Use Case |
|-------------|-------------|------------------|
| `inform` | Share information | Status updates, announcements |
| `request` | Request action/data | Ask for status, data query |
| `propose` | Suggest action/plan | Coordination proposals |
| `confirm` | Acknowledge/accept | Confirm receipt, accept proposal |
| `reject` | Decline/refuse | Reject proposal, indicate failure |
| `query` | Ask question | Information requests |

## Layer Contexts

Messages can specify their operational layer:

- **`L1`**: Base layer - direct operations
- **`L2`**: Coordination layer - multi-agent orchestration
- **`L3`**: Meta layer - system-level coordination
- **Combined**: `L1/L2`, `L2/L3`, `L1/L2/L3` for cross-layer operations

## DLP Tagging and Logging

Every published message automatically receives:

1. **DLP Tag** with:
   - Unique tag ID: `glyph::sender->recipient::counter`
   - Operation type: `glyph_mesh_message`
   - Data hash for integrity verification
   - Anchor protocols: `EOS_SEED_ORION`
   - T1/SRB anchors: `T1`, `SRB`
   - Symbolic patterns with message metadata

2. **Structured Logging** with:
   - Component identification
   - Action tracking
   - Sanitized message details
   - DLP tag reference
   - Delivery statistics

## Exception Handling

The controller provides robust error handling:

- **Handler isolation**: Exceptions in one handler don't affect others
- **Continued delivery**: If one subscriber fails, others still receive messages
- **Error logging**: All exceptions are logged with full context
- **Non-blocking**: Failed handlers don't block message processing

## Integration Patterns

### Singleton Pattern

Use the global controller for system-wide coordination:

```python
from src.aurora.agents import get_glyph_mesh_controller

# Get singleton instance
controller = get_glyph_mesh_controller()

# All calls to get_glyph_mesh_controller() return the same instance
```

### Agent Implementation Pattern

Example agent that participates in the mesh:

```python
from src.aurora.agents import get_glyph_mesh_controller, MeshMessage, build_message

class GlyphAgent:
    def __init__(self, name: str):
        self.name = name
        self.controller = get_glyph_mesh_controller()
        self.controller.subscribe(name, self.handle_message)
        self.received_messages = []
    
    def handle_message(self, msg: MeshMessage):
        """Handle incoming messages"""
        self.received_messages.append(msg)
        
        if msg.performative == "request":
            # Respond to requests
            response = build_message(
                sender=self.name,
                recipient=msg.sender,
                performative="inform",
                content={"status": "active", "responding_to": msg.content}
            )
            self.controller.publish(response)
    
    def send_message(self, recipient: str, content: dict):
        """Send a message to another agent"""
        msg = build_message(
            sender=self.name,
            recipient=recipient,
            performative="inform",
            content=content
        )
        self.controller.publish(msg)
    
    def cleanup(self):
        """Cleanup when agent shuts down"""
        self.controller.unsubscribe(self.name, self.handle_message)
```

## Synergy Dashboard Integration

The Glyph Mesh Controller provides the foundation for multi-agent observability:

1. **Message Flow Tracking**: All messages are logged and DLP-tagged
2. **Agent Coordination Visibility**: Subscribe/unsubscribe events tracked
3. **Performance Metrics**: Message counts, delivery statistics, handler errors
4. **Audit Trail**: Complete provenance chain via DLP tags

### Getting Statistics

```python
controller = get_glyph_mesh_controller()

# Get current stats
stats = controller.get_stats()
print(f"Subscribers: {stats['subscriber_count']}")
print(f"Messages: {stats['message_count']}")
print(f"Handlers per agent: {stats['subscribers']}")

# Get DLP manifest for audit
manifest = controller.get_dlp_manifest()
print(f"Total tagged messages: {manifest['total_tags']}")
print(f"Anchor protocols: {manifest['aurora_metadata']['anchor_protocols']}")
```

## Multi-Agent Orchestration

### Workflow Example

Coordinating multiple agents for a complex task:

```python
from src.aurora.agents import get_glyph_mesh_controller, build_message

controller = get_glyph_mesh_controller()

# 1. Announce task to all agents
announcement = build_message(
    sender="Orchestrator",
    recipient="ALL",
    performative="inform",
    content={"task": "data_analysis", "phase": "prepare"}
)
controller.publish(announcement)

# 2. Request status from specific agent
status_request = build_message(
    sender="Orchestrator",
    recipient="Glyphon",
    performative="request",
    content={"action": "status_check"}
)
controller.publish(status_request)

# 3. Propose coordination plan
proposal = build_message(
    sender="Orchestrator",
    recipient="ALL",
    performative="propose",
    content={"plan": "parallel_processing", "agents": ["Glyphon", "Caelion"]}
)
controller.publish(proposal)
```

## Security Considerations

1. **Log Injection Prevention**: All message fields are sanitized before logging
2. **Handler Isolation**: Malicious or buggy handlers can't crash the system
3. **DLP Tagging**: Complete audit trail for security analysis
4. **No External Dependencies**: Fully in-process, no network exposure

## Performance Characteristics

- **Synchronous, in-process**: Low latency, no network overhead
- **Message delivery**: O(n) where n = number of subscribers
- **Memory footprint**: Minimal, only active subscriptions stored
- **DLP overhead**: Negligible, hash computation + JSON serialization

## Future Extensions

The v1 API is designed for extensibility:

- **Topics/Channels**: Group messages by topic
- **Priority Queues**: Prioritize critical messages
- **Reply-To Fields**: Support request-response patterns
- **Message Filtering**: Subscribe to specific performatives or senders
- **Async Support**: Non-blocking message delivery
- **Persistence**: Optional message history storage

## API Reference

### Core Classes

- `MeshMessage`: Dataclass for structured messages
- `GlyphMeshController`: Main controller class
- `build_message()`: Helper for creating messages
- `get_glyph_mesh_controller()`: Get singleton instance

### Controller Methods

- `subscribe(agent_name, handler)`: Register agent handler
- `unsubscribe(agent_name, handler)`: Remove agent handler
- `publish(message)`: Publish message to mesh
- `get_stats()`: Get controller statistics
- `get_dlp_manifest()`: Get DLP audit manifest

## Examples

See `tests/test_glyph_mesh_controller.py` for comprehensive examples including:
- Direct message delivery
- Broadcast messaging
- Exception handling
- DLP tag verification
- Multi-agent scenarios

## Anchors and Tags

- **Anchors**: T1, SRB, EOS_SEED_ORION
- **DLP**: glyph_mesh_controller_core_v1
- **Symbolic Tags**: GLYPH_MESH_CORE, MULTI_AGENT_COORDINATION, SYNERGY_BACKPLANE

## Support

For questions or issues:
1. Review test suite for usage examples
2. Check DLP tags in logs for debugging
3. Use `get_stats()` for runtime diagnostics
4. Consult Synergy Dashboard for multi-agent coordination insights
