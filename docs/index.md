# Aurora CloudBank Symbolic — Documentation Index

This directory contains reference documentation for developers working with Aurora CloudBank Symbolic. This index is a navigation surface, not a blanket authority grant: use [`CANON_INDEX.md`](../CANON_INDEX.md) for canonical doctrine and committed runtime code plus tests for behavioral truth.

## Directory authority map

| Directory | Purpose | Authority note |
| --- | --- | --- |
| [`api/`](api/) | API catalogs, governance, schemas, and inventory snapshots | Follow [`api/API_CATALOG_GOVERNANCE.md`](api/API_CATALOG_GOVERNANCE.md) before treating a catalog as current runtime truth. |
| [`architecture/`](architecture/) | Active architecture, topology, and authority-boundary references | [`architecture/LAYER_ARCHITECTURE.md`](architecture/LAYER_ARCHITECTURE.md) is canonical for the L1/L2/L3 model; other files state their own scope. |
| [`ethics/`](ethics/) | Ethics navigation, evaluations, and recovered-protocol planning | [`ethics/README.md`](ethics/README.md) preserves the boundary between runtime evidence and planning artifacts. |
| [`qgia/`](qgia/) | Staged QGIA integration document package | Read [`qgia/README.md`](qgia/README.md) first. Indexing does not activate, register, or canon-promote the package. |
| [`specs/`](specs/) | Technical and promotion specifications | A specification is not proof of implementation; verify status in code and tests. |
| [`modules/`](modules/) | Module-facing documentation | Runtime modules and their tests remain authoritative for behavior. |
| [`reference/`](reference/) | Convenience catalogs and reference guides | Verify generated or snapshot material against its governed source before citing it as current. |
| [`security/`](security/) | Remediation records, status reports, and penetration-test scope/history | Root [`SECURITY.md`](../SECURITY.md) governs disclosure policy; current controls require code and test evidence. |
| [`review-notes/`](review-notes/) | Dated review and audit evidence | Non-canonical observations; revalidate findings against live repository state. |
| [`archive/`](archive/) | Superseded, historical, or custody material | Historical context only; archive placement does not confer current authority. |

## Root structural controls

| File | Semantics |
| --- | --- |
| [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) | The single canonical pre-commit configuration. `pre-commit` discovers this default filename, and repository scripts target it directly. |
| `.rebuild_prevention_active` | An ignored, local timestamp receipt written in the script's current working directory (normally the repository root) by [`scripts/activate_rebuild_protection.sh`](../scripts/activate_rebuild_protection.sh). No build or runtime path consumes it as an enforcement lock; it is safe to delete and regenerate. |

---

## Setup and Development

| Document | Description |
| --- | --- |
| [python_env_setup.md](python_env_setup.md) | Python environment setup and virtual env configuration |
| [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md) | Running tests locally, markers, coverage |
| [CODE_QUALITY_SYSTEM.md](CODE_QUALITY_SYSTEM.md) | Linting, formatting, and automated quality gates |
| [DEPENDENCY_VERSION_POLICY.md](DEPENDENCY_VERSION_POLICY.md) | Dependency pinning and version policy |
| [DEPENDENCY_MANAGEMENT.md](DEPENDENCY_MANAGEMENT.md) | Managing and updating dependencies |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Full dependency listing with notes |

## API Reference

| Document | Description |
| --- | --- |
| [reference/API_CATALOG.md](reference/API_CATALOG.md) | Complete route listing for all 30+ routers |
| [reference/v2_API_REFERENCE.md](reference/v2_API_REFERENCE.md) | Detailed API reference guide |
| [api/API_CATALOG.json](api/API_CATALOG.json) | Machine-readable API catalog (JSON) |
| [api/api_schema.json](api/api_schema.json) | OpenAPI schema snapshot |

## Core Modules

