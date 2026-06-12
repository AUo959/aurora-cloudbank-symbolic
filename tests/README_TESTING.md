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

## Assertion Quality Guidelines

Behavioral tests should prove that an object works, not just that it exists. Assertions like
`assert X is not None` and `assert hasattr(obj, "field")` are weak in most unit and integration
tests because a broken object can still instantiate and expose attributes while returning the wrong
state, the wrong values, or the wrong side effects.

Prefer assertions that exercise the object under test and verify a concrete outcome:
- returned field values
- state updates on the object
- collection contents
- serialized output
- observable side effects

### Before/after examples from Tier 1 tests

**Example 1 — manager/anchor behavior**
```python
# Before (tests/test_quantum_core.py)
result = anchor.anchor_quantum_symbolic_state(test_data)
assert result is not None

# After
result = anchor.anchor_quantum_symbolic_state(test_data)
assert set(result) == {"quantum_anchor", "symbolic_anchor", "hybrid_coordination"}
```

**Example 2 — generated model behavior**
```python
# Before (tests/test_quantum_forge_v2.py)
agent = forge.generate_agent(...)
assert agent is not None

# After
agent = forge.generate_agent(...)
assert agent.metadata["purpose"] == "Research agent"
```

**Example 3 — subsystem wiring behavior**
```python
# Before (tests/test_monitoring_system.py)
monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
assert monitoring.audit_logger is not None

# After
monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
assert monitoring.audit_logger.storage_path == Path(tmpdir) / "audit_log.jsonl"
```

## Good assertion patterns

### Managers
Call a method and verify the returned state or stored side effect.
```python
result = anchor.anchor_quantum_symbolic_state({"test": "data"})
assert result["symbolic_anchor"]["logical_consistency_verified"] is True
```

### Dataclasses
Assert a specific field value instead of mere existence.
```python
verdict = EthicsVerdict(allowed=True, score=0.85, reason="ok", engine="gumas")
assert verdict.score == 0.85
```

### Collections
Assert length, membership, or an element property.
```python
top_memories = memory_enhancer.retrieve_by_priority(top_k=2)
assert len(top_memories) <= 2
```

### Strings
Assert content, structure, or parsing behavior.
```python
channel = flowstate.create_flow_channel("agent_001", "BridgeAgent")
assert channel.split("::")[1:3] == ["agent_001", "BridgeAgent"]
```

## When instantiation checks are acceptable

Instantiation-only assertions are acceptable in narrowly scoped smoke tests where the explicit goal
is “import/construct without crashing,” or in compatibility checks that intentionally guard optional
dependencies. Label those tests clearly as smoke/setup coverage, and use `# noqa: shallow-ok` for
rare cases where a shallow assertion is still the right tool.

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

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Aurora CloudBank Architecture](../README.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
