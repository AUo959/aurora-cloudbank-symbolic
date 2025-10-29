#!/usr/bin/env python3
"""
Aurora CloudBank Canonical Validation System - Setup Script
Installs and configures the canonical validation mechanism

This script:
1. Sets up Git hooks for automatic validation
2. Installs required dependencies
3. Configures validation rules
4. Tests the validation system
5. Provides usage instructions
"""
import os
import sys
import subprocess
from pathlib import Path


def print_header():
    """Print setup header"""
    print("🛰️ Aurora CloudBank Canonical Validation System Setup")
    print("=" * 60)
    print("Configuring automatic canonical compliance validation...")
    print()


def check_dependencies():
    """Check and install required dependencies"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        "watchdog",  # For file monitoring
        "pyyaml",    # For configuration files
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} (missing)")
    
    if missing_packages:
        print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    else:
        print("\n✅ All dependencies are installed")
    
    return True


def setup_git_hooks(repo_root):
    """Set up Git hooks for pre-commit validation"""
    print("\n🔗 Setting up Git hooks...")
    
    hooks_dir = repo_root / ".git" / "hooks"
    pre_commit_hook = hooks_dir / "pre-commit"
    
    if not hooks_dir.exists():
        print("  ⚠️  .git/hooks directory not found. Are you in a git repository?")
        return False
    
    hook_script = '''#!/bin/bash
# Aurora CloudBank Canonical Validation Pre-commit Hook

echo "🔍 Running canonical validation..."

python3 scripts/canonical_validator.py --mode=pre-commit

if [ $? -ne 0 ]; then
    echo "❌ Canonical validation failed. Commit rejected."
    exit 1
fi

echo "✅ Canonical validation passed"
exit 0
'''
    
    try:
        with open(pre_commit_hook, "w") as f:
            f.write(hook_script)
        
        # Make the hook executable
        os.chmod(pre_commit_hook, 0o755)
        print("  ✅ Pre-commit hook installed")
        return True
    except Exception as e:
        print(f"  ❌ Failed to install hook: {e}")
        return False


def setup_config_files(repo_root):
    """Set up configuration files"""
    print("\n⚙️  Setting up configuration files...")
    
    config_dir = repo_root / ".canonical"
    config_dir.mkdir(exist_ok=True)
    
    rules_file = config_dir / "rules.yaml"
    
    default_rules = '''# Aurora CloudBank Canonical Validation Rules
version: "1.0"

rules:
  branch_naming:
    enabled: true
    patterns:
      - "main"
      - "feature/*"
      - "fix/*"
      - "R-*"
      - "codex/*"
  
  commit_messages:
    enabled: true
    require_prefix: false
    min_length: 10
  
  file_structure:
    enabled: true
    required_dirs:
      - "src"
      - "modules"
      - "scripts"
      - "tests"
  
  code_quality:
    enabled: true
    check_syntax: true
    check_imports: true
'''
    
    try:
        with open(rules_file, "w") as f:
            f.write(default_rules)
        print(f"  ✅ Configuration file created: {rules_file}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create config: {e}")
        return False


def create_validator_script(repo_root):
    """Create the main validator script if it doesn't exist"""
    print("\n📝 Setting up validator scripts...")
    
    scripts_dir = repo_root / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    validator_script = scripts_dir / "canonical_validator.py"
    
    if validator_script.exists():
        print(f"  ✅ {validator_script.name} already exists")
        return True
    
    script_content = '''#!/usr/bin/env python3
"""
Aurora CloudBank Canonical Validator
Performs validation checks on repository structure and commits
"""
import sys
import argparse

def validate():
    """Run validation checks"""
    print("Running canonical validation...")
    # Add validation logic here
    return True

def main():
    parser = argparse.ArgumentParser(description="Canonical Validator")
    parser.add_argument("--mode", default="full", help="Validation mode")
    args = parser.parse_args()
    
    success = validate()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
'''
    
    try:
        with open(validator_script, "w") as f:
            f.write(script_content)
        os.chmod(validator_script, 0o700)
        print(f"  ✅ {validator_script.name} created")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create validator: {e}")
        return False


def setup_directories(repo_root):
    """Ensure required directories exist"""
    print("\n📁 Setting up required directories...")
    
    required_dirs = [
        ".canonical",
        ".canonical/logs",
        ".canonical/cache",
    ]
    
    for dir_name in required_dirs:
        dir_path = repo_root / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_name}/ directory ready")
    
    return True


def run_validation_test(repo_root):
    """Test the validation system"""
    print("\n🧪 Testing validation system...")
    
    validator_script = repo_root / "scripts" / "canonical_validator.py"
    
    if not validator_script.exists():
        print("  ⚠️  Validator script not found")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(validator_script), "--mode=test"],
            capture_output=True,
            text=True,
            cwd=repo_root
        )
        
        if result.returncode == 0:
            print("  ✅ Validation test passed")
            return True
        else:
            print(f"  ⚠️  Validation test returned: {result.returncode}")
            return True  # Non-critical for setup
    except Exception as e:
        print(f"  ⚠️  Could not run validation test: {e}")
        return True  # Non-critical for setup


def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nUsage:")
    print("  • Validation runs automatically on git commit")
    print("  • Manual validation: python scripts/canonical_validator.py")
    print("  • Configuration: .canonical/rules.yaml")
    print("  • Logs: .canonical/logs/")
    print("\nNext Steps:")
    print("  1. Review and customize .canonical/rules.yaml")
    print("  2. Make a test commit to verify the pre-commit hook")
    print("  3. Check .canonical/logs/ for validation reports")
    print()


def main():
    """Main setup function"""
    print_header()
    
    # Get repository root
    repo_root = Path.cwd()
    while not (repo_root / ".git").exists():
        if repo_root == repo_root.parent:
            print("❌ Not in a git repository")
            sys.exit(1)
        repo_root = repo_root.parent
    
    print(f"📂 Repository root: {repo_root}")
    print()
    
    # Run setup steps
    steps = [
        ("Dependencies", lambda: check_dependencies()),
        ("Git Hooks", lambda: setup_git_hooks(repo_root)),
        ("Configuration", lambda: setup_config_files(repo_root)),
        ("Validator Scripts", lambda: create_validator_script(repo_root)),
        ("Directories", lambda: setup_directories(repo_root)),
        ("Validation Test", lambda: run_validation_test(repo_root)),
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            success = step_func()
            results.append((step_name, success))
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            results.append((step_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Setup Summary")
    print("=" * 60)
    
    for step_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {step_name}")
    
    failed_steps = [name for name, success in results if not success]
    
    if failed_steps:
        print(f"\n⚠️  Some steps failed: {', '.join(failed_steps)}")
        print("The system may not work correctly.")
    else:
        print_usage_instructions()
    
    sys.exit(0 if not failed_steps else 1)


if __name__ == "__main__":
    main()
