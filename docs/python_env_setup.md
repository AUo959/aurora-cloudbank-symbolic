# Python Environment Quickstart

This guide prevents the recurring `externally-managed-environment` error that appears when trying to
install packages such as **NumPy** or **pytest** inside the base Debian image. The fix is to provision a
user-scoped virtual environment and install the required Debian helpers (`python3-pip`, `python3-venv`).

## TL;DR

```bash
# From the repository root (inside the devcontainer)
./scripts/setup_python_venv.sh
source "$HOME/.venvs/aurora-cloudbank/bin/activate"
python -m pytest tests/nexus/unit/test_hybrid_orchestrator.py -v
```

## Why this is needed

- Debian 13 ships Python 3.13 with [PEP 668](https://peps.python.org/pep-0668/) protection enabled, so
  `pip install` writes are rejected unless you isolate them in a virtual environment.
- The default image omits `pip`/`venv`, so the first step is to install `python3-pip` and `python3-venv` via apt.
- Using a user-level venv keeps system packages intact and avoids permission issues.

## What the helper script does

`scripts/setup_python_venv.sh` performs the following steps safely and idempotently:

1. Installs the Debian packages `python3-pip` and `python3-venv` if they are missing.
2. Creates a reusable virtual environment at `~/.venvs/aurora-cloudbank` (configurable via environment variables).
3. Upgrades `pip` inside that environment.
4. Installs the baseline tooling expected by the tests (`numpy`, `pytest`).

You can re-run the script at any time; it will skip work when everything is already in place.

## Using the environment

Activate the environment for an interactive session:

```bash
source "$HOME/.venvs/aurora-cloudbank/bin/activate"
```

Or invoke the interpreter directly without activation:

```bash
$HOME/.venvs/aurora-cloudbank/bin/python -m pytest tests/...
```

## Customising

- Override the Python binary: `PYTHON_BIN=/usr/bin/python3 ./scripts/setup_python_venv.sh`
- Change the virtual environment location: `AURORA_VENV_ROOT="$HOME/.cache/venvs" ./scripts/setup_python_venv.sh`
- Install extra packages afterwards: `~/.venvs/aurora-cloudbank/bin/pip install black isort`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `sudo: command not found` | Run inside the provided devcontainer or install the Debian packages manually. |
| `python3: No module named ensurepip` | Re-run the script; it installs `python3-pip`/`python3-venv`, which contain `ensurepip`. |
| `externally-managed-environment` persists | Ensure you're using the virtual environment's `pip` (`~/.venvs/aurora-cloudbank/bin/pip`). |

Following this workflow keeps future `pip install` operations clean and prevents accidental modifications to the
system Python installation.
