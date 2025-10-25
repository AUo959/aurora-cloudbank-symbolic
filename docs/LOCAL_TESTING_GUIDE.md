# Local Testing Guide

## Quick Start

### Install Dependencies
```bash
# Install core dependencies (required for most tests)
pip3 install -r requirements.txt

# Verify installation
python3 -c "import fastapi, numpy, pandas, yaml; print('✅ Core deps installed')"
```

### Run Tests
```bash
# Fast stability check (lint + all tests)
make check

# Run all tests
make test

# Run specific test markers
pytest -m unit          # Fast unit tests only
pytest -m integration   # Integration tests
pytest -m "not slow"    # Skip slow tests
```

## Test Results

**Current Status (after dependency fix):**
- ✅ **206 tests passing** (out of 212 total)
- ⚠️ **6 failures** (data/config issues, not dependencies)
- ⏭️ **3 tests skipped** (PyTorch not installed - optional)

### Failures Breakdown

1. **Timestamp Test (1 failure)**
   - `tests/nexus/test_memory_manager.py::test_timestamp_recording`
   - Issue: Uses deprecated `datetime.utcnow()`, should use `datetime.now(datetime.UTC)`
   - Impact: Low (deprecation warning)

2. **CASK Tool Tests (3 failures)**
   - Missing data files: `CASK_A.tsv`, `Risks.tsv`, `SOTA.csv`
   - Tests: `test_load_specifications`, `test_load_risk_assessment`, `test_load_vs_sota`
   - Impact: Low (optional feature, needs data fixtures)

3. **Memory Compression (2 failures)**
   - `test_three_tier_memory`, `test_field_awareness_scaling`
   - Issue: Synapse compression logic, not PyTorch dependency
   - Impact: Medium (new feature from this session, needs validation)

## Optional Dependencies

### PyTorch (for Flash Attention)
```bash
# Install PyTorch (2+ GB download)
pip3 install torch>=2.0.0

# Verify
python3 -c "import torch; print(f'✅ PyTorch {torch.__version__}')"
```

**What changes with PyTorch:**
- 3 skipped tests in `test_memory_compression.py` will run
- Flash Attention features enabled (field awareness scaling)
- Memory compression validated

Without PyTorch, the system gracefully falls back to standard attention.

## CI vs Local Testing

### CI (GitHub Actions)
- **Goal**: Fast validation (< 5 minutes)
- **Dependencies**: Minimal (flake8, pytest only)
- **Tests**: Syntax check, basic structure validation
- **Philosophy**: Catch breaking changes, not enforce perfection

### Local (Developer Machine)
- **Goal**: Complete validation
- **Dependencies**: Full requirements.txt
- **Tests**: All 212 tests including integration
- **Philosophy**: Comprehensive validation before push

## Makefile Targets

```bash
make check        # Fast: scoped lint (tools/) + full tests
make test         # Run complete test suite
make lint-tools   # Lint modernized tools (matches CI scope)
make lint-all     # Broad lint (may surface legacy issues)
```

## Test Markers

Tests are organized with pytest markers:

**Speed-based:**
- `@pytest.mark.unit` - Fast unit tests (< 1 second)
- `@pytest.mark.integration` - Integration tests (1-10 seconds)
- `@pytest.mark.slow` - Slow tests (> 10 seconds)

**Component-based:**
- `@pytest.mark.aurora` - Aurora core system
- `@pytest.mark.quantum` - Quantum processing
- `@pytest.mark.security` - Security & auth
- `@pytest.mark.api` - API endpoints

**Run selectively:**
```bash
pytest -m unit              # Fast tests only
pytest -m "not slow"        # Skip slow tests
pytest -m "api or security" # API and security tests
```

## Troubleshooting

### Import Errors
```bash
# Check installed packages
pip3 list | grep -E "fastapi|numpy|pandas|pyyaml"

# Reinstall if missing
pip3 install -r requirements.txt
```

### Test Collection Errors
```bash
# Try with verbose output
pytest tests/ -v --tb=short

# Check specific file
python3 -c "import tests.test_file_name"
```

### Virtual Environment Issues
```bash
# Check Python version
python3 --version  # Should be 3.12+

# Check pip version
pip3 --version

# Check site-packages location
python3 -c "import site; print(site.getsitepackages())"
```

## Best Practices

1. **Before committing**: Run `make check` (lint + tests)
2. **After pulling**: Run `pip3 install -r requirements.txt` (update deps)
3. **When adding features**: Add tests with appropriate markers
4. **For CI**: Keep minimal workflow fast, validate locally for comprehensive check

## Integration with CI Fix

This guide complements `docs/CI_WORKFLOW_FIX.md`:
- **CI**: Fast syntax validation (no heavy deps)
- **Local**: Complete functional validation (full deps)
- **Both**: Catch issues at different stages

The two-tier strategy ensures:
- Fast feedback on syntax/structure (CI)
- Thorough validation before merge (local)
- No CI timeouts from heavy dependencies

---

**Thread: T1→T8→T9→INFINITE**  
**DLP: context_tag=local_testing_guide, symbolic_hash=VALIDATION_WORKFLOW_v1**
