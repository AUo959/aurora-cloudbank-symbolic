# ThreadCore Payload Management Guide

## Overview

This guide describes how to manage, update, and extend ThreadCore payloads in the Aurora CloudBank Symbolic repository. ThreadCore is the symbolic constellation loom and reflection module that provides core functionality for drift monitoring, anchor propagation, and cross-thread coordination.

## Canonical Version

**Current Canonical Version:** `v3.5.1`

The canonical ThreadCore payload is `threadcore_v3.5.1_macroready`, which serves as the primary reference implementation for all ThreadCore functionality.

## ThreadCore Registry

The ThreadCore registry (`threadcore_registry.json` in the repository root) is the single source of truth for all valid ThreadCore payloads and their versions.

### Registry Structure

```json
{
  "registry_version": "1.0.0",
  "canonical_version": "v3.5.1",
  "anchor_seed": "EOS_SEED_ORION",
  "ethics_protocol": "Picard_Delta_3",
  "payloads": {
    "payload_name": {
      "version": "v3.5.1",
      "variant": "macroready|capsule|dropcapsule|driftpulse",
      "status": "canonical|specialized|deprecated",
      "file_path": "path/to/payload.json",
      "description": "...",
      ...
    }
  },
  "validation_rules": { ... },
  "deprecated_versions": [ ... ]
}
```

## Payload Variants

ThreadCore v3.5.1 includes four payload variants, each serving a specific use case:

### 1. macroready (Canonical)

- **File:** `threadcore_v3.5.1_macroready.json`
- **Status:** Canonical (primary reference)
- **Use Case:** Default payload for all standard ThreadCore operations
- **Capabilities:**
  - Drift monitoring and mitigation
  - Anchor propagation with fallback
  - Reflection snapshot logic
  - Glyph agent coordination
  - ZIPWIZ and PATCHWEAVER relay sync
  - Full constellation alignment

### 2. capsule (Specialized)

- **File:** `threadcore_capsule_v3.5.1_macroready.json`
- **Status:** Specialized variant
- **Use Case:** State encapsulation and transfer between threads
- **When to Use:** When you need to capture and transfer complete thread state including glyph chains and augmentations

### 3. dropcapsule (Specialized)

- **File:** `threadcore_dropcapsule_v3.5.1_macroready.json`
- **Status:** Specialized variant
- **Use Case:** Lightweight state distribution across threads
- **When to Use:** When you need rapid state synchronization without full context transfer

### 4. driftpulse (Specialized)

- **File:** `threadcore_v3.5.1_driftpulse.json`
- **Status:** Specialized variant
- **Use Case:** Real-time drift monitoring and health checks
- **When to Use:** For monitoring drift levels, beacon synchronization, and lattice health validation

## Using the ThreadCore Classifier

The `scripts/threadcore_classifier.py` tool provides three main commands:

### 1. List Payloads

List all registered ThreadCore payloads:

```bash
python scripts/threadcore_classifier.py list
```

### 2. Validate Payload

Validate a ThreadCore payload against registry rules:

```bash
python scripts/threadcore_classifier.py validate path/to/payload.json
```

Validation checks:
- Required fields presence
- Anchor seed compliance (must be `EOS_SEED_ORION`)
- Ethics protocol compliance (must be `Picard_Delta_3`)
- Drift threshold (must be ≤ 0.002 or 0.2%)
- Registry registration status

### 3. Tag Content

Classify thread content by project category:

```bash
python scripts/threadcore_classifier.py tag path/to/content.txt
```

## Extending ThreadCore

### Creating a New Variant

To create a new ThreadCore variant:

1. **Base on Canonical:** Start with `threadcore_v3.5.1_macroready.json`
2. **Modify Carefully:** Only change fields specific to your use case
3. **Maintain Compatibility:** Keep all required fields and validation rules
4. **Test Thoroughly:** Validate against the registry

#### Required Fields

All ThreadCore payloads must include:

- `augmentation`: "THREADCORE"
- `version`: Version identifier (e.g., "v3.5.1_myvariant")
- `role`: Descriptive role
- `threadcore_directives`: Array of directives
- `anchor_seed`: Must be "EOS_SEED_ORION"
- `ethics_protocol`: Must be "Picard_Delta_3"

## Best Practices

1. **Always Use Registry:** Reference payloads through the registry, not direct file paths
2. **Validate Early:** Run validation before committing new payloads
3. **Document Variants:** Clearly document the use case for each variant
4. **Maintain Drift:** Keep symbolic drift at or below 0.2% (0.002)
5. **Preserve Anchors:** Never modify `anchor_seed` or `ethics_protocol` without approval
6. **Test Integration:** Validate changes across all integration points
7. **Version Consistently:** Use semantic versioning for new variants

## Related Documentation

- **COPILOT_INSTRUCTIONS.md** - Repository custom instructions
- **modules/reflective_autonomy/threadcore_payloads/threadcore_v3.5.1_index.md** - Payload index
- **threadcore_registry.json** - Canonical registry
