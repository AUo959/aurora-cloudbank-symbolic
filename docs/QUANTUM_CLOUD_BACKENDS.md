# Quantum Cloud Backends Integration Guide

**Version:** 1.0.0
**Anchor:** T1-QSS-002
**Status:** Production

## Overview

Aurora CloudBank Symbolic now supports three major quantum cloud providers:

- **IBM Quantum** - Access to IBM's quantum computers and cloud simulators
- **Azure Quantum** - Microsoft's quantum workspace with multiple backend providers
- **AWS Braket** - Amazon's quantum computing service

All implementations feature:
- ✅ **Graceful degradation** - System works without cloud credentials
- ✅ **Fault tolerance** - Automatic retry with exponential backoff
- ✅ **Circuit breakers** - Prevents cascading failures
- ✅ **Future-proof** - Optional dependencies, easy to extend

---

## Installation

### Option 1: Install All Quantum Backends

```bash
pip install -r requirements-optional.txt
```

### Option 2: Install Specific Backends

**IBM Quantum:**
```bash
pip install qiskit-ibm-runtime>=0.15.0 qiskit-ibm-provider>=0.7.0
```

**Azure Quantum:**
```bash
pip install azure-quantum>=1.0.0 cirq>=1.3.0
```

**AWS Braket:**
```bash
pip install amazon-braket-sdk>=1.65.0
```

---

## Configuration

### 1. IBM Quantum Setup

#### Prerequisites
- IBM Quantum account: https://quantum.ibm.com/
- API token from IBM Quantum dashboard

#### Environment Variables

```bash
# Required
export IBM_QUANTUM_TOKEN="your_ibm_quantum_token_here"

# Optional (with defaults)
export IBM_QUANTUM_INSTANCE="ibm_quantum/default/main"
export IBM_QUANTUM_BACKEND="ibmq_qasm_simulator"  # or hardware: ibm_kyoto, ibm_osaka, etc.
export IBM_QUANTUM_CHANNEL="ibm_quantum"
```

#### Available Backends
- **Simulators:** `ibmq_qasm_simulator`, `simulator_statevector`
- **Hardware:** `ibm_kyoto`, `ibm_osaka`, `ibm_brisbane`, `ibm_sherbrooke`, etc.

#### Example Usage

```python
from modules.quantum_simulator import get_orchestrator, QuantumBackend

# Initialize orchestrator
orchestrator = await get_orchestrator()

# Execute circuit on IBM Quantum
result = await orchestrator.execute_quantum_circuit(
    backend=QuantumBackend.IBMQ,
    num_qubits=5,
    num_shots=1000,
    seed=42
)

print(f"Measurement counts: {result.counts}")
print(f"Execution time: {result.execution_time_ms}ms")
```

---

### 2. Azure Quantum Setup

#### Prerequisites
- Azure subscription: https://azure.microsoft.com/
- Azure Quantum workspace created
- Appropriate permissions on subscription and resource group

#### Environment Variables

```bash
# Required
export AZURE_QUANTUM_SUBSCRIPTION_ID="your_subscription_id"
export AZURE_QUANTUM_RESOURCE_GROUP="your_resource_group"
export AZURE_QUANTUM_WORKSPACE_NAME="your_workspace_name"

# Optional (with defaults)
export AZURE_QUANTUM_LOCATION="eastus"
export AZURE_QUANTUM_TARGET="ionq.simulator"  # or: ionq.qpu, quantinuum.qpu, etc.
```

#### Available Targets
- **IonQ:** `ionq.simulator`, `ionq.qpu`
- **Quantinuum:** `quantinuum.sim.h1-1sc`, `quantinuum.qpu.h1-1`
- **Rigetti:** `rigetti.sim.qvm`, `rigetti.qpu.aspen-*`

#### Creating Azure Quantum Workspace

```bash
# Install Azure CLI
az extension add --name quantum

# Create resource group (if needed)
az group create --name myResourceGroup --location eastus

# Create quantum workspace
az quantum workspace create \
    --resource-group myResourceGroup \
    --name myQuantumWorkspace \
    --location eastus \
    --storage-account /subscriptions/{subscription}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage}
```