| Document | Description |
| --- | --- |
| [QUANTUM_FORGE_V3_COMPLETE_GUIDE.md](QUANTUM_FORGE_V3_COMPLETE_GUIDE.md) | Quantum Forge v3.0 — agent generation, entanglement networks, joy evolution |
| [QUANTUM_FORGE_V3_QUICK_REFERENCE.md](QUANTUM_FORGE_V3_QUICK_REFERENCE.md) | Quantum Forge v3.0 quick reference card |
| [QUANTUM_CLOUD_BACKENDS.md](QUANTUM_CLOUD_BACKENDS.md) | AWS Braket, Azure Quantum, IBM Quantum, Google Cirq integration |
| [R2_AGENT_TELEMETRY.md](R2_AGENT_TELEMETRY.md) | R2 Agent Telemetry — distributed tracing, Prometheus metrics, anomaly detection |
| [SYNERGY_DASHBOARD.md](SYNERGY_DASHBOARD.md) | Component registry, dependency graph, health monitoring |
| [SYNERGY_DASHBOARD_QUICKSTART.md](SYNERGY_DASHBOARD_QUICKSTART.md) | Synergy Dashboard quick start |
| [SYNERGY_DASHBOARD_UI.md](SYNERGY_DASHBOARD_UI.md) | Synergy Dashboard UI reference |
| [CONNECTOR_SDK.md](CONNECTOR_SDK.md) | Connector SDK — building custom connectors |
| [CONNECTOR_FRAMEWORK_GUIDE.md](CONNECTOR_FRAMEWORK_GUIDE.md) | Connector framework internals |
| [CONNECTOR_QUICK_REFERENCE.md](CONNECTOR_QUICK_REFERENCE.md) | Connector quick reference card |

## QGIA Integration (Staged)

