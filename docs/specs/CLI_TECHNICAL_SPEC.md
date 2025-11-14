# Aurora CLI Technical Specification

**Project:** Aurora CloudBank Symbolic CLI
**Version:** 0.1.0
**Date:** 2025-11-09
**Status:** Design

---

## 1. Overview

The Aurora CLI is a unified command-line tool for interacting with Aurora CloudBank Symbolic, providing project scaffolding, scenario execution, memory management, and developer utilities.

### 1.1 Goals

- **Unified Interface:** Single CLI for all Aurora operations
- **Developer Productivity:** Fast, intuitive commands
- **Great UX:** Helpful errors, progress bars, colored output
- **Extensibility:** Plugin architecture for custom commands
- **Documentation:** Built-in help and examples

---

## 2. Command Structure

```bash
aurora [global-options] <command> [command-options] [arguments]
```

### 2.1 Global Options

```bash
--help, -h          Show help
--version, -v       Show version
--config FILE       Use custom config file
--api-key KEY       Override API key
--base-url URL      Override base URL
--verbose           Enable verbose output
--quiet             Suppress output
--no-color          Disable colored output
--format FORMAT     Output format (text, json, yaml)
```

---

## 3. Commands

### 3.1 Project Management

#### `aurora init`

Initialize a new Aurora project.

```bash
aurora init [project-name] [options]

Options:
  --template TEMPLATE    Project template (python, javascript, docker)
  --path PATH            Project directory (default: current)
  --no-git               Don't initialize git repository
  --skip-install         Don't install dependencies

Examples:
  aurora init my-quantum-app
  aurora init my-app --template python
  aurora init . --template javascript
```

**Generated Structure (Python):**

```
my-quantum-app/
├── .aurora/
│   └── config.yaml          # Aurora configuration
├── scenarios/
│   └── example.json         # Example scenario
├── src/
│   ├── __init__.py
│   └── main.py              # Entry point with SDK usage
├── tests/
│   └── test_scenarios.py
├── .env.example             # Environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

#### `aurora config`

Manage configuration.

```bash
aurora config set <key> <value>
aurora config get <key>
aurora config list
aurora config validate

Examples:
  aurora config set api_key sk_live_...
  aurora config set base_url https://api.aurora.dev
  aurora config get api_key
  aurora config list
```

---

### 3.2 Authentication

#### `aurora auth`

Authentication management.

```bash
aurora auth login                    # Interactive login
aurora auth logout                   # Remove credentials
aurora auth status                   # Show auth status
aurora auth whoami                   # Show current user

Examples:
  aurora auth login
  Enter API key: sk_live_...
  ✓ Successfully authenticated as user@example.com

  aurora auth status
  ✓ Authenticated
  User: user@example.com
  API Key: sk_live_...abc (last 3 chars)
```

---

### 3.3 Development

#### `aurora dev`

Start development server.

```bash
aurora dev [options]

Options:
  --port PORT            Port number (default: 8000)
  --playground           Start with playground UI
  --docs                 Start with documentation
  --hot-reload           Enable hot reload

Examples:
  aurora dev
  aurora dev --port 3000 --playground
  aurora dev --docs
```

---

### 3.4 Quantum Scenarios

#### `aurora scenario`

Manage quantum scenarios.

```bash
aurora scenario run <scenario> [options]
aurora scenario list
aurora scenario describe <scenario>
aurora scenario template <scenario>
aurora scenario validate <file>

Options (run):
  --config FILE          Load params from JSON/YAML file
  --param KEY=VALUE      Set parameter (can be repeated)
  --output FILE          Save result to file
  --format FORMAT        Output format (text, json, yaml)
  --watch                Watch for changes and re-run

Examples:
  # Run with inline params
  aurora scenario run supply_chain --param suppliers=5 --param variance=0.2

  # Run with config file
  aurora scenario run supply_chain --config scenario.json

  # List scenarios
  aurora scenario list

  # Get template
  aurora scenario template supply_chain > my_scenario.json

  # Validate config
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

---

### 3.5 Memory Management

#### `aurora memory`

Memory operations.

```bash
aurora memory create <content> [options]
aurora memory get <id>
aurora memory update <id> [options]
aurora memory delete <id>
aurora memory search <query> [options]
aurora memory list [options]

Options (create):
  --tier TIER            Storage tier (active, compressed, archived)
  --tag TAG              Add tag (can be repeated)
  --metadata KEY=VALUE   Add metadata (can be repeated)

Options (search):
  --top-k N              Number of results (default: 10)
  --tier TIER            Filter by tier

Options (list):
  --tier TIER            Filter by tier
  --tag TAG              Filter by tag
  --limit N              Max results

Examples:
  # Create memory
  aurora memory create "User preferences" --tier active --tag preferences

  # Search
  aurora memory search "quantum algorithms" --top-k 5

  # List active memories
  aurora memory list --tier active

  # Delete memory
  aurora memory delete mem_abc123
```

---

### 3.6 Thread Bridge

#### `aurora bridge`

Thread bridge operations.

```bash
aurora bridge register <node-id> [options]
aurora bridge status [node-id]
aurora bridge list
aurora bridge sync <repo>

Options (register):
  --port PORT            Port number
  --region REGION        Geographic region

Examples:
  aurora bridge register node-01 --port 8000 --region us-west
  aurora bridge status
  aurora bridge sync my-repo
```

---

### 3.7 Decision Intelligence

#### `aurora decision`

Decision intelligence tools.

```bash
aurora decision oracle [options]
aurora decision monte-carlo [options]
aurora decision forecast [options]

Options (oracle):
  --option OPTION        Add option (can be repeated)
  --criteria KEY=WEIGHT  Add criteria with weight
  --samples N            Monte Carlo samples (default: 10000)

Examples:
  aurora decision oracle \
    --option "Cloud Provider A" \
    --option "Cloud Provider B" \
    --option "On-Premise" \
    --criteria cost=0.4 \
    --criteria performance=0.3 \
    --criteria security=0.3
```

---

### 3.8 Code Generation

#### `aurora generate`

Generate code and templates.

```bash
aurora generate client <language> [options]
aurora generate examples <scenario>
aurora generate config

Options (client):
  --output DIR           Output directory
  --language LANG        Client language (python, javascript, go)

Examples:
  aurora generate client python --output ./client
  aurora generate examples supply_chain
  aurora generate config > aurora.yaml
```

---

### 3.9 Deployment

#### `aurora deploy`

Deploy Aurora applications.

```bash
aurora deploy [options]

Options:
  --platform PLATFORM    Deployment platform (docker, kubernetes, lambda)
  --env ENV              Environment (dev, staging, prod)
  --build                Build before deploy
  --config FILE          Deployment config file

Examples:
  aurora deploy --platform docker
  aurora deploy --platform kubernetes --env production
```

---

### 3.10 Utilities

#### `aurora validate`

Validate files and configurations.

```bash
aurora validate config <file>
aurora validate scenario <file>

Examples:
  aurora validate config aurora.yaml
  aurora validate scenario scenario.json
```

#### `aurora format`

Format configuration files.

```bash
aurora format <file>

Examples:
  aurora format scenario.json
  aurora format aurora.yaml
```

#### `aurora docs`

Open documentation.

```bash
aurora docs [topic]

Examples:
  aurora docs                    # Open main docs
  aurora docs scenarios          # Open scenarios guide
  aurora docs api               # Open API reference
```

#### `aurora playground`

Open playground in browser.

```bash
aurora playground

Examples:
  aurora playground
  Opening playground at https://playground.aurora.dev...
```

---

## 4. Architecture

### 4.1 Package Structure

```
aurora-cli/
├── src/
│   └── aurora_cli/
│       ├── __init__.py
│       ├── __main__.py          # Entry point
│       ├── cli.py               # Main CLI app (typer)
│       │
│       ├── commands/            # Command implementations
│       │   ├── __init__.py
│       │   ├── init.py          # aurora init
│       │   ├── auth.py          # aurora auth
│       │   ├── config.py        # aurora config
│       │   ├── dev.py           # aurora dev
│       │   ├── scenario.py      # aurora scenario
│       │   ├── memory.py        # aurora memory
│       │   ├── bridge.py        # aurora bridge
│       │   ├── decision.py      # aurora decision
│       │   ├── generate.py      # aurora generate
│       │   ├── deploy.py        # aurora deploy
│       │   └── utils.py         # aurora validate, format, etc.
│       │
│       ├── templates/           # Project templates
│       │   ├── python/
│       │   ├── javascript/
│       │   └── docker/
│       │
│       ├── core/
│       │   ├── client.py        # SDK client wrapper
│       │   ├── config.py        # Config management
│       │   └── output.py        # Output formatting
│       │
│       └── utils/
│           ├── console.py       # Rich console output
│           ├── spinner.py       # Progress indicators
│           └── validators.py    # Input validation
│
├── tests/
├── pyproject.toml
└── README.md
```

### 4.2 Technology Stack

**CLI Framework:** Typer (builds on Click)
- Type hints for automatic validation
- Auto-generated help
- Command grouping
- Shell completion

**Output:** Rich
- Colored output
- Progress bars
- Tables
- Syntax highlighting

**Configuration:** PyYAML + python-dotenv
- YAML config files
- Environment variables
- Hierarchical config

**SDK:** aurora-sdk
- Reuse SDK for API calls
- Consistent error handling

---

## 5. Configuration

### 5.1 Config File Locations

Searched in order:

1. `--config` flag
2. `.aurora/config.yaml` (project)
3. `~/.aurora/config.yaml` (user)
4. Environment variables

### 5.2 Config Format

```yaml
# .aurora/config.yaml
api_key: sk_test_...
base_url: http://localhost:8000
timeout: 30
max_retries: 3

# Default scenario params
scenarios:
  supply_chain:
    num_suppliers: 5
    demand_variance: 0.2

# CLI preferences
cli:
  color: true
  format: text
  verbose: false
```

---

## 6. Output Formatting

### 6.1 Text Output (Default)

