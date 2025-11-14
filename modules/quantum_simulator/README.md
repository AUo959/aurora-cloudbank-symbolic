# Quantum Simulator Module

**Anchor:** T1-QSS-001
**Version:** 2.0.0 (Cloud Backends Integrated)

## Overview

The Quantum Simulator module provides a unified interface for quantum computing across multiple backends, from local simulators to cloud quantum services.

## Features

### 🎯 Core Capabilities
- **7 Scenario Types**: Supply chain, energy grid, risk analysis, optimization, Monte Carlo, quantum annealing, variational algorithms
- **Multi-Backend Support**: Local mock/simulator + 3 cloud providers
- **Fault Tolerance**: Circuit breakers, automatic retry, exponential backoff
- **Graceful Degradation**: Falls back to available providers automatically

### ☁️ Cloud Quantum Backends

| Provider | Backend ID | Status | Notes |
|----------|-----------|--------|-------|
| **IBM Quantum** | `ibmq` | ✅ Integrated | Qiskit Runtime, hardware + simulators |
| **Azure Quantum** | `azure_quantum` | ✅ Integrated | IonQ, Quantinuum, Rigetti support |
| **AWS Braket** | `aws_braket` | ✅ Integrated | Local + managed simulators, hardware |
| Local Mock | `mock` | ✅ Always available | Testing and development |
| Local Simulator | `simulator` | ✅ Always available | Classical quantum simulation |

## Quick Start

### Installation

```bash
# Install optional quantum backend dependencies
pip install -r requirements-optional.txt

# Or install specific providers
pip install qiskit-ibm-runtime     # IBM Quantum
pip install azure-quantum cirq     # Azure Quantum
pip install amazon-braket-sdk      # AWS Braket
```

### Configuration

Set environment variables for cloud providers:

```bash
# IBM Quantum
export IBM_QUANTUM_TOKEN="your_token"

# Azure Quantum
export AZURE_QUANTUM_SUBSCRIPTION_ID="..."
export AZURE_QUANTUM_RESOURCE_GROUP="..."
export AZURE_QUANTUM_WORKSPACE_NAME="..."

# AWS Braket
export AWS_BRAKET_DEVICE_ARN="local:braket/default"  # Local simulator (free)
```

### Usage

```python
from modules.quantum_simulator import get_orchestrator, QuantumBackend

# Initialize orchestrator
orchestrator = await get_orchestrator()

# Execute quantum circuit
result = await orchestrator.execute_quantum_circuit(
    backend=QuantumBackend.IBMQ,
    num_qubits=5,
    num_shots=1000
)

print(f"Counts: {result.counts}")
print(f"Execution time: {result.execution_time_ms}ms")
```

## Architecture

```
quantum_simulator/
├── __init__.py              # Module exports
├── orchestrator.py          # Multi-backend orchestration
├── cloud_providers.py       # IBM Quantum, Azure, AWS Braket
├── schemas.py              # Pydantic models
├── scenario_engine.py      # Scenario execution logic
├── scenario_cache.py       # Result caching (60-80% hit rate)
├── quantum_state.py        # Quantum state utilities
├── dlp_integration.py      # Data lineage protocol
└── api.py                  # FastAPI endpoints (13+)
```

## Provider Implementation

### QuantumProvider Interface

All providers implement the abstract `QuantumProvider` base class:

```python
class QuantumProvider(ABC):
    @abstractmethod
    async def execute_circuit(self, num_qubits, num_shots, seed) -> MeasurementResult:
        """Execute quantum circuit"""

    @abstractmethod
    async def optimize(self, objective_fn, num_vars, method, max_iter, seed) -> OptimizationResult:
        """Run quantum optimization"""

    @abstractmethod
    async def check_availability(self) -> bool:
        """Check backend availability"""
```

### Fault Tolerance Features

**Circuit Breaker** (IBM Quantum):
```python
circuit_breaker_threshold = 5      # Open after 5 failures
circuit_breaker_timeout = 60.0     # Reset after 60 seconds
```

**Retry Logic** (All providers):
```python
max_retries = 3
retry_delay = 2.0  # Exponential backoff: 2s, 4s, 8s
```

**Graceful Fallback**:
```python
# Automatically falls back to mock provider if cloud unavailable
provider = orchestrator.get_provider(QuantumBackend.IBMQ)
# Returns MockQuantumProvider if IBM Quantum not configured
```

