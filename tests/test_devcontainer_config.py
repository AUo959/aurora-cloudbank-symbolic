"""
Tests for DevContainer configuration validation.
Ensures codespace initialization scripts are correctly configured.
"""
import json
import os
import pytest
from pathlib import Path


@pytest.fixture
def repo_root():
    """Get repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def devcontainer_dir(repo_root):
    """Get .devcontainer directory."""
    return repo_root / ".devcontainer"


def test_devcontainer_configs_exist(devcontainer_dir):
    """Test that devcontainer configuration files exist."""
    assert devcontainer_dir.exists(), ".devcontainer directory should exist"
    assert (devcontainer_dir / "devcontainer.json").exists(), "devcontainer.json should exist"
    assert (devcontainer_dir / "post-create.sh").exists(), "post-create.sh should exist"


def test_devcontainer_json_valid(devcontainer_dir):
    """Test that devcontainer.json is valid JSON."""
    config_file = devcontainer_dir / "devcontainer.json"
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    assert isinstance(config, dict), "devcontainer.json should be a JSON object"
    assert "name" in config, "devcontainer.json should have a name field"


def test_devcontainer_improved_json_valid(devcontainer_dir):
    """Test that devcontainer-improved.json is valid JSON."""
    config_file = devcontainer_dir / "devcontainer-improved.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        assert isinstance(config, dict), "devcontainer-improved.json should be a JSON object"
        assert "name" in config, "devcontainer-improved.json should have a name field"


def test_python_scripts_use_python_interpreter(devcontainer_dir):
    """
    Test that Python scripts are executed with python3, not bash.
    This prevents the issue where .py files are incorrectly interpreted as bash scripts.
    """
    config_files = [
        devcontainer_dir / "devcontainer.json",
        devcontainer_dir / "devcontainer-improved.json"
    ]
    
    for config_file in config_files:
        if not config_file.exists():
            continue
            
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check onCreateCommand
        if "onCreateCommand" in config:
            cmd = config["onCreateCommand"]
            # If the command references a .py file, it should use python3
            if ".py" in cmd:
                assert not cmd.strip().startswith("bash ") or "bash .devcontainer/" in cmd, \
                    f"Python scripts in onCreateCommand should use python3, not bash in {config_file.name}"
                if "scripts/" in cmd and ".py" in cmd:
                    assert "python3 " in cmd or "python " in cmd, \
                        f"Python scripts should be executed with python3 in {config_file.name}"
        
        # Check postStartCommand
        if "postStartCommand" in config:
            cmd = config["postStartCommand"]
            if ".py" in cmd:
                assert not cmd.strip().startswith("bash ") or "bash .devcontainer/" in cmd, \
                    f"Python scripts in postStartCommand should use python3, not bash in {config_file.name}"
                if "scripts/" in cmd and ".py" in cmd:
                    assert "python3 " in cmd or "python " in cmd, \
                        f"Python scripts should be executed with python3 in {config_file.name}"
        
        # Check postCreateCommand
        if "postCreateCommand" in config:
            cmd = config["postCreateCommand"]
            # Allow bash for .sh files, but not for .py files
            if ".py" in cmd and "scripts/" in cmd:
                assert not cmd.strip().startswith("bash scripts/"), \
                    f"Python scripts in postCreateCommand should use python3, not bash in {config_file.name}"


def test_prevent_rebuild_failures_script_exists(repo_root):
    """Test that the prevent_rebuild_failures.py script exists."""
    script_path = repo_root / "scripts" / "prevent_rebuild_failures.py"
    assert script_path.exists(), "scripts/prevent_rebuild_failures.py should exist"


def test_prevent_rebuild_failures_is_python(repo_root):
    """Test that prevent_rebuild_failures.py has Python shebang."""
    script_path = repo_root / "scripts" / "prevent_rebuild_failures.py"
    if script_path.exists():
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        
        assert first_line.startswith("#!") and "python" in first_line, \
            "prevent_rebuild_failures.py should have a Python shebang"


def test_post_create_script_is_bash(devcontainer_dir):
    """Test that post-create.sh has bash shebang."""
    script_path = devcontainer_dir / "post-create.sh"
    if script_path.exists():
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        
        assert first_line.startswith("#!") and ("bash" in first_line or "sh" in first_line), \
            "post-create.sh should have a bash/sh shebang"


def test_devcontainer_consistency(devcontainer_dir):
    """Test that both devcontainer files use consistent interpreter patterns."""
    main_config = devcontainer_dir / "devcontainer.json"
    improved_config = devcontainer_dir / "devcontainer-improved.json"
    
    if not (main_config.exists() and improved_config.exists()):
        pytest.skip("Both devcontainer files not present")
    
    with open(main_config, 'r') as f:
        main = json.load(f)
    
    with open(improved_config, 'r') as f:
        improved = json.load(f)
    
    # Check that both use the same pattern for onCreateCommand if present
    if "onCreateCommand" in main and "onCreateCommand" in improved:
        main_cmd = main["onCreateCommand"]
        improved_cmd = improved["onCreateCommand"]
        
        # Both should use python3 for .py scripts in the same way
        if "scripts/prevent_rebuild_failures.py" in main_cmd:
            assert "python3 scripts/prevent_rebuild_failures.py" in main_cmd, \
                "devcontainer.json should use python3 for prevent_rebuild_failures.py"
        
        if "scripts/prevent_rebuild_failures.py" in improved_cmd:
            assert "python3 scripts/prevent_rebuild_failures.py" in improved_cmd, \
                "devcontainer-improved.json should use python3 for prevent_rebuild_failures.py"