```bash
$ aurora scenario run supply_chain --param suppliers=5

⣽ Running scenario... (2.3s)

✓ Scenario completed

Scenario ID: scen_abc123
Optimal State: [1, 0, 1, 0, 1]
Cost Reduction: 23.4%
Execution Time: 1.24s

Metrics:
  cost_reduction: 23.4
  reliability: 0.95
  efficiency: 0.87
```

### 6.2 JSON Output

```bash
$ aurora scenario run supply_chain --format json

{
  "scenario_id": "scen_abc123",
  "scenario_type": "supply_chain_optimization",
  "status": "completed",
  "optimal_state": [1, 0, 1, 0, 1],
  "metrics": {
    "cost_reduction": 23.4,
    "reliability": 0.95,
    "efficiency": 0.87
  },
  "execution_time": 1.24
}
```

### 6.3 Table Output

```bash
$ aurora memory list

┌──────────────┬────────────────────┬────────┬──────────┬───────────┐
│ ID           │ Content            │ Tier   │ Tags     │ Created   │
├──────────────┼────────────────────┼────────┼──────────┼───────────┤
│ mem_abc123   │ User preferences   │ active │ prefs    │ 2 days    │
│ mem_def456   │ Algorithm results  │ active │ quantum  │ 1 week    │
│ mem_ghi789   │ Historical data    │ arch   │ history  │ 1 month   │
└──────────────┴────────────────────┴────────┴──────────┴───────────┘
```

---

## 7. Error Handling

### 7.1 User-Friendly Errors

```bash
$ aurora scenario run invalid_scenario

✗ Error: Scenario not found

Available scenarios:
  • supply_chain_optimization
  • energy_grid_balancing
  • risk_assessment
  • portfolio_optimization

Run 'aurora scenario list' to see all available scenarios.
```

### 7.2 Verbose Mode

```bash
$ aurora scenario run supply_chain --verbose

[DEBUG] Loading config from /home/user/.aurora/config.yaml
[DEBUG] API key: sk_test_...abc (last 3 chars)
[DEBUG] Base URL: http://localhost:8000
[INFO] Initializing Aurora client...
[DEBUG] Creating HTTP transport...
[INFO] Running scenario: supply_chain_optimization
[DEBUG] Request: POST /quantum/scenario/supply_chain
[DEBUG] Params: {"num_suppliers": 5, "demand_variance": 0.2}
[DEBUG] Response: 201 Created (1.24s)
[INFO] Scenario completed: scen_abc123
```

---

## 8. Shell Completion

Support for bash, zsh, fish:

```bash
# Install completion
aurora --install-completion

# Use completion
aurora scen<TAB>
aurora scenario <TAB>
  run       -- Run a quantum scenario
  list      -- List available scenarios
  describe  -- Describe a scenario
  template  -- Get scenario template
```

---

## 9. Plugin System

Future: Allow custom commands via plugins.

```python
# ~/.aurora/plugins/my_plugin.py
from aurora_cli.plugin import Plugin

class MyPlugin(Plugin):
    name = "my-command"

    def run(self, args):
        print("Hello from plugin!")
```

```bash
aurora my-command
Hello from plugin!
```

---

## 10. Examples

### 10.1 Complete Workflow

```bash
# 1. Initialize project
aurora init quantum-supply-chain --template python
cd quantum-supply-chain

# 2. Configure
aurora config set api_key sk_live_...

# 3. Edit scenario config
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
aurora validate scenario scenarios/supply_chain.json
✓ Scenario configuration is valid

# 5. Run scenario
aurora scenario run supply_chain --config scenarios/supply_chain.json --output results.json
⣽ Running scenario... (3.2s)
✓ Scenario completed
Results saved to results.json

# 6. Save to memory
aurora memory create "Supply chain results from 2025-11-09" \
  --tag results --tag supply_chain

# 7. Search memories
aurora memory search "supply chain" --top-k 5
```

---

## 11. Testing

### 11.1 Unit Tests

```python
from typer.testing import CliRunner
from aurora_cli.cli import app

runner = CliRunner()

def test_scenario_list():
    result = runner.invoke(app, ["scenario", "list"])
    assert result.exit_code == 0
    assert "supply_chain_optimization" in result.output
```

### 11.2 Integration Tests

Test against live API (local dev server).

---

## 12. Distribution

### 12.1 PyPI Package

```bash
pip install aurora-cli
```

### 12.2 Standalone Binary

Use PyInstaller to create standalone executable:

```bash
# macOS
aurora-macos-x64

# Linux
aurora-linux-x64

# Windows
aurora-windows-x64.exe
```

---

## 13. Dependencies

```toml
[project]
dependencies = [
    "aurora-sdk>=0.1.0",      # Aurora SDK
    "typer>=0.9.0",           # CLI framework
    "rich>=13.0.0",           # Rich output
    "pyyaml>=6.0",            # YAML config
    "python-dotenv>=1.0.0",   # .env files
    "httpx>=0.28.0",          # HTTP client
]
```

---

## 14. Future Enhancements

- Interactive mode (REPL)
- Scenario wizard (guided creation)
- Deployment pipelines
- CI/CD integrations
- Metrics dashboard
- Log streaming
- File watching for auto-reload

---

**Status:** Ready for Implementation
**Next Steps:** Implement core CLI with typer