## API Endpoints

### REST API (13 endpoints)

```
POST   /api/quantum/scenario                  # Submit scenario
GET    /api/quantum/scenario/{id}             # Get results
GET    /api/quantum/scenario/{id}/status      # Check status
DELETE /api/quantum/scenario/{id}             # Cancel scenario
GET    /api/quantum/scenarios                 # List scenarios
POST   /api/quantum/scenarios/batch           # Batch submit
GET    /api/quantum/backends                  # List backends
GET    /api/quantum/health                    # Health check
POST   /api/quantum/circuit/execute           # Execute circuit
POST   /api/quantum/optimize                  # Run optimization
GET    /api/quantum/cache/stats               # Cache statistics
POST   /api/quantum/cache/clear               # Clear cache
```

### WebSocket API

```
WS /api/quantum/stream/{scenario_id}         # Real-time updates
```

## Scenario Types

### 1. Supply Chain Optimization
```python
scenario = ScenarioRequest(
    scenario_type=ScenarioType.SUPPLY_CHAIN,
    backend=QuantumBackend.IBMQ,
    parameters={"num_warehouses": 5, "num_products": 20}
)
```

### 2. Energy Grid Forecasting
```python
scenario = ScenarioRequest(
    scenario_type=ScenarioType.ENERGY_GRID,
    forecast_config=ForecastConfig(
        time_steps=24,
        variables=["demand", "solar", "wind"]
    )
)
```

### 3. Risk Analysis
```python
scenario = ScenarioRequest(
    scenario_type=ScenarioType.RISK_ANALYSIS,
    parameters={"risk_factors": 10, "scenarios": 1000}
)
```

## Performance

### Caching
- **Hit Rate**: 60-80% in production
- **TTL**: Configurable per scenario type
- **Backend**: Redis-compatible

### Execution Times
| Backend | 5 qubits, 1000 shots | Notes |
|---------|---------------------|-------|
| Mock | ~100ms | Local simulation |
| Simulator | ~200ms | Higher fidelity |
| IBM Quantum | ~5-30s | Queue time + execution |
| Azure Quantum | ~3-20s | Varies by target |
| AWS Braket | ~1-15s | Local=1s, managed=15s |

## Testing

```bash
# Unit tests
pytest tests/quantum_simulator/ -v

# Integration tests (requires cloud credentials)
pytest tests/quantum_simulator/ -v -m integration

# Skip cloud tests
pytest tests/quantum_simulator/ -v -m "not integration"
```

## Documentation

- **Full Guide**: `/docs/QUANTUM_CLOUD_BACKENDS.md`
- **API Reference**: Swagger UI at `/docs` when running Aurora API
- **Examples**: `/examples/quantum_scenarios/`

## Dependencies

### Required (Core)
```
fastapi>=0.118.0
qiskit>=1.4.2
qiskit-aer>=0.13.0
numpy>=1.24.0
pydantic>=2.5.0
```

### Optional (Cloud Backends)
```
qiskit-ibm-runtime>=0.15.0     # IBM Quantum
azure-quantum>=1.0.0           # Azure Quantum
cirq>=1.3.0                    # Azure Quantum (required)
amazon-braket-sdk>=1.65.0      # AWS Braket
```

## Troubleshooting

### Provider Not Available

```python
# Check provider status
orchestrator = await get_orchestrator()
available = orchestrator.list_available_backends()
print(f"Available: {available}")
```

### Import Errors

```bash
# Check which libraries are installed
python -c "import qiskit_ibm_runtime; print('IBM ✅')"
python -c "import azure.quantum; print('Azure ✅')"
python -c "import braket; print('AWS ✅')"
```

### Cloud Authentication

```bash
# IBM Quantum
echo $IBM_QUANTUM_TOKEN

# Azure Quantum
az account show

# AWS Braket
aws sts get-caller-identity
```

## Future Enhancements

- [ ] Full VQE/QAOA implementation with problem Hamiltonians
- [ ] Hybrid classical-quantum workflows
- [ ] Job queueing and batch processing
- [ ] Cost analytics and budget limits
- [ ] Google Quantum AI integration
- [ ] D-Wave quantum annealing support

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Docs**: `/docs/QUANTUM_CLOUD_BACKENDS.md`

---

**Last Updated**: 2025-11-09
**Status**: Production Ready
