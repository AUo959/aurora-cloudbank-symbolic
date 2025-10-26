# Aurora CloudBank CLI Tools

This directory contains command-line interface tools for the Aurora CloudBank Symbolic platform.

## Available Tools

### 🌟 Onboarding Wizard (`onboarding_wizard.py`)

**NEW!** Interactive wizard to guide new developers through Aurora CloudBank setup and best practices.

#### Features
- **Environment Health Check**: Verify your development environment via `make health-check`
- **Automated Setup**: Run `make setup` to prepare your environment
- **Makefile Commands**: Discover and learn about available make commands
- **Symbolic Anchor Tracking**: Learn to track and manage symbolic anchors
- **Memory Sealing**: Understand file/directory sealing for integrity
- **Quicksave Workflow**: Master quicksave operations (create, list, load)
- **Demos & API**: Launch demos and start the API server
- **Interactive Prompts**: Confirm before executing each action
- **Clear Guidance**: Educational content throughout

#### Usage

Run the onboarding wizard:

```bash
python tools/cli/onboarding_wizard.py
```

Or using Python 3:

```bash
python3 tools/cli/onboarding_wizard.py
```

The wizard will guide you through each step interactively, allowing you to:
- Skip steps you've already completed
- Learn about Aurora CloudBank features
- Execute setup commands with confirmation
- Explore the symbolic infrastructure

#### What You'll Learn

1. **Environment Setup** - Get your development environment ready
2. **Make Commands** - Understand the key Makefile targets
3. **Symbolic Anchors** - Track T-series threads and DLP tags
4. **Memory Sealing** - Protect and verify code snapshots
5. **Quicksave System** - Save and restore work contexts
6. **System Demos** - Explore quantum and AI capabilities

#### Completion Record

Upon completion, the wizard saves a record to:
```
.aurora/onboarding/completion_record.json
```

This tracks which steps you've completed and when.

---

### ⚓ Aurora Developer CLI (`aurora_dev_cli.py`)

Unified command interface for symbolic operations.

#### Features
- Automated manifest generation
- Thread sealing and resume capabilities
- Integration with Aurora/GUMAS infrastructure
- State snapshot and restore commands

#### Usage

Track symbolic anchors:
```bash
python tools/cli/aurora_dev_cli.py anchor track
python tools/cli/aurora_dev_cli.py anchor track --pattern T71
python tools/cli/aurora_dev_cli.py anchor resolve <anchor_id>
```

Seal files or directories:
```bash
python tools/cli/aurora_dev_cli.py seal tools/cli
python tools/cli/aurora_dev_cli.py seal file.py --seal-id my_seal
python tools/cli/aurora_dev_cli.py seal <target> --verify --seal-id <id>
```

Generate manifests:
```bash
python tools/cli/aurora_dev_cli.py manifest
python tools/cli/aurora_dev_cli.py manifest --target T71_INFRA
python tools/cli/aurora_dev_cli.py manifest --json
```

System status:
```bash
python tools/cli/aurora_dev_cli.py status
python tools/cli/aurora_dev_cli.py status --json
```

For full help:
```bash
python tools/cli/aurora_dev_cli.py --help
```

---

## Quick Start for New Developers

**Start here!** Run the onboarding wizard:

```bash
python tools/cli/onboarding_wizard.py
```

This interactive guide will walk you through:
1. Checking your environment health
2. Setting up dependencies
3. Learning the Makefile commands
4. Understanding symbolic operations
5. Exploring the Aurora CloudBank ecosystem

---

## Related Documentation

- **Main README**: `../../README.md`
- **Contributing Guide**: `../../CONTRIBUTING.md`
- **Tools Overview**: `../README.md`
- **Health Dashboard**: `../../AURORA_HEALTH_OPTIMIZATION_COMPLETE.md`

---

## Support

For questions or issues:
- Review the documentation files listed above
- Check open issues on GitHub
- Join project discussions
- Submit detailed bug reports

---

## Thread Context

**Thread**: T71 → Symbolic Infrastructure Genesis  
**DLP**: context_tag=cli_tools, symbolic_hash=DEVELOPER_TOOLS_v1
