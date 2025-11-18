# ThreadCore Payloads Directory

This directory contains the canonical ThreadCore payload files for the Aurora CloudBank Symbolic system.

## Registry

All payloads in this directory are registered in the **ThreadCore Registry** at the repository root: `threadcore_registry.json`

The registry is the single source of truth for:
- Valid payload versions
- Canonical vs specialized variants
- Deprecation status
- File paths and descriptions

## Current Payloads

### Canonical Payload

**threadcore_v3.5.1_macroready.json** - Primary canonical payload
- Version: v3.5.1
- Status: Canonical (primary reference)
- Use Case: Default for all standard ThreadCore operations

### Specialized Variants

**threadcore_capsule_v3.5.1_macroready.json**
- Variant: capsule
- Use Case: State encapsulation and transfer between threads

**threadcore_dropcapsule_v3.5.1_macroready.json**
- Variant: dropcapsule
- Use Case: Lightweight state distribution across threads

**threadcore_v3.5.1_driftpulse.json**
- Variant: driftpulse
- Use Case: Real-time drift monitoring and health checks

## Usage

### Validation

Validate a payload against the registry:

```bash
python scripts/threadcore_classifier.py validate \
  modules/reflective_autonomy/threadcore_payloads/threadcore_v3.5.1_macroready.json
```

### Listing All Payloads

List all registered payloads:

```bash
python scripts/threadcore_classifier.py list
```

## Documentation

For complete documentation on ThreadCore payload management:
- **docs/threadcore/THREADCORE_MANAGEMENT.md** - Full management guide
- **threadcore_registry.json** - Registry specification
- **threadcore_v3.5.1_index.md** - Payload index

## Required Fields

All ThreadCore payloads must include:
- `augmentation`: "THREADCORE"
- `version`: Version identifier
- `role`: Descriptive role
- `threadcore_directives`: Array of directives
- `anchor_seed`: Must be "EOS_SEED_ORION"
- `ethics_protocol`: Must be "Picard_Delta_3"

## Modification Guidelines

**DO NOT** modify payloads directly without:
1. Validating against the registry
2. Updating the registry if creating new variants
3. Following the extension guidelines in docs/threadcore/THREADCORE_MANAGEMENT.md
4. Testing integration points

## Anchor Compliance

All payloads in this directory:
- ✅ Anchor Seed: `EOS_SEED_ORION`
- ✅ Ethics Protocol: `Picard_Delta_3`
- ✅ Drift Threshold: ≤ 0.2% (0.002)
- ✅ Glyph Resonance: `LOOMFIELD_ACTIVE`

## Support

For questions or issues:
1. Review docs/threadcore/THREADCORE_MANAGEMENT.md
2. Check threadcore_registry.json for current status
3. Run validation with scripts/threadcore_classifier.py
4. Consult tests/test_threadcore_registry.py for examples
