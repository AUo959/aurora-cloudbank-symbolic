# Aurora Ethics Gate Module

## Overview

The **Ethics Gate** is a central ethics evaluation system for Aurora CloudBank Symbolic that provides consistent ethics enforcement across all high-impact operations. It wraps the existing GUMAS Ethics API and prepares for future Picard_Delta_3 integration.

## Purpose

The Ethics Gate serves as a unified interface for:

- **Ethics Evaluation**: Evaluate actions and commands against GUMAS ethics rules
- **Consistent Enforcement**: Apply the same ethics standards across API endpoints, relay systems, and admin tools
- **DLP Tracking**: Track all ethics evaluations with Data Lineage Protocol tags
- **Anchor Compliance**: Include T1/SRB anchors and EOS_SEED_ORION/Picard_Delta_3 references
- **Structured Logging**: Log evaluations with anchor references for audit trails
- **Future Integration**: Prepare for Picard_Delta_3 ethics engine with minimal code changes

## Architecture

### Components

```
src/aurora/ethics/
├── __init__.py          # Module exports
└── ethics_gate.py       # Core implementation
    ├── EthicsVerdict    # Normalized verdict dataclass
    ├── GUMASEthicsClient # HTTP adapter for GUMAS API
    ├── EthicsGate       # Main evaluation class
    └── EthicsViolation  # Exception for blocked actions

src/aurora/relays/
├── __init__.py          # Module exports
└── relay_manager.py     # Cross-layer relay with ethics integration
    ├── RelayMessage     # Message dataclass
    └── RelayManager     # Relay manager with ethics checks
```

### Data Flow

```
Action/Command
     ↓
EthicsGate.evaluate()
     ↓
GUMASEthicsClient.evaluate()
     ↓
GUMAS HTTP API (/gumas/evaluate)
     ↓
Normalized Response
     ↓
EthicsVerdict (allowed, score, reason)
     ↓
DLP Tag Generation (with anchors)
     ↓
Structured Logging
     ↓
Return to Caller
```

## Usage

### Basic Evaluation

```python
from src.aurora.ethics import EthicsGate, GUMASEthicsClient, EthicsViolation

# Initialize client and gate
client = GUMASEthicsClient(base_url="http://localhost:8000")
gate = EthicsGate(client=client, threshold=0.7)

# Evaluate an action
action = {
    "type": "delete_node",
    "node_id": "critical_001",
    "layer": "L2"
}

context = {
    "agent_id": "admin",
    "route": "/api/nodes/delete",
    "source": "api_endpoint"
}

verdict = await gate.evaluate(action, context)

# Check result
if not verdict.allowed:
    raise EthicsViolation(f"Action blocked: {verdict.reason}", verdict)

# Proceed with action
print(f"Action allowed (score={verdict.score:.2f})")
```

### Relay Manager Integration

```python
from src.aurora.relays import RelayManager, RelayMessage
from src.aurora.ethics import EthicsGate, GUMASEthicsClient, EthicsViolation

# Initialize relay manager with ethics gate
client = GUMASEthicsClient()
gate = EthicsGate(client=client, threshold=0.7)
manager = RelayManager(ethics_gate=gate)

# Create message requiring ethics check
message = RelayMessage(
    message_id="msg_001",
    source_layer="L1",
    target_layer="L2",
    message_type="state_change",
    payload={"action": "update_config", "key": "threshold"},
    requires_ethics_check=True  # Enable ethics evaluation
)

# Send message (raises EthicsViolation if blocked)
try:
    result = await manager.send_message(message)
    print(f"Message delivered: {result['message_id']}")
except EthicsViolation as e:
    print(f"Message blocked: {e.message}")
    print(f"Score: {e.verdict.score}, Reason: {e.verdict.reason}")
```

### API Endpoint Integration

```python
from fastapi import APIRouter, HTTPException
from src.aurora.ethics import EthicsGate, GUMASEthicsClient, EthicsViolation

router = APIRouter()
ethics_gate = EthicsGate(GUMASEthicsClient(), threshold=0.7)

@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    """Delete node with ethics check"""
    
    # Evaluate through ethics gate
    action = {
        "type": "delete_node",
        "node_id": node_id,
        "resource": "system_node"
    }
    
    context = {
        "agent_id": "api_user",
        "route": f"/nodes/{node_id}",
        "source": "api"
    }
    
    try:
        verdict = await ethics_gate.evaluate(action, context)
        
        if not verdict.allowed:
            # Return safe, generic error to client
            raise HTTPException(
                status_code=403,
                detail="Action not permitted by ethics policy"
            )
        
        # Detailed reason logged server-side (see logs)
        
        # Proceed with deletion
        # ... perform actual deletion ...
        
        return {"status": "success", "node_id": node_id}
        
    except EthicsViolation as e:
        # Log detailed reason server-side
        logger.warning(
            "Ethics gate blocked delete_node: %s (score=%.2f)",
            e.verdict.reason,
            e.verdict.score,
            extra={
                "node_id": node_id,
                "verdict": e.verdict.to_dict()
            }
        )
        raise HTTPException(
            status_code=403,
            detail="Action not permitted by ethics policy"
        )
```

## Configuration

### Threshold

The `threshold` parameter controls the minimum ethics score required for approval:

- **Default**: `0.7` (70%)
- **Range**: `0.0` to `1.0`
- **Lower threshold**: More permissive (allow more actions)
- **Higher threshold**: More restrictive (block more actions)

```python
# Permissive (50% threshold)
gate = EthicsGate(client, threshold=0.5)

# Standard (70% threshold)
gate = EthicsGate(client, threshold=0.7)

# Strict (90% threshold)
gate = EthicsGate(client, threshold=0.9)
```

### Score Calculation

Ethics scores are calculated based on violation severity:

| Violation Severity | Score | Typical Outcome (threshold=0.7) |
|-------------------|-------|----------------------------------|
| None (compliant)  | 1.0   | ✅ Allowed                       |
| Low               | 0.7   | ✅ Allowed (at threshold)        |
| Medium            | 0.5   | ❌ Blocked                       |
| High              | 0.3   | ❌ Blocked                       |
| Critical          | 0.0   | ❌ Blocked                       |

## DLP Tracking

Every ethics evaluation generates a DLP tag with:

- **Tag ID**: `ethics::gate::evaluation::{timestamp}`
- **Operation**: `"ethics_gate_evaluate"`
- **Anchor Protocols**: `["EOS_SEED_ORION", "Picard_Delta_3"]`
- **T1/SRB Anchors**: `["T1", "SRB"]`
- **Symbolic Patterns**: Ethics context with action type, source, agent, score, allowed

## References

- **GUMAS Ethics API**: `modules/gumas/api/routes.py`
- **Native DLP Export**: `src/core/native_dlp_export.py`
- **Ethics Engine**: `src/monitoring/ethics_engine.py`
- **Relay Agents**: `src/entities/relay_agents.py`

## Version

- **Module**: `aurora.ethics.ethics_gate`
- **Version**: `1.0.0`
- **DLP**: `ethics_gate_core_v1`
- **Anchors**: `T1`, `SRB`, `EOS_SEED_ORION`, `Picard_Delta_3`
- **Tags**: `ETHICS_GATE_CORE`, `GUMAS_INTEGRATION`, `PICARD_DELTA_3_READY`
