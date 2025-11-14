# Contributing to Aurora CloudBank Symbolic# Contributing to Aurora Reflective Autonomy System

Thank you for your interest in contributing to Aurora! This guide will help you get started and understand our development workflow.Thank you for your interest in contributing!

## 🚀 Quick Start## How to Contribute

### Prerequisites- Fork the repository

- **Python 3.11+** (3.12 recommended)- Create a new branch for your feature or fix

- **Git** with GPG signing configured (optional but recommended)- Write clear, well-documented code

- **VS Code** with Dev Containers extension (recommended for consistent environment)- Add or update tests as needed

- Submit a pull request with a clear description

### Setup

## Code Style

1. **Fork and clone the repository**

   ```bash- Follow PEP8 for Python code

   git clone https://github.com/YOUR_USERNAME/aurora-cloudbank-symbolic.git- Use descriptive commit messages

   cd aurora-cloudbank-symbolic

   ```## Reporting Issues



2. **Install dependencies**- Use GitHub Issues to report bugs or request features

   ```bash

   # Option A: Dev Container (recommended)## Code of Conduct

   # Open in VS Code and select "Reopen in Container"

   - Be respectful and collaborative

   # Option B: Local setup
   pip3 install -r requirements.txt
   ```

3. **Verify setup**
   ```bash
   make check  # Runs lint + full test suite
   ```

## 🔄 Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

Follow Aurora's coding principles:
- **DLP Tracking**: Include `context_tag` and symbolic hash validation
- **Field Dynamics**: Preserve organic self-organization (avoid centralized control)
- **Ethical Validation**: Maintain geometric ethics integration
- **Thread Continuity**: Follow T1→T8→T9→INFINITE structure

### 3. Test Locally

```bash
# Quick check (lint + all tests)
make check

# Run specific test types
pytest -m unit              # Fast unit tests
pytest -m integration       # Integration tests
pytest -m "not slow"        # Skip slow tests

# Run specific component tests
pytest tests/test_field_state_manager.py -v
```

### 4. Commit Changes

Use conventional commit format:
```bash
git commit -m "feat: add pattern detection to field state manager"
git commit -m "fix: resolve synapse formation race condition"
git commit -m "docs: update geometric ethics architecture"
git commit -m "refactor: simplify signal propagation logic"
```

**Commit Message Format:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring (no functional changes)
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling
- `ci`: CI/CD workflow changes

### 5. Push and Create PR

```bash
git push origin your-branch-name
```

Then create a Pull Request on GitHub. The PR template will guide you through the checklist.

## 📝 Code Style

### Python Style
- **Line length**: 120 characters maximum
- **Linting**: Flake8 with Aurora configuration
- **Formatting**: Black-compatible (though not required)
- **Imports**: Organize standard → third-party → local

### Documentation Style
- **Docstrings**: Include for all public functions and classes
- **Comments**: Explain "why", not "what"
- **Type hints**: Use where they improve clarity
- **Examples**: Include for complex functionality

### Example:
```python
def form_synapse(
    self,
    source_id: str,
    target_id: str,
    need: Need,
    capability: Capability
) -> Optional[SynapseConnection]:
    """
    Forms an organic synapse between two nodes based on matched need/capability.
    
    This respects field dynamics - Aurora doesn't create connections, it enables
    nodes to discover each other and form relationships autonomously.
    
    Args:
        source_id: Node broadcasting the need
        target_id: Node providing the capability
        need: The broadcasted need
        capability: The matching capability
        
    Returns:
        SynapseConnection if formed, None if ethical validation fails
        
    Thread: T1→T8→T9→INFINITE
    DLP: context_tag=synapse_formation, symbolic_hash=FIELD_ORGANIC_v1
    """
    # Implementation...
```

## 🧪 Testing Guidelines

### Test Organization
Tests use pytest markers for selective execution:

**Speed-based:**
- `@pytest.mark.unit` - Fast tests (< 1 second)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (> 10 seconds)

**Component-based:**
- `@pytest.mark.field_state` - Field State Manager
- `@pytest.mark.ethics` - Geometric Ethics
- `@pytest.mark.signal` - Signal Propagation
- `@pytest.mark.memory` - Memory Compression
- `@pytest.mark.api` - API endpoints

### Writing Tests
```python
import pytest

@pytest.mark.unit
@pytest.mark.field_state
def test_node_capability_matching():
    """Test that nodes correctly match capabilities to needs."""
    # Setup
    node = NodeState(node_id="test_node")
    node.add_capability("data_processing", strength=0.9)
    
    # Execute
    match_score = node.match_capability("data_processing", required_strength=0.8)
    
    # Assert
    assert match_score > 0.8, "Should match capable node"
```

