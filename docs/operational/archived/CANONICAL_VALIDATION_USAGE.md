# Aurora CloudBank Canonical Validation System - Usage Guide

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
