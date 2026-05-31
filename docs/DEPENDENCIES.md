# Aurora CloudBank Dependencies

Aurora CloudBank currently tracks three root-level Python requirements files.
Keep this page and `CLAUDE.md` aligned with the actual files in the repository.

## Dependency Files

| File | Purpose | Typical use |
|------|---------|-------------|
| `requirements.txt` | Core runtime dependencies | Application runtime, containers, dependency CI |
| `requirements-dev.txt` | Development and test tooling | Local testing, linting, maintenance scripts |
| `requirements-optional.txt` | Optional integrations and heavier feature dependencies | Quantum cloud backends, notebooks, telemetry extensions |

## Recommended Setup

```bash
make setup
```

`make setup` runs `scripts/setup_environment.sh`, installs `requirements.txt`,
and then installs `requirements-dev.txt` when present.

For a direct runtime-only install:

```bash
pip install -r requirements.txt
```

For local work that needs optional integrations:

```bash
pip install -r requirements.txt -r requirements-optional.txt
```

## Inventory Guard

Run the requirements inventory audit after changing dependency docs,
workflows, or setup scripts:

```bash
python scripts/audit_requirements_inventory.py
```

The audit fails if current operational docs or dependency CI reference a
root-level `requirements*.txt` file that is not tracked in the repository.

## Maintenance Rules

1. Add runtime packages to `requirements.txt`.
2. Add test, lint, and maintenance tooling to `requirements-dev.txt`.
3. Add optional integrations or heavyweight feature dependencies to
   `requirements-optional.txt`.
4. Update this document and run the inventory audit whenever the tracked
   requirements inventory changes.