#### Example Usage

```python
from modules.quantum_simulator import get_orchestrator, QuantumBackend

orchestrator = await get_orchestrator()

# Execute on Azure Quantum
result = await orchestrator.execute_quantum_circuit(
    backend=QuantumBackend.AZURE_QUANTUM,
    num_qubits=4,
    num_shots=500
)
```

---

### 3. AWS Braket Setup

#### Prerequisites
- AWS account: https://aws.amazon.com/
- AWS CLI configured with credentials
- S3 bucket for results (if using managed devices)

#### Environment Variables

```bash
# For local simulator (free, no credentials needed)
export AWS_BRAKET_DEVICE_ARN="local:braket/default"

# For managed simulators and hardware
export AWS_BRAKET_DEVICE_ARN="arn:aws:braket:::device/quantum-simulator/amazon/sv1"
export AWS_BRAKET_S3_BUCKET="your-s3-bucket-name"
export AWS_BRAKET_S3_PREFIX="aurora-quantum"
export AWS_REGION="us-east-1"

# AWS credentials (via AWS CLI or environment)
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
```

#### Available Devices

**Local Simulator (Free):**
- `local:braket/default` - Local simulator (no cloud costs)

**Managed Simulators:**
- `arn:aws:braket:::device/quantum-simulator/amazon/sv1` - State vector simulator
- `arn:aws:braket:::device/quantum-simulator/amazon/tn1` - Tensor network simulator
- `arn:aws:braket:::device/quantum-simulator/amazon/dm1` - Density matrix simulator

**Quantum Hardware:**
- IonQ: `arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1`
- Rigetti: `arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3`
- QuEra: `arn:aws:braket:us-east-1::device/qpu/quera/Aquila`

#### Example Usage

```python
from modules.quantum_simulator import get_orchestrator, QuantumBackend

orchestrator = await get_orchestrator()

# Local simulator (free)
result = await orchestrator.execute_quantum_circuit(
    backend=QuantumBackend.AWS_BRAKET,
    num_qubits=8,
    num_shots=2000
)

# Or use environment variable to switch devices without code changes
# export AWS_BRAKET_DEVICE_ARN="arn:aws:braket:::device/quantum-simulator/amazon/sv1"
```

---

## Fault Tolerance Features

### Automatic Retry with Exponential Backoff

All providers implement retry logic:

```python
max_retries = 3
retry_delay = 2.0  # seconds

# Retry schedule:
# Attempt 1: immediate
# Attempt 2: 2s delay
# Attempt 3: 4s delay
# Attempt 4: 8s delay
```

### Circuit Breaker Protection

IBM Quantum provider includes circuit breaker:

```python
circuit_breaker_threshold = 5      # failures before opening
circuit_breaker_timeout = 60.0     # seconds before retry

# After 5 failures:
# - Circuit OPENS (blocks requests)
# - Wait 60 seconds
# - Circuit RESETS automatically
```

### Graceful Degradation

If cloud providers are unavailable:

```python
# Automatic fallback to mock provider
provider = orchestrator.get_provider(QuantumBackend.IBMQ)
# Returns mock provider if IBM Quantum unavailable
```

---

## API Reference

### Backend Selection

```python
from modules.quantum_simulator.schemas import QuantumBackend

# Available backends
QuantumBackend.MOCK              # Local mock (always available)
QuantumBackend.SIMULATOR         # Local simulator (always available)
QuantumBackend.IBMQ             # IBM Quantum Cloud
QuantumBackend.AZURE_QUANTUM    # Azure Quantum
QuantumBackend.AWS_BRAKET       # AWS Braket
```

### Execute Quantum Circuit

