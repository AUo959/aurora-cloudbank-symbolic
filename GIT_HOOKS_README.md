# Aurora Git Hooks Documentation

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
