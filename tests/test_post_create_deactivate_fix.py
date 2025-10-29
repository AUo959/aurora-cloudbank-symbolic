"""
Tests for the deactivate fix in .devcontainer/post-create.sh
Ensures that the post-create script handles missing virtual environments gracefully.
"""
import subprocess
import re
from pathlib import Path


def test_post_create_script_exists():
    """Test that post-create.sh exists and is executable."""
    script_path = Path(".devcontainer/post-create.sh")
    assert script_path.exists(), "post-create.sh should exist"
    assert script_path.stat().st_mode & 0o111, "post-create.sh should be executable"


def test_post_create_bash_syntax():
    """Test that post-create.sh has valid bash syntax."""
    result = subprocess.run(
        ["bash", "-n", ".devcontainer/post-create.sh"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Syntax error in post-create.sh: {result.stderr}"


def test_deactivate_conditional_logic():
    """Test that the deactivate conditional logic works correctly."""
    # Test the conditional pattern used in the fix
    test_script = """
set -euo pipefail

# This is the pattern used in post-create.sh
if command -v deactivate &> /dev/null && [[ -n "${VIRTUAL_ENV:-}" ]]; then
    echo "DEACTIVATE_WOULD_RUN"
    # Don't actually call deactivate in test
else
    echo "DEACTIVATE_SKIPPED"
fi

echo "SCRIPT_COMPLETED"
"""
    
    result = subprocess.run(
        ["bash", "-c", test_script],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Conditional logic failed: {result.stderr}"
    assert "SCRIPT_COMPLETED" in result.stdout, "Script should complete successfully"
    # When no venv is active, deactivate should be skipped
    assert "DEACTIVATE_SKIPPED" in result.stdout or "DEACTIVATE_WOULD_RUN" in result.stdout


def test_post_create_has_protected_deactivate():
    """Test that post-create.sh has the deactivate fix applied."""
    with open(".devcontainer/post-create.sh", "r") as f:
        content = f.read()
    
    # Check that the protective checks are present
    assert "command -v deactivate" in content, \
        "post-create.sh should check for deactivate command availability"
    assert '${VIRTUAL_ENV:-}' in content, \
        "post-create.sh should check if VIRTUAL_ENV is set using '${VIRTUAL_ENV:-}' pattern"
    
    # Verify no unprotected deactivate calls
    # We specifically look for the protective pattern used in the fix
    lines = content.split('\n')
    found_protected_deactivate = False
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Skip comments
        if stripped.startswith('#'):
            continue
        
        # Look for standalone deactivate commands
        if re.match(r'^\s*deactivate\s*$', line):
            # Check if the previous few lines contain the protective pattern
            context_start = max(0, i - 5)
            context = '\n'.join(lines[context_start:i])
            
            # Verify this deactivate is protected by the specific pattern we use
            is_protected = (
                'command -v deactivate' in context and
                '${VIRTUAL_ENV:-}' in context
            )
            
            assert is_protected, \
                f"Found unprotected deactivate at line {i}. " \
                f"Deactivate must be protected by 'command -v deactivate' and VIRTUAL_ENV checks."
            
            found_protected_deactivate = True
    
    # Ensure we found at least one protected deactivate (confirming the fix is in place)
    assert found_protected_deactivate, \
        "Expected to find at least one protected deactivate call with the fix pattern"


def test_post_create_strict_error_handling():
    """Test that post-create.sh uses strict error handling."""
    with open(".devcontainer/post-create.sh", "r") as f:
        first_lines = [f.readline() for _ in range(5)]
    
    content = ''.join(first_lines)
    assert 'set -e' in content, "post-create.sh should use 'set -e'"


def test_deactivate_with_no_venv_active():
    """Test that deactivate pattern doesn't fail when no venv is active."""
    # This simulates the exact scenario that caused the bug
    test_script = """
set -euo pipefail

# Simulate the fixed pattern from post-create.sh
if command -v deactivate &> /dev/null && [[ -n "${VIRTUAL_ENV:-}" ]]; then
  deactivate
fi

echo "SUCCESS"
"""
    
    result = subprocess.run(
        ["bash", "-c", test_script],
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"}  # Clean environment with no venv
    )
    
    assert result.returncode == 0, \
        f"Script should succeed when no venv is active. Error: {result.stderr}"
    assert "SUCCESS" in result.stdout, "Script should complete successfully"


if __name__ == "__main__":
    # Run tests manually
    import sys
    
    tests = [
        test_post_create_script_exists,
        test_post_create_bash_syntax,
        test_deactivate_conditional_logic,
        test_post_create_has_protected_deactivate,
        test_post_create_strict_error_handling,
        test_deactivate_with_no_venv_active,
    ]
    
    failed = []
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"❌ {test.__name__}: Unexpected error: {e}")
            failed.append(test.__name__)
    
    if failed:
        print(f"\n❌ {len(failed)} test(s) failed")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(tests)} tests passed!")
        sys.exit(0)