```python
result = await orchestrator.execute_quantum_circuit(
    backend=QuantumBackend.IBMQ,
    num_qubits=5,           # Number of qubits
    num_shots=1000,         # Measurement shots
    seed=42                 # Optional: random seed
)

# Result fields
result.counts              # Dict[str, int] - measurement counts
result.probabilities       # Dict[str, float] - probabilities
result.total_shots         # int - total shots
result.execution_time_ms   # float - execution time
```

### Run Optimization

```python
from modules.quantum_simulator.schemas import OptimizationMethod

def objective_function(params):
    # Your objective function
    return sum(p**2 for p in params)

result = await orchestrator.run_optimization(
    backend=QuantumBackend.AZURE_QUANTUM,
    objective_function=objective_function,
    num_variables=10,
    method=OptimizationMethod.QAOA,
    max_iterations=100,
    seed=42
)

# Result fields
result.optimal_solution      # Dict[str, float] - optimal parameters
result.objective_value       # float - final objective value
result.iterations           # int - iterations performed
result.converged            # bool - convergence status
result.convergence_history  # List[float] - value history
```

### Check Backend Availability

```python
# List all available backends
available = orchestrator.list_available_backends()
print(f"Available backends: {available}")

# Check specific backend
provider = orchestrator.providers[QuantumBackend.IBMQ]
if provider and provider.is_available:
    print("IBM Quantum is ready!")
```

---

## Scenario-Based Examples

### Supply Chain Optimization

```python
from modules.quantum_simulator import ScenarioRequest, ScenarioType, QuantumBackend, OptimizationMethod

request = ScenarioRequest(
    scenario_type=ScenarioType.SUPPLY_CHAIN,
    name="Q1 Logistics Optimization",
    description="Optimize distribution across 5 warehouses",
    backend=QuantumBackend.IBMQ,
    optimization_method=OptimizationMethod.QAOA,
    parameters={
        "num_warehouses": 5,
        "num_products": 20,
        "demand_variability": 0.15
    },
    num_shots=5000,
    max_iterations=200,
    seed=42
)

# Submit via API or directly
result = await scenario_engine.run_scenario(request)
```

### Energy Grid Forecasting

```python
request = ScenarioRequest(
    scenario_type=ScenarioType.ENERGY_GRID,
    name="Peak Demand Forecast",
    backend=QuantumBackend.AZURE_QUANTUM,
    forecast_config=ForecastConfig(
        time_steps=24,
        variables=["demand", "solar", "wind"],
        initial_conditions={
            "demand": 1000.0,
            "solar": 200.0,
            "wind": 150.0
        },
        uncertainty_level=0.2
    ),
    num_shots=3000
)

result = await scenario_engine.run_scenario(request)
```

---

## Cost Optimization

### Free Tiers and Simulators

**IBM Quantum:**
- Free tier: 10 minutes/month on quantum hardware
- Simulators: Free (with rate limits)

**Azure Quantum:**
- Free credits: $500 USD for new workspaces
- IonQ simulator: Free
- Quantinuum simulator: Free (limited)

**AWS Braket:**
- Local simulator: Free (runs locally)
- On-demand pricing for managed services
- Free tier: First month includes some credits

### Cost Control Strategies

```python
# 1. Start with local simulators
backend = QuantumBackend.SIMULATOR  # Local, free

# 2. Use cloud simulators before hardware
backend = QuantumBackend.IBMQ
backend_name = "ibmq_qasm_simulator"  # Free simulator

# 3. Limit shot counts for testing
num_shots = 100  # vs 10,000 for production

# 4. Use AWS Braket local simulator
export AWS_BRAKET_DEVICE_ARN="local:braket/default"
```

---

## Troubleshooting

### IBM Quantum

**Issue: "401 Unauthorized"**
```bash
# Check token validity
echo $IBM_QUANTUM_TOKEN
# Regenerate token at https://quantum.ibm.com/
```

**Issue: "Backend not found"**
```bash
# List available backends
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; service = QiskitRuntimeService(); print(service.backends())"
```

### Azure Quantum

**Issue: "Workspace not found"**
```bash
# Verify workspace exists
az quantum workspace show \
    --resource-group $AZURE_QUANTUM_RESOURCE_GROUP \
    --name $AZURE_QUANTUM_WORKSPACE_NAME
```

