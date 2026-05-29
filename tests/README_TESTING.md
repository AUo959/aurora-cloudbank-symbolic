# Aurora CloudBank Testing Guide

Comprehensive guide to testing the Aurora CloudBank Symbolic system.

## Test Organization

Tests are organized with pytest markers for selective execution and clear categorization.

### Speed-Based Markers

Run tests based on execution speed for rapid feedback cycles:

- **`@pytest.mark.unit`** - Fast unit tests (< 1 second)
  - Test individual functions and classes in isolation
  - Mock external dependencies
  - Run frequently during development
  - Example: `pytest -m unit`

- **`@pytest.mark.integration`** - Integration tests (1-10 seconds)
  - Test interactions between components
  - May use real dependencies
  - Run before commits
  - Example: `pytest -m integration`

- **`@pytest.mark.slow`** - Slow tests (> 10 seconds)
  - End-to-end tests
  - Performance tests
  - Full system integration
  - Example: `pytest -m slow`

- **`@pytest.mark.smoke`** - Critical smoke tests
  - Must-pass tests for quick validation
  - Run in CI/CD pipelines first
  - Example: `pytest -m smoke`

### Component-Based Markers

Run tests for specific system components:

- **`@pytest.mark.native`** - Native implementation tests
- **`@pytest.mark.opal2`** - Opal2 modular system tests
- **`@pytest.mark.aurora`** - Aurora core system tests
- **`@pytest.mark.quantum`** - Quantum processing tests
- **`@pytest.mark.security`** - Security and authentication tests
- **`@pytest.mark.api`** - API and web interface tests
- **`@pytest.mark.cli`** - Command line interface tests

### Priority Markers

- **`@pytest.mark.critical`** - Must-pass tests for production
- **`@pytest.mark.regression`** - Regression prevention tests

## Running Tests

### Quick Commands

```bash
# Run all tests
pytest tests/

# Fast feedback - unit tests only
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Critical tests only
pytest -m critical

# Component-specific
pytest -m aurora      # Aurora core tests
pytest -m opal2       # Opal2 system tests
pytest -m api         # API tests

# Specific test file
pytest tests/test_aurora_symbolic.py

# With verbose output
pytest -v tests/

# With coverage
pytest --cov=. --cov-report=term-missing tests/
```

### Common Test Workflows

**During Development:**
```bash
# Fast feedback loop
pytest -m unit -x  # Stop on first failure

# Watch mode (requires pytest-watch)
ptw -- -m unit
```

**Before Commit:**
```bash
# Run critical tests
pytest -m critical

# Run all but slow tests
pytest -m "not slow"
```

**Before PR:**
```bash
# Full test suite with coverage
pytest --cov=. --cov-report=html tests/

# Check coverage report
open htmlcov/index.html
```

**CI/CD Pipeline:**
```bash
# Smoke tests first (fast validation)
pytest -m smoke

# Then critical tests
pytest -m critical

# Finally full suite
pytest tests/
```

## Test Structure

### Good Test Practices

**1. Use Clear Test Names**
```python
@pytest.mark.unit
@pytest.mark.aurora
def test_t1_anchor_advances_state_correctly():
    """Test that T1 anchor advances state with valid data"""
    # Test implementation
```

**2. Follow AAA Pattern**
```python
def test_symbolic_engine_executes_chain():
    # Arrange
    engine = SymbolicEngine()
    start, end = 1, 3
    
    # Act
    results = engine.execute_chain(start, end)
    
    # Assert
    assert len(results) == 3
    assert all(isinstance(r, dict) for r in results)
```

**3. Use Appropriate Markers**
```python
@pytest.mark.integration  # Tests multiple components
@pytest.mark.aurora       # Tests aurora core
@pytest.mark.critical     # Must pass for production
async def test_api_health_endpoint_returns_status():
    """Integration test for health endpoint"""
    # Test implementation
```

**4. Mock External Dependencies**
```python
@pytest.mark.unit
def test_dlp_tracker_creates_tag(mocker):
    """Unit test with mocked file I/O"""
    mock_open = mocker.patch('builtins.open')
    tracker = DLPTracker()
    result = tracker.create_tag("test_context")
    assert result["success"]
    mock_open.assert_called_once()
```

## Test Coverage Goals

- **Unit Tests:** 80%+ coverage for core logic
- **Integration Tests:** Cover all major workflows
- **API Tests:** Cover all endpoints
- **Critical Path:** 100% coverage for security-sensitive code

## Continuous Testing

### Pre-Commit Hook
```bash
# Run critical tests before each commit
git config core.hooksPath .githooks
```

### VS Code Integration
Add to `.vscode/settings.json`:
```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests"
  ]
}
```

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

**Async Test Failures:**
```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

**Slow Test Suite:**
```bash
# Run only fast tests during development
pytest -m "unit and not slow"
```

## Chain Notation

**Test Execution Protocol:**
- `#TEST//UNIT//FAST_FEEDBACK//`
- `#TEST//INTEGRATION//COMPONENT_VALIDATION//`
- `#TEST//FULL_SUITE//RELEASE_VALIDATION//`

**DLP Context:**
- context_tag: "aurora_testing"
- All test runs tracked for quality metrics
- Ethics validation: Picard_Delta_3 ✅

## Assertion Patterns (anti-pattern: instantiation-only checks, #791)

`grep -rcE "assert.*is not None|assert hasattr" tests/` shows **333**
assertion lines fitting these shallow patterns across **61 files**. They
confirm an object was created or has an attribute — they do **not**
confirm behavior. A logic regression that produces a wrong-but-non-None
result still passes them.

### Anti-pattern

```python
# Avoid: confirms only that construction returned something.
result = orchestrator.run_scenario(...)
assert result is not None
assert hasattr(result, "objective_value")
```

### Replacement

```python
# Prefer: assert the behavior the test is named for.
result = orchestrator.run_scenario(...)
assert result.objective_value > 0, result
assert result.solution.is_feasible, result
# Use isinstance / type checks where shape matters
assert isinstance(result.iterations, int) and result.iterations >= 1
```

### Tier-1 modules (priority for cleanup)

Files with the highest hollow-assertion density — start here:

| File                                            | Hollow sites |
|-------------------------------------------------|--------------|
| `tests/test_quantum_core.py`                    | 34           |
| `tests/test_quantum_forge_v3.py`                | 27           |
| `tests/test_bridge_v2_basic.py`                 | 20           |
| `tests/test_thread_transfer_bridge_v2.py`       | 16           |
| `tests/test_subroutines_quick.py`               | 14           |
| `tests/test_mcp_consolidation.py`               | 13           |
| `tests/test_subroutines.py`                     | 12           |
| `tests/test_memory_retrieval_full.py`           | 12           |

Refresh this table by running:
```bash
for f in $(grep -rln "assert.*is not None\|assert hasattr" --include="*.py" tests/); do
  c=$(grep -cE "assert.*is not None|assert hasattr" "$f"); echo "$c $f";
done | sort -rn | head -20
```

### Progress tracking

`scripts/benchmark_scorecard.py` reports the total count under the
**Hollow assertion count** row. The target is **<100 in Tier 1
modules** (#791 acceptance criterion).

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Aurora CloudBank Architecture](../README.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
