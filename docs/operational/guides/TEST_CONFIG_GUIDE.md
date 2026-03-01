# Aurora CloudBank Test Configuration Guide

## 🧪 Test Environment Setup

### **Requirements Installed:**

- `pytest>=7.0.0` - Core testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `pytest-asyncio>=0.21.0` - Async test support
- `coverage>=7.0.0` - Coverage analysis

### **Test Configuration:**

- Configuration file: `pyproject.toml`
- Test directory: `tests/`
- Markers configured for selective testing

## 🚀 Running Tests

### **Quick Commands:**

```bash
# Native implementation tests (fastest)
./run_tests.sh native

# Quick validation (native + smoke tests)
./run_tests.sh quick

# Complete test suite
./run_tests.sh all

# Performance benchmarks
./run_tests.sh benchmark
```

### **Python Test Runner:**

```bash
# Individual test types
python3 test_runner.py native
python3 test_runner.py unit
python3 test_runner.py smoke
python3 test_runner.py api
python3 test_runner.py benchmark
python3 test_runner.py all
```

### **Direct pytest:**

```bash
# Run specific test file
pytest tests/test_native_implementations.py -v

# Run tests by marker
pytest -m native -v
pytest -m "unit and smoke" -v

# Run with coverage (when enabled)
pytest --cov=src --cov-report=html
```

## 📋 Test Markers

### **Speed-based markers:**

- `@pytest.mark.unit` - Fast unit tests (< 1 second)
- `@pytest.mark.integration` - Integration tests (1-10 seconds)
- `@pytest.mark.slow` - Slow tests (> 10 seconds)
- `@pytest.mark.smoke` - Critical smoke tests

### **Component-based markers:**

- `@pytest.mark.native` - Native implementation tests
- `@pytest.mark.opal2` - Opal2 modular system tests
- `@pytest.mark.aurora` - Aurora core system tests
- `@pytest.mark.quantum` - Quantum processing tests
- `@pytest.mark.api` - API and web interface tests

### **Environment markers:**

- `@pytest.mark.local` - Local development only
- `@pytest.mark.ci` - CI/CD pipeline tests
- `@pytest.mark.network` - Network access required

### **Priority markers:**

- `@pytest.mark.critical` - Must-pass for production
- `@pytest.mark.regression` - Regression prevention
- `@pytest.mark.performance` - Performance benchmarks

## ✅ Test Status

### **Native Implementation Tests:**

- **Total tests:** 24
- **Status:** ✅ All passing
- **Coverage:** VSA, Quantum, Symbolic Anchors
- **Performance:** ~0.18 seconds

### **Key Test Classes:**

1. `TestNativeVSA` - Vector Symbolic Architecture
2. `TestNativeQuantum` - Quantum simulation
3. `TestNativeSymbolicAnchor` - Symbolic anchoring
4. `TestPerformanceOptimizations` - Performance validation

## 🎯 Performance Results

### **Benchmark Summary:**

- **Native operations:** 0.21 seconds
- **Import speedup:** 6300x faster than heavy dependencies
- **Memory reduction:** 84x less memory usage
- **Zero external dependencies:** ✅

### **Test Execution Speed:**

- Native tests: ~0.18 seconds (24 tests)
- Performance benchmark: ~0.21 seconds
- Total validation time: < 1 second

## 🔧 Troubleshooting

### **Common Issues:**

1. **Import errors:** Ensure `PYTHONPATH` includes project root
2. **Missing pytest:** Run `pip install pytest pytest-cov`
3. **Slow tests:** Use markers to run subset: `pytest -m "unit and not slow"`

### **Configuration Files:**

- `pyproject.toml` - Main pytest configuration
- `test_runner.py` - Python test orchestration
- `run_tests.sh` - Shell script wrapper
- `requirements.txt` - Test dependencies

## 📊 Coverage

Coverage reporting is configured but simplified for this optimized environment:

- Focus on critical native implementations
- Coverage threshold: 50% minimum
- HTML reports generated in `htmlcov/`

## 🚀 CI/CD Integration

Test markers support CI/CD pipeline optimization:

```bash
# Quick CI validation
pytest -m "smoke and critical" --tb=short

# Full CI suite
pytest -m "not slow" --tb=short

# Performance validation
python3 performance_benchmark.py
```