**Issue: "Target not available"**
```python
# List available targets
from azure.quantum import Workspace
workspace = Workspace(...)
targets = workspace.get_targets()
for target in targets:
    print(f"{target.name}: {target.current_availability}")
```

### AWS Braket

**Issue: "Access Denied to S3"**
```bash
# Verify S3 bucket permissions
aws s3 ls s3://$AWS_BRAKET_S3_BUCKET/
```

**Issue: "Device not available"**
```python
# Check device status
from braket.aws import AwsDevice
device = AwsDevice("arn:aws:braket:...")
print(f"Status: {device.status}")
```

### General Issues

**Issue: "Provider not available"**
```python
# Check if dependencies installed
import importlib
libs = ['qiskit_ibm_runtime', 'azure.quantum', 'braket']
for lib in libs:
    try:
        importlib.import_module(lib)
        print(f"✅ {lib} installed")
    except ImportError:
        print(f"❌ {lib} not installed")
```

---

## Best Practices

### 1. Environment-Specific Configuration

```bash
# .env.development
IBM_QUANTUM_BACKEND=ibmq_qasm_simulator

# .env.production
IBM_QUANTUM_BACKEND=ibm_kyoto
```

### 2. Credential Management

```bash
# NEVER commit credentials to git
echo ".env" >> .gitignore

# Use secret management
aws secretsmanager get-secret-value --secret-id quantum/ibm-token
az keyvault secret show --vault-name myVault --name ibm-quantum-token
```

### 3. Error Handling

```python
from modules.quantum_simulator import get_orchestrator, QuantumBackend

try:
    orchestrator = await get_orchestrator()
    result = await orchestrator.execute_quantum_circuit(
        backend=QuantumBackend.IBMQ,
        num_qubits=5,
        num_shots=1000
    )
except RuntimeError as e:
    # Fallback to simulator
    print(f"Cloud backend failed: {e}")
    result = await orchestrator.execute_quantum_circuit(
        backend=QuantumBackend.SIMULATOR,
        num_qubits=5,
        num_shots=1000
    )
```

### 4. Testing Strategy

```python
import pytest

@pytest.mark.integration
async def test_ibm_quantum():
    """Test IBM Quantum integration (requires credentials)."""
    orchestrator = await get_orchestrator()

    # Skip if not configured
    provider = orchestrator.providers[QuantumBackend.IBMQ]
    if not provider or not provider.is_available:
        pytest.skip("IBM Quantum not configured")

    result = await orchestrator.execute_quantum_circuit(
        backend=QuantumBackend.IBMQ,
        num_qubits=2,
        num_shots=10
    )
    assert result.total_shots == 10
```

---

## Future Enhancements

### Planned Features

1. **VQE/QAOA Implementation**
   - Problem-specific Hamiltonian encoding
   - Full variational algorithm support

2. **Hybrid Classical-Quantum**
   - Automatic workload partitioning
   - Classical preprocessing/postprocessing

3. **Job Queueing**
   - Batch job submission
   - Priority scheduling

4. **Advanced Monitoring**
   - Real-time job status tracking
   - Cost analytics dashboard

5. **Additional Providers**
   - Google Quantum AI (Sycamore)
   - Xanadu (PennyLane/Strawberry Fields)
   - D-Wave (quantum annealing)

---

## Support

### Documentation
- Aurora CloudBank Docs: `/docs`
- IBM Quantum: https://docs.quantum.ibm.com/
- Azure Quantum: https://learn.microsoft.com/azure/quantum/
- AWS Braket: https://docs.aws.amazon.com/braket/

### Community
- GitHub Issues: https://github.com/yourusername/aurora-cloudbank-symbolic/issues
- Discussions: https://github.com/yourusername/aurora-cloudbank-symbolic/discussions

---

**Last Updated:** 2025-11-09
**Maintainers:** Aurora CloudBank Team
**License:** MIT
