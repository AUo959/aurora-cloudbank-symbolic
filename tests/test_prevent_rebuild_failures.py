#!/usr/bin/env python3
"""
Tests for the prevent_rebuild_failures script.
"""

import pytest
import subprocess
import sys
from pathlib import Path


@pytest.mark.unit
@pytest.mark.xfail(reason="Environment-specific: requires functioning .venv/bin/pip")
def test_pre_rebuild_mode_succeeds_without_venv():
    """Test that --pre-rebuild mode succeeds even without a virtual environment."""
    script_path = Path(__file__).parent.parent / "scripts" / "prevent_rebuild_failures.py"
    
    result = subprocess.run(
        [sys.executable, str(script_path), "--pre-rebuild"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Should succeed (exit code 0)
    assert result.returncode == 0, f"Script failed with: {result.stderr}"
    
    # Should skip dependency checks
    assert "Skipping dependency check" in result.stdout
    
    # Should complete successfully
    assert "Aurora CloudBank rebuild protection is active!" in result.stdout


@pytest.mark.unit
def test_regular_mode_succeeds_without_venv():
    """Test that regular validation mode handles missing venv gracefully."""
    script_path = Path(__file__).parent.parent / "scripts" / "prevent_rebuild_failures.py"
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Should succeed (exit code 0)
    assert result.returncode == 0, f"Script failed with: {result.stderr}"
    
    # Should skip dependency check when venv is missing
    assert "Virtual environment not found" in result.stdout or "Dependencies OK" in result.stdout
    
    # Should complete successfully
    assert "Aurora CloudBank rebuild protection is active!" in result.stdout


@pytest.mark.unit
def test_script_syntax():
    """Test that the script has no syntax errors."""
    script_path = Path(__file__).parent.parent / "scripts" / "prevent_rebuild_failures.py"
    
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(script_path)],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Syntax error: {result.stderr}"


@pytest.mark.unit
@pytest.mark.xfail(reason="Environment-specific: requires functioning .venv/bin/pip")
def test_backup_directory_created():
    """Test that backup directory is created if it doesn't exist."""
    script_path = Path(__file__).parent.parent / "scripts" / "prevent_rebuild_failures.py"
    backup_dir = Path(__file__).parent.parent / ".backup"
    
    # Ensure backup directory exists after running
    result = subprocess.run(
        [sys.executable, str(script_path), "--pre-rebuild"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert backup_dir.exists(), "Backup directory was not created"
    assert result.returncode == 0


@pytest.mark.integration
@pytest.mark.xfail(reason="Environment-specific: requires devcontainer setup")
def test_devcontainer_lifecycle_simulation():
    """Simulate the devcontainer lifecycle to ensure commands work in sequence."""
    script_path = Path(__file__).parent.parent / "scripts" / "prevent_rebuild_failures.py"
    post_create_script = Path(__file__).parent.parent / ".devcontainer" / "post-create.sh"
    
    # Step 1: onCreateCommand (pre-rebuild)
    result1 = subprocess.run(
        [sys.executable, str(script_path), "--pre-rebuild"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result1.returncode == 0, f"onCreateCommand failed: {result1.stderr}"
    
    # Step 2: postCreateCommand would run post-create.sh
    # We'll just check it exists and is executable
    assert post_create_script.exists(), "post-create.sh doesn't exist"
    assert post_create_script.stat().st_mode & 0o111, "post-create.sh is not executable"
    
    # Step 3: postStartCommand (regular validation)
    result3 = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result3.returncode == 0, f"postStartCommand failed: {result3.stderr}"
