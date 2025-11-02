# Aurora CloudBank Symbolic - Cross-Repository Collaboration

## 🚀 Overview

Aurora CloudBank Symbolic now features advanced cross-repository collaboration capabilities, enabling distributed agent workflows, shared symbolic context, and coordinated CI/CD operations across multiple GitHub repositories.

## ✨ Key Features

### 🔗 Multi-Repository Capsules
- **Linked Repositories**: Track and manage connections between repositories
- **Shared Anchors**: Cryptographically verified trust chains across repos
- **Agent Rosters**: Define which agents can operate in each context
- **Version Compatibility**: Backward-compatible capsule schema (v1.0 → v2.0)

### 📊 Real-Time Drift Monitoring
- **Live Drift Tracking**: Monitor symbolic drift across operations
- **Three-Level Alerts**: Green (<0.1%), Yellow (0.1-0.2%), Red (>0.2%)
- **Trend Analysis**: Detect increasing/decreasing drift patterns
- **Historical Analytics**: Track drift events over time

### 🛡️ Security & Ethics
- **EOS_SEED_ORION Anchor**: Cryptographic verification of all operations
- **Picard_Delta_3 Protocol**: Ethics enforcement across repositories
- **Signed Capsules**: SHA-256 signatures for integrity
- **Trust Levels**: pending → trusted → verified progression

### 🔄 Automated Workflows
- **GitHub Actions Integration**: One-click capsule export and exchange
- **Workflow Triggering**: Cross-repo CI/CD coordination
- **Agent Notifications**: Automatic alerts on status changes
- **DLP Tracking**: Complete audit trail for compliance

## 🚦 Quick Start

### Prerequisites
- Python 3.12+
- FastAPI application running (aurora_api.py)
- GitHub repository with Actions enabled

### Installation

```bash
# Clone the repository
git clone https://github.com/AUo959/aurora-cloudbank-symbolic
cd aurora-cloudbank-symbolic

# Install dependencies
make setup
# or
pip install -r requirements-lock.txt

# Verify installation
python -c "from src.collab.capsule_schema import MultiRepoCapsule; print('✅ Collab module ready')"
```

### Basic Usage

#### 1. Export a Capsule

```bash
# Export capsule for collaboration with external repo
python export_capsule.py \
  --repo-url https://github.com/example/external-repo \
  --agents R-2,Copilot \
  --output capsule.json
```

**Output:**
```
🚀 Starting capsule export for https://github.com/example/external-repo
   Target: example/external-repo
✅ Anchor integrity verified
✅ Capsule exported to: capsule.json
✅ Export completed successfully
   Capsule ID: COLLAB_example_external-repo_1730160000
   Agents: R-2, Copilot
   Shared Anchors: 1
```

#### 2. Import a Capsule

```bash
# Import and validate capsule
python import_capsule.py \
  --capsule capsule.json \
  --validate-anchors \
  --accept-agents R-2,Copilot \
  --trust-level trusted
```

**Output:**
```
🚀 Starting capsule import from capsule.json
✅ Capsule parsed: COLLAB_example_external-repo_1730160000
🔍 Validating anchor integrity...
✅ Anchor integrity verified
🔍 Validating ethics compliance...
✅ Ethics compliance verified
...
✅ Import completed successfully
```

#### 3. Use the API

```python
import requests

# Start FastAPI server
# python aurora_api.py

# Export capsule via API
response = requests.post(
    "http://localhost:8000/collab/context/export",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={
        "repo_url": "https://github.com/example/repo",
        "agents": ["R-2", "Copilot"],
        "include_anchors": True
    }
)

print("Export result:", response.json())

# Get drift statistics
response = requests.get(
    "http://localhost:8000/collab/drift/statistics",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

print("Drift stats:", response.json())
```

## 📚 API Reference

### Endpoints

Base URL: `/collab`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/context/export` | POST | Export signed capsule |
| `/context/import` | POST | Import and validate capsule |
| `/workflow/trigger` | POST | Trigger external workflow |
| `/invite` | POST | Send repo linking invitation |
| `/agents/sync` | POST | Synchronize agent status |
| `/status` | GET | Get collaboration system status |
| `/drift/statistics` | GET | Get drift statistics |
| `/drift/events` | GET | Get drift event history |
| `/drift/diff` | POST | Compute capsule differences |

Full API documentation available at `/docs` when server is running.

## 🏗️ Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│           Aurora CloudBank Symbolic                 │
│                                                     │
│  ┌──────────────┐        ┌──────────────┐         │
│  │  Capsule     │───────▶│  DLP Tracker │         │
│  │  Schema      │        │              │         │
│  └──────────────┘        └──────────────┘         │
│         │                        │                 │
│         ▼                        ▼                 │
│  ┌──────────────┐        ┌──────────────┐         │
│  │    Export/   │───────▶│    Drift     │         │
│  │    Import    │        │   Monitor    │         │
│  │     CLI      │        │              │         │
│  └──────────────┘        └──────────────┘         │
│         │                        │                 │
│         ▼                        ▼                 │
│  ┌──────────────────────────────────────┐         │
│  │      Collaboration API Router        │         │
│  │  (FastAPI with Bearer Auth)          │         │
│  └──────────────────────────────────────┘         │
│                    │                               │
└────────────────────┼───────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   External Repository   │
        │  (GitHub/GitLab/etc.)  │
        └────────────────────────┘
```

### Data Flow

