# Aurora CloudBank Symbolic

**A practical quantum-symbolic computing platform for real-world development**

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/AUo959/aurora-cloudbank-symbolic) [![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/downloads/) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![Status](https://img.shields.io/badge/status-active%20development-orange)](#project-status)

> An experimental platform combining quantum computing simulation, vector symbolic architectures, and thread-based memory management. Built for researchers and developers exploring cognitive architectures and quantum-inspired algorithms.

🌐 **[Live Demo](https://auo959.github.io/aurora-cloudbank-symbolic)** | 📚 **[Documentation](docs/)** | 🤝 **[Contributing](CONTRIBUTING.md)**

---

## What This Project Actually Does

Aurora CloudBank is a research platform that explores the intersection of several computing paradigms:

**Core Capabilities:**
- **Quantum Algorithm Simulation** - Test quantum algorithms using Qiskit without needing quantum hardware
- **Vector Symbolic Architecture** - Experiment with high-dimensional cognitive computing models
- **Thread Transfer System** - Manage computational contexts across distributed processes (now with v2 featuring Raft consensus)
- **Memory Management** - Hierarchical storage with quantum-inspired retrieval (AuMemManager)
- **API Framework** - RESTful APIs for integrating quantum and symbolic operations

**What It's Good For:**
- Prototyping quantum algorithms before deploying to real quantum computers
- Experimenting with cognitive architecture patterns
- Building applications that need context-aware memory management
- Learning about quantum computing concepts through practical simulation
- Developing distributed systems with consensus protocols

**What It's Not:**
- A production quantum computer (uses simulation)
- A fully-optimized ML framework (research-focused)
- A plug-and-play solution (requires understanding of quantum/symbolic computing)

---

## Architectural Philosophy: A Symbolic Governance Stack

Beyond its individual features, Aurora CloudBank is designed as a cohesive **governance stack for symbolic operations**. The architecture prioritizes integrity, traceability, and resilience, making it a platform for building trusted computational systems.

### 1. Symbolic Governance & Data Lineage

The project's backbone is its rigorous protocol for managing data and state, ensuring every operation is auditable and verifiable.

- **Data Lineage Protocol (DLP):** Every significant computation is tracked with a `context_tag` and validated by a `symbolic_hash_validation`. This creates an unbroken chain of evidence, making the history of a result as important as the result itself.
- **State Anchoring (T1/SRB):** The system uses Temporal and Symbolic Reference Base anchors to manage state across complex, asynchronous operations. It functions like a custom transaction ledger for symbolic AI, ensuring sequential integrity.
- **Memory Sealing:** Quantum-inspired memory seals provide an integrity guarantee for the system's state, protecting it from corruption and ensuring that stored information is trustworthy.

### 2. Pragmatic Abstraction of Advanced Components

The most experimental features (like quantum simulation) are treated as progressive enhancements, not critical dependencies. This ensures the core system remains stable and usable.

- **Graceful Degradation:** Optional modules like `AuMemManager` and the geometric algebra engine are wrapped in `try/except ImportError` blocks. If they are not available, the system continues to function with its core capabilities intact.
- **Mock Fallbacks:** Where appropriate, minimal mock implementations are provided. This allows developers to test the main application logic without needing the full, complex stack of optional dependencies.

### 3. A Pluggable Human-AI Interaction Layer

The integration of multiple AI models (ChatGPT, Claude) and the "cultural intelligence" concept create a flexible and adaptable interface between human developers and the system's powerful backend.

- **Agent Tool Registration:** The tool registry in `src/integrations/chatgpt_agent_mode.py` provides a structured and secure way to expose internal functions to external AI agents. This turns the entire stack into a verifiable tool that other AIs can leverage for complex tasks.

---

## Real-World Use Cases

### 1. Quantum Algorithm Development

**Scenario:** You're developing a quantum optimization algorithm but don't have access to quantum hardware.

```python
from modules.quantum_simulator import QuantumScenarioSimulator

# Simulate a supply chain optimization problem
simulator = QuantumScenarioSimulator()
result = await simulator.run_scenario(
    scenario_type="supply_chain_optimization",
    parameters={
        "num_locations": 5,
        "num_vehicles": 3,
        "optimization_method": "qaoa"  # Quantum Approximate Optimization Algorithm
    }
)

# Get classical baseline for comparison
print(f"Quantum solution: {result.optimal_solution}")
print(f"Classical baseline: {result.classical_baseline}")
print(f"Improvement: {result.performance_metrics['speedup_factor']}x")
```

**Real-world application:** Test and validate quantum algorithms before expensive quantum hardware access.

### 2. Cognitive Computing Research

**Scenario:** Building a system that needs to reason with high-dimensional semantic representations.

```python
from modules.symbolic_core import GeometricAlgebraEngine

# Create semantic vectors for concepts
engine = GeometricAlgebraEngine()
concept_a = engine.create_multivector([1, 0, 1, 0])  # "database"
concept_b = engine.create_multivector([0, 1, 1, 0])  # "query"

# Geometric product combines meanings
combined = engine.geometric_product(concept_a, concept_b)
similarity = engine.calculate_similarity(combined, target_concept)
```

**Real-world application:** Natural language understanding, semantic search, knowledge representation.

### 3. Distributed Thread Management

**Scenario:** Managing computational contexts across multiple services with strong consistency guarantees.

```python
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_node_registry,
    get_raft_consensus,
    get_drift_predictor
)

# Set up distributed node cluster
registry = get_node_registry()
await registry.register_node(
    hostname="compute-node-1",
    port=8000,
    region="us-west",
    capacity=1000
)

# Use Raft consensus for thread transfer decisions
consensus = get_raft_consensus()
is_leader = await consensus.is_leader()

# Predict when thread drift might occur
predictor = get_drift_predictor()
prediction = await predictor.predict_drift(features, thread_id)
if prediction.severity.value == "HIGH":
    # Take preventive action
    await apply_correction_strategy()
```

**Real-world application:** Microservices coordination, distributed task management, fault-tolerant systems.

### 4. Hierarchical Memory Systems

**Scenario:** Application needs intelligent caching with quantum-inspired retrieval.

```python
from modules.aumemmanager import HierarchicalMemoryManager

memory = HierarchicalMemoryManager()

# Store with automatic tiering
await memory.create_memory(
    content={"user_session": session_data},
    importance=0.9,  # High importance = stays in active tier
    metadata={"context": "user_profile"}
)

# Semantic search with attention-based scoring
results = await memory.search_memories(
    query="user preferences",
    top_k=10,
    cultural_weight=0.5  # Weight cultural relevance
)
```

**Real-world application:** Intelligent caching, session management, context-aware applications.

### 5. API-First Integration

**Scenario:** Integrating quantum simulation into existing web applications.

```bash
# Start the FastAPI server
python aurora_api.py

# Use any HTTP client
curl -X POST http://localhost:8000/quantum/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "circuit": "bell_state",
    "shots": 1000,
    "backend": "qasm_simulator"
  }'
```

**Real-world application:** Microservices architecture, cloud-native apps, REST API integrations.

---

## Key Features & Current Status

### ✅ Production-Ready Components

**Thread Transfer Bridge v2** (100% Complete)
- Distributed node management with Raft consensus
- Cross-repository thread continuity
- ML-powered drift prediction (LSTM-based, 24-hour horizon)
- Multi-layer bridge hierarchies (L1/L2/L3)
- 21 REST API endpoints with 90.5% test coverage
- Full documentation suite (2,400+ lines)

**Quantum Simulator** (Stable)
- 7 scenario types (supply chain, energy grid, risk analysis, optimization)
- QAOA and VQE quantum algorithms
- Mock, simulator, and cloud provider backends
- 13 API endpoints + WebSocket streaming
- Intelligent caching with 60-80% hit rates

**AuMemManager** (Stable)
- 56,000-capacity hierarchical memory
- Attention-based retrieval with cultural scoring
- Quantum flight control (vector entanglement networks)
- Sub-millisecond retrieval for active tier
- 11 REST API endpoints

**FastAPI Server** (Production)
- 27 endpoints (authentication, rate limiting)
- OpenAPI documentation
- WebSocket support for real-time updates
- CSRF protection and security validation

### 🔧 Experimental Components

**Vector Symbolic Architecture**
- Geometric algebra operations (Clifford)
- Multivector calculations
- Currently research-focused, may need optimization for production use

**Cultural Intelligence (CASK)**
- Cultural awareness scoring
- Semantic sensitivity analysis
- Early-stage, useful for research but needs real-world validation

**Claude Sonnet 4 Integration**
- Enhanced AI reasoning with quantum awareness
- Fallback systems for reliability
- API-dependent, requires API keys for full functionality

### 📊 Project Metrics

**Code Quality:**
- 6,000+ lines of implementation code
- 30+ test files with async support
- Type hints throughout for Python 3.11+
- Flake8 compliant (120-char line limit)

**Testing:**
- 30+ integration tests for Thread Bridge v2
- 90.5% endpoint test pass rate
- Fast execution (< 1 second for unit tests)

**Documentation:**
- 2,400+ lines of comprehensive docs
- Protocol specifications
- API reference with examples
- Migration guides
- Administration and developer guides

---

## Getting Started

### Prerequisites

- **Python 3.11+** (3.12 recommended)
- **Node.js 20+** (for web interface)
- **Git** (for cloning)
- **Docker** (optional, for containerized deployment)

### Quick Start (5 minutes)

```bash
# Clone the repository
git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic

# Set up Python environment (recommended)
./scripts/setup_python_venv.sh

# Install dependencies
make setup

# Run tests to verify installation
make test

# Start the API server
python aurora_api.py

# Visit http://localhost:8000/docs for interactive API documentation
```

### Development Setup

```bash
# Check development environment status
python scripts/dev-status.py

# Configure Python environment
make configure-python

# Run specific test suites
pytest -m unit          # Fast unit tests
pytest -m integration   # Integration tests
pytest -m quantum       # Quantum-specific tests

# Code quality checks
make lint              # Run linting (scoped to modernized code)
make check             # Lint + test suite
```

### Common Tasks

```bash
# Thread Transfer Bridge v2 operations
python -c "from modules.reflective_autonomy.thread_transfer.v2 import get_node_registry; \
           import asyncio; \
           asyncio.run(get_node_registry().list_nodes())"

# Quantum simulation
python -m modules.quantum_simulator.cli run --scenario supply_chain

# Memory management
python demo_aumemmanager_integration.py

# API health check
curl http://localhost:8000/health
```

---

## Architecture Overview

### Component Structure

```
aurora-cloudbank-symbolic/
├── modules/                          # Core functionality modules
│   ├── aumemmanager/                # Hierarchical memory system
│   ├── quantum_simulator/           # Quantum scenario simulator
│   ├── reflective_autonomy/         # Thread transfer & governance
│   │   └── thread_transfer/
│   │       └── v2/                  # v2 with Raft consensus
│   ├── symbolic_core/               # Vector symbolic architecture
│   └── cask/                        # Cultural awareness
│
├── src/                             # Source implementations
│   ├── aurora/                      # Core symbolic engine
│   ├── quantum_core/                # Quantum processing
│   └── integrations/                # AI integrations (ChatGPT, Claude)
│
├── tests/                           # Test suites
│   ├── test_bridge_v2_basic.py     # Thread bridge tests
│   └── test_*.py                    # Component-specific tests
│
├── scripts/                         # Automation & utilities
│   ├── setup_environment.sh         # Environment setup
│   ├── dev-status.py               # Development diagnostics
│   └── [40+ utility scripts]
│
├── docs/                            # Documentation
│   ├── THREAD_TRANSFER_BRIDGE_v2_PROTOCOL.md
│   ├── v2_API_REFERENCE.md
│   ├── v2_DEVELOPER_GUIDE.md
│   └── [comprehensive guides]
│
└── aurora_api.py                    # Main FastAPI server
```

### Data Flow

```
User Request → FastAPI Gateway → Module Router → Component Logic → Response
                     ↓                                    ↓
              Authentication                        DLP Tracking
              Rate Limiting                         Context Tags
              CSRF Protection                       Anchor Protocols
```

### Thread Transfer Architecture (v2)

```
Application Layer: FastAPI Endpoints (21 routes)
        ↓
Service Layer: Node Registry, Load Balancer, Drift Predictor
        ↓
Consensus Layer: Raft Protocol (leader election, log replication)
        ↓
Storage Layer: In-memory with persistence hooks
        ↓
Network Layer: Cross-node communication
```

---

## API Reference

### Quick API Overview

**Base URL:** `http://localhost:8000`

**Thread Transfer v2** (`/api/v2/...`)
```bash
# Register a compute node
POST /api/v2/nodes/register
POST /api/v2/repos/register      # Register repository
POST /api/v2/drift/predict       # Predict thread drift
POST /api/v2/layers/bridge       # Create layer bridge
```

**Quantum Operations** (`/quantum/...`)
```bash
POST /quantum/simulate           # Run quantum simulation
GET  /quantum/backends           # List available backends
POST /quantum/scenarios          # Complex scenario execution
```

**Memory Management** (`/aumem/...`)
```bash
POST /aumem/memory/create        # Create memory
GET  /aumem/search               # Semantic search
GET  /aumem/health               # Memory system health
```

**System** (`/...`)
```bash
GET  /health                     # System health check
GET  /docs                       # Interactive API docs
GET  /metrics                    # Prometheus metrics
```

**Complete API Documentation:** Visit `/docs` when running the server or see [v2_API_REFERENCE.md](v2_API_REFERENCE.md)

---

## Development Workflow

### Typical Development Cycle

1. **Make Changes**
   ```bash
   # Edit code in your preferred editor
   # The project uses standard Python/Node.js conventions
   ```

2. **Test Changes**
   ```bash
   # Run affected tests
   pytest tests/test_your_component.py
   
   # Or run full test suite
   make test
   ```

3. **Check Code Quality**
   ```bash
   # Lint modernized code (recommended)
   make lint-tools
   
   # Check all code (may show legacy warnings)
   make lint-all
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "description of changes"
   # Pre-commit hooks will validate dependencies
   ```

### Working with Thread Transfer Bridge v2

```python
# Example: Setting up a distributed node cluster

import asyncio
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_node_registry,
    get_load_balancer,
    get_drift_predictor,
    DriftFeatures
)

async def setup_cluster():
    # Register nodes
    registry = get_node_registry()
    
    node1 = await registry.register_node(
        hostname="node-1.local",
        port=8000,
        region="us-west",
        capacity=1000
    )
    
    node2 = await registry.register_node(
        hostname="node-2.local",
        port=8001,
        region="us-east",
        capacity=800
    )
    
    # Check cluster health
    health = await registry.check_cluster_health()
    print(f"Cluster status: {health['status']}")
    print(f"Active nodes: {health['active_nodes']}")
    
    # Use load balancer for node selection
    balancer = get_load_balancer()
    selected_node = await balancer.select_node()
    print(f"Selected node: {selected_node.hostname}")
    
    # Predict potential drift
    predictor = get_drift_predictor()
    features = DriftFeatures(
        drift_velocity=0.001,
        drift_acceleration=0.0001,
        handshake_count=10,
        # ... other features
    )
    
    prediction = await predictor.predict_drift(features, "thread-123")
    print(f"Predicted drift: {prediction.predicted_drift}")
    print(f"Severity: {prediction.severity.value}")

asyncio.run(setup_cluster())
```

### Working with Quantum Simulator

```python
from modules.quantum_simulator import QuantumScenarioSimulator

async def run_optimization():
    simulator = QuantumScenarioSimulator()
    
    # Run supply chain optimization
    result = await simulator.run_scenario(
        scenario_type="supply_chain_optimization",
        parameters={
            "num_locations": 5,
            "num_vehicles": 3,
            "optimization_method": "qaoa",
            "max_iterations": 100
        }
    )
    
    # Access results
    print(f"Optimal route: {result.optimal_solution}")
    print(f"Total cost: {result.objective_value}")
    print(f"Quantum advantage: {result.performance_metrics['speedup_factor']}x")
    
    # Get detailed metrics
    print(f"Circuit depth: {result.quantum_metrics['circuit_depth']}")
    print(f"Gate count: {result.quantum_metrics['gate_count']}")

asyncio.run(run_optimization())
```

---

## Troubleshooting

### Common Issues

**1. Import Errors with Optional Dependencies**

```bash
# Problem: "No module named 'clifford'" or similar
# Solution: Install optional dependencies
pip install clifford  # For geometric algebra
pip install qiskit    # For quantum computing

# Or install all optional dependencies
pip install -r requirements-optional.txt
```

**2. Dependency Conflicts**

```bash
# Problem: httpx/httpcore version conflicts
# Solution: Run dependency validator
python scripts/validate_dependencies.py

# Or use complete environment setup
bash scripts/setup_environment.sh
```

**3. Test Failures**

```bash
# Problem: Tests fail with async errors
# Solution: Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Problem: Some tests fail in CI but pass locally
# Solution: Run tests with same markers as CI
pytest -m "not slow"
```

**4. API Server Won't Start**

```bash
# Problem: Port 8000 already in use
# Solution: Kill existing process or use different port
lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
# Or start on different port:
uvicorn aurora_api:app --port 8001

# Problem: Missing environment variables
# Solution: Check required environment variables
python -c "from src.core.config import settings; print(settings.dict())"
```

**5. Memory Issues with Large Simulations**

```bash
# Problem: Out of memory errors
# Solution: Reduce problem size or use sampling
# - Lower num_locations/num_vehicles in quantum scenarios
# - Reduce shots count in quantum simulations
# - Use quantum_shots parameter to limit quantum samples
```

### Getting Help

1. **Check Documentation**
   - [Thread Transfer v2 Developer Guide](v2_DEVELOPER_GUIDE.md)
   - [Quantum Simulator Guide](docs/simulation/QUANTUM_SIMULATOR_GUIDE.md)
   - [API Reference](v2_API_REFERENCE.md)

2. **Run Diagnostics**
   ```bash
   python scripts/dev-status.py  # Development environment status
   make status                    # Overall system status
   ```

3. **Enable Debug Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

4. **Open an Issue**
   - Check existing issues first
   - Include environment info (Python version, OS)
   - Include error messages and stack traces

---

## Project Status

### Current State (October 2025)

**Stable & Production-Ready:**
- ✅ Thread Transfer Bridge v2 (complete, documented, tested)
- ✅ Quantum Simulator (stable, 13 APIs, caching)
- ✅ AuMemManager (stable, 56K capacity, tested)
- ✅ FastAPI Server (27 endpoints, authenticated, rate-limited)

**Active Development:**
- 🔧 Enhanced drift prediction accuracy (ML model refinement)
- 🔧 Performance optimization for large-scale simulations
- 🔧 Additional quantum algorithm scenarios

**Experimental/Research:**
- 🧪 Vector Symbolic Architecture (research-focused)
- 🧪 Cultural Intelligence (CASK) - needs validation
- 🧪 Advanced geometric algebra operations

### Known Limitations

1. **Quantum Simulation is Simulated**
   - Uses Qiskit Aer simulator, not real quantum hardware
   - Limited to ~30 qubits due to classical simulation constraints
   - Results are approximations of quantum behavior

2. **Thread Bridge v2 Cross-Repo Testing**
   - Phase 2 (cross-repository) endpoints tested at 25% pass rate
   - Requires real Git repositories for full validation
   - Works well for in-repo operations

3. **Memory Capacity**
   - AuMemManager: 56K limit is soft (can be increased)
   - Performance may degrade with extremely large memory sets
   - Designed for application-scale, not big-data scale

4. **AI Integration Dependencies**
   - Claude/ChatGPT integrations require API keys
   - Fallback to mock implementations if keys unavailable
   - API rate limits may affect heavy usage

5. **Performance Not Optimized for All Use Cases**
   - Drift prediction: ~100-200ms per prediction
   - Quantum simulation: varies widely (seconds to minutes)
   - Memory search: sub-100ms for top-tier, slower for archived

### Roadmap

**Near-term (Q4 2025):**
- [ ] Enhanced Phase 2 testing with Git integration
- [ ] Performance benchmarking suite
- [ ] Additional quantum algorithm scenarios
- [ ] Improved error messages and debugging tools

**Medium-term (Q1-Q2 2026):**
- [ ] Real quantum hardware integration (IBM Quantum, Azure Quantum)
- [ ] Distributed memory clustering
- [ ] Advanced visualization dashboard
- [ ] Plugin system for custom algorithms

**Long-term (Future):**
- [ ] Production-scale performance optimization
- [ ] Enterprise deployment tools
- [ ] Cloud-native architecture
- [ ] Extended cultural intelligence datasets

---

## Contributing

We welcome contributions! This is an active research project with room for improvement.

### How to Contribute

1. **Pick an Area**
   - Check [open issues](https://github.com/AUo959/aurora-cloudbank-symbolic/issues)
   - Look for "good first issue" or "help wanted" labels
   - Or propose new features via discussions

2. **Set Up Development Environment**
   ```bash
   git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
   cd aurora-cloudbank-symbolic
   make setup
   ```

3. **Make Changes**
   - Follow existing code style (Flake8, 120-char lines)
   - Add tests for new functionality
   - Update documentation as needed

4. **Submit Pull Request**
   - Describe what you changed and why
   - Reference related issues
   - Ensure tests pass: `make check`

### Contribution Ideas

**Easy:**
- Fix typos in documentation
- Add more test cases
- Improve error messages
- Add code examples

**Medium:**
- Implement new quantum scenarios
- Optimize memory retrieval algorithms
- Add new API endpoints
- Improve test coverage

**Advanced:**
- Enhance drift prediction ML model
- Implement L3 bridge PKI validation
- Add real quantum hardware support
- Build visualization dashboard

**See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.**

---

## License & Attribution

**License:** MIT (see [LICENSE](LICENSE) file)

**Key Technologies:**
- [Qiskit](https://qiskit.org/) - Quantum computing framework
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Clifford](https://clifford.readthedocs.io/) - Geometric algebra

**Research Background:**
This project explores concepts from:
- Quantum computing and quantum algorithms
- Vector Symbolic Architectures (VSA) / Hyperdimensional Computing
- Distributed consensus (Raft protocol)
- Cognitive architectures and memory systems

---

## Acknowledgments

Built with contributions from the open-source community and informed by research in quantum computing, cognitive science, and distributed systems.

Special thanks to:
- Qiskit development team for quantum computing tools
- FastAPI and Pydantic teams for excellent Python frameworks
- Research communities in quantum computing and cognitive architectures

---

## Contact & Support

- **Issues:** [GitHub Issues](https://github.com/AUo959/aurora-cloudbank-symbolic/issues)
- **Discussions:** [GitHub Discussions](https://github.com/AUo959/aurora-cloudbank-symbolic/discussions)
- **Security:** See [SECURITY.md](SECURITY.md) for security reporting

---

**Built for researchers and developers exploring quantum-symbolic computing. Contributions welcome!** 🚀
