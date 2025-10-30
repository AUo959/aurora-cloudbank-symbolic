# Code Improvement Engine

## Overview

The **Code Improvement Engine** is an automated code quality analysis system that identifies improvement opportunities in Python codebases. It uses pattern-based detection to find common issues across multiple quality dimensions including refactoring needs, performance bottlenecks, security risks, readability concerns, and maintainability problems.

## Features

- **Multi-Category Analysis**: Detects issues across 6 improvement categories
- **Severity Scoring**: Ranks suggestions by impact level (Low, Medium, High, Critical)
- **Confidence Scoring**: Each suggestion includes a confidence score (0.0-1.0)
- **Pattern-Based Detection**: 5 built-in patterns with extensible architecture
- **Directory Scanning**: Analyze entire codebases efficiently
- **Advanced Filtering**: Filter by confidence, category, severity, and pattern
- **REST API**: Full FastAPI integration for programmatic access
- **Automated Reporting**: Generate comprehensive analysis reports

## Core Concepts

### Improvement Categories

| Category | Description | Focus Area |
|----------|-------------|------------|
| `REFACTORING` | Code structure improvements | Complexity, duplication |
| `PERFORMANCE` | Efficiency optimizations | Algorithms, resources |
| `SECURITY` | Security vulnerabilities | Error handling, validation |
| `READABILITY` | Code clarity enhancements | Naming, magic numbers |
| `MAINTAINABILITY` | Long-term code health | Function length, modularity |
| `TESTING` | Test coverage and quality | Unit tests, assertions |

### Severity Levels

| Level | Priority | Typical Response |
|-------|----------|-----------------|
| `LOW` | Nice-to-have | Address during refactoring |
| `MEDIUM` | Important | Schedule for next sprint |
| `HIGH` | Urgent | Fix within days |
| `CRITICAL` | Blocking | Fix immediately |

### Confidence Scores

Each suggestion includes a confidence score indicating detection accuracy:

- **0.9-1.0**: High confidence - Very likely a real issue
- **0.7-0.9**: Good confidence - Probably worth addressing
- **0.5-0.7**: Moderate confidence - Review before applying
- **Below 0.5**: Low confidence - May be false positive

## Built-In Patterns

### 1. High Complexity Detection

**Pattern ID**: `high_complexity`  
**Category**: Refactoring  
**Severity**: Medium

Detects deeply nested code structures that reduce readability.

```python
# Detected:
def process(data):
    if data:
        if data.valid:
            if data.has_items:
                if data.items > 10:
                    return "complex"  # Nesting depth: 4
```

**Suggestion**: Extract nested logic into helper functions.

### 2. Duplicate Code Detection

**Pattern ID**: `duplicate_code`  
**Category**: Refactoring  
**Severity**: Medium

Identifies repeated code blocks that should be extracted.

```python
# Detected:
def func_a():
    x = calculate()
    y = transform(x)
    return y

def func_b():
    x = calculate()  # Duplicate
    y = transform(x)  # Duplicate
    return y
```

**Suggestion**: Extract common logic into shared function.

### 3. Long Function Detection

**Pattern ID**: `long_function`  
**Category**: Maintainability  
**Severity**: Low

Flags functions exceeding 50 lines (configurable threshold).

```python
# Detected:
def mega_function():
    # ... 60 lines of code ...
    pass
```

**Suggestion**: Split into smaller, focused functions.

### 4. Magic Number Detection

**Pattern ID**: `magic_numbers`  
**Category**: Readability  
**Severity**: Low

Identifies unexplained numeric literals.

```python
# Detected:
max_users = 9999  # What does 9999 mean?
timeout = 3600     # Why 3600?
```

**Suggestion**: Replace with named constants:

```python
MAX_USERS = 9999  # System capacity limit
TIMEOUT_SECONDS = 3600  # 1 hour in seconds
```

### 5. Missing Error Handling

**Pattern ID**: `error_handling`  
**Category**: Security  
**Severity**: High

