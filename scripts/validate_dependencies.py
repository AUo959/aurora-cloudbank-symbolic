#!/usr/bin/env python3
"""
Aurora CloudBank Dependency Validation Script
Prevents build errors by validating dependency compatibility before installation.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple


def check_dependency_conflicts(requirements_file: str) -> bool:
    """Check for dependency conflicts using pip's dependency resolver."""
    print("🔍 Validating dependency compatibility...")
    
    try:
        # Use pip check to validate installed packages
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Dependency conflicts detected:\\n{result.stdout}{result.stderr}")
            return False
        else:
            print("✅ No dependency conflicts detected")
            
        # Test installation without actually installing
        print("📋 Testing dependency resolution...")
        test_result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", requirements_file,
            "--dry-run", "--report", "/dev/stdout"
        ], capture_output=True, text=True)
        
        if test_result.returncode != 0:
            print(f"❌ Dependency resolution failed:\\n{test_result.stderr}")
            return False
            
        print("✅ All dependencies are compatible!")
        return True
        
    except Exception as e:
        print(f"⚠️ Validation error: {e}")
        return False


def validate_critical_versions() -> bool:
    """Validate critical Aurora dependency versions."""
    critical_deps = {
        "httpx": ">=0.28.0",  # Supports httpcore 1.x
        "httpcore": ">=1.0.0",  # Required for h11 0.16.0
        "h11": ">=0.16.0",  # Security updates
        "fastapi": ">=0.100.0",
        "starlette": ">=0.40.0"
    }
    
    print("🔧 Validating critical Aurora dependencies...")
    
    for package, version_spec in critical_deps.items():
        try:
            import pkg_resources
            pkg_resources.require(f"{package}{version_spec}")
            print(f"✅ {package}: OK")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as e:
            print(f"❌ {package}: {e}")
            return False
    
    return True


def backup_requirements():
    """Backup current requirements before changes."""
    requirements_files = [
        "requirements.txt",
        "requirements-lock.txt",
        "pyproject.toml"
    ]
    
    backup_dir = Path(".backup/requirements")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            backup_path = backup_dir / f"{req_file}.backup"
            subprocess.run(["cp", req_file, str(backup_path)])
            print(f"📦 Backed up {req_file} to {backup_path}")


def main():
    """Main validation workflow."""
    print("🌟 Aurora CloudBank Dependency Validator")
    print("=" * 50)
    
    # Backup current state
    backup_requirements()
    
    # Check if we have a requirements file
    req_file = "requirements-lock.txt" if Path("requirements-lock.txt").exists() else "requirements.txt"
    
    if not Path(req_file).exists():
        print(f"❌ No requirements file found ({req_file})")
        return False
    
    # Validate dependencies
    if not check_dependency_conflicts(req_file):
        print("\\n🚨 Dependency validation failed!")
        print("💡 Run 'pip install -r requirements-lock.txt --dry-run' for details")
        return False
    
    # Validate critical versions if packages are installed
    try:
        if not validate_critical_versions():
            print("\\n⚠️ Critical version validation failed!")
            return False
    except ImportError:
        print("ℹ️ Packages not installed yet, skipping version validation")
    
    print("\\n✅ All dependency validations passed!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)