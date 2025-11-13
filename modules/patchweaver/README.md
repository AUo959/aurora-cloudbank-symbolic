# PatchWeaver

**Controlled, DLP-aware, ethics-gated state patching engine for Aurora CloudBank Symbolic**

## Overview

PatchWeaver enables fine-grained modifications to simulation or narrative state (L2/L3) while preserving Aurora/GUMAS continuity, anchor, and ethics guarantees.

### Key Features

- **Structured Patch Operations**: Apply set/delete operations on nested dict structures
- **Hash-Sealed State**: Before/after state snapshots for traceability and recovery
- **DLP Tagging**: Full anchor protocols (T1/SRB, EOS_SEED_ORION, Picard_Delta_3)
- **Ethics Gate Integration**: All patches validated before application
- **Flexible State Backends**: Dependency injection for any storage mechanism
- **Comprehensive Audit Trail**: Full operation history via DLP tracker

## Installation

PatchWeaver is part of the Aurora CloudBank Symbolic core. No additional installation required.

```python
from src.aurora.patching.patchweaver import PatchWeaver, PatchResult
from src.core.native_dlp_export import NativeDLPTracker
from src.monitoring.ethics_engine import EthicsEngine
```

## Quick Start

### Basic Usage

```python
from src.aurora.patching.patchweaver import PatchWeaver
from src.monitoring.ethics_engine import EthicsEngine
from src.core.native_dlp_export import NativeDLPTracker

# Set up state backend (in-memory example)
state_storage = {"simulation": {"status": "active", "score": 100}}

# Create PatchWeaver with ethics gate
ethics = EthicsEngine()
weaver = PatchWeaver(
    load_state=lambda: state_storage,
    save_state=lambda s: state_storage.update(s),
    ethics_gate=ethics
)

# Apply a patch
patch = {
    "set": {
        "simulation/score": 150,
        "simulation/updated": "2025-11-13"
    },
    "delete": [
        "simulation/old_field"
    ]
}

result = weaver.apply_patch(
    patch=patch,
    context={"agent_id": "admin", "context_tag": "score_update"}
)

if result.applied:
    print(f"Patch applied successfully")
    print(f"Before hash: {result.before_hash[:12]}...")
    print(f"After hash: {result.after_hash[:12]}...")
    print(f"Modified {len(result.modified_paths)} paths")
else:
    print(f"Patch blocked: {result.reason}")
```

## Patch Format

Patches are structured as dictionaries with optional `set` and `delete` operations:

### Set Operations

Set operations use slash-separated paths to navigate nested dictionaries:

```python
{
    "set": {
        "top_level_key": "value",
        "nested/path/to/key": "value",
        "deeply/nested/structure": {"can": "be", "complex": True}
    }
}
```

- Paths use `/` as separator: `"a/b/c"` → `state["a"]["b"]["c"]`
- Intermediate dicts are created automatically
- Values can be any JSON-serializable type
- Existing values are overwritten

### Delete Operations

Delete operations remove keys at specified paths:

```python
{
    "delete": [
        "top_level_key",
        "nested/path/to/remove",
        "another/key"
    ]
}
```

