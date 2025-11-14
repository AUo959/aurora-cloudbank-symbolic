# Relay Manager and Semantic Firewall

## Overview

The Relay Manager is the central enforcement point for all cross-layer messages (L3→L2, L2→L1) in Aurora CloudBank Symbolic. It provides:

- **Schema Validation**: Validates messages against layer-specific schemas (L1, L2, L3)
- **Anchor Resolution**: Attaches and verifies T1/SRB anchor references
- **Ethics Checks**: Integrates with GUMAS ethics engine for high-impact operations
- **Narrative Firewall**: Translates or rejects symbolic L3 content before it reaches L2/L1
- **DLP Tracking**: Full data lineage and provenance tracking for all relay operations

## Architecture

### Layer Definitions

- **L3 (Symbolic/Metaphorical)**: Highest abstraction layer - allows symbolic metaphors, narrative expressions, philosophical queries
- **L2 (Simulation Events)**: Concrete simulation layer - structured events with explicit event_type and parameters
- **L1 (Real-World Actions)**: Lowest layer - direct real-world actions and outputs, no symbolic content allowed

### Components

1. **RelayManager** (`src/aurora/relays/relay_manager.py`)
   - Central coordinator for cross-layer messages
   - Enforces schema validation, anchor protocols, and ethics checks
   - Provides statistics and manifest export

2. **SchemaValidator** (`src/aurora/core/schema_validation.py`)
   - Validates messages against JSON schemas
   - Supports L1, L2, and L3 schema definitions
   - Graceful degradation when jsonschema is unavailable

3. **NarrativeFirewall** (`src/aurora/core/narrative_firewall.py`)
   - Classifies messages as symbolic, literal, or mixed
   - Translates metaphors to concrete L2 events
   - Quarantines untranslatable symbolic content

## Usage

### Basic Example

```python
from src.aurora.relays.relay_manager import get_relay_manager

# Get the global relay manager instance
relay = get_relay_manager()

# Send a message from L2 to L1
payload = {
    "schema_version": "1.0.0",
    "message_type": "l2_simulation_event",
    "event_type": "quantum_simulation",
    "parameters": {"num_qubits": 8, "shots": 1024},
    "context_tag": "my_operation"
}

result = relay.send_cross_layer_message(
    source_layer="L2",
    target_layer="L1",
    payload=payload
)

if result["success"]:
    print(f"Message processed: {result['request_id']}")
    print(f"DLP Tag: {result['dlp_tag_id']}")
```

### L3 to L2 Translation

```python
from src.aurora.relays.relay_manager import get_relay_manager

relay = get_relay_manager()

# Send symbolic L3 message
symbolic_payload = {
    "schema_version": "1.0.0",
    "message_type": "l3_symbolic",
    "content_type": "symbolic_metaphor",
    "payload": {
        "text": "the stars weep"  # Will be translated to "solar_storm"
    },
    "context_tag": "symbolic_event"
}

result = relay.send_cross_layer_message(
    source_layer="L3",
    target_layer="L2",
    payload=symbolic_payload
)

# Check if translation occurred
if result["checks_performed"]["narrative_firewall"]:
    print("Message was translated by narrative firewall")
    print(f"Translated event type: {result['payload']['event_type']}")
```

### Adding Custom Translation Rules

```python
from src.aurora.core.narrative_firewall import get_firewall

firewall = get_firewall()

# Add custom metaphor-to-concrete mapping
firewall.add_translation_rule(
    metaphor="dawn breaks",
    concrete_event="scenario_execution"
)
```

### Handling Errors

```python
from src.aurora.relays.relay_manager import (
    get_relay_manager,
    SchemaViolation,
    EthicsViolation
)

relay = get_relay_manager()

try:
    result = relay.send_cross_layer_message(
        source_layer="L3",
        target_layer="L1",
        payload=payload
    )
except SchemaViolation as e:
    print(f"Schema validation failed: {e.message}")
    print(f"Layer: {e.layer}")
    print(f"Details: {e.details}")
except EthicsViolation as e:
    print(f"Ethics check failed: {e.message}")
    print(f"Violations: {e.details['violations']}")
```

### Exporting Relay Manifests

```python
from src.aurora.relays.relay_manager import get_relay_manager

relay = get_relay_manager()

# Export relay operation manifest
manifest = relay.export_relay_manifest("my_relay_manifest")

print(f"Total messages processed: {manifest['relay_statistics']['messages_processed']}")
print(f"Success rate: {manifest['relay_statistics']['success_rate']:.2%}")
print(f"Translation rules: {manifest['firewall_statistics']['translation_rules']}")
```

## Schema Definitions

### L1 Schema (Real-World Actions)

**Allowed action_type values:**
- `system_output`
- `api_response`
- `data_export`
- `file_write`
- `database_commit`
- `external_api_call`
- `notification_send`

**Required fields:**
- `schema_version` (semver format)
- `message_type` (must be "l1_action")
- `action_type`
- `parameters` (object)
- `context_tag` (DLP tag)

**Prohibited:**
- No symbolic/metaphorical content
- No `content_type` field

### L2 Schema (Simulation Events)

**Allowed event_type values:**
- `quantum_simulation`
- `symbolic_computation`
- `entity_interaction`
- `scenario_execution`
- `memory_operation`
- `drift_measurement`
- `architecture_validation`
- `solar_storm`
- `anomaly_event`
- `faction_event`

