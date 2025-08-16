import subprocess

# !/usr/bin/env python3
"""

        from canonical_validator import CanonicalValidator

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
        "pyyaml",  # For configuration files
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

    return True


def setup_git_hooks():
    """Set up Git hooks for validation"""
    print("\n🔗 Setting up Git hooks...")

    git_dir = Path(".git")
    if not git_dir.exists():
        print("  ⚠️ Not a Git repository - skipping Git hooks setup")
        return True

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    # Setup pre-commit hook
    pre_commit_hook = hooks_dir / "pre-commit"
    hook_content = """#!/bin/bash
# Aurora CloudBank Canonical Validation Pre-commit Hook
python3 scripts/git_pre_commit_hook.py
"""

    try:
        with open(pre_commit_hook, "w", encoding="utf-8") as f:
            f.write(hook_content)

        # Make executable
        os.chmod(pre_commit_hook, 0o755)
        print("  ✅ Pre-commit hook installed")

        return True
    except Exception as e:
        print(f"  ❌ Failed to setup Git hooks: {e}")
        return False


def create_validation_scripts():
    """Ensure validation scripts are executable"""
    print("\n🔧 Configuring validation scripts...")

    scripts = ["scripts/canonical_validator.py", "scripts/git_pre_commit_hook.py", "scripts/continuous_validator.py"]

    for script_path in scripts:
        script = Path(script_path)
        if script.exists():
            # Make executable
            os.chmod(script, 0o755)
            print(f"  ✅ {script.name} configured")
        else:
            print(f"  ❌ {script.name} not found")
            return False

    return True


def create_validation_directories():
    """Create necessary directories for validation"""
    print("\n📁 Creating validation directories...")

    directories = ["config", "logs", "reports"]

    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"  ✅ {dir_name}/ directory ready")

    return True


def test_validation_system():
    """Test the validation system"""
    print("\n🧪 Testing validation system...")

    try:
        # Import and test validator
        sys.path.insert(0, "scripts")

        validator = CanonicalValidator()
        print("  ✅ Validator import successful")

        # Test configuration loading
        config_file = Path("config/canonical_validation.yaml")
        if config_file.exists():
            print("  ✅ Configuration file found")
        else:
            print("  ⚠️ Configuration file not found - using defaults")

        # Run quick validation test
        test_results = validator.validate_file("GitHub_Copilot_Custom_Instructions_Aurora_GUMAS.txt")
        print(f"  ✅ Test validation completed ({len(test_results)} checks)")

        return True
    except Exception as e:
        print(f"  ❌ Validation system test failed: {e}")
        return False


def create_usage_documentation():
    """Create usage documentation"""
    print("\n📚 Creating usage documentation...")

    usage_doc = """# Aurora CloudBank Canonical Validation System - Usage Guide

## Overview
The canonical validation system ensures all development work adheres to the ORION CORE canonical specification automatically.

## Components

### 1. Canonical Validator (`scripts/canonical_validator.py`)
Main validation engine that checks files against canonical specifications.

**Usage:**
```bash
# Validate entire workspace
python3 scripts/canonical_validator.py

# Validate specific file
python3 scripts/canonical_validator.py --file path/to/file.md
```

### 2. Git Pre-commit Hook (`scripts/git_pre_commit_hook.py`)
Automatically validates files before each commit.

**Features:**
- Blocks commits with critical canonical violations
- Auto-fixes minor issues
- Provides clear remediation guidance
- Generates validation reports

### 3. Continuous Monitor (`scripts/continuous_validator.py`)
Real-time file monitoring and validation.

**Usage:**
```bash
# Start continuous monitoring
python3 scripts/continuous_validator.py

# Run one-time validation
python3 scripts/continuous_validator.py --once
```

### 4. Configuration (`config/canonical_validation.yaml`)
Comprehensive configuration for validation rules, auto-fix settings, and escalation policies.

## Validation Rules

### Auto-Fixed Issues (Low Impact)
- Case corrections (API endpoints, file names)
- Format standardization
- Minor spelling corrections
- Whitespace normalization

