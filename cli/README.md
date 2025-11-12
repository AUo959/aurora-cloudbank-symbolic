# Aurora CLI

[![PyPI version](https://badge.fury.io/py/aurora-cli.svg)](https://pypi.org/project/aurora-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Unified command-line interface for [Aurora CloudBank Symbolic](https://github.com/AUo959/aurora-cloudbank-symbolic) - quantum-symbolic computing platform.

## Features

- 🚀 **Project Scaffolding** - Initialize new projects with templates
- ⚡ **Fast Operations** - Run scenarios, manage memories, and more
- 🎨 **Beautiful Output** - Rich terminal UI with colors and tables
- 🔧 **Configuration Management** - Easy config with YAML files
- 📊 **Multiple Formats** - Output as text, JSON, or YAML
- 🔄 **Auto-completion** - Shell completion for bash, zsh, fish

## Installation

```bash
pip install aurora-cli
```

**Requirements:** Python 3.11 or higher

## Quick Start

```bash
# Set up configuration
aurora config set api_key sk_test_...

# Initialize a new project
aurora init my-quantum-app

# Run a quantum scenario
aurora scenario run supply_chain --param suppliers=5

# Create a memory
aurora memory create "Important note" --tag note

# Open playground in browser
aurora playground

# Open documentation
aurora docs
```

## Commands

### Project Management

#### `aurora init`

Initialize a new Aurora project with templates.

```bash
# Create new project
aurora init my-quantum-app

# With specific template
aurora init my-app --template python

# In current directory
aurora init . --template javascript
```

**Generated Project Structure (Python):**

```
my-quantum-app/
├── .aurora/
│   └── config.yaml
├── scenarios/
│   └── example.json
├── src/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_scenarios.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

### Configuration

#### `aurora config`

Manage Aurora configuration.

```bash
# Set configuration value
aurora config set api_key sk_live_...
aurora config set base_url https://api.aurora.dev

# Get configuration value
aurora config get api_key

# List all configuration
aurora config list

# Validate configuration
aurora config validate
```

**Configuration File:** `~/.aurora/config.yaml`

**Example:**

```yaml
api_key: sk_test_...
base_url: http://localhost:8000
timeout: 30
max_retries: 3
```

---

### Quantum Scenarios

#### `aurora scenario`

Manage and run quantum scenarios.

```bash
# Run scenario with inline parameters
aurora scenario run supply_chain --param suppliers=5 --param variance=0.2

# Run with config file
aurora scenario run supply_chain --config scenario.json

# Save output to file
aurora scenario run supply_chain --output result.json

# List available scenarios
aurora scenario list

# Get scenario template
aurora scenario template supply_chain > my_scenario.json

# Validate scenario config
aurora scenario validate my_scenario.json
```

**scenario.json example:**

```json
{
  "scenario": "supply_chain_optimization",
  "params": {
    "num_suppliers": 5,
    "demand_variance": 0.2,
    "cost_weights": [0.3, 0.4, 0.2, 0.5, 0.3]
  }
}
```

**Output Example:**

```
⠋ Running scenario supply_chain... (2.3s)
✓ Scenario completed

Scenario Result
Scenario ID: scen_abc123
Status: completed
Optimal State: [1, 0, 1, 0, 1]
Execution Time: 1.24s

Metrics:
  cost_reduction: 23.40
  reliability: 0.95
  efficiency: 0.87
```

---

### Memory Management

#### `aurora memory`

Work with the hierarchical memory system.

```bash
# Create memory
aurora memory create "Important note" --tier active --tag note

# Get memory by ID
aurora memory get mem_abc123

# Search memories
aurora memory search "quantum algorithms" --top-k 5

# List memories
aurora memory list --tier active

# Update memory
aurora memory update mem_abc123 --tag updated

# Delete memory
aurora memory delete mem_abc123

# Get statistics
aurora memory stats
```

---

### Development

#### `aurora dev`

Start development server.

```bash
# Start server
aurora dev

# Custom port
aurora dev --port 3000

# With playground UI
aurora dev --playground

# With documentation
aurora dev --docs
```

---

### Utilities

#### `aurora playground`

Open interactive playground in browser.

```bash
aurora playground
# Opens https://playground.aurora.dev
```

#### `aurora docs`

Open documentation in browser.

```bash
# Main documentation
aurora docs

# Specific topic
aurora docs scenarios
aurora docs api
aurora docs quickstart
```

#### `aurora status`

Show Aurora environment status.

```bash
aurora status

# Output:
Aurora Environment Status
┌────────────────┬──────────────────────────────┐
│ Configuration  │ Value                        │
├────────────────┼──────────────────────────────┤
│ API Key        │ sk_test_...abc (configured)  │
│ Base URL       │ http://localhost:8000        │
│ Version        │ 0.1.0                        │
│ Python         │ 3.11.5                       │
└────────────────┴──────────────────────────────┘
```

---

## Output Formats

### Text (Default)

Human-readable output with colors and formatting.

```bash
aurora scenario run supply_chain
```

### JSON

Machine-readable JSON output.

```bash
aurora scenario run supply_chain --format json
```

```json
{
  "scenario_id": "scen_abc123",
  "scenario_type": "supply_chain_optimization",
  "status": "completed",
  "optimal_state": [1, 0, 1, 0, 1],
  "metrics": {
    "cost_reduction": 23.4,
    "reliability": 0.95
  },
  "execution_time": 1.24
}
```

### YAML

YAML output (with `--format yaml`).

```bash
aurora scenario run supply_chain --format yaml
```

```yaml
scenario_id: scen_abc123
scenario_type: supply_chain_optimization
status: completed
optimal_state:
  - 1
  - 0
  - 1
  - 0
  - 1
metrics:
  cost_reduction: 23.4
  reliability: 0.95
execution_time: 1.24
```

---

## Shell Completion

Enable auto-completion for your shell:

### Bash

```bash
aurora --install-completion bash
source ~/.bashrc
```

### Zsh

```bash
aurora --install-completion zsh
source ~/.zshrc
```

### Fish

```bash
aurora --install-completion fish
```

### Usage

```bash
aurora scen<TAB>
# Completes to: aurora scenario

aurora scenario <TAB>
# Shows: run  list  template  validate
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AURORA_API_KEY` | API key for authentication | (required) |
| `AURORA_BASE_URL` | Base URL for API | `http://localhost:8000` |
| `AURORA_TIMEOUT` | Request timeout in seconds | `30.0` |
| `AURORA_MAX_RETRIES` | Maximum retry attempts | `3` |

### Config File Locations

Searched in order:

1. `.aurora/config.yaml` (project directory)
2. `~/.aurora/config.yaml` (user home)
3. Environment variables

---

## Examples

### Complete Workflow

```bash
# 1. Initialize project
aurora init quantum-supply-chain --template python
cd quantum-supply-chain

# 2. Configure
aurora config set api_key sk_live_...

# 3. Create scenario config
cat > scenarios/supply_chain.json <<EOF
{
  "scenario": "supply_chain_optimization",
  "params": {
    "num_suppliers": 10,
    "demand_variance": 0.3
  }
}
EOF

# 4. Validate
aurora scenario validate scenarios/supply_chain.json

# 5. Run scenario
aurora scenario run supply_chain \
  --config scenarios/supply_chain.json \
  --output results.json

# 6. Save to memory
aurora memory create "Supply chain results from 2025-11-09" \
  --tag results \
  --tag supply_chain

# 7. Search memories
aurora memory search "supply chain" --top-k 5
```

### Batch Processing

```bash
# Run multiple scenarios and save results
for scenario in supply_chain energy_grid risk_assessment; do
  aurora scenario run $scenario \
    --output "results_${scenario}.json"
done
```

### Development Workflow

```bash
# Start dev server with playground
aurora dev --playground --port 3000

# In another terminal, run scenarios
aurora scenario run supply_chain --param suppliers=5

# Open docs
aurora docs api
```

---

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/AUo959/aurora-cloudbank-symbolic
cd aurora-cloudbank-symbolic/cli

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/aurora_cli

# Linting
ruff check src/aurora_cli
black --check src/aurora_cli
```

---

## Dependencies

- aurora-sdk >= 0.1.0
- typer[all] >= 0.9.0
- rich >= 13.0.0
- pyyaml >= 6.0
- python-dotenv >= 1.0.0

---

## Documentation

- **Full Documentation:** https://developers.aurora.dev
- **CLI Guide:** https://developers.aurora.dev/cli
- **Examples:** https://github.com/AUo959/aurora-cloudbank-symbolic/tree/main/examples

---

## Support

- **Issues:** https://github.com/AUo959/aurora-cloudbank-symbolic/issues
- **Discussions:** https://github.com/AUo959/aurora-cloudbank-symbolic/discussions
- **Email:** developers@aurora.dev

---

## License

MIT License - see [LICENSE](../../LICENSE) file for details.

---

Made with ❤️ by the Aurora CloudBank Team