Detects risky operations without try/except blocks.

```python
# Detected:
data = open('/tmp/file.txt').read()  # No error handling
value = int(user_input)              # No validation
```

**Suggestion**: Add appropriate error handling:

```python
try:
    with open('/tmp/file.txt') as f:
        data = f.read()
except IOError as e:
    logger.error("Failed to read file: %s", e)
    raise
```

## Quick Start

### Python API Usage

```python
from src.improvement import get_improvement_engine

# Get singleton engine instance
engine = get_improvement_engine()

# Analyze a single file
suggestions = engine.analyze_file("path/to/file.py")

for suggestion in suggestions:
    print(f"{suggestion.severity.value}: {suggestion.description}")
    print(f"  Line {suggestion.line_number}: {suggestion.suggested_fix}")
    print(f"  Confidence: {suggestion.confidence_score:.2f}")

# Analyze entire directory
results = engine.analyze_directory("src/", file_patterns=["*.py"])

# Generate report
report = engine.generate_report(results)
print(f"Analyzed {report['total_files_analyzed']} files")
print(f"Found {report['total_suggestions']} suggestions")
```

### REST API Usage

#### Analyze File

```bash
curl -X POST http://localhost:8000/improvements/analyze-file \
  -H "Content-Type: application/json" \
  -d '{"file_path": "src/module.py"}'
```

Response:
```json
[
  {
    "file_path": "src/module.py",
    "line_number": 42,
    "category": "readability",
    "severity": "low",
    "description": "Magic number detected: 9999",
    "rationale": "Magic numbers reduce code clarity.",
    "suggested_fix": "Replace with named constant",
    "confidence_score": 0.7
  }
]
```

#### Analyze Directory

```bash
curl -X POST http://localhost:8000/improvements/analyze-directory \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "src/",
    "min_confidence": 0.7,
    "categories": ["security", "refactoring"],
    "severities": ["high", "critical"]
  }'
```

Response:
```json
{
  "total_files_analyzed": 15,
  "total_suggestions": 42,
  "by_category": {
    "security": 8,
    "refactoring": 34
  },
  "by_severity": {
    "high": 8,
    "critical": 2
  },
  "suggestions": {
    "src/module1.py": [...],
    "src/module2.py": [...]
  }
}
```

#### List Available Options

```bash
# Get all categories
curl http://localhost:8000/improvements/categories

# Get all severity levels
curl http://localhost:8000/improvements/severities

# Get registered patterns
curl http://localhost:8000/improvements/patterns

# Check engine health
curl http://localhost:8000/improvements/health
```

## Advanced Usage

### Custom Filtering

```python
from src.improvement import ImprovementCategory, ImprovementSeverity

engine = get_improvement_engine()

# Analyze with filters
suggestions = engine.analyze_file("module.py")
filtered = engine.filter_suggestions(
    suggestions,
    min_confidence=0.8,
    categories={ImprovementCategory.SECURITY, ImprovementCategory.REFACTORING},
    severities={ImprovementSeverity.HIGH, ImprovementSeverity.CRITICAL}
)
```

### Custom Patterns

Create custom detection patterns by extending `ImprovementPattern`:

```python
from src.improvement.engine import ImprovementPattern, ImprovementSuggestion
from src.improvement import ImprovementCategory, ImprovementSeverity

class CustomPattern(ImprovementPattern):
    def __init__(self):
        super().__init__(
            name="my_custom_pattern",
            category=ImprovementCategory.TESTING,
            severity=ImprovementSeverity.MEDIUM
        )
    
    def detect(self, file_path, content):
        """Custom detection logic"""
        suggestions = []
        
        # Example: Detect missing docstrings
        for i, line in enumerate(content.split('\n'), 1):
            if line.strip().startswith('def ') and '"""' not in content:
                suggestions.append(ImprovementSuggestion(
                    file_path=str(file_path),
                    line_number=i,
                    category=self.category,
                    severity=self.severity,
                    description="Function missing docstring",
                    rationale="Docstrings improve code documentation",
                    suggested_fix="Add function docstring",
                    confidence_score=0.8
                ))
        
        return suggestions

# Register custom pattern
engine = get_improvement_engine()
engine.register_pattern(CustomPattern())
```

