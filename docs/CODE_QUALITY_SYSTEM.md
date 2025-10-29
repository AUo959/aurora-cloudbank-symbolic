# Code Quality Analysis System

**Implementation of Issue #258: Integrate SonarQube and flake8 for Automated Code Quality Analysis**

## Overview

The Aurora Code Quality Analysis System provides automated code quality checking, reporting, and issue creation for the Aurora CloudBank Symbolic ecosystem. It integrates flake8 and SonarCloud to maintain high code standards and provides Aurora-native reflection integration with DLP tracking.

## Features

### ✅ Automated Analysis
- **flake8 Integration**: Comprehensive Python linting with customizable rules
- **SonarCloud Analysis**: Deep code quality and security scanning
- **Severity Classification**: Violations categorized as Critical, High, Medium, or Low
- **Quality Gates**: Automatic blocking of merges with critical violations

### ✅ Aurora Integration
- **Reflection Reports**: Analysis results in Aurora reflection format with DLP tracking
- **Chain Notation**: References Issue #258 (`001//258//`)
- **Symbolic Hash Validation**: Ensures integrity of analysis reports
- **T1/SRB Anchors**: Maintains temporal and symbolic reference tracking

### ✅ Automated Issue Creation
- **Critical Violation Tracking**: Auto-creates GitHub issues for critical problems
- **Smart Batching**: Limits issue creation to prevent spam (max 10 per run)
- **Contextual Information**: Issues include file location, error codes, and fix recommendations
- **PR Integration**: Posts analysis summaries as PR comments

### ✅ CI/CD Integration
- **GitHub Actions Workflow**: Automated analysis on every push and PR
- **Pull Request Comments**: Summary reports posted directly to PRs
- **Artifact Storage**: Analysis reports stored for 30 days
- **Configurable Triggers**: Manual runs with custom options

## Components

### 1. Code Quality Analyzer (`src/core/code_quality_analyzer.py`)

Main analysis engine that runs flake8 and generates structured reports.

**Key Classes:**
- `CodeQualityViolation`: Represents a single code quality issue
- `CodeQualityReport`: Aggregated analysis results
- `CodeQualityAnalyzer`: Main analyzer with flake8 integration

**Usage:**
```python
from src.core.code_quality_analyzer import CodeQualityAnalyzer

# Initialize analyzer
analyzer = CodeQualityAnalyzer()

# Run analysis
report = analyzer.run_flake8_analysis(['src', 'tests'])

# Generate Aurora reflection
reflection = analyzer.generate_reflection_report(report)

# Get critical violations for issue creation
critical = analyzer.get_critical_violations(report)
```

**CLI Usage:**
```bash
# Run analysis on current directory
python src/core/code_quality_analyzer.py

# Analyze specific paths
python src/core/code_quality_analyzer.py src/ modules/

# Generate Aurora reflection format
python src/core/code_quality_analyzer.py --reflection

# Save report to file
python src/core/code_quality_analyzer.py --output reports/quality.json
```

### 2. Issue Creator (`src/core/code_quality_issue_creator.py`)

Automatically creates GitHub issues for critical code quality violations.

**Key Classes:**
- `GitHubIssue`: Represents a GitHub issue
- `CodeQualityIssueCreator`: Creates and manages quality-related issues

**Usage:**
```python
from src.core.code_quality_issue_creator import CodeQualityIssueCreator

# Initialize creator
creator = CodeQualityIssueCreator('AUo959', 'aurora-cloudbank-symbolic')

# Create issues from violations
created = creator.batch_create_issues(
    critical_violations,
    commit_sha='abc123',
    pr_number=42,
    max_issues=10
)
```

**CLI Usage:**
```bash
# Create issues from report
python src/core/code_quality_issue_creator.py \
  --report reports/quality.json \
  --owner AUo959 \
  --repo aurora-cloudbank-symbolic \
  --commit abc123 \
  --pr 42 \
  --max-issues 5
```

### 3. GitHub Actions Workflow (`.github/workflows/code-quality.yml`)

Automated CI/CD workflow for code quality analysis.

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch with options

**Jobs:**
1. **code-quality**: Runs flake8, generates reports, creates issues
2. **sonarcloud**: Performs SonarCloud analysis (requires token)

**Outputs:**
- PR comments with analysis summary
- Uploaded report artifacts
- GitHub issues for critical violations (on main branch only)
- Job summary with metrics

### 4. SonarCloud Configuration (`sonar-project.properties`)

Configuration for SonarCloud integration.

**Settings:**
- Project: `AUo959_aurora-cloudbank-symbolic`
- Organization: `auo959`
- Python versions: 3.11, 3.12
- Source directories: `src`, `modules`, main scripts
- Test directories: `tests`
- Comprehensive exclusions for non-source files

## Severity Levels

### Critical (🔴)
- **Runtime Errors (E9)**: Code that will fail at runtime
- **Syntax Errors (F7)**: Invalid Python syntax
- **Undefined Names (F82)**: References to undefined variables

**Action**: Automatic issue creation, blocks merge

### High (🟠)
- **Unused Imports (F401)**: Imported but never used
- **Redefined Names (F811)**: Duplicate definitions
- **Import Order (E402)**: Improper import placement

**Action**: Flagged in reports, reviewed in PR

### Medium (🟡)
- **Line Length (E501)**: Lines exceeding 120 characters
- **Complexity (C9)**: Functions with high cyclomatic complexity
- **Warnings (W)**: Style warnings

**Action**: Informational, encouraged to fix

### Low (🟢)
- **Indentation (E1)**: Spacing issues
- **Whitespace (E2)**: Whitespace formatting
- **Blank Lines (E3)**: Blank line conventions

**Action**: Informational only

## Configuration

### flake8 (`.flake8`)

Current configuration:
```ini
[flake8]
max-line-length = 120
exclude = deploykit_tmp/*,.venv/*,scripts/deprecated/*
```

### Workflow Customization

Edit `.github/workflows/code-quality.yml` to customize:
- **Paths to analyze**: Modify step arguments
- **Issue creation threshold**: Change `max_issues` parameter
- **Analysis frequency**: Modify triggers
- **Quality gates**: Adjust pass/fail criteria

## Setting Up SonarCloud

1. **Enable SonarCloud**:
   - Visit https://sonarcloud.io
   - Sign in with GitHub
   - Add Aurora repository

2. **Configure Secrets**:
   ```bash
   # Add to GitHub repository secrets
   SONAR_TOKEN=your_sonarcloud_token
   ```

3. **Verify Configuration**:
   - Check `sonar-project.properties`
   - Update organization if different
   - Adjust exclusions as needed

## Usage Examples

### Running Analysis Locally

```bash
# Install dependencies
pip install flake8 requests

# Run analysis
python src/core/code_quality_analyzer.py --output reports/local.json

# View critical violations
python -c "
import json
with open('reports/local.json') as f:
    report = json.load(f)
    critical = [v for v in report['violations'] if v['severity'] == 'critical']
    print(f'Found {len(critical)} critical violations')
"
```

### Integrating with Pre-commit

Add to `.pre-commit-config.yaml`:
```yaml
  - repo: local
    hooks:
      - id: aurora-quality
        name: Aurora Code Quality
        entry: python src/core/code_quality_analyzer.py
        language: system
        pass_filenames: false
```

### CI/CD Integration

The workflow runs automatically on:
- Every push to main/develop
- Every PR
- Manual trigger from Actions tab

### Manual Workflow Dispatch

1. Go to **Actions** → **Code Quality Analysis**
2. Click **Run workflow**
3. Select branch
4. Optionally enable issue creation
5. Click **Run workflow**

## Report Format

### Standard Report
```json
{
  "timestamp": "2025-10-29T12:00:00Z",
  "total_violations": 10,
  "critical_count": 0,
  "high_count": 2,
  "medium_count": 5,
  "low_count": 3,
  "passed": true,
  "violations": [
    {
      "file_path": "src/example.py",
      "line_number": 42,
      "column": 5,
      "code": "E501",
      "message": "line too long (125 > 120 characters)",
      "severity": "medium"
    }
  ],
  "analysis_metadata": {
    "analyzer": "flake8",
    "paths_analyzed": ["src"],
    "config_file": ".flake8"
  }
}
```

### Aurora Reflection Format
```json
{
  "context_tag": "code_quality_analysis",
  "timestamp": "2025-10-29T12:00:00Z",
  "symbolic_hash_validation": "abc123def456",
  "analysis_summary": {
    "passed": true,
    "total_violations": 10,
    "severity_breakdown": {
      "critical": 0,
      "high": 2,
      "medium": 5,
      "low": 3
    }
  },
  "violations": [...],
  "metadata": {...},
  "dlp_trail": {
    "anchor_protocol": "T1/SRB",
    "analysis_version": "1.0.0",
    "chain_notation": "001//258//"
  }
}
```

## Troubleshooting

### flake8 Not Installed
```bash
pip install flake8
```

### GitHub Token Missing
Set `GITHUB_TOKEN` environment variable or configure in GitHub Actions secrets.

### SonarCloud Token Missing
Add `SONAR_TOKEN` to repository secrets via Settings → Secrets → Actions.

### Analysis Timeout
Increase timeout in workflow YAML:
```yaml
timeout-minutes: 20  # Increase from 15
```

### Too Many Issues Created
Adjust `max_issues` parameter in workflow or issue creator CLI.

## Testing

Run the test suite:
```bash
# Run all code quality tests
pytest tests/test_code_quality_analyzer.py -v

# Run with coverage
pytest tests/test_code_quality_analyzer.py --cov=src/core --cov-report=term

# Run specific test
pytest tests/test_code_quality_analyzer.py::TestCodeQualityAnalyzer::test_parse_flake8_output -v
```

## Maintenance

### Updating Severity Mappings

Edit `SEVERITY_MAP` in `src/core/code_quality_analyzer.py`:
```python
SEVERITY_MAP = {
    'E501': 'low',  # Downgrade line length to low priority
    'NEW_CODE': 'high',  # Add new error code
}
```

### Adding Custom Rules

Create `.flake8` extensions or plugins:
```bash
pip install flake8-docstrings flake8-bugbear
```

Update `.flake8` configuration accordingly.

## Future Enhancements

- [ ] Trend tracking and historical analysis
- [ ] Custom flake8 plugins for Aurora-specific patterns
- [ ] Integration with Aurora's consciousness/awareness system
- [ ] Automated PR fixes for simple violations
- [ ] Multi-language support (JavaScript, Go)
- [ ] Real-time analysis during development

## References

- **Issue #258**: Original feature request
- **flake8 Documentation**: https://flake8.pycqa.org
- **SonarCloud**: https://sonarcloud.io
- **Aurora DLP Protocol**: See `src/core/native_dlp_export.py`

## Support

For issues or questions:
1. Check this documentation
2. Review existing GitHub issues
3. Create new issue with `code-quality` label
4. Reference Issue #258 for context

---

*This system implements Issue #258 and maintains Aurora's ethical validation principles and DLP tracking standards.*
