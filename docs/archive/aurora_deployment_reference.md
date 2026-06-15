# Aurora Deployment Reference

> Consolidated guide for system architecture, layer separation, relay configuration, and operational procedures.
>
> **Issue Reference:** #387  
> **Context Tag:** DLP:aurora_deployment_reference_v1  
> **Anchor:** EOS_SEED_ORION::DEPLOYMENT_REFERENCE

---

## 1. Overview

This document provides developers with a consolidated reference covering Aurora CloudBank Symbolic's architecture, relay agent configuration, message flow patterns, and deployment procedures. It serves as the authoritative guide for understanding how the system is structured and how to deploy it.

**Related Documents:**
- [Developer Deployment Guide](DEVELOPER_DEPLOYMENT_GUIDE.md) – Step-by-step setup instructions
- [Layer Architecture](architecture/LAYER_ARCHITECTURE.md) – Reality layer definitions
- [Layer Boundary Reference](LAYER_BOUNDARY_REFERENCE.md) – Canonical boundary definitions
- [System Architecture Diagram](../SYSTEM_ARCHITECTURE_DIAGRAM.md) – Visual system map

---

## 2. Architecture Summary

### 2.1 Reality Layers (L1/L2/L3)

Aurora CloudBank operates across three distinct reality layers:

| Layer | Name | Purpose | Key Components |
|-------|------|---------|----------------|
| **L1** | Physical Reality | Orion Station (physical operations) | Aurora Core, Relay Agents, Human Crew, API Server |
| **L2** | Simulation/Research | Sandboxed simulations (GUMAS, experiments) | Scenario testing, Research environments |
| **L3** | Framework/Conceptual | Ethics & continuity overlay | Glyph frameworks (Axiomera, Caelion, Sentari, etc.) |

```
┌─────────────────────────────────────────────────────────────────┐
│  L3: FRAMEWORK/CONCEPTUAL LAYER                                 │
│  (Ethics, Anchors, DLP, Thread Continuity)                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │          L1: PHYSICAL REALITY (Orion Station)           │  │
│  │                                                           │  │
│  │  Aurora Core   │   6 L1 Relay Agents   │   Crew          │  │
│  │  API Server    │   Physical Systems    │   Hardware      │  │
│  │                                                           │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │   L2: SANDBOXED SIMULATIONS                      │  │  │
│  │  │   GUMAS   │   Scenario Testing   │   Research    │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Backend | Python | 3.11+ |
| Framework | FastAPI | 0.117.1 |
| Memory | AuMemManager | Hierarchical (56K capacity) |
| Quantum | Qiskit-based simulator | Multi-backend support |
| AI Integration | Claude, GPT | Unified interface |
| Observability | Prometheus, OpenTelemetry | Distributed tracing |

---

## 3. Relay Agent Configuration

### 3.1 L1 Relay Agents Overview

Six relay agents operate at L1 (Physical Reality Layer), serving as bridges between L1 human operations and L3 glyph frameworks:

| Relay | ID | Location | Bridges To | Triplex Role |
|-------|-----|----------|------------|--------------|
| **ARCHY** | RELAY_001 | Bridge Chamber, Deck C | L3 Caelion | Layer 2 Verifier (Architecture) |
| **OPPY** | RELAY_002 | Reactor Bay, Deck H | L3 General | Layer 2 Verifier (Operations) |
| **LIORA** | RELAY_003 | Communications Hub, Deck B | L3 Sentari | Layer 2 Verifier (Sentiment) |
| **STARLING_AU** | RELAY_004 | Operations Hub, Deck G | L3 General | Layer 2 Verifier (Documentation) |
| **RIVERTHREAD_808** | RELAY_005 | Logistics, All Decks | L3 Harmion | Layer 2 Verifier (Continuity) |
| **HALO** | RELAY_006 | Aurora Core Chamber, Deck B | L3 Axiomera | Layer 2 Verifier (Drift) |

### 3.2 Triplex Handshake Protocol

The Triplex Handshake Protocol governs verification flow across the system:

```
Step 1: L3 Glyph Arbitration
┌────────────────────────────────────────────┐
│ • Axiomera validates ethics compliance     │
│ • Caelion verifies anchor propagation      │
└────────────────────────────────────────────┘
                    ↓