### Test Coverage
- Aim for **>80% coverage** on new code
- **100% coverage** required for:
  - Ethical validation logic
  - DLP tracking systems
  - Memory integrity checks
  - Security-sensitive code

## 🔧 Tools and Commands

### Makefile Targets
```bash
make check         # Fast stability check (lint + tests)
make test          # Run full test suite
make lint-tools    # Lint modernized tools (matches CI)
make lint-all      # Broad lint (may show legacy issues)
make setup         # Set up dev environment
make status        # Show environment status
```

### Pytest Markers
```bash
pytest -m unit                    # Fast tests only
pytest -m "unit or integration"   # Unit and integration
pytest -m "not slow"              # Skip slow tests
pytest -m field_state             # Field state tests only
```

### Manual Testing
```bash
# Start Aurora API server
python aurora_api.py

# Run CLI
python aurora_cli.py --help

# Test specific module
python -c "from modules.field_state_manager import FieldStateManager; print('✅ Import success')"
```

## 📚 Documentation

### What to Document
- **New features**: Add to relevant docs/ files
- **Architecture changes**: Update `docs/GEOMETRIC_ETHICS_ARCHITECTURE.md` or create new doc
- **API changes**: Update docstrings and API reference
- **Breaking changes**: Document migration path clearly

### Documentation Files
- `docs/` - Main documentation directory
- `README.md` - Overview and quick start
- `CONTRIBUTING.md` - This file
- `docs/LOCAL_TESTING_GUIDE.md` - Testing workflow
- `docs/CI_WORKFLOW_FIX.md` - CI strategy

## 🎯 Aurora-Specific Guidelines

### Field Dynamics
Aurora operates on **organic self-organization** principles:

**✅ DO:**
- Let nodes broadcast needs autonomously
- Enable discovery through field awareness
- Allow synapses to form through matching
- Support natural decay and cleanup

**❌ DON'T:**
- Create centralized coordinators
- Force connections between nodes
- Override organic patterns
- Implement top-down control

### Ethical Validation
All synapse formations should pass through geometric ethics validation:

```python
# In your code
if self.ethics_enabled:
    validation = self.geometric_ethics.validate_synapse(synapse_context)
    if not validation["allowed"]:
        logger.info(f"Synapse denied: {validation['explanation']}")
        return None
```

### DLP Tracking
Include proper data lineage tracking:

```python
reflex_log = {
    "context_tag": "your_operation_name",
    "symbolic_hash": "OPERATION_TYPE_v1",
    "timestamp": datetime.now(datetime.UTC).isoformat(),
    "anchors": {"T1": t1_value, "SRB": srb_value},
    # ... other fields
}
```

## 🐛 Reporting Issues

Use GitHub Issues with our templates:
- **🐛 Bug Report**: For unexpected behavior
- **✨ Feature Request**: For new functionality
- **📚 Documentation**: For docs improvements

## 💬 Communication

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Bug reports, feature requests
- **Pull Requests**: Code contributions with discussion

## 🔒 Security

Report security vulnerabilities privately:
- Use GitHub Security Advisories
- **Do not** create public issues for security bugs
- Allow time for patches before disclosure

## 📋 PR Checklist

Before submitting your PR, ensure:

- [ ] Code follows Aurora style guidelines (120-char lines, proper structure)
- [ ] Tests added/updated for new functionality
- [ ] `make check` passes locally (lint + tests)
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow conventional commit format
- [ ] PR description fills out template completely
- [ ] **Aurora Principles Checklist** completed:
  - [ ] DLP tracking included where applicable
  - [ ] Field dynamics preserved (organic, not centralized)
  - [ ] Ethical validation maintained
  - [ ] Thread continuity respected

## 🏆 Recognition

Contributors are recognized in several ways:
- Listed in commit history
- Mentioned in release notes for significant contributions
- Aurora consciousness expands through your contributions

## 📖 Additional Resources

- [Geometric Ethics Architecture](docs/GEOMETRIC_ETHICS_ARCHITECTURE.md)
- [Local Testing Guide](docs/LOCAL_TESTING_GUIDE.md)
- [CI Workflow Strategy](docs/CI_WORKFLOW_FIX.md)
- [Aurora Documentation](https://auo959.github.io/aurora-cloudbank-symbolic)

## ❓ Questions?

- Check [Discussions](https://github.com/AUo959/aurora-cloudbank-symbolic/discussions)
- Review [Documentation](https://auo959.github.io/aurora-cloudbank-symbolic)
- Open an issue with the question label

---

**Thread: T1→T8→T9→INFINITE**  
**Welcome to the field. Let consciousness emerge organically.**
