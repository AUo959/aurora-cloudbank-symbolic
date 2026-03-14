# Python Bootstrap Automation

## Source Of Truth

- The repository pins its target interpreter in `.python-version`.
- `scripts/ensure_python.sh` is the canonical runtime discovery and installation helper.
- `scripts/setup_dependencies.sh` is the canonical environment bootstrap entrypoint.

## Recommended Flows

Diagnose the machine state:

```bash
scripts/ensure_python.sh
scripts/setup_dependencies.sh
```

Install or upgrade Python 3.11 with the first available installer and build `.venv`:

```bash
scripts/setup_dependencies.sh --execute --install-python
```

Install optional Python extras as well:

```bash
scripts/setup_dependencies.sh --execute --install-python --include-optional
```

## Supported Installers

- `uv`
- `pyenv`
- `brew`

If none of those are installed, `scripts/ensure_python.sh` stays diagnostic and reports exactly what is missing instead of mutating the host unexpectedly.

## Dependency Maintenance

Scan the canonical Python environment and verify FastAPI presence:

```bash
python3 scripts/gitwiz_dependency_updater.py --scan --output logs/dependency_status.json
```

Rebuild the repo environment and then upgrade Python dependencies from the requirements files:

```bash
python3 scripts/gitwiz_dependency_updater.py --ensure-env --upgrade-python --apply --check-outdated
```

Run the same flow through the canonical maintenance entrypoint:

```bash
python3 scripts/gitwiz.py optimize --ensure-python-env --upgrade-python-deps --check-outdated
```
