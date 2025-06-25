# Aurora Reflective Autonomy System

A fully operational, ethics-aligned symbolic governance and self-healing system.

## Features
- Modular symbolic governance engine
- Self-monitoring and self-healing autonomy loop
- Ethics protocol and governance capsule
- Full audit logging and restoration capability

## Quick Start
```bash
git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic
make install
make run
```

## Directory Structure
- `modules/reflective_autonomy/` — Core system modules
- `config/` — Configuration files
- `scripts/` — Deployment and helper scripts
- `docs/` — Documentation
- `tests/` — Unit and integration tests
- `logs/` — Runtime and audit logs
- `.github/` — CI/CD and templates

## Node.js Command Node Service

A Node.js command node service is orchestrated alongside the Python backend using Docker Compose.

- Service directory: `services/command_node/`
- To build and run all services:

```bash
docker-compose up --build
```

- The command node listens on port 3001 by default.
- Replace the placeholder app in `services/command_node/` with your real Node.js code when ready.

## Aurora Instance Bridge

An optional bridge service enables live message relays between multiple Aurora instances. Run the server:

```bash
python -m modules.instance_bridge.bridge_server
```

Connect an instance using the included client:

```bash
python -m modules.instance_bridge.bridge_client ws://localhost:8090 main example-id
```

Each channel aggregates messages across platforms, allowing chat fields to stay synchronized.

## Orion Backup Sync Utility
Use `python scripts/orion_backup_sync.py --help` to export and synchronize the staff registry and Orion Station blueprint. Backups are stored in `backups/` and `--rollback` restores the latest snapshot.

## Module Integration Tool
Use `python scripts/module_integrator.py --help` to merge new modules across branches. The tool validates anchor compliance, logs telemetry to `logs/telemetry.log`, and supports per-module rollback.


## Contributing
See `CONTRIBUTING.md` for guidelines.

## License
See `LICENSE` for terms.
