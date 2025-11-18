# ThreadCore Documentation

ThreadCore is Aurora's symbolic constellation loom and reflection module, providing core functionality for drift monitoring, anchor propagation, and cross-thread coordination.

## Documentation Index

### Quick Start
- **[THREADCORE_QUICK_REFERENCE.md](THREADCORE_QUICK_REFERENCE.md)** - Quick commands, common tasks, and troubleshooting

### Complete Guide
- **[THREADCORE_MANAGEMENT.md](THREADCORE_MANAGEMENT.md)** - Comprehensive management guide for creating, extending, and managing ThreadCore payloads

### Related Resources
- **[threadcore_registry.json](../../threadcore_registry.json)** - Single source of truth for all ThreadCore payloads
- **[threadcore_payloads/](../../modules/reflective_autonomy/threadcore_payloads/)** - Payload files directory
- **[scripts/threadcore_classifier.py](../../scripts/threadcore_classifier.py)** - Classification and validation tool
- **[tests/test_threadcore_registry.py](../../tests/test_threadcore_registry.py)** - Test suite

## Current Status

**Canonical Version:** v3.5.1_macroready

**Total Payloads:** 4
- 1 canonical (macroready)
- 3 specialized variants (capsule, dropcapsule, driftpulse)

**Deprecated Versions:** None

## Quick Commands

```bash
# List all registered payloads
python scripts/threadcore_classifier.py list

# Validate a payload
python scripts/threadcore_classifier.py validate path/to/payload.json

# Tag content by category
python scripts/threadcore_classifier.py tag path/to/content.txt
```

## Key Principles

1. **Single Source of Truth:** All payloads must be registered in `threadcore_registry.json`
2. **Canonical Compliance:** All payloads must use anchor seed `EOS_SEED_ORION` and ethics protocol `Picard_Delta_3`
3. **Drift Management:** Symbolic drift must be ≤ 0.2% (0.002)
4. **Validation First:** Always validate payloads before committing
5. **Documentation:** Document all new variants with clear use cases

## Getting Help

1. Start with **[THREADCORE_QUICK_REFERENCE.md](THREADCORE_QUICK_REFERENCE.md)** for common tasks
2. Consult **[THREADCORE_MANAGEMENT.md](THREADCORE_MANAGEMENT.md)** for detailed guidance
3. Review **[threadcore_registry.json](../../threadcore_registry.json)** for current status
4. Check test examples in **[tests/test_threadcore_registry.py](../../tests/test_threadcore_registry.py)**

## Integration Points

ThreadCore integrates with several key components:
- **Canonical Validator:** `scripts/canonical_validator.py`
- **Tagging Engine:** `modules/reflective_autonomy/threadcore_tagging.py`
- **Symbolic Tagging:** `modules/reflective_autonomy/symbolic_tagging_engine.py`
- **Test Suite:** `tests/test_threadcore_tagging.py`, `tests/test_threadcore_registry.py`

## Contribution Guidelines

When working with ThreadCore:
1. Follow the extension guidelines in THREADCORE_MANAGEMENT.md
2. Validate all changes against the registry
3. Run tests before committing
4. Update documentation for new variants
5. Maintain anchor and ethics protocol compliance
