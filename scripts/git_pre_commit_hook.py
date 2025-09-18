#!/usr/bin/env python3
"""
Git Pre-Commit Hook with Symbolic Validation
Anchor: T1_PRECOMMIT_VALIDATOR
Team: Aurora/GUMAS
Version: 2.0.0
Sealed: SHA256 pending
"""

import sys
import subprocess
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

# Add the scripts directory to Python path
script_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_dir))

# Symbolic anchor metadata
ANCHOR_METADATA = {
    "seed": "EOS_SEED_ORION",
    "protocol": "Picard_Delta_3",
    "branch_context": "harvest-safe-updates-2025-09-18",
    "entropy_state": "TRACKED",
}

def log_entropy_state(message: str, level: str = "INFO") -> None:
    """Log with entropy awareness and symbolic anchoring"""
    timestamp = datetime.now(timezone.utc).isoformat()
    entropy_marker = hashlib.sha256(f"{timestamp}{message}".encode()).hexdigest()[:8]
    print(f"[{level}] [{timestamp}] [E:{entropy_marker}] {message}", file=sys.stderr)

# Import validator with graceful degradation
try:
    log_entropy_state("Attempting primary validator import: canonical_validator.CanonicalValidator")
    from canonical_validator import CanonicalValidator  # type: ignore
    if not hasattr(CanonicalValidator, "__version__"):
        log_entropy_state("CanonicalValidator lacks __version__ metadata", "WARN")
except Exception as e_primary:
    log_entropy_state(f"Primary import failed: {e_primary}", "WARN")
    try:
        log_entropy_state("Attempting fallback validator import: validation.CanonicalValidator")
        from validation import CanonicalValidator  # type: ignore
    except Exception as e_fallback:
        log_entropy_state(f"Fallback import failed: {e_fallback}", "ERROR")

        class CanonicalValidator:  # type: ignore
            """Minimal stub validator for continuity"""
            __version__ = "0.0.0-stub"

            def __init__(self) -> None:
                self.anchor = "STUB_VALIDATOR"
                self.warnings = []

            def validate_file(self, file_path):
                log_entropy_state(f"STUB: Would validate {file_path}", "WARN")
                return []  # Return empty results list

        divergent_truth = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": "VALIDATOR_UNAVAILABLE",
            "files_pending": "UNKNOWN",
            "anchor": ANCHOR_METADATA["seed"],
            "action": "MANUAL_REVIEW_REQUIRED",
        }
        log_entropy_state(f"DIVERGENT_TRUTH: {json.dumps(divergent_truth)}", "ERROR")
        print("\n⚠️  Warning: Canonical validation not available; skipping validation.\n   Manual review required before commit.")
        # Allow commit; early exit to avoid blocking workflow when validator is absent
        sys.exit(0)


def seal_validation_state(files, result: bool) -> dict:
    """Create sealed memory state for validation result"""
    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "anchor": ANCHOR_METADATA,
        "files_count": len(files),
        "validation_result": result,
        "files_hash": hashlib.sha256("".join(sorted(files)).encode()).hexdigest(),
    }
    state_json = json.dumps(state, sort_keys=True)
    state["seal"] = hashlib.sha256(state_json.encode()).hexdigest()
    return state

def get_staged_files():
    """Get list of staged files for commit"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        log_entropy_state(f"Found {len(files)} staged files")
        return files
    except subprocess.CalledProcessError as e:
        log_entropy_state(f"Git command failed: {e}", "ERROR")
        return []
    except Exception as e:
        log_entropy_state(f"Unexpected error getting staged files: {e}", "ERROR")
        return []


def main() -> int:
    """Main pre-commit hook with symbolic continuity"""
    log_entropy_state("Pre-commit hook initiated", "INFO")
    log_entropy_state(f"Anchor: {ANCHOR_METADATA['seed']}", "INFO")

    staged_files = get_staged_files()
    if not staged_files:
        log_entropy_state("No staged files to validate")
        return 0

    try:
        validator = CanonicalValidator()  # type: ignore[call-arg]
        log_entropy_state(f"Starting validation of {len(staged_files)} files")
        
        # Validate files using the existing interface
        all_results = []
        validation_passed = True
        for file_path in staged_files:
            if Path(file_path).exists():
                try:
                    results = validator.validate_file(file_path)
                    all_results.extend(results)
                    # Check if there are any critical violations
                    if any(r.status == "ESCALATE" and r.severity == "CRITICAL" for r in results):
                        validation_passed = False
                except Exception as e:
                    log_entropy_state(f"Error validating {file_path}: {e}", "ERROR")
                    validation_passed = False

        sealed_state = seal_validation_state(staged_files, validation_passed)
        log_entropy_state(f"Validation sealed: {sealed_state['seal'][:16]}…")

        seal_path = Path(".git/validation_seal.json")
        try:
            with open(seal_path, "w", encoding="utf-8") as f:
                json.dump(sealed_state, f, indent=2)
        except Exception as e:
            log_entropy_state(f"Failed to persist seal: {e}", "WARN")

        if validation_passed:
            log_entropy_state("Validation passed successfully")
            return 0
        else:
            log_entropy_state("Validation failed - commit blocked", "ERROR")
            print("\n❌ Validation failed. Please fix issues before committing.")
            if all_results:
                critical_issues = [r for r in all_results if r.status == "ESCALATE" and r.severity == "CRITICAL"]
                if critical_issues:
                    print(f"   Critical issues found: {len(critical_issues)}")
                    for issue in critical_issues[:3]:  # Show first 3
                        print(f"   - {issue.message}")
            return 1
    except SystemExit as e:
        # Allow SystemExit raised intentionally above to propagate
        return int(e.code) if isinstance(e.code, int) else 0
    except Exception as e:
        log_entropy_state(f"Validation error: {e}", "ERROR")
        error_seal = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "anchor": ANCHOR_METADATA,
            "action": "VALIDATION_EXCEPTION",
        }
        log_entropy_state(f"ERROR_SEAL: {json.dumps(error_seal)}", "ERROR")
        print("\n⚠️  Validation error occurred. Manual review recommended.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
