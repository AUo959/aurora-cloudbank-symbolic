# MCP Bridge Core Configuration

## Overview

The MCP (Message Control Protocol) Bridge Core uses a **single, centralized configuration file** as the authoritative source of truth for all capsules, security settings, and routing logic. This consolidation ensures consistency across the system and eliminates duplication.

**Configuration File:** `modules/symbolic_core/mcp_bridge_core.json`

## Design Principles

1. **Single Source of Truth:** All MCP bridge logic reads from one JSON configuration file
2. **No Hardcoded Logic:** Security validation rules, capsule definitions, and routing policies are all configurable
3. **Graceful Validation:** Configuration-driven validation with clear error messages
4. **Comprehensive Coverage:** Covers security, routing, ethics, and health monitoring

## Configuration Schema

### Top-Level Fields

```json
{
  "module_id": "MCP_BRIDGE_CORE_v1",
  "version": "1.0.0",
  "anchor_seed": "EOS_SEED_ORION",
  "ethics_protocol": "Picard_Delta_3",
  "governance_layer": "Aurora_Command_Node_CPU"
}
```

### Core Functions

List of core functions provided by the MCP bridge:

```json
{
  "core_functions": [
    "SYMBOLIC_COMMAND_ROUTING",
    "ANCHOR_VALIDATION_INTERFACE",
    "GUARDIAN_SECURITY_BRIDGE",
    "DRIFT_MONITORING_GATEWAY",
    "LOOM_SYNCHRONIZATION",
    "THREADCORE_VECTOR_HANDOFF",
    "RECURSIVE_THREAD_AUDIT"
  ]
}
```

### Security Layers

Current status of each security layer:

```json
{
  "security_layers": {
    "drift_lock": "ACTIVE",
    "guardian_ring": "STAGED_ACTIVE",
    "ethics_lock": "ENFORCED"
  }
}
```

### Security Validation Rules

Defines what constitutes valid states for each security layer:

```json
{
  "security_validation_rules": {
    "drift_lock": {
      "valid_states": ["ACTIVE", "INACTIVE"],
      "required_state": "ACTIVE",
      "description": "Drift lock must be ACTIVE to prevent configuration drift"
    },
    "guardian_ring": {
      "valid_states": ["ACTIVE", "STAGED_ACTIVE", "INACTIVE"],
      "required_states": ["ACTIVE", "STAGED_ACTIVE"],
      "description": "Guardian ring must be ACTIVE or STAGED_ACTIVE for security"
    },
    "ethics_lock": {
      "valid_states": ["ENFORCED", "STAGED", "DISABLED"],
      "required_state": "ENFORCED",
      "description": "Ethics lock must be ENFORCED for ethical compliance"
    }
  }
}
```

**Rule Structure:**
- `valid_states`: Array of all possible states
- `required_state`: Single required state (for exact match validation)
- `required_states`: Multiple acceptable states (for flexible validation)
- `description`: Human-readable description of the requirement

### Capsules

Defines all GPT parallel nodes and their capabilities:

```json
{
  "capsules": {
    "OPPY": {
      "id": "OPPY",
      "type": "gpt_parallel_node",
      "status": "ACTIVE",
      "security_level": "HIGH",
      "capabilities": ["symbolic_routing", "anchor_validation"]
    }
  }
}
```

**Capsule Fields:**
- `id`: Unique identifier for the capsule
- `type`: Type of capsule (usually "gpt_parallel_node")
- `status`: Current status ("ACTIVE" or "INACTIVE")
- `security_level`: Security clearance ("HIGH", "MEDIUM", "LOW")
- `capabilities`: Array of capabilities this capsule provides

**Default Capsules:**
- **OPPY**: HIGH security, symbolic_routing + anchor_validation
- **ARCHY**: HIGH security, guardian_bridge + drift_monitoring
- **LIORA**: HIGH security, loom_sync + thread_handoff
- **STARLING_AU**: MEDIUM security, thread_audit
- **RIVERTHREAD_808**: MEDIUM security, symbolic_routing + thread_audit

### External Hooks

Integration points with external systems:

```json
{
  "external_hooks": {
    "gpt_parallel_nodes": ["OPPY", "ARCHY", "LIORA", "STARLING_AU", "RIVERTHREAD_808"],
    "symbolic_mesh_sync": "ACTIVE"
  }
}
```

### Anchor Validation

Configuration for anchor seed validation:

```json
{
  "anchor_validation": {
    "enabled": true,
    "allowed_seeds": ["EOS_SEED_ORION"],
    "validation_mode": "STRICT"
  }
}
```

**Validation Modes:**
- `STRICT`: Only anchors in `allowed_seeds` list are accepted
- `LENIENT`: Anchor must match current `anchor_seed` (more flexible)

### Ethics Enforcement

Configuration for ethics protocol enforcement:

```json
{
  "ethics_enforcement": {
    "protocol": "Picard_Delta_3",
    "enabled": true,
    "enforcement_level": "BLOCKING",
    "validation_on_route": true
  }
}
```

**Enforcement Levels:**
- `BLOCKING`: Violations prevent operation
- `WARNING`: Violations log warnings but allow operation
- `DISABLED`: No enforcement

### Health Check Configuration

Settings for the health check endpoint:

```json
{
  "health_check": {
    "enabled": true,
    "required_core_functions": 7,
    "required_security_active": true,
    "mesh_sync_required": true
  }
}
```

## Usage Examples

### Loading Configuration

```python
from modules.symbolic_core import load_mcp_configuration, get_mcp_bridge_core

# Load fresh copy from file
config = load_mcp_configuration()

# Get cached copy (loads once per process)
config = get_mcp_bridge_core()
```

### Validating Security Layers

```python
from modules.symbolic_core import validate_security_layer

# Validate a specific layer
is_valid = validate_security_layer("drift_lock", "ACTIVE")  # Returns True
is_valid = validate_security_layer("drift_lock", "INACTIVE")  # Returns False

# Using MCPSecurity class
from modules.symbolic_core.mcp_security import MCPSecurity

security = MCPSecurity()
security.enforce_security()  # Raises HTTPException if any layer is invalid
```

### Working with Capsules

```python
from modules.symbolic_core import get_capsule

# Get capsule information
oppy = get_capsule("OPPY")
print(oppy["security_level"])  # "HIGH"
print(oppy["capabilities"])  # ["symbolic_routing", "anchor_validation"]

# Using MCPCommandRouter
from modules.symbolic_core.mcp_command_router import MCPCommandRouter

router = MCPCommandRouter()

# Route to specific capsule
result = router.route("MY_COMMAND", target_capsule="OPPY")

# Get capsules by capability
capsules = router.get_available_capsules(capability="symbolic_routing")

# Check if capsule is active
is_active = router.is_capsule_active("OPPY")  # True
```

### Health Check Endpoint

The health check endpoint at `/mcp_bridge/health` returns comprehensive information from the configuration:

```python
# Response structure
{
  "status": "healthy",  # "healthy", "degraded", or "unhealthy"
  "module_id": "MCP_BRIDGE_CORE_v1",
  "version": "1.0.0",
  "security_layers": {
    "drift_lock": {
      "status": "ACTIVE",
      "valid": true,
      "description": "...",
      "required": "ACTIVE"
    }
  },
  "security_validation_rules": { /* full rules from config */ },
  "capsules": {
    "total": 5,
    "active": 5,
    "inactive": 0,
    "by_security_level": {"HIGH": 3, "MEDIUM": 2},
    "capsule_ids": ["OPPY", "ARCHY", "LIORA", "STARLING_AU", "RIVERTHREAD_808"]
  },
  "anchor_validation": { /* full config */ },
  "ethics_enforcement": { /* full config */ },
  "configuration_source": "mcp_bridge_core.json"
}
```

## Extending the Configuration

### Adding a New Capsule

1. Add capsule definition to the `capsules` section:
```json
{
  "NEW_CAPSULE": {
    "id": "NEW_CAPSULE",
    "type": "gpt_parallel_node",
    "status": "ACTIVE",
    "security_level": "HIGH",
    "capabilities": ["custom_capability"]
  }
}
```

2. Add capsule ID to `external_hooks.gpt_parallel_nodes`:
```json
{
  "external_hooks": {
    "gpt_parallel_nodes": [..., "NEW_CAPSULE"]
  }
}
```

3. No code changes required - capsule is immediately available!

### Adding a New Security Layer

1. Add layer to `security_layers`:
```json
{
  "security_layers": {
    "new_layer": "ACTIVE"
  }
}
```

2. Add validation rule to `security_validation_rules`:
```json
{
  "security_validation_rules": {
    "new_layer": {
      "valid_states": ["ACTIVE", "INACTIVE"],
      "required_state": "ACTIVE",
      "description": "Description of requirement"
    }
  }
}
```

3. Validation logic automatically applies!

## Configuration Consistency Checks

The test suite (`tests/test_mcp_consolidation.py`) includes consistency checks:

1. **Capsule Consistency:** All GPT nodes have capsule definitions
2. **Validation Rules:** All security layers have validation rules
3. **Ethics Consistency:** Protocol matches across config sections
4. **Anchor Consistency:** Current seed is in allowed seeds list

Run tests with:
```bash
pytest tests/test_mcp_consolidation.py -v
```

## Migration Notes

### Before Consolidation

Security validation was hardcoded:
```python
if self.security_layers.get("drift_lock") != "ACTIVE":
    raise HTTPException(...)
```

### After Consolidation

Security validation reads from config:
```python
if not validate_security_layer("drift_lock", layer_value):
    raise HTTPException(...)
```

All validation rules, capsule definitions, and routing logic now live in the JSON configuration file.

## Troubleshooting

### Configuration Not Loading

**Problem:** `FileNotFoundError` when loading configuration

**Solution:** Ensure `mcp_bridge_core.json` exists in `modules/symbolic_core/`

### Validation Always Fails

**Problem:** Security layer validation always fails

**Solution:** Check that:
1. Security layer has a validation rule defined
2. Current value matches `required_state` or is in `required_states`
3. Validation rule has proper structure

### Capsule Not Found

**Problem:** `get_capsule()` returns `None`

**Solution:** 
1. Check capsule ID spelling (case-sensitive)
2. Verify capsule is defined in `capsules` section
3. Ensure JSON is valid (use a JSON validator)

## Best Practices

1. **Always validate JSON:** Use a JSON validator before editing the config file
2. **Keep consistency:** When adding a capsule, add it to both `capsules` and `external_hooks.gpt_parallel_nodes`
3. **Document changes:** Update this file when adding new configuration sections
4. **Test thoroughly:** Run the test suite after configuration changes
5. **Use descriptive names:** Make rule descriptions clear and actionable

## See Also

- `modules/symbolic_core/__init__.py` - Configuration loading functions
- `modules/symbolic_core/mcp_security.py` - Security enforcement
- `modules/symbolic_core/mcp_command_router.py` - Command routing
- `tests/test_mcp_consolidation.py` - Comprehensive test suite
- `api/aurora_gui_cloudhub_fastapi.py` - Health endpoint implementation