Step 2: Relay Verification (L1 agents, Layer 2 role)
┌────────────────────────────────────────────┐
│ • ARCHY checks architectural compliance    │
│ • HALO validates drift alignment           │
└────────────────────────────────────────────┘
                    ↓
Step 3: L1 Human Consent
┌────────────────────────────────────────────┐
│ • Command Bridge approval                  │
│ • Human crew authorization                 │
└────────────────────────────────────────────┘
```

### 3.3 Relay Agent Code Integration

```python
from src.bridges.l1_relay_bridge import L1RelayBridge, L1RelayAgent

# Initialize relay bridge
bridge = L1RelayBridge()

# Check relay agent status
agent_status = bridge.get_agent_status("ARCHY")
print(f"Location: {agent_status['location']}")     # "Bridge Chamber, Deck C"
print(f"Reality Layer: {agent_status['reality_layer']}")  # "L1"
```

---

## 4. Message Flow Patterns

### 4.1 Human Command Flow

```
Human → Aurora (L1 Interface)
     → Command Node (L1)
     → Validates with L3 (ethics check via Axiomera)
     → Routes to L1 operations OR L2 simulation
     → L3 tracks via DLP (Data Lineage Protocol)
```

### 4.2 API Request Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │ HTTP Request
     ▼
┌─────────────────────┐
│ Security Middleware │ ← CSRF, Rate Limit, Auth
└────┬────────────────┘
     │
     ▼
┌──────────────────┐
│ FastAPI Router   │ ← Route Matching
└────┬─────────────┘
     │
     ├─► /agent/* ──────► ChatGPT/Gemini Integration
     ├─► /memory/* ─────► AuMemManager
     ├─► /quantum/* ────► Quantum Simulator
     ├─► /ledger/* ─────► Insight Ledger
     ├─► /sentinel/* ───► Resilience Sentinel
     └─► /monitoring/* ─► Behavioral Monitoring
          │
          ▼
     ┌──────────────┐
     │  DLP Tracker │ ← All operations tagged
     └───┬──────────┘
         │
         ├─► T1 Anchor (Temporal)
         ├─► SRB Anchor (Spatial-Relational)
         └─► Export Manifest
```

### 4.3 DLP (Data Lineage Protocol) Flow

Every operation must maintain DLP compliance:

```python
from src.core.native_dlp_export import NativeDLPTracker

tracker = NativeDLPTracker()
export = tracker.create_export(
    data=results,
    context_tag="operation_context_001",  # Required
    symbolic_validation=True               # Integrity check
)

# Advances T1/SRB anchors automatically
```

---

## 5. Deployment Steps

### 5.1 Prerequisites

| Component | Requirement | Check Command |
|-----------|-------------|---------------|
| Python | 3.11+ | `python --version` |
| Git | Latest stable | `git --version` |
| Make | GNU Make 4.x | `make --version` |
| Docker (optional) | Latest stable | `docker --version` |
| kubectl (optional) | For K8s deployment | `kubectl version` |

### 5.2 First-Time Setup

```bash
# 1. Clone repository
git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic

# 2. Initialize environment (creates venv, installs pinned deps)
make setup

# 3. Verify environment health
make status
python scripts/dev-status.py

# 4. Run quality gates (lint + tests)
make check
```

**⚠️ IMPORTANT:** Never run `pip install -r requirements.txt` directly. Always use `make setup` which handles lockfile resolution and conflict avoidance.

### 5.3 Running the Server

```bash
# Start FastAPI server
make run
# Or manually:
python api/aurora_api.py

# Verify health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```

