# Aurora Python SDK

[![PyPI version](https://badge.fury.io/py/aurora-sdk.svg)](https://pypi.org/project/aurora-sdk/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for [Aurora CloudBank Symbolic](https://github.com/AUo959/aurora-cloudbank-symbolic) - a quantum-symbolic computing platform combining quantum algorithm simulation, vector symbolic architectures, and AI decision intelligence.

## Features

- 🎯 **Intuitive API** - Pythonic interface with full type hints
- ⚡ **Async-First** - Native async/await support with httpx
- 🔒 **Type Safe** - Pydantic models for request/response validation
- 🔄 **Auto-Retry** - Intelligent retry logic with exponential backoff
- 📊 **Well-Documented** - Comprehensive docs and examples
- 🧪 **Fully Tested** - >90% test coverage

## Installation

```bash
pip install aurora-sdk
```

**Requirements:** Python 3.11 or higher

## Quick Start

```python
from aurora_sdk import AuroraClient

# Initialize client
client = AuroraClient(api_key="sk_test_...")

# Run quantum supply chain optimization
result = await client.quantum.run_scenario(
    "supply_chain_optimization",
    num_suppliers=5,
    demand_variance=0.2
)

print(f"Optimal configuration: {result.optimal_state}")
print(f"Cost reduction: {result.metrics['cost_reduction']:.1f}%")
```

## Authentication

### API Key

Get your API key from the [Aurora Dashboard](https://dashboard.aurora.dev) and set it:

```python
# Option 1: Pass directly
client = AuroraClient(api_key="sk_test_...")

# Option 2: Environment variable
import os
os.environ["AURORA_API_KEY"] = "sk_test_..."
client = AuroraClient()

# Option 3: .env file
# Create .env file with: AURORA_API_KEY=sk_test_...
from aurora_sdk import Config
config = Config.from_env()
client = AuroraClient(config=config)
```

## Usage Examples

### Quantum Scenarios

Run various quantum simulation scenarios:

```python
# Supply Chain Optimization
result = await client.quantum.run_scenario(
    "supply_chain_optimization",
    num_suppliers=5,
    demand_variance=0.2,
    cost_weights=[0.3, 0.4, 0.2, 0.5, 0.3]
)

# Energy Grid Balancing
result = await client.quantum.run_scenario(
    "energy_grid_balancing",
    num_nodes=10,
    demand_pattern="variable"
)

# Risk Assessment
result = await client.quantum.run_scenario(
    "risk_assessment",
    portfolio_size=100,
    risk_tolerance=0.05
)
```

### Quantum Circuits

Create and simulate quantum circuits:

```python
# Bell state
circuit = await client.quantum.create_circuit(
    circuit_type="bell",
    num_qubits=2
)

# GHZ state
circuit = await client.quantum.create_circuit(
    circuit_type="ghz",
    num_qubits=3
)

# Custom circuit
circuit = await client.quantum.create_circuit(
    circuit_type="custom",
    num_qubits=4,
    gates=[
        {"gate": "h", "qubits": [0]},
        {"gate": "cx", "qubits": [0, 1]},
        {"gate": "cx", "qubits": [1, 2]}
    ]
)
```

### Memory Management

Work with the hierarchical memory system:

```python
# Create memory
memory = await client.memory.create(
    content="User preferences for quantum algorithms",
    tier="active",
    tags=["preferences", "quantum"],
    metadata={"source": "user_input", "priority": "high"}
)

# Search memories
results = await client.memory.search(
    query="quantum optimization",
    top_k=10,
    tier="active"
)

for memory in results:
    print(f"• {memory.content} (score: {memory.attention_score:.2f})")

# Update memory
updated = await client.memory.update(
    memory.memory_id,
    tags=["preferences", "quantum", "reviewed"]
)

# Delete memory
await client.memory.delete(memory.memory_id)

# Get statistics
stats = await client.memory.get_stats()
print(f"Total memories: {stats.total_memories}")
print(f"Active: {stats.active_count}")
print(f"Compressed: {stats.compressed_count}")
print(f"Archived: {stats.archived_count}")
```

### List Operations with Pagination

Automatically paginate through large result sets:

```python
# List all active memories
async for memory in client.memory.list(tier="active"):
    print(memory.content)

# List with custom page size
async for memory in client.memory.list(page_size=50, tier="active"):
    print(memory.content)
```

### Context Manager

Use the client as an async context manager for automatic cleanup:

```python
async with AuroraClient(api_key="sk_test_...") as client:
    result = await client.quantum.run_scenario("supply_chain")
    print(result.optimal_state)
# Client automatically closed
```

### Error Handling

Handle various error conditions:

```python
from aurora_sdk import (
    AuroraClient,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ResourceNotFoundError
)

try:
    result = await client.quantum.run_scenario("supply_chain")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
    print(f"Details: {e.details}")
except ResourceNotFoundError as e:
    print(f"Resource not found: {e}")
```

### Custom Configuration

Configure client behavior:

```python
from aurora_sdk import AuroraClient, Config

# Custom configuration
config = Config(
    api_key="sk_test_...",
    base_url="https://api.aurora.dev",
    timeout=60.0,          # 60 second timeout
    max_retries=5,         # Retry up to 5 times
    cache_ttl=300,         # Cache for 5 minutes
    log_level="DEBUG"      # Enable debug logging
)

client = AuroraClient(config=config)
```

## Advanced Usage

### List Available Resources

```python
# List available scenarios
scenarios = await client.quantum.list_scenarios()
for scenario in scenarios:
    print(scenario)

# List quantum backends
backends = await client.quantum.list_backends()
for backend in backends:
    print(f"{backend.backend_id}: {backend.max_qubits} qubits")
```

### Batch Operations

Execute multiple operations efficiently:

```python
import asyncio

# Run scenarios concurrently
results = await asyncio.gather(
    client.quantum.run_scenario("supply_chain", num_suppliers=5),
    client.quantum.run_scenario("energy_grid", num_nodes=10),
    client.quantum.run_scenario("risk_assessment", portfolio_size=100)
)

for result in results:
    print(f"{result.scenario_type}: {result.optimal_state}")
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AURORA_API_KEY` | API key for authentication | (required) |
| `AURORA_BASE_URL` | Base URL for API | `http://localhost:8000` |
| `AURORA_TIMEOUT` | Request timeout in seconds | `30.0` |
| `AURORA_MAX_RETRIES` | Maximum retry attempts | `3` |
| `AURORA_CACHE_TTL` | Cache TTL in seconds | `0` (disabled) |
| `AURORA_LOG_LEVEL` | Logging level | `INFO` |

### .env File Example

Create a `.env` file in your project root:

```bash
AURORA_API_KEY=sk_test_your_key_here
AURORA_BASE_URL=https://api.aurora.dev
AURORA_TIMEOUT=60
AURORA_MAX_RETRIES=5
AURORA_LOG_LEVEL=DEBUG
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/AUo959/aurora-cloudbank-symbolic
cd aurora-cloudbank-symbolic/sdk/python

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=aurora_sdk --cov-report=html

# Type checking
mypy src/aurora_sdk

# Linting
ruff check src/aurora_sdk
black --check src/aurora_sdk

# Format code
black src/aurora_sdk
ruff check --fix src/aurora_sdk
```

## Documentation

- **Full Documentation:** https://developers.aurora.dev
- **API Reference:** https://developers.aurora.dev/api
- **Examples:** https://github.com/AUo959/aurora-cloudbank-symbolic/tree/main/examples
- **Playground:** https://playground.aurora.dev

## Requirements

- Python 3.11+
- httpx >= 0.28.0
- pydantic >= 2.5.0
- python-dotenv >= 1.0.0
- typing-extensions >= 4.8.0

## Contributing

Contributions are welcome! Please see our [Contributing Guide](../../CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Support

- **Issues:** https://github.com/AUo959/aurora-cloudbank-symbolic/issues
- **Discussions:** https://github.com/AUo959/aurora-cloudbank-symbolic/discussions
- **Email:** developers@aurora.dev

## Links

- **Homepage:** https://aurora.dev
- **Documentation:** https://developers.aurora.dev
- **GitHub:** https://github.com/AUo959/aurora-cloudbank-symbolic
- **PyPI:** https://pypi.org/project/aurora-sdk/
- **Playground:** https://playground.aurora.dev

---

Made with ❤️ by the Aurora CloudBank Team
