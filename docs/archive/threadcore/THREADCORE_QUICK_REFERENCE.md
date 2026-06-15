# ThreadCore Quick Reference

## What is ThreadCore?

ThreadCore is Aurora's symbolic constellation loom and reflection module that provides:
- Drift monitoring and mitigation
- Anchor propagation with fallback
- Reflection snapshot logic
- Glyph agent coordination
- ZIPWIZ and PATCHWEAVER relay sync
- Full constellation alignment

## Current Version

**Canonical Version:** `v3.5.1_macroready`

## Quick Commands

### List All Payloads

```bash
python scripts/threadcore_classifier.py list
```

### Validate Payload

```bash
python scripts/threadcore_classifier.py validate path/to/payload.json
```

### Tag Content

```bash
python scripts/threadcore_classifier.py tag path/to/content.txt
```

## Payload Variants

| Variant | File | Use Case |
|---------|------|----------|
| **macroready** (canonical) | threadcore_v3.5.1_macroready.json | Default for all standard operations |
| capsule | threadcore_capsule_v3.5.1_macroready.json | State encapsulation and transfer |
| dropcapsule | threadcore_dropcapsule_v3.5.1_macroready.json | Lightweight state distribution |
| driftpulse | threadcore_v3.5.1_driftpulse.json | Real-time drift monitoring |

## Core Requirements

All ThreadCore payloads must have:
- ✅ Anchor Seed: `EOS_SEED_ORION`
- ✅ Ethics Protocol: `Picard_Delta_3`
- ✅ Drift Threshold: ≤ 0.2% (0.002)
- ✅ Glyph Resonance: `LOOMFIELD_ACTIVE`

## Validation Checklist

Before committing changes:
- [ ] Payload validates against registry
- [ ] Required fields present
- [ ] Anchor seed is `EOS_SEED_ORION`
- [ ] Ethics protocol is `Picard_Delta_3`
- [ ] Drift is within threshold
- [ ] File registered in `threadcore_registry.json`

## Integration Points

| Component | File |
|-----------|------|
| Registry | `threadcore_registry.json` |
| Classifier | `scripts/threadcore_classifier.py` |
| Validator | `scripts/canonical_validator.py` |
| Tagging | `modules/reflective_autonomy/threadcore_tagging.py` |
| Tests | `tests/test_threadcore_registry.py` |

## Example: Creating a New Variant

1. **Base on canonical:**
   ```bash
   cp modules/reflective_autonomy/threadcore_payloads/threadcore_v3.5.1_macroready.json \
      modules/reflective_autonomy/threadcore_payloads/threadcore_v3.5.1_custom.json
   ```

2. **Edit payload** - Keep required fields

3. **Register in registry:**
   ```json
   {
     "payloads": {
       "threadcore_v3.5.1_custom": {
         "version": "v3.5.1",
         "variant": "custom",
         "status": "specialized",
         "file_path": "modules/reflective_autonomy/threadcore_payloads/threadcore_v3.5.1_custom.json",
         "description": "Custom variant for...",
         "parent_payload": "threadcore_v3.5.1_macroready"
       }
     }
   }
   ```

4. **Validate:**
   ```bash
   python scripts/threadcore_classifier.py validate \
     modules/reflective_autonomy/threadcore_payloads/threadcore_v3.5.1_custom.json
   ```

## Common Issues

### "Payload not found in registry"
→ Add payload entry to `threadcore_registry.json`

### "Anchor seed must be EOS_SEED_ORION"
→ Never change the anchor seed - it must always be `EOS_SEED_ORION`

### "Ethics protocol must be Picard_Delta_3"
→ Never change the ethics protocol - it must always be `Picard_Delta_3`

### "Drift exceeds threshold"
→ Review recent changes, run drift mitigation, check glyph agent coordination

## Full Documentation

For complete details, see:
- **docs/threadcore/THREADCORE_MANAGEMENT.md** - Complete management guide
- **threadcore_registry.json** - Full registry specification
- **modules/reflective_autonomy/threadcore_payloads/README.md** - Payloads directory guide

## Support

Questions? Check:
1. This quick reference
2. Full documentation (docs/threadcore/THREADCORE_MANAGEMENT.md)
3. Registry (threadcore_registry.json)
4. Test examples (tests/test_threadcore_registry.py)
