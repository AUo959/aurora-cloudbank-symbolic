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
  "files_count": 5,
  "validation_result": true,
  "files_hash": "abc123...",
  "seal": "sha256_hash_of_state"
}
```

## Testing
```bash
python scripts/test_pre_commit_hook.py
```

## Troubleshooting
- Check logs for `DIVERGENT_TRUTH` markers when validator is unavailable.
- Verify validator availability: `python -c "from canonical_validator import CanonicalValidator"`.
- If validation crashes, see `ERROR_SEAL` entries in stderr and `.git/validation_seal.json`.

## Next Steps
- Integrate with CI to surface seals as artifacts.
- Add dashboard for validation analytics and drift detection.
- Consider chain-of-seals verification across commits.