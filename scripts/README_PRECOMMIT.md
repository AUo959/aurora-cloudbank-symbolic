# Git Pre-Commit Hook with Symbolic Validation

## Anchors and Ethics
- Primary Anchor: T1_PRECOMMIT_VALIDATOR
- Seed: EOS_SEED_ORION
- Protocol: Picard_Delta_3
- Team: Aurora/GUMAS

## Overview
Enhanced pre-commit hook with symbolic anchor tracking, entropy-aware logging, and memory sealing protocols. Ensures commits pass through canonical validation while preserving traceability and state recovery.

## Features
- Three-tier validator fallback: primary → secondary → stub
- Entropy-state tracking with markers on every log
- SHA256 memory sealing for validation states
- Divergent-truth detection and explicit logging
- Graceful degradation when validator is unavailable
- State persistence to `.git/validation_seal.json`

## Install
```bash
cp scripts/git_pre_commit_hook.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Usage
- Runs automatically on `git commit`.
- Manual run: `python scripts/git_pre_commit_hook.py`
- View sealed state: `cat .git/validation_seal.json | jq .`

## Validation State Schema
```json
{
  "timestamp": "2025-09-18T05:17:56.123456",
  "anchor": {
    "seed": "EOS_SEED_ORION",
    "protocol": "Picard_Delta_3",
    "branch_context": "harvest-safe-updates-2025-09-18",
    "entropy_state": "TRACKED"
  },
  "files_count": 3,
  "validation_result": true,
  "files_hash": "sha256...",
  "validator_mode": "primary",
  "seal": "sha256..."
}
```

## Validator Modes

### Primary Mode
- Import: `canonical_validator.CanonicalValidator`
- Full validation capability
- Memory sealing enabled

### Fallback Mode  
- Import: `validation.CanonicalValidator`
- Limited validation capability
- Memory sealing enabled

### Stub Mode
- No validator available
- Logs DIVERGENT_TRUTH
- Allows commit with warnings
- Conservative behavior

## Testing
```bash
# Run all tests
python scripts/test_pre_commit_hook.py

# Run specific test
python -m unittest scripts.test_pre_commit_hook.TestPreCommitHook.test_entropy_logging
```

## Troubleshooting

### Validator Import Failures
- Check if `canonical_validator.py` exists in scripts/
- Verify Python path includes scripts directory
- Review entropy logs for specific import errors

### Memory Seal Issues
- Ensure `.git/` directory is writable
- Check `validation_seal.json` for integrity
- Review seal hash consistency

### Performance Concerns
- Entropy logging adds minimal overhead (~5ms per operation)
- Memory sealing involves file I/O (~10-50ms)
- Total pre-commit overhead: typically <200ms

## Next Steps
- Integration with CI/CD pipelines
- Enhanced validator capabilities
- Distributed validation state sync
- Real-time entropy monitoring dashboard