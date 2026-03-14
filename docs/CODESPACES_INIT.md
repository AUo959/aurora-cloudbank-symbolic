# Infallible Codespaces Initialization

This guide describes the self-healing bootstrap process used by the Aurora repository.

## Overview

The script `scripts/infallible_codespace_init.py` is executed automatically when a Codespace is created. It bootstraps the Python environment, installs Node dependencies when needed, and runs the onboarding hook. When you run it locally outside Codespaces, it defaults to a diagnostic dry run so you can inspect the plan before mutating the machine.

You can re-run the bootstrap script at any time:

```bash
python3 scripts/infallible_codespace_init.py
python3 scripts/infallible_codespace_init.py --execute
```

Use `--execute` for a local rebuild. The plain command is useful for checking what the script would do before it changes the environment.