### Batch Processing

```python
from pathlib import Path
import json

engine = get_improvement_engine()

# Process multiple directories
projects = [
    Path("project_a/src"),
    Path("project_b/src"),
    Path("project_c/src")
]

all_results = {}
for project_dir in projects:
    results = engine.analyze_directory(project_dir)
    report = engine.generate_report(results)
    all_results[str(project_dir)] = report

# Export consolidated report
with open("analysis_report.json", "w") as f:
    json.dump(all_results, f, indent=2)
```

## API Reference

### Python API

#### `CodeImprovementEngine`

Main engine class for code analysis.

##### Methods

**`analyze_file(file_path: Path) -> List[ImprovementSuggestion]`**

Analyze a single Python file.

- **Parameters**: `file_path` - Path to file
- **Returns**: List of improvement suggestions
- **Raises**: `IOError` if file cannot be read

**`analyze_directory(directory: Path, file_patterns: List[str] = ["*.py"]) -> Dict[str, List[ImprovementSuggestion]]`**

Analyze all files in a directory.

- **Parameters**:
  - `directory` - Directory path
  - `file_patterns` - Glob patterns for files (default: Python files)
- **Returns**: Dictionary mapping file paths to suggestion lists

**`filter_suggestions(...) -> List[ImprovementSuggestion]`**

Filter suggestions by criteria.

- **Parameters**:
  - `suggestions` - List to filter
  - `min_confidence` - Minimum confidence (0.0-1.0)
  - `categories` - Set of allowed categories
  - `severities` - Set of allowed severities
- **Returns**: Filtered suggestion list

**`generate_report(results: Dict) -> Dict`**

Generate summary statistics.

- **Parameters**: `results` - Analysis results from `analyze_directory`
- **Returns**: Report dictionary with statistics

**`register_pattern(pattern: ImprovementPattern) -> None`**

Add custom detection pattern.

- **Parameters**: `pattern` - Pattern instance
- **Side effects**: Pattern added to detection pipeline

#### `ImprovementSuggestion`

Data class representing a single improvement suggestion.

##### Attributes

- `file_path: str` - File containing the issue
- `line_number: int` - Line number
- `category: ImprovementCategory` - Category enum
- `severity: ImprovementSeverity` - Severity enum
- `description: str` - Human-readable description
- `rationale: str` - Why this is an issue
- `suggested_fix: str` - How to fix it
- `automated_fix_available: bool` - Can be auto-fixed
- `safe_to_auto_apply: bool` - Safe for automation
- `confidence_score: float` - Detection confidence (0.0-1.0)

##### Methods

**`to_dict() -> Dict`**

Convert to dictionary for JSON serialization.

### REST API Endpoints

#### `POST /improvements/analyze-file`

Analyze single file.

**Request Body**:
```json
{
  "file_path": "path/to/file.py"
}
```

**Response**: `List[ImprovementSuggestion]` (200 OK)

#### `POST /improvements/analyze-directory`

Analyze directory with filtering.

**Request Body**:
```json
{
  "directory": "src/",
  "file_patterns": ["*.py"],
  "categories": ["security"],
  "severities": ["high", "critical"],
  "min_confidence": 0.7
}
```

**Response**: `AnalysisReportResponse` (200 OK)

#### `GET /improvements/categories`

List available categories.

**Response**: `List[str]` (200 OK)

#### `GET /improvements/severities`

List severity levels.

**Response**: `List[str]` (200 OK)

#### `GET /improvements/patterns`

List registered patterns.

**Response**: `List[PatternInfo]` (200 OK)

#### `GET /improvements/health`

Engine health status.

**Response**: Engine configuration (200 OK)

## Integration

### FastAPI Integration