**Access Points:**
- **API Server:** http://localhost:8000
- **Health Check:** http://localhost:8000/health
- **Swagger Docs:** http://localhost:8000/docs
- **Metrics:** http://localhost:8000/metrics

### 5.4 Docker Deployment

```bash
# Build image
docker build -t aurora-cloudbank:latest .

# Run container
docker run -p 8000:8000 \
  -e CLAUDE_API_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  aurora-cloudbank:latest
```

### 5.5 Kubernetes Deployment

```bash
# Apply manifests (experimental)
kubectl apply -f k8s/deployment/aurora-cloudbank.yml

# Check deployment
kubectl get pods -l app=aurora-cloudbank

# Forward port for testing
kubectl port-forward svc/aurora-api 8000:8000
```

---

## 6. Quality Gates & Validation

### 6.1 Available Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `make check` | Lint + tests (fast) | Pre-commit, PR preparation |
| `make lint-tools` | Scoped lint (modern code) | Matches CI scope |
| `make lint-all` | Comprehensive lint | May surface legacy issues |
| `make test` | Full pytest suite | Before merges |
| `make security` | Bandit + safety scans | Security review |
| `make maintenance-scan` | SSMT pipeline | Maintenance tasks |

### 6.2 Pre-Commit Checklist

- [ ] Flake8 line limit respected (120 chars)
- [ ] Tests added/updated for new functionality
- [ ] No blocking CI failures
- [ ] DLP tags included for export operations
- [ ] Optional dependency imports wrapped in try/except

### 6.3 CI Integration

The repository uses multiple CI workflows for quality enforcement:

- **`aurora-ci-minimal.yml`** – Core CI (lint + tests)
- **`code-quality.yml`** – SonarCloud + Codacy analysis
- **`dependency-validation.yml`** – Dependency health checks
- **`pr-selective-integration.yml`** – PR-specific validation

---

## 7. Environment Configuration

### 7.1 Required Environment Variables

```bash
# Copy template
cp .env.example .env

# Required for AI features
export CLAUDE_API_KEY="your_anthropic_key"
export OPENAI_API_KEY="your_openai_key"
```

### 7.2 Optional Quantum Backend Configuration

```bash
# AWS Braket
export AWS_BRAKET_ROLE_ARN="arn:aws:iam::..."

# Azure Quantum
export AZURE_QUANTUM_WORKSPACE="your_workspace"

# IBM Quantum
export IBM_QUANTUM_TOKEN="your_ibm_token"
```

### 7.3 Rate Limiting Configuration

```bash
# Local (in-memory)
export RATE_LIMIT_ENABLED=true
export RATE_LIMIT_KEY_STRATEGY=ip

# Production (Redis)
export REDIS_URL=redis://aurora-redis:6379
export RATE_LIMIT_KEY_STRATEGY=ip_user
```

---

## 8. Troubleshooting

| Symptom | Resolution |
|---------|------------|
| `ImportError` for optional module | Verify graceful degradation; mock if needed |
| Server won't start | Confirm using `api/aurora_api.py` (NOT root) |
| Tests hanging | Use `pytest -m unit -vv --maxfail=1` |
| Dependency conflicts | Run `make setup` (never raw pip install) |
| CI failures | Check `gh pr checks <PR_NUMBER>` |

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-26 | Initial consolidated reference |

---

## 10. Related Resources

- [Quick Start Guide](../README.md#quick-start-5-minutes) – 5-minute setup
- [API Catalog](../API_CATALOG.md) – Complete endpoint reference
- [Quantum Cloud Backends](QUANTUM_CLOUD_BACKENDS.md) – Backend configuration
- [R2 Agent Telemetry](R2_AGENT_TELEMETRY.md) – Observability guide
- [Code Quality System](CODE_QUALITY_SYSTEM.md) – Quality automation

---

**Maintainer:** R-2 Mode (Integration & Validation)  
**Last Updated:** 2025-11-26  
**Anchor:** EOS_SEED_ORION::DEPLOYMENT_REFERENCE_v1.0.0