- Paths use same `/` separator format
- Deletion is idempotent (no error if key doesn't exist)
- Only the final key in path is removed
- Parent structures remain intact

### Mixed Operations

You can combine set and delete in a single patch:

```python
{
    "set": {
        "config/new_setting": "value",
        "status": "updated"
    },
    "delete": [
        "config/deprecated_setting",
        "temp_data"
    ]
}
```

Operations are applied in deterministic order:
1. All `set` operations (in dict iteration order)
2. All `delete` operations (in list order)

## Ethics Gate Integration

All patches must pass ethics validation before being applied:

```python
from src.monitoring.ethics_engine import (
    EthicsEngine, 
    EthicsRule, 
    RuleCategory, 
    ViolationSeverity
)

# Create ethics engine with custom rules
ethics = EthicsEngine()

# Add custom rule for patch restrictions
critical_data_rule = EthicsRule(
    id="PATCH_001",
    name="Protect Critical Data",
    description="Prevent modification of critical simulation data",
    category=RuleCategory.SAFETY,
    severity=ViolationSeverity.CRITICAL,
    auto_block=True,
    conditions=["modifies_critical_data"]
)
ethics.add_rule(critical_data_rule)

# Use with PatchWeaver
weaver = PatchWeaver(
    load_state=load_fn,
    save_state=save_fn,
    ethics_gate=ethics
)

# Patches that violate rules will be blocked
result = weaver.apply_patch(
    patch={"set": {"critical/data": "new_value"}},
    context={
        "agent_id": "user",
        "modifies_critical_data": True  # Triggers rule
    }
)

assert result.applied is False
assert "Ethics gate blocked" in result.reason
```

## DLP Tagging and Anchors

Every patch operation creates a comprehensive DLP tag:

```python
result = weaver.apply_patch(patch, context)

# Get patch history from DLP tracker
history = weaver.get_patch_history()

for entry in history:
    print(f"Operation: {entry['operation']}")
    print(f"Timestamp: {entry['datetime']}")
    print(f"Anchors: {entry['anchor_protocols']}")
    print(f"T1/SRB: {entry['t1_srb_anchors']}")
    
    metadata = entry['symbolic_patterns']['patch_metadata']
    print(f"Modified paths: {metadata['modified_paths']}")
    print(f"Before hash: {metadata['before_hash'][:12]}...")
    print(f"After hash: {metadata['after_hash'][:12]}...")
```

### Anchor Protocols

Each patch is tagged with:

- **T1/SRB Anchors**: `T1`, `SRB` - Temporal and spatial-relational boundaries
- **EOS_SEED_ORION**: End-of-Sequence seed for Orion Station continuity
- **Picard_Delta_3**: Delta-3 protocol compliance
- **PATCHWEAVER_CORE**: PatchWeaver-specific anchor

## State Backends

PatchWeaver supports any state backend via dependency injection:

### In-Memory State

```python
state = {"data": "value"}

weaver = PatchWeaver(
    load_state=lambda: state,
    save_state=lambda s: state.update(s),
    ethics_gate=ethics
)
```

### File-Based State

```python
import json
from pathlib import Path

STATE_FILE = Path("state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

weaver = PatchWeaver(
    load_state=load_state,
    save_state=save_state,
    ethics_gate=ethics
)
```

### Database-Backed State

```python
def load_state():
    # Query database
    row = db.query("SELECT state FROM app_state WHERE id = 1")
    return json.loads(row['state'])

def save_state(state):
    # Update database
    db.execute(
        "UPDATE app_state SET state = ? WHERE id = 1",
        [json.dumps(state)]
    )

weaver = PatchWeaver(
    load_state=load_state,
    save_state=save_state,
    ethics_gate=ethics
)
```

## Hash Verification

PatchWeaver provides state integrity verification:

```python
# Apply patch and save result
result = weaver.apply_patch(patch, context)
print(f"New state hash: {result.after_hash}")

# Later, verify state hasn't changed
if weaver.verify_state_hash(result.after_hash):
    print("State integrity verified ✓")
else:
    print("State has been modified! ✗")
```

## API Usage

PatchWeaver is exposed via admin API endpoint (see API integration):

```bash
# Apply patch via API
curl -X POST https://aurora.example.com/admin/patchweaver/apply \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d '{
    "patch": {
      "set": {
        "config/setting": "value"
      },
      "delete": ["old_key"]
    },
    "context": {
      "agent_id": "admin_user",
      "context_tag": "config_update",
      "reason": "Update production config"
    }
  }'
```

Response:

```json
{
  "applied": true,
  "reason": "ok",
  "before_hash": "a1b2c3d4...",
  "after_hash": "e5f6g7h8...",
  "modified_paths": [
    "set:config/setting",
    "delete:old_key"
  ],
  "timestamp": "2025-11-13T23:45:00Z"
}
```

## Security Considerations

### Admin-Only Access

PatchWeaver operations are restricted to admin users:

- CSRF protection required
- Authentication token required
- Rate limiting enforced (strict)
- All operations logged with full audit trail

### Ethics Validation

All patches must pass ethics gate validation:

- Critical violations block patches automatically
- Violations are logged for review
- Custom rules can be added per deployment
- Remediation suggestions provided

### State Integrity

State modifications are tracked and verifiable:

- SHA256 hashes before and after
- Full DLP audit trail
- Recovery possible via hash verification
- Idempotent operations (safe to retry)

## Advanced Usage

### Custom Ethics Rules

```python
from src.monitoring.ethics_engine import EthicsRule

# Prevent modifications during maintenance windows
maintenance_rule = EthicsRule(
    id="PATCH_MAINTENANCE",
    name="Block During Maintenance",
    description="Prevent state changes during maintenance",
    category=RuleCategory.SAFETY,
    severity=ViolationSeverity.HIGH,
    auto_block=True,
    conditions=["in_maintenance_window"]
)

ethics.add_rule(maintenance_rule)

# Patches with this context will be blocked
result = weaver.apply_patch(
    patch={"set": {"data": "value"}},
    context={
        "agent_id": "admin",
        "in_maintenance_window": True
    }
)
```

### Batch Operations

```python
# Apply multiple patches in sequence
patches = [
    {"set": {"stage": "1"}},
    {"set": {"stage": "2"}},
    {"set": {"stage": "3", "complete": True}}
]

results = []
for i, patch in enumerate(patches):
    result = weaver.apply_patch(
        patch=patch,
        context={
            "agent_id": "batch_processor",
            "context_tag": f"batch_operation_{i}",
            "batch_id": "batch_001"
        }
    )
    results.append(result)
    
    if not result.applied:
        print(f"Batch failed at step {i}: {result.reason}")
        break
```

### Dry-Run Mode (Future Enhancement)

While not implemented in v1, dry-run mode is planned:

```python
# Future: Preview patch without applying
result = weaver.preview_patch(patch, context)
print(f"Would modify {len(result.modified_paths)} paths")
print(f"Ethics violations: {len(result.violations)}")
```

## Troubleshooting

### Patch Not Applied

Check the result reason:

```python
if not result.applied:
    print(f"Failure reason: {result.reason}")
    
    # Check for ethics violations
    if "Ethics gate blocked" in result.reason:
        # Review ethics rules and context
        violations = ethics.get_violations(agent_id=context["agent_id"])
        for v in violations:
            print(f"Violation: {v.rule_name} - {v.description}")
```

### State Load/Save Errors

```python
try:
    result = weaver.apply_patch(patch, context)
except Exception as e:
    print(f"Error: {e}")
    # Check state backend connectivity
    # Verify load_state/save_state functions
```

### Hash Mismatches

```python
# If verification fails, check for external modifications
if not weaver.verify_state_hash(expected_hash):
    current_state = weaver.load_state()
    current_hash = weaver._compute_hash(current_state)
    print(f"Expected: {expected_hash}")
    print(f"Current: {current_hash}")
    # Review state for unexpected changes
```

## Related Documentation

- [Native DLP Export System](../../src/core/native_dlp_export.py) - Data lineage and provenance
- [Ethics Engine](../../src/monitoring/ethics_engine.py) - Rule-based ethics validation
- [Symbolic Engine](../../src/aurora/core/symbolic_engine.py) - T1/SRB anchors
- [API Integration](../../api/aurora_api.py) - FastAPI endpoints

## Version History

- **v1.0.0** (2025-11-13): Initial release
  - Set/delete patch operations
  - Ethics gate integration
  - DLP tagging with full anchors
  - Hash-sealed state snapshots
  - Comprehensive audit trail

## License

Part of Aurora CloudBank Symbolic - See repository LICENSE for details.