This portal provides contributor navigation only. The
[`CANON_INDEX.md` QGIA section](../CANON_INDEX.md#qgia-integration-staged-documentation-package)
is the AI-agent routing map, and [`qgia/README.md`](qgia/README.md) governs the
package's provenance and authority boundaries. The documents remain `STAGING`
and `DOCUMENT_PACKAGE_ONLY`; links here do not implement runtime activation.

| Document | Description |
| --- | --- |
| [qgia/README.md](qgia/README.md) | Package scope, provenance, review order, and non-activation boundary |
| [qgia/QGIA_Runtime_OnePager.md](qgia/QGIA_Runtime_OnePager.md) | Reviewed analytical-process snapshot |
| [qgia/QGIA_Axiom_Doctrine_Narrative.md](qgia/QGIA_Axiom_Doctrine_Narrative.md) | Axiom doctrine and runtime-application rationale |
| [qgia/QUANTUM_FORGE_Axiom_Node_Manifest.md](qgia/QUANTUM_FORGE_Axiom_Node_Manifest.md) | Reconciled 23-node human-readable axiom registry |
| [qgia/SIM_WATCHCON_Confidence_Module.md](qgia/SIM_WATCHCON_Confidence_Module.md) | Confidence and WATCHCON contract |
| [qgia/GUMAS_Audit_Schema.md](qgia/GUMAS_Audit_Schema.md) | GUMAS ethics-audit event specification |
| [qgia/RESETCORE_Bootstrap.md](qgia/RESETCORE_Bootstrap.md) | Explicit session-restore reference |
| [qgia/PAT_Command_Sheet.md](qgia/PAT_Command_Sheet.md) | PAT operator command reference |

## Ethics and Safety

| Document | Description |
| --- | --- |
| [GEOMETRIC_ETHICS_ARCHITECTURE.md](GEOMETRIC_ETHICS_ARCHITECTURE.md) | Five-dimension geometric ethics field — picard_delta_3, thermax_continuity, layer_integrity, collective_welfare, transparency |
| [LAYER_BOUNDARY_REFERENCE.md](LAYER_BOUNDARY_REFERENCE.md) | L1/L2/L3 layer boundary enforcement reference |
| [ethics/geometric_curvature_v2_evaluation.md](ethics/geometric_curvature_v2_evaluation.md) | Geometric ethics curvature v2 — interaction-aware model evaluation (issue #994) |
| [DLP_GOVERNANCE_POLICY.md](DLP_GOVERNANCE_POLICY.md) | Data Lineage Protocol governance and compliance |
| [MONITORING_SYSTEM.md](MONITORING_SYSTEM.md) | Drift detection, ethics engine, behavioral monitoring, audit logger |
| [MONITORING_QUICKSTART.md](MONITORING_QUICKSTART.md) | Monitoring quick start |
| [TELEMETRY_OBSERVABILITY.md](TELEMETRY_OBSERVABILITY.md) | Observability architecture and instrumentation |
| [OPENTELEMETRY.md](OPENTELEMETRY.md) | OpenTelemetry integration guide |

## Security and Auth

| Document | Description |
| --- | --- |
| [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md) | Security implementation guidelines |
| [SECURITY_PATTERNS.md](SECURITY_PATTERNS.md) | Security patterns and anti-patterns |
| [OAUTH2_SETUP_GUIDE.md](OAUTH2_SETUP_GUIDE.md) | OAuth2 and JWT authentication setup |
| [RBAC_INTEGRATION_EXAMPLES.md](RBAC_INTEGRATION_EXAMPLES.md) | Role-based access control integration examples |
| [RBAC_SECURITY_SUMMARY.md](RBAC_SECURITY_SUMMARY.md) | RBAC security model summary |
| [Rate-Limiting.md](Rate-Limiting.md) | Rate limiting configuration and strategies |
| [security/pentest_scope_v1.md](security/pentest_scope_v1.md) | Penetration test scope definition |
| [security/SECURITY_FIXES.md](security/SECURITY_FIXES.md) | Security fix log |

## Deployment

| Document | Description |
| --- | --- |
| [DEVELOPER_DEPLOYMENT_GUIDE.md](DEVELOPER_DEPLOYMENT_GUIDE.md) | Deployment options and environment configuration |
| [VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md) | Vercel deployment guide for web frontend |

## Architecture

| Document | Description |
| --- | --- |
| [architecture/SYMBOLIC_DATA_ARCHITECTURE.md](architecture/SYMBOLIC_DATA_ARCHITECTURE.md) | Scoped VSA symbolic-data and schema overview |
| [architecture/LAYER_ARCHITECTURE.md](architecture/LAYER_ARCHITECTURE.md) | L1/L2/L3 layer architecture detail |
| [architecture/SYSTEM_ARCHITECTURE_DIAGRAM.md](architecture/SYSTEM_ARCHITECTURE_DIAGRAM.md) | System architecture diagram and component map |
| [architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md](architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md) | Runtime topology reference |

## Specs

| Document | Description |
| --- | --- |
| [specs/CLI_TECHNICAL_SPEC.md](specs/CLI_TECHNICAL_SPEC.md) | CLI technical specification |
| [specs/PYTHON_SDK_TECHNICAL_SPEC.md](specs/PYTHON_SDK_TECHNICAL_SPEC.md) | Python SDK technical specification |
| [specs/AUMEMMANAGER_PROMOTION_STARTER_SPEC.md](specs/AUMEMMANAGER_PROMOTION_STARTER_SPEC.md) | AuMemManager promotion specification |

## Operations

| Document                                                          | Description                  |
| ----------------------------------------------------------------- | ---------------------------- |
| [INCIDENT_RESPONSE_RUNBOOK.md](INCIDENT_RESPONSE_RUNBOOK.md)      | Incident response procedures |

---

## Not finding what you need?

- See `docs/archive/` for historical internal reports, phase summaries, and session notes.
- The interactive API docs are at `http://localhost:8000/docs` when the server is running.
- `API_CATALOG.md` (root) has the full route listing.
- `CONTRIBUTING.md` (root) has the contribution guide.
- `CLAUDE.md` (root) has AI assistant guidance for working with this codebase.