1. **Export**: Local context → Capsule creation → DLP tagging → Drift recording → Export file/API
2. **Import**: External capsule → Validation → Anchor check → Ethics verify → Drift monitor → Activation
3. **Sync**: Agent status → Compare rosters → Flag missing → Log changes → Return report

## 🔬 Testing

### Unit Tests

```bash
# Run all collab tests
pytest tests/test_collab_capsule.py -v

# Run specific test
pytest tests/test_collab_capsule.py::TestMultiRepoCapsule::test_create_capsule -v

# Run with coverage
pytest tests/test_collab_capsule.py --cov=src/collab
```

### Integration Tests

```bash
# Test full export-import cycle
bash test_integration.sh

# Test API endpoints
python test_api_integration.py
```

### Manual Testing

```bash
# 1. Export capsule
python export_capsule.py --repo-url https://github.com/test/repo --agents R-2 --output /tmp/test.json

# 2. Verify capsule structure
cat /tmp/test.json | jq '.capsule | keys'

# 3. Import capsule
python import_capsule.py --capsule /tmp/test.json --validate-anchors

# 4. Check drift stats via API
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/collab/drift/statistics | jq
```

## 📖 Documentation

- **User Guide**: [docs/CROSS_REPO_COLLABORATION.md](docs/CROSS_REPO_COLLABORATION.md)
- **API Reference**: `/docs` endpoint (Swagger UI)
- **Architecture**: [THREAD_TRANSFER_PROTOCOL.md](modules/reflective_autonomy/thread_transfer/THREAD_TRANSFER_PROTOCOL.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🎯 Use Cases

### 1. Distributed Agent Coordination

Multiple repositories running Aurora agents can share context and coordinate actions:

```bash
# Repo A exports context
python export_capsule.py --repo-url https://github.com/org/repo-b --agents R-2,Aurora

# Transfer capsule to Repo B

# Repo B imports and continues work
python import_capsule.py --capsule capsule.json --trust-level trusted
```

### 2. Multi-Repo CI/CD

Trigger workflows across repositories when changes occur:

```yaml
# In Repository A
- name: Export and trigger
  run: |
    python export_capsule.py --repo-url https://github.com/org/repo-b --agents R-2
    curl -X POST https://api.github.com/repos/org/repo-b/dispatches \
      -d '{"event_type":"aurora_sync"}'
```

### 3. Shared Knowledge Base

Maintain consistent symbolic knowledge across multiple projects:

```python
from src.collab.capsule_schema import MultiRepoCapsule, create_shared_anchor

# Create shared anchor for common knowledge
anchor = create_shared_anchor(
    anchor_name="SHARED_KNOWLEDGE_BASE",
    anchor_seed="EOS_SEED_ORION",
    metadata={"domain": "quantum_computing"}
)

# Include in all project capsules
```

## 🛠️ Configuration

### Environment Variables

```bash
# .env file
AURORA_ANCHOR_SEED=EOS_SEED_ORION
AURORA_ETHICS_PROTOCOL=Picard_Delta_3
AURORA_DRIFT_THRESHOLD_YELLOW=0.001
AURORA_DRIFT_THRESHOLD_RED=0.002
AURORA_API_TOKEN=your_token_here
```

### Capsule Configuration

```python
# Custom capsule configuration
from src.collab.capsule_schema import MultiRepoCapsule

capsule = MultiRepoCapsule(
    capsule_id="CUSTOM_001",
    anchor_seed="EOS_SEED_ORION",
    ethics_protocol="Picard_Delta_3",
    agent_roster=["R-2", "Copilot", "Custom-Agent"],
    metadata={
        "organization": "example-org",
        "purpose": "cross-repo-ml-training"
    }
)
```

## 🚨 Troubleshooting

### Common Issues

**Q: Import fails with "Anchor integrity validation failed"**

A: Ensure the `anchor_seed` matches `EOS_SEED_ORION` and the capsule hasn't been manually modified.

**Q: Drift level is RED**

A: Symbolic drift exceeded 0.2%. Review recent operations and consider re-exporting with aligned state.

**Q: API returns 401 Unauthorized**

A: Verify your bearer token is valid and included in the Authorization header.

**Q: Agents not syncing**

A: Use `/collab/agents/sync` endpoint and check for missing agents in the response.

### Debug Mode

```bash
# Enable verbose logging
python export_capsule.py --repo-url URL --agents R-2 --verbose

# Check API logs
tail -f aurora_api.log

# Export drift metrics
python -c "from src.collab.drift_monitor import get_drift_monitor; \
           get_drift_monitor().export_metrics('drift_debug.json')"
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/aurora-cloudbank-symbolic
cd aurora-cloudbank-symbolic

# Create feature branch
git checkout -b feature/collab-enhancement

# Make changes and test
pytest tests/test_collab_capsule.py -v

# Commit and push
git commit -m "feat: add collab enhancement"
git push origin feature/collab-enhancement
```

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **EOS_SEED_ORION**: Core anchor protocol
- **Picard_Delta_3**: Ethics framework
- **ThreadCore v3.5.1**: Continuity infrastructure
- **R-2 Agent**: Functionality and integration lead

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/AUo959/aurora-cloudbank-symbolic/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AUo959/aurora-cloudbank-symbolic/discussions)
- **Email**: support@aurora-cloudbank.example

---

**Thread**: T1→COLLAB→README  
**DLP**: context_tag=collab_readme  
**Anchor**: EOS_SEED_ORION  
**Ethics**: Picard_Delta_3

**Version**: 1.0.0  
**Last Updated**: October 29, 2025