```python
from fastapi import FastAPI
from src.improvement.api import router

app = FastAPI()
app.include_router(router)

# Engine available at /improvements/* endpoints
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Code Quality Analysis
  run: |
    curl -X POST http://localhost:8000/improvements/analyze-directory \
      -H "Content-Type: application/json" \
      -d '{"directory": "src/", "severities": ["critical"]}' \
      | jq '.total_suggestions'
    
    # Fail if critical issues found
    if [ $? -ne 0 ]; then exit 1; fi
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python3 << EOF
from src.improvement import get_improvement_engine, ImprovementSeverity

engine = get_improvement_engine()
results = engine.analyze_directory("src/")
report = engine.generate_report(results)

# Block commit if critical issues found
critical_count = report["by_severity"].get("critical", 0)
if critical_count > 0:
    print(f"❌ {critical_count} critical issues found!")
    exit(1)
EOF
```

## Configuration

### Pattern Thresholds

Customize detection thresholds by modifying pattern classes:

```python
from src.improvement.engine import LongFunctionPattern

# Increase long function threshold
LongFunctionPattern.max_lines = 100  # Default: 50
```

### Global Settings

```python
from src.improvement import get_improvement_engine, reset_improvement_engine

# Reset engine to clear patterns
reset_improvement_engine()

# Get fresh engine with default patterns
engine = get_improvement_engine()
```

## Performance

### Benchmarks

- **Single file analysis**: ~50-200ms (typical Python module)
- **Directory analysis**: ~2-10s (100 files, ~10K LOC)
- **Pattern detection**: O(n) where n = lines of code

### Optimization Tips

1. **Use file patterns** to exclude non-Python files
2. **Apply filters early** to reduce processing
3. **Batch process** multiple files in single `analyze_directory` call
4. **Cache results** for unchanged files

## Troubleshooting

### Issue: Slow analysis on large codebases

**Solution**: Use more specific file patterns and exclude test directories:

```python
results = engine.analyze_directory(
    "src/",
    file_patterns=["src/**/*.py"]  # Exclude tests, docs, etc.
)
```

### Issue: Too many false positives

**Solution**: Increase confidence threshold:

```python
filtered = engine.filter_suggestions(suggestions, min_confidence=0.8)
```

### Issue: Custom pattern not firing

**Solution**: Verify pattern registration and check `detect()` return value:

```python
engine = get_improvement_engine()
print(f"Patterns registered: {len(engine._patterns)}")

# Debug custom pattern
pattern = MyCustomPattern()
test_suggestions = pattern.detect(Path("test.py"), "def test(): pass")
print(f"Detected: {len(test_suggestions)}")
```

## Best Practices

1. **Start with high severity** - Address critical/high issues first
2. **Use confidence scores** - Focus on high-confidence suggestions (>0.7)
3. **Review before applying** - Don't blindly apply all suggestions
4. **Combine with linters** - Use alongside tools like Flake8, Pylint
5. **Customize patterns** - Add domain-specific detection logic
6. **Automate reporting** - Integrate into CI/CD pipeline
7. **Track metrics** - Monitor improvement trends over time

## Security Considerations

- **No code execution**: Engine only parses, never runs analyzed code
- **Read-only operations**: No files modified unless explicitly requested
- **Path validation**: File paths sanitized to prevent traversal attacks
- **Rate limiting**: API endpoints should be rate-limited in production
- **Authentication**: Secure `/improvements/*` endpoints appropriately

## Contributing

To add new detection patterns:

1. Extend `ImprovementPattern` base class
2. Implement `detect()` method
3. Add comprehensive tests
4. Document pattern behavior
5. Register with engine

See `src/improvement/engine.py` for pattern examples.

## License

Part of Aurora CloudBank Symbolic - See repository license.

## Related Documentation

- [OpenTelemetry Integration](./OPENTELEMETRY.md) - Observability setup
- [Synergy Dashboard](./SYNERGY_DASHBOARD.md) - Component registry
- [Contributing Guide](../CONTRIBUTING.md) - Development workflow