### Escalated Issues (Require Attention)
- **Critical**: Anchor seed mismatches, security violations
- **High**: Picard_Delta_3 violations, layer architecture issues
- **Medium**: Staff name inconsistencies, API structure problems
- **Low**: Documentation formatting, communication syntax

## Common Workflows

### Development Workflow
1. Make code changes
2. Validation runs automatically (if continuous monitor enabled)
3. Auto-fixes applied immediately for minor issues
4. Critical issues generate alerts for immediate attention

### Git Workflow
1. Stage files: `git add .`
2. Attempt commit: `git commit -m "message"`
3. Pre-commit validation runs automatically
4. Commit proceeds if no critical violations
5. Critical violations block commit with guidance

### Manual Validation
```bash
# Full workspace validation
python3 scripts/canonical_validator.py

# Generate detailed report
python3 scripts/canonical_validator.py --report

# Validate and fix specific file
python3 scripts/canonical_validator.py --file myfile.md --auto-fix
```

## Configuration Options

### Auto-fix Settings
- Enable/disable automatic fixes
- Set similarity thresholds for corrections
- Configure backup creation
- Limit fixes per file

### Escalation Rules
- Define severity levels
- Configure notification methods
- Set blocking conditions for Git commits

### File Patterns
- Include/exclude file types
- Custom validation rules
- Project-specific requirements

## Monitoring and Reporting

### Validation Reports
- Generated automatically in `reports/` directory
- Include summaries, fixes applied, and escalations
- Available in multiple formats (Markdown, JSON, YAML)

### Alert System
- Critical violations generate immediate alerts
- Alerts include specific remediation steps
- Alerts saved until issues resolved

### Logging
- All validation events logged
- Searchable validation history
- Performance metrics tracking

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure dependencies installed (`pip install watchdog pyyaml`)
2. **Permission errors**: Make scripts executable (`chmod +x scripts/*.py`)
3. **Git hook issues**: Verify hook permissions and Git repository status

### Getting Help
- Check validation reports for detailed guidance
- Review `canonical_validation.yaml` configuration
- Examine validation logs for error patterns

## Best Practices
1. Enable continuous monitoring during active development
2. Review validation reports regularly
3. Address high-priority issues promptly
4. Keep canonical specification up to date
5. Use auto-fixes for consistency improvements

---

**System Status**: Canonical validation system ready for use
**Configuration**: See `config/canonical_validation.yaml`
**Support**: Aurora CloudBank Development Team
"""

    with open("CANONICAL_VALIDATION_USAGE.md", "w", encoding="utf-8") as f:
        f.write(usage_doc)

    print("  ✅ Usage documentation created")
    return True


def main():
    """Main setup function"""
    print_header()

    setup_steps = [
        ("Dependencies", check_dependencies),
        ("Git Hooks", setup_git_hooks),
        ("Scripts", create_validation_scripts),
        ("Directories", create_validation_directories),
        ("Testing", test_validation_system),
        ("Documentation", create_usage_documentation),
    ]

    failed_steps = []

    for step_name, step_function in setup_steps:
        try:
            if not step_function():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} setup failed: {e}")
            failed_steps.append(step_name)

    print("\n" + "=" * 60)

    if failed_steps:
        print(f"⚠️ Setup completed with issues in: {', '.join(failed_steps)}")
        print("Please review the errors above and re-run setup if needed.")
    else:
        print("✅ Aurora CloudBank Canonical Validation System setup complete!")
        print("\n🎯 Next Steps:")
        print("1. Review configuration: config/canonical_validation.yaml")
        print("2. Test validation: python3 scripts/canonical_validator.py")
        print("3. Start continuous monitoring: python3 scripts/continuous_validator.py")
        print("4. Read usage guide: CANONICAL_VALIDATION_USAGE.md")
        print("\n🔗 Git Integration:")
        print("- Pre-commit validation: Enabled automatically")
        print("- Blocks critical violations")
        print("- Auto-fixes minor issues")
        print("\n🛰️ Aurora CloudBank canonical compliance is now automated!")


if __name__ == "__main__":
    main()
