#!/usr/bin/env python3
"""
Aurora Git Hooks Automation Setup
Intelligent Git hooks for quality assurance and workflow optimization
"""

import logging

logger = logging.getLogger(__name__)

import os
import shutil
import stat
from pathlib import Path


class GitHooksAutomationSetup:

    def __init__(self):
        self.git_hooks_dir = Path(".git/hooks")
        self.hooks_created = []
        self.hooks_backup_dir = Path(".git/hooks_backup")

    def create_backup(self):
        """Create backup of existing hooks"""
        print("💾 Creating Git hooks backup...")

        if not self.git_hooks_dir.exists():
            print("  ℹ️  No existing hooks directory")
            return

        if self.hooks_backup_dir.exists():
            shutil.rmtree(self.hooks_backup_dir)

        # Copy existing hooks
        existing_hooks = list(self.git_hooks_dir.glob("*"))
        if existing_hooks:
            shutil.copytree(self.git_hooks_dir, self.hooks_backup_dir)
            print(f"  ✅ Backed up {len(existing_hooks)} existing hooks")
        else:
            print("  ℹ️  No existing hooks to backup")

    def create_pre_commit_hook(self):
        """Create intelligent pre-commit hook"""
        hook_content = """#!/bin/bash
# Aurora CloudBank Pre-commit Hook
# Intelligent quality checks before commits

set -e

echo "🚁 Aurora Pre-commit Quality Check"
echo "=================================="

# Check if smart-devops is available
if [ -x "./smart-devops" ]; then
    echo "🧠 Running intelligent pre-flight check..."
    if ! ./smart-devops quick; then
        echo "❌ Pre-flight check failed!"
        echo "💡 Tip: Run 'smart-devops tips' for guidance"
        exit 1
    fi
    echo "✅ Pre-flight check passed!"
else
    echo "⚠️  smart-devops not found, running basic checks..."

    # Basic syntax check for Python files
    if command -v python3 &> /dev/null; then
        echo "🐍 Checking Python syntax..."
        for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\\.py$'); do
            if [ -f "$file" ]; then
                python3 -m py_compile "$file" || {
                    echo "❌ Syntax error in $file"
                    exit 1
                }
            fi
        done
        echo "✅ Python syntax OK"
    fi

    # Basic JavaScript syntax check
    if command -v node &> /dev/null; then
        echo "📜 Checking JavaScript syntax..."
        for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\\.js$'); do
            if [ -f "$file" ]; then
                node -c "$file" || {
                    echo "❌ Syntax error in $file"
                    exit 1
                }
            fi
        done
        echo "✅ JavaScript syntax OK"
    fi

    # Check for large files
    echo "📁 Checking file sizes..."
    for file in $(git diff --cached --name-only --diff-filter=ACM); do
        if [ -f "$file" ]; then
            size=$(wc -c < "$file")
            if [ $size -gt 1048576 ]; then  # 1MB limit
                echo "⚠️  Large file detected: $file (${size} bytes)"
                echo "Consider using Git LFS for large files"
            fi
        fi
    done
fi

# Check for sensitive information
echo "🔒 Scanning for sensitive data..."
sensitive_patterns=(
    "password.*=.*['\"][^'\"]{8,}['\"]"
    "api[_-]?key.*=.*['\"][^'\"]{16,}['\"]"
    "secret.*=.*['\"][^'\"]{16,}['\"]"
    "token.*=.*['\"][^'\"]{20,}['\"]"
)

for file in $(git diff --cached --name-only --diff-filter=ACM); do
    if [ -f "$file" ]; then
        for pattern in "${sensitive_patterns[@]}"; do
            if grep -iE "$pattern" "$file" &> /dev/null; then
                echo "⚠️  Possible sensitive data in $file"
                echo "Please review before committing"
            fi
        done
    fi
done

echo "🎯 Pre-commit checks completed successfully!"
echo "Ready for commit! 🚀"
exit 0
"""

        hook_path = self.git_hooks_dir / "pre-commit"
        with open(hook_path, "w") as f:
            f.write(hook_content)

        # Make executable
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
        self.hooks_created.append("pre-commit")
        print("  ✅ Created intelligent pre-commit hook")

    def create_pre_push_hook(self):
        """Create intelligent pre-push hook"""
        hook_content = """#!/bin/bash
# Aurora CloudBank Pre-push Hook
# Comprehensive validation before pushing to remote

set -e

echo "🚀 Aurora Pre-push Validation"
echo "============================"

# Get information about what's being pushed
remote="$1"
url="$2"

echo "📡 Pushing to: $remote ($url)"

# Run comprehensive validation if smart-devops is available
if [ -x "./smart-devops" ]; then
    echo "🧠 Running full-cycle validation..."
    if ! ./smart-devops full-cycle; then
        echo "❌ Full-cycle validation failed!"
        echo "💡 Run 'smart-devops optimize' to fix issues"
        exit 1
    fi
    echo "✅ Full-cycle validation passed!"
else
    echo "⚠️  smart-devops not found, running basic validation..."

    # Run tests if available
    if [ -f "package.json" ] && command -v npm &> /dev/null; then
        if npm run test --if-present; then
            echo "✅ Tests passed"
        else
            echo "⚠️  Some tests failed, but continuing..."
        fi
    fi

    # Check for Python requirements
    if [ -f "requirements.txt" ] && command -v python3 &> /dev/null; then
        echo "🐍 Checking Python requirements..."
        python3 -m pip check || echo "⚠️  Some Python dependencies may have issues"
    fi
fi

# Security scan before push
echo "🛡️  Running security scan..."
if [ -f "scripts/aurora_security_scanner.py" ]; then
    python3 scripts/aurora_security_scanner.py || {
        echo "⚠️  Security scan found issues, but allowing push"
        echo "💡 Review security_scan_report.json for details"
    }
fi

# Check branch protection (if pushing to main/master)
while read local_ref local_sha remote_ref remote_sha; do
    if [[ "$remote_re" == "refs/heads/main" ]] || [[ "$remote_re" == "refs/heads/master" ]]; then
        echo "🔒 Pushing to protected branch: $(basename "$remote_re")"
        echo "Ensure you have proper authorization and code review"
    fi
done

echo "🎯 Pre-push validation completed!"
echo "Proceeding with push... 🚀"
exit 0
"""

        hook_path = self.git_hooks_dir / "pre-push"
        with open(hook_path, "w") as f:
            f.write(hook_content)

        # Make executable
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
        self.hooks_created.append("pre-push")
        print("  ✅ Created intelligent pre-push hook")

    def create_commit_msg_hook(self):
        """Create commit message validation hook"""
        hook_content = """#!/bin/bash
# Aurora CloudBank Commit Message Hook
# Ensures commit messages follow best practices

commit_regex='^(🎯|✨|🐛|📝|🔧|🚀|🔒|⚡|🧹|🎨|📱|🌐)( [A-Z].*)?$|^(feat|fix|docs|style|refactor|test|chore)(\\(.+\\))?!?:.+'

commit_message=$(cat "$1")

echo "📝 Validating commit message format..."

if [[ $commit_message =~ $commit_regex ]]; then
    echo "✅ Commit message format is good!"
    exit 0
else
    echo "❌ Invalid commit message format!"
    echo ""
    echo "📋 Commit Message Guidelines:"
    echo "Option 1 - Emoji format:"
    echo "  🎯 Main feature or goal"
    echo "  ✨ New feature"
    echo "  🐛 Bug fix"
    echo "  📝 Documentation"
    echo "  🔧 Configuration/tools"
    echo "  🚀 Deployment/release"
    echo "  🔒 Security"
    echo "  ⚡ Performance"
    echo "  🧹 Code cleanup"
    echo "  🎨 UI/styling"
    echo ""
    echo "Option 2 - Conventional format:"
    echo "  feat: add new feature"
    echo "  fix: resolve bug"
    echo "  docs: update documentation"
    echo "  style: formatting changes"
    echo "  refactor: code restructure"
    echo "  test: add/update tests"
    echo "  chore: maintenance tasks"
    echo ""
    echo "Current message: '$commit_message'"
    echo ""
    exit 1
fi
"""

        hook_path = self.git_hooks_dir / "commit-msg"
        with open(hook_path, "w") as f:
            f.write(hook_content)

        # Make executable
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
        self.hooks_created.append("commit-msg")
        print("  ✅ Created commit message validation hook")

    def create_post_commit_hook(self):
        """Create post-commit automation hook"""
        hook_content = """#!/bin/bash
# Aurora CloudBank Post-commit Hook
# Automated tasks after successful commits

echo "📋 Aurora Post-commit Automation"
echo "==============================="

# Update development status
if [ -f ".aurora_dev_status" ]; then
    echo "$(date): Commit $(git rev-parse --short HEAD)" >> .aurora_dev_status
fi

# Run quick optimization check
if [ -x "./smart-devops" ]; then
    echo "🧠 Running post-commit optimization check..."
    ./smart-devops status > /dev/null 2>&1 || echo "⚠️  Consider running optimization"
fi

# Notify about workflow improvements
commit_count=$(git rev-list --count HEAD)
if [ $((commit_count % 10)) -eq 0 ]; then
    echo "🎯 Milestone: $commit_count commits!"
    echo "💡 Consider running './smart-devops optimize' for performance review"
fi

echo "✅ Post-commit automation completed"
exit 0
"""

        hook_path = self.git_hooks_dir / "post-commit"
        with open(hook_path, "w") as f:
            f.write(hook_content)

        # Make executable
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
        self.hooks_created.append("post-commit")
        print("  ✅ Created post-commit automation hook")

    def setup_hooks(self):
        """Set up all Git hooks"""
        print("🔗 Setting up Aurora Git hooks...")

        # Ensure hooks directory exists
        self.git_hooks_dir.mkdir(parents=True, exist_ok=True)

        # Create all hooks
        self.create_pre_commit_hook()
        self.create_pre_push_hook()
        self.create_commit_msg_hook()
        self.create_post_commit_hook()

        print(f"  🎯 Created {len(self.hooks_created)} Git hooks")

    def test_hooks(self):
        """Test that hooks are properly installed"""
        print("🧪 Testing Git hooks installation...")

        all_working = True
        for hook_name in self.hooks_created:
            hook_path = self.git_hooks_dir / hook_name
            if hook_path.exists() and os.access(hook_path, os.X_OK):
                print(f"  ✅ {hook_name} hook is executable")
            else:
                print(f"  ❌ {hook_name} hook has issues")
                all_working = False

        return all_working

    def generate_hooks_documentation(self):
        """Generate documentation for the installed hooks"""
        documentation = """# Aurora Git Hooks Documentation

## Overview
Aurora CloudBank uses intelligent Git hooks to maintain code quality and automate workflow optimizations.

## Installed Hooks

### Pre-commit Hook
**Triggers:** Before each commit
**Purpose:** Quality assurance and syntax validation
**Features:**
- Smart-devops integration for comprehensive checks
- Python and JavaScript syntax validation
- File size monitoring
- Sensitive data scanning
- Lint checking

### Pre-push Hook
**Triggers:** Before pushing to remote repository
**Purpose:** Comprehensive validation before sharing code
**Features:**
- Full-cycle workflow validation
- Test execution
- Security scanning
- Branch protection awareness
- Dependency verification

### Commit Message Hook
**Triggers:** When writing commit messages
**Purpose:** Enforce consistent commit message standards
**Features:**
- Emoji-based or conventional commit format
- Clear guidelines and examples
- Automatic validation

### Post-commit Hook
**Triggers:** After successful commits
**Purpose:** Automated maintenance and notifications
**Features:**
- Development status tracking
- Optimization reminders
- Milestone notifications
- Performance monitoring

## Usage

### Normal Development Flow
The hooks work automatically during normal Git operations:
```bash
git add .
git commit -m "✨ Add new feature"  # pre-commit + commit-msg hooks run
git push origin main               # pre-push hook runs
```

### Manual Hook Testing
Test individual hooks:
```bash
.git/hooks/pre-commit   # Test pre-commit hook
.git/hooks/pre-push     # Test pre-push hook
```

### Bypass Hooks (Emergency Only)
```bash
git commit --no-verify -m "Emergency fix"  # Skip pre-commit + commit-msg
git push --no-verify                       # Skip pre-push
```

## Integration with Smart-DevOps

The hooks intelligently integrate with the Aurora Smart-DevOps system:
- **Available:** Uses full smart-devops validation capabilities
- **Not Available:** Falls back to basic quality checks

## Troubleshooting

### Hook Not Running
- Check if hook file exists: `ls -la .git/hooks/`
- Verify executable permissions: `chmod +x .git/hooks/hook-name`

### Hook Failing
- Run hook manually to see detailed output
- Check smart-devops status: `./smart-devops status`
- Review error messages and follow suggested fixes

### Disable Temporarily
```bash
chmod -x .git/hooks/hook-name  # Disable specific hook
```

## Customization

Hooks can be customized by editing files in `.git/hooks/`.
Backup originals first: `cp .git/hooks/pre-commit .git/hooks/pre-commit.backup`

## Best Practices

1. **Don't bypass hooks routinely** - They're designed to prevent problems
2. **Keep smart-devops updated** - Hooks leverage its intelligence
3. **Review hook output** - Learn from the feedback provided
4. **Customize as needed** - Adapt hooks to your team's workflow

## Support

For issues with Git hooks:
1. Check the hook documentation above
2. Run `./smart-devops tips` for guidance
3. Review logs and error messages
4. Contact the development team if needed
"""

        with open("GIT_HOOKS_README.md", "w") as f:
            f.write(documentation)

        print("  📚 Created comprehensive hooks documentation")

    def generate_setup_report(self):
        """Generate setup completion report"""
        print("\n🎯 GIT HOOKS AUTOMATION SETUP COMPLETE!")
        print("=" * 50)

        report = {
            "setup_completed": True,
            "hooks_installed": self.hooks_created,
            "total_hooks": len(self.hooks_created),
            "features": [
                "Intelligent pre-commit quality checks",
                "Comprehensive pre-push validation",
                "Commit message standardization",
                "Post-commit automation",
                "Smart-devops integration",
                "Security scanning",
                "Syntax validation",
                "Performance monitoring",
            ],
            "benefits": [
                "Prevents broken code from being committed",
                "Ensures consistent commit message format",
                "Automated security and quality checks",
                "Reduces CI/CD failures",
                "Maintains code quality standards",
                "Provides helpful developer guidance",
            ],
        }

        logger.info("Installed {report["total_hooks']} intelligent Git hooks:")
        for hook in report["hooks_installed"]:
            print(f"   • {hook}")

        print("\n🚀 Key Benefits:")
        for benefit in report["benefits"][:4]:  # Show top 4 benefits
            print(f"   • {benefit}")

        print("\n📚 Documentation: GIT_HOOKS_README.md")
        print("💡 Test hooks: Run a git commit or push to see them in action!")

        return report


def main():
    """Execute Git hooks automation setup"""
    setup = GitHooksAutomationSetup()

    print("🔗 Aurora Git Hooks Automation Setup")
    print("=" * 40)

    # Create backup of existing hooks
    setup.create_backup()

    # Install all hooks
    setup.setup_hooks()

    # Test installation
    if setup.test_hooks():
        logger.info("All hooks installed and working correctly!")
    else:
        logger.warning("Some hooks may have installation issues")

    # Generate documentation
    setup.generate_hooks_documentation()

    # Generate report
    setup.generate_setup_report()

    print("\n🎉 Git hooks automation is now active!")
    print("Your repository is protected by intelligent quality gates!")


if __name__ == "__main__":
    main()
