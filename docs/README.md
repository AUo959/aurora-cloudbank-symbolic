# Aurora CloudBank - Documentation Index

## 📚 **Comprehensive Documentation Suite**

Welcome to the Aurora CloudBank documentation. This quantum-symbolic platform includes documentation for setup, runtime governance, development planning, security, observability, and advanced symbolic/quantum modules.

## 🧭 **Current Development Control Plane**

Start here when deciding what to build, review, or triage next:

- **[Current Development Roadmap](ROADMAP.md)** — central priority and sequencing document
- **[Review Notes Intake Queue](review-notes/README.md)** — persistent destination for outside reviews, session observations, risks, and architectural tensions
- **[Runtime API Governance](api/API_CATALOG_GOVERNANCE.md)** — source-of-truth rules for active API surfaces
- **[Runtime Topology and L3 Authority](architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md)** — current runtime authority map
- **[Runtime Path Drift Ledger](architecture/RUNTIME_PATH_DRIFT_LEDGER.md)** — stale/conflicting path and route claims to resolve

## 🛡️ **Rebuild Protection System**

- **[Rebuild Failure Prevention](../REBUILD_FAILURE_PREVENTION.md)** - Complete guide to the rebuild protection system
- **[Rebuild Protection Status](../REBUILD_PROTECTION_ACTIVATED.md)** - Current system status and emergency commands
- **Emergency Commands**:
  - `bash scripts/emergency_rebuild_recovery.sh` - Complete disaster recovery
  - `python3 scripts/prevent_rebuild_failures.py` - System validation
  - `bash scripts/activate_rebuild_protection.sh` - Protection status

## 🏆 **System Health & Optimization**

- **[Health Optimization Complete](../AURORA_HEALTH_OPTIMIZATION_COMPLETE.md)** - Historical 95.8/100 achievement report
- **[Security Guidelines](SECURITY_GUIDELINES.md)** - Enterprise-grade security framework
- **[Dependency Management](DEPENDENCY_MANAGEMENT.md)** - Dependency handling guidance

## 🚀 **Quick Start & Setup**

- **[Main README](../README.md)** - Complete project overview and quick start
- **[Phase 0 Completion Report](PHASE0_COMPLETION_REPORT.md)** - Security baseline implementation
- **[Playground Quickstart](PLAYGROUND_QUICKSTART.md)** - Gallery-driven starter scenarios with PII masking defaults

## 🔧 **Technical Documentation**

- **[Architecture Overview](architecture.md)** - Quantum-symbolic system design
- **[API Schema Documentation](symbolicvector_api_schema.md)** - VSA-based symbolic data structures
- **[API Surface Inventory](api/api_surface_inventory.json)** - Machine-readable API surface registry

## 🌟 **Advanced Features**

- **VSA-Based Symbolic Data** - Vector Symbolic Architecture implementation (see `modules/symbolic_core/vsa.py`)
- **Opal2 Graphics Module** - Quantum symbolic vector graphics processing (see `modules/opal2/`)
- **Quantum Computing Integration** - Hybrid quantum-classical processing capabilities

## 📋 **Recent Planning Updates**

### [2026-05-28] Central roadmap and review intake wiring

- Added `docs/ROADMAP.md` as the active development roadmap.
- Promoted `docs/review-notes/` as the persistent intake queue for outside/session reviews.
- Linked runtime governance, topology, and path-drift docs from this index.

### [2025-09-27] Bulletproof Rebuild Protection System

- Multi-layer failsafe system prevents DevContainer rebuild failures.
- Emergency recovery scripts support disaster scenarios.
- Automatic backup creation includes timestamped state preservation.
- Comprehensive logging and audit trails are documented.

### [2025-06-30] Opal2 Graphics Card Module

- Introduces `modules/opal2` with the first Opal2 component.
- `GlyphGenerator` combines geometric algebra with quantum symbolic vectors.
- Designed to function as a lightweight graphics card for hybrid symbolic processing.
- Configuration lives in `config/opal2_graphics.yaml`.

### [2025-06-25] VSA-Based Symbolic Data & API Schema Update

- Symbolic data structures are now VSA-based (see `modules/symbolic_core/vsa.py`).
- All symbolic REST/WebSocket endpoints use the `SymbolicVector` JSON schema.
- Extension points support quantum/geometric plugins.

## 🚀 **Getting Started**

1. **Clone Repository**: `git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git`
2. **Quick Setup**: `make setup`
3. **Validate System**: `make check`
4. **Review Current Work**: read [`ROADMAP.md`](ROADMAP.md)

## 🆘 **Emergency Support**

If you encounter setup or runtime issues:

1. **System Health**: `python3 scripts/prevent_rebuild_failures.py`
2. **Emergency Recovery**: `bash scripts/emergency_rebuild_recovery.sh`
3. **Protection Status**: `bash scripts/activate_rebuild_protection.sh`

---

*Built for consistency, clarity, and care.*