**Required fields:**
- `schema_version`
- `message_type` (must be "l2_simulation_event")
- `event_type`
- `parameters` (object)
- `context_tag`

**Optional fields:**
- `anchor_id` (T1/SRB anchor)
- `lore_id` (narrative reference)
- `entity_ids` (array of entity identifiers)
- `location` (station location)
- `risk_score` (0.0 to 1.0)

### L3 Schema (Symbolic/Metaphorical)

**Allowed content_type values:**
- `symbolic_metaphor`
- `narrative_expression`
- `abstract_concept`
- `poetic_insight`
- `philosophical_query`
- `axiom_evaluation`
- `ethics_consideration`
- `lore_fragment`

**Required fields:**
- `schema_version`
- `message_type` (must be "l3_symbolic")
- `content_type`
- `payload` (flexible object)
- `context_tag`

**Payload structure:**
- `text` (string) - Textual symbolic content
- `symbols` (array) - List of symbolic elements
- `metaphor_mapping` (object) - Optional mapping
- `narrative_context` (string) - Lore context

## Narrative Firewall Translation Rules

The narrative firewall includes default translation rules for common metaphors:

| Metaphor | Translates To |
|----------|---------------|
| "the stars weep" | solar_storm |
| "stellar tears" | solar_storm |
| "cosmic storm" | solar_storm |
| "heavens darken" | anomaly_event |
| "void opens" | anomaly_event |
| "system trembles" | drift_measurement |
| "memory fades" | memory_operation |
| "consciousness shifts" | entity_interaction |
| "wisdom flows" | symbolic_computation |
| "truth emerges" | architecture_validation |
| "the fleet gathers" | faction_event |
| "shadows lengthen" | anomaly_event |

Custom rules can be added via `firewall.add_translation_rule()`.

## Integration with Existing Systems

### DLP Tracking

Every relay operation creates a DLP tag with:
- Operation type (`relay_L3_to_L2`, etc.)
- Source and target layers
- Request ID for tracing
- Anchor protocols (EOS_SEED_ORION, etc.)
- T1/SRB anchor references
- Symbolic patterns

### Ethics Engine Integration

The relay manager integrates with GUMAS ethics engine for:
- All L2→L1 transitions
- All L3→L1 transitions
- High-risk operations (risk_score > 0.5)
- Specific high-impact actions (external_api_call, database_commit, file_write)

Ethics violations result in `EthicsViolation` exceptions with detailed violation information.

### Anchor Protocol Resolution

The relay manager automatically adds and verifies anchor protocols:
- **T1_TEMPORAL_ANCHOR**: Added to all messages
- **SRB_BOUNDARY_ANCHOR**: Added when crossing layers
- **EOS_SEED_ORION**: Added for L3 source messages
- **REALITY_BRIDGE**: Added for L1 target messages

## Testing

Run the test suite:

```bash
# All relay manager tests
pytest tests/test_relay_manager.py -v

# Schema validation tests
pytest tests/test_schema_validation.py -v

# Narrative firewall tests
pytest tests/test_narrative_firewall.py -v

# Run all relay-related tests
pytest tests/test_relay_manager.py tests/test_schema_validation.py tests/test_narrative_firewall.py -v
```

## Statistics and Monitoring

Get relay manager statistics:

```python
from src.aurora.relays.relay_manager import get_relay_manager

relay = get_relay_manager()
stats = relay.get_statistics()

print(f"Messages processed: {stats['messages_processed']}")
print(f"Messages blocked: {stats['messages_blocked']}")
print(f"Messages translated: {stats['messages_translated']}")
print(f"Ethics checks: {stats['ethics_checks_performed']}")
print(f"Success rate: {stats['success_rate']:.2%}")
```

## Error Types

### SchemaViolation
Raised when a message fails schema validation for the target layer.
- Contains: `message`, `layer`, `details`

### AnchorViolation
Raised when anchor protocols are violated.
- Contains: `message`, `anchor_type`, `details`

### EthicsViolation
Raised when ethics checks fail.
- Contains: `message`, `violation_details` with list of violations

### RelayUnavailable
Raised when the relay service encounters an internal error.
- Contains: `message`, `reason`

All exceptions inherit from `RelayException` and provide a `to_dict()` method for structured error responses.

## Future Extensions

### Planned Features
- AI-assisted metaphor translation (beyond rule-based)
- Dynamic schema evolution and versioning
- Distributed relay manager for multi-node deployments
- Real-time relay operation dashboards
- Advanced quarantine review and manual translation approval
- Integration with additional ethics frameworks

### Extensibility
- Custom schema validators can be registered
- Translation rules can be loaded from configuration files
- Ethics engines can be swapped via dependency injection
- DLP trackers can be customized or replaced

## DLP and Anchors

**DLP Tag**: `relay_manager_semantic_firewall_v1`

**Anchors**: T1, SRB, EOS_SEED_ORION

**Symbolic Tags**: 
- L1_L3_BOUNDARY_ENFORCEMENT
- SEMANTIC_FIREWALL
- RELAY_MANAGER_CORE

## References

- Symbolic Engine: `src/aurora/core/symbolic_engine.py`
- Native DLP Export: `src/core/native_dlp_export.py`
- Ethics Engine: `src/monitoring/ethics_engine.py`
- Aurora API: `api/aurora_api.py`
