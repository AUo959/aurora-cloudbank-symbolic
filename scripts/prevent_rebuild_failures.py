#!/usr/bin/env python3
"""
Aurora CloudBank Rebuild Failure Prevention System
Comprehensive protection against DevContainer rebuild issues.
"""

import logging

logger = logging.getLogger(__name__)

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class RebuildFailurePrevention:
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.status_file = self.workspace_root / ".rebuild_prevention_status.json"
        self.backup_dir = self.workspace_root / ".backup"
        self.venv_dir = self.workspace_root / ".venv"
        
    def log_status(self, status: str, message: str = ""):
        """Log current status to status file."""
        status_data = {
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "workspace": str(self.workspace_root)
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        
        print(f"📊 Status: {status} - {message}")
    
    def check_environment_health(self, skip_dependencies: bool = False) -> bool:
        """Check if the current environment is healthy.
        
        Args:
            skip_dependencies: If True, skip dependency checks (useful during pre-rebuild)
        """
        print("🔍 Checking environment health...")
        
        # Check Python availability
        if not shutil.which("python3"):
            logger.error("Python 3 not available")
            return False
        
        # Determine which Python to use (venv or system)
        venv_python = self.venv_dir / "bin" / "python"
        if venv_python.exists():
            python_executable = str(venv_python)
            print("📦 Using virtual environment Python")
        else:
            python_executable = "python3"
            print("🐍 Using system Python (venv not available)")
        
        # Check if Python is functional
        try:
            result = subprocess.run([
                python_executable,
                "-c", "import sys; print(sys.version)"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.error("Python environment is not functional")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("Python environment check failed")
            return False
        
        # Check critical dependencies (only if not skipped and venv exists)
        if not skip_dependencies:
            if not venv_python.exists():
                logger.warning("Virtual environment not found, skipping dependency check")
                return True
            
            try:
                result = subprocess.run([
                    python_executable,
                    "-c", "import fastapi, httpx, httpcore, h11; print('Dependencies OK')"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    logger.error("Critical dependencies missing or broken")
                    print(f"   Error: {result.stderr}")
                    return False
                logger.info("{result.stdout.strip()}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.error("Dependency check failed")
                return False
        else:
            logger.warning("Skipping dependency check (pre-rebuild mode)")
        
        logger.info("Environment health check passed")
        return True
    
    def create_pre_rebuild_backup(self):
        """Create comprehensive backup before rebuild."""
        print("💾 Creating pre-rebuild backup...")
        
        # Ensure backup directory exists (setup step)
        if not self.backup_dir.exists():
            print("📁 Creating backup directory...")
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / f"pre_rebuild_{backup_timestamp}"
        backup_subdir.mkdir(parents=True, exist_ok=True)
        
        # Backup requirements files
        for req_file in ["requirements.txt", "requirements-lock.txt", "pyproject.toml"]:
            if (self.workspace_root / req_file).exists():
                shutil.copy2(
                    self.workspace_root / req_file,
                    backup_subdir / req_file
                )
                print(f"📦 Backed up {req_file}")
        
        # Backup pip freeze if virtual environment exists
        if self.venv_dir.exists():
            try:
                result = subprocess.run([
                    str(self.venv_dir / "bin" / "pip"),
                    "freeze"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    with open(backup_subdir / "pip_freeze.txt", 'w') as f:
                        f.write(result.stdout)
                    print("📦 Backed up pip freeze")
            except subprocess.TimeoutExpired:
                logger.warning("Pip freeze backup timed out")
        
        # Create rebuild recovery script
        recovery_script = backup_subdir / "emergency_recovery.sh"
        with open(recovery_script, 'w') as f:
            f.write(f'''#!/bin/bash
# Emergency Recovery Script - Generated {backup_timestamp}
set -e

echo "🚨 Aurora CloudBank Emergency Recovery"
echo "====================================="

cd "{self.workspace_root}"

# Remove corrupted environment
rm -rf .venv

# Create fresh environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install from backup
if [ -f "{backup_subdir}/requirements-lock.txt" ]; then
    echo "Installing from backed up requirements-lock.txt..."
    pip install -r "{backup_subdir}/requirements-lock.txt"
elif [ -f "{backup_subdir}/pip_freeze.txt" ]; then
    echo "Installing from backed up pip freeze..."
    pip install -r "{backup_subdir}/pip_freeze.txt"
else
    echo "❌ No backup requirements found"
    exit 1
fi

echo "✅ Emergency recovery completed"
''')
        
        recovery_script.chmod(0o755)
        print(f"🆘 Created emergency recovery script: {recovery_script}")
        
        self.log_status("backup_created", f"Backup created at {backup_subdir}")
        return backup_subdir
    
    def install_rebuild_protection(self):
        """Install comprehensive rebuild protection."""
        print("🛡️ Installing rebuild protection...")
        
        # Create pre-rebuild hook
        hooks_dir = self.workspace_root / ".devcontainer" / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        pre_rebuild_hook = hooks_dir / "pre-rebuild.sh"
        with open(pre_rebuild_hook, 'w') as f:
            f.write(f'''#!/bin/bash
# Aurora CloudBank Pre-Rebuild Protection Hook
set -e

echo "🛡️ Aurora CloudBank Pre-Rebuild Protection"
echo "==========================================="

# Run backup and validation
python3 "{self.workspace_root / "scripts" / "prevent_rebuild_failures.py"}" --pre-rebuild

echo "✅ Pre-rebuild protection completed"
''')
        
        pre_rebuild_hook.chmod(0o755)
        
        # Update DevContainer configuration
        devcontainer_json = self.workspace_root / ".devcontainer" / "devcontainer.json"
        if devcontainer_json.exists():
            print("📝 DevContainer configuration exists - manual update needed")
            print(f"   Add: '\"onCreateCommand\": \"bash {pre_rebuild_hook}\"'")
        
        print("🛡️ Rebuild protection installed")
    
    def run_validation_suite(self, skip_dependencies: bool = False):
        """Run comprehensive validation suite.
        
        Args:
            skip_dependencies: If True, skip dependency checks (useful during pre-rebuild)
            
        Returns:
            tuple: (all_passed: bool, validation_results: dict)
        """
        print("🧪 Running validation suite...")
        
        validation_results = {
            "environment_health": self.check_environment_health(skip_dependencies=skip_dependencies),
            "dependency_validation": self.validate_dependencies() if not skip_dependencies else True,
            "script_integrity": self.check_script_integrity(),
            "backup_systems": self.check_backup_systems()
        }
        
        all_passed = all(validation_results.values())
        
        if all_passed:
            logger.info("All validation checks passed")
        else:
            failed_checks = [k for k, v in validation_results.items() if not v]
            self.log_status("validation_failed", f"Failed checks: {', '.join(failed_checks)}")
            logger.error("Validation failed: %s", ', '.join(failed_checks))
        
        return all_passed, validation_results
    
    def validate_dependencies(self) -> bool:
        """Validate dependency configuration."""
        if not (self.workspace_root / "requirements-lock.txt").exists():
            logger.error("requirements-lock.txt not found")
            return False
        
        # Check for critical dependencies
        with open(self.workspace_root / "requirements-lock.txt", 'r') as f:
            content = f.read()
            
        critical_deps = ["fastapi", "httpx", "httpcore", "h11", "starlette"]
        missing_deps = [dep for dep in critical_deps if dep not in content]
        
        if missing_deps:
            logger.error("Missing critical dependencies: %s", ', '.join(missing_deps))
            return False
        
        logger.info("Dependency validation passed")
        return True
    
    def check_script_integrity(self) -> bool:
        """Check integrity of critical scripts."""
        critical_scripts = [
            "scripts/validate_dependencies.py",
            "scripts/setup_environment.sh",
            ".devcontainer/post-create.sh"
        ]
        
        for script_path in critical_scripts:
            full_path = self.workspace_root / script_path
            if not full_path.exists():
                logger.error("Critical script missing: {script_path}")
                return False
            
            if not os.access(full_path, os.X_OK):
                logger.error("Critical script not executable: {script_path}")
                return False
        
        logger.info("Script integrity check passed")
        return True
    
    def check_backup_systems(self) -> bool:
        """Check backup system availability (validation only - does not create directories)."""
        if not self.backup_dir.exists():
            logger.warning("Backup directory not found")
            return False

        # Check if we have recent backups (look in subdirectories too)
        backup_files = (
            list(self.backup_dir.rglob("*requirements*.txt")) +
            list(self.backup_dir.rglob("*requirements*.backup"))
        )

        if not backup_files:
            logger.warning("No backup files found yet")
            return False

        logger.info("Backup system check passed ({len(backup_files)} backup files found)")
        return True


def main():
    """Main prevention system."""
    preventer = RebuildFailurePrevention()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--pre-rebuild":
        # Pre-rebuild mode - skip dependency checks since they aren't installed yet
        preventer.log_status("pre_rebuild_started", "Pre-rebuild protection starting")
        preventer.create_pre_rebuild_backup()
        preventer.install_rebuild_protection()
        
        # Run validation with DLP tracking for degraded state
        all_passed, validation_results = preventer.run_validation_suite(skip_dependencies=True)
        
        if not all_passed:
            # Log degraded state with DLP-style context tags and tracking
            failed_checks = [k for k, v in validation_results.items() if not v]
            degraded_state = {
                "context_tag": "PRE_REBUILD_DEGRADED_STATE",
                "t1_anchor": f"T1_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "srb_anchor": "SRB:REBUILD_PROTECTION_DEGRADED",
                "failed_checks": failed_checks,
                "validation_results": validation_results,
                "symbolic_hash": hashlib.sha256(
                    json.dumps(validation_results, sort_keys=True).encode()
                ).hexdigest()[:16],
                "timestamp": datetime.now().isoformat()
            }
            
            logger.warning("Pre-rebuild validation degraded state detected:")
            print(f"   Context: {degraded_state['context_tag']}")
            print(f"   Failed checks: {', '.join(failed_checks)}")
            print(f"   Symbolic hash: {degraded_state['symbolic_hash']}")
            
            # Log degraded state to status file for tracking
            preventer.log_status(
                "pre_rebuild_degraded", 
                f"Degraded state: {', '.join(failed_checks)}"
            )
            
            # Save degraded state metadata for DLP traceability
            degraded_state_file = preventer.workspace_root / ".rebuild_degraded_state.json"
            with open(degraded_state_file, 'w') as f:
                json.dump(degraded_state, f, indent=2)
            
            logger.warning("Continuing with degraded state (pre-rebuild phase)...")
        
        preventer.log_status("pre_rebuild_completed", "Pre-rebuild protection completed")
    else:
        # Regular validation mode - check everything including dependencies
        preventer.log_status("validation_started", "Regular validation starting")
        all_passed, _ = preventer.run_validation_suite(skip_dependencies=False)
        if not all_passed:
            sys.exit(1)
        preventer.log_status("validation_completed", "Regular validation completed")
    
    print("🎯 Aurora CloudBank rebuild protection is active!")


if __name__ == "__main__":
    main()
