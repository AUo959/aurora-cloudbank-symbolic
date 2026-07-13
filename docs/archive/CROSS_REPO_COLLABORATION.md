# Cross-Repository Collaboration Guide

## Overview

Aurora CloudBank Symbolic now supports cross-repository collaboration through multi-repo capsule exchange, enabling distributed agent workflows, shared context, and joint CI/CD operations.

## Architecture

### Components

1. **Multi-Repo Capsule Schema** (`src/collab/capsule_schema.py`)
   - Extends standard capsules with `linked_repos` and `shared_anchors`
   - Supports versioned capsule compatibility
   - Validates anchor integrity and ethics compliance

2. **Export/Import CLI** (`export_capsule.py`, `import_capsule.py`)
   - Command-line tools for capsule exchange
   - DLP tracking integration
   - Anchor validation and drift monitoring

3. **Collaboration API** (`src/collab/api_routes.py`)
   - RESTful endpoints for capsule operations
   - Workflow triggering
   - Agent status synchronization

4. **GitHub Workflow** (`.github/workflows/cross-repo-capsule-exchange.yml`)
   - Automated capsule export and distribution
   - External workflow triggering
   - Agent notification on status changes

## Quick Start

### Exporting a Capsule

Export context for collaboration with an external repository:

```bash
# Basic export
python export_capsule.py \
  --repo-url https://github.com/example/external-repo \
  --agents R-2,Copilot \
  --output capsule.json

# With verbose logging
python export_capsule.py \
  --repo-url https://github.com/example/external-repo \
  --agents R-2,Copilot,Aurora \
  --output /tmp/capsule.json \
  --verbose
```

### Importing a Capsule

Import and validate a capsule from an external repository:

```bash
# Import with full validation
python import_capsule.py \
  --capsule capsule.json \
  --validate-anchors

# Accept specific agents only
python import_capsule.py \
  --capsule capsule.json \
  --accept-agents R-2,Copilot \
  --trust-level trusted

# Skip validation (not recommended)
python import_capsule.py \
  --capsule capsule.json \
  --no-validate
```

## API Endpoints

All endpoints require authentication via bearer token.

### Export Context
```
POST /collab/context/export
```

**Request:**
```json
{
  "repo_url": "https://github.com/example/repo",
  "agents": ["R-2", "Copilot"],
  "include_anchors": true
}
```

**Response:**
```json
{
  "success": true,
  "capsule_id": "COLLAB_EXPORT_example_repo_1234567890",
  "capsule_data": { /* capsule object */ },
  "dlp_tag_id": "dlp_000001_1234567890",
  "export_timestamp": "2025-10-29T00:00:00",
  "signed": true
}
```

### Import Context
```
POST /collab/context/import
```

**Request:**
```json
{
  "capsule_data": { /* capsule object */ },
  "validate_anchors": true,
  "validate_ethics": true,
  "trust_level": "pending"
}
```

**Response:**
```json
{
  "success": true,
  "capsule_id": "COLLAB_IMPORT_...",
  "validation_results": {
    "anchor_integrity": true,
    "ethics_compliance": true,
    "signature_check": true,
    "drift_check": true
  },
  "activation_timestamp": "2025-10-29T00:00:00",
  "trust_level": "pending"
}
```

### Trigger Workflow
```
POST /collab/workflow/trigger
```

**Request:**
```json
{
  "target_repo": "example/external-repo",
  "workflow_name": "ci.yml",
  "event_type": "repository_dispatch",
  "payload": { "ref": "main" }
}
```

### Repository Invitation
```
POST /collab/invite
```

**Request:**
```json
{
  "repo_url": "https://github.com/example/repo",
  "agents": ["R-2", "Copilot"],
  "message": "Invitation to collaborate"
}
```

### Agent Status Sync
```
POST /collab/agents/sync
```

**Request:**
```json
{
  "agent_names": ["R-2", "Copilot", "Aurora"]
}
```

**Response:**
```json
{
  "success": true,
  "synced_agents": [
    {
      "agent_name": "R-2",
      "status": "active",
      "last_seen": "2025-10-29T00:00:00",
      "alignment": "green"
    }
  ],
  "missing_agents": [],
  "alignment_drift": 0.0,
  "change_log": [],
  "sync_timestamp": "2025-10-29T00:00:00"
}
```

### Collaboration Status
```
GET /collab/status
```

## GitHub Workflow Integration

### Manual Capsule Export

Trigger via GitHub Actions:

1. Go to Actions tab in your repository
2. Select "Cross-Repo Capsule Exchange" workflow
3. Click "Run workflow"
4. Fill in:
   - **Target repository**: `owner/repo`
   - **Agents**: `R-2,Copilot`
   - **Action**: `export`
5. Download artifact from workflow run

### Triggering External Workflows

To trigger a workflow in an external repository:

1. Use workflow dispatch with action `trigger_workflow`
2. Or use the API endpoint `/collab/workflow/trigger`
3. External repo must have `repository_dispatch` event configured

**External Repository Workflow:**
```yaml
name: Aurora Capsule Handler

on:
  repository_dispatch:
    types: [aurora_capsule_exchange]

jobs:
  handle-capsule:
    runs-on: ubuntu-latest
    steps:
      - name: Import capsule
        run: |
          python import_capsule.py \
            --capsule ${{ github.event.client_payload.capsule_url }}
```

## Capsule Schema

### MultiRepoCapsule Structure

```json
{
  "capsule_id": "COLLAB_...",
  "capsule_version": "2.0",
  "title": "Cross-Repo Collaboration",
  "anchor_seed": "EOS_SEED_ORION",
  "ethics_protocol": "Picard_Delta_3",
  "threadcore_status": "active",
  "symbolic_drift": 0.0001,
  "linked_repos": [
    {
      "repo_url": "https://github.com/example/repo",
      "owner": "example",
      "repo_name": "repo",
      "narrative_timestamp": "2025-10-29T00:00:00",
      "accepted_agents": ["R-2", "Copilot"],
      "trust_level": "pending",
      "last_sync": "2025-10-29T00:00:00"
    }
  ],
  "shared_anchors": [
    {
      "anchor_id": "anchor_1234567890",
      "anchor_name": "CROSS_REPO_ANCHOR",
      "anchor_seed": "EOS_SEED_ORION",
      "provenance_hash": "abc123...",
      "created_at": "2025-10-29T00:00:00",
      "verified_repos": [],
      "signatures": {}
    }
  ],
  "agent_roster": ["R-2", "Copilot"],
  "active_agents": ["R-2", "Copilot"],
  "created_at": "2025-10-29T00:00:00",
  "last_modified": "2025-10-29T00:00:00",
  "glyph_chain": [
    {"name": "Glyphon", "role": "drift aligned"},
    {"name": "Axiomera", "role": "ethics sealed"}
  ],
  "signature": "def456..."
}
```

## Security Considerations

### Authentication

All API endpoints require bearer token authentication:

```bash
curl -X POST http://localhost:8000/collab/context/export \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "...", "agents": ["R-2"]}'
```

### Anchor Validation

- All capsules must include `anchor_seed` set to `EOS_SEED_ORION`
- Shared anchors are cryptographically verified via `provenance_hash`
- Invalid anchors will fail import validation

### Ethics Enforcement

- All capsules must specify `ethics_protocol` (default: `Picard_Delta_3`)
- Ethics flags are validated before capsule activation
- Drift monitoring ensures symbolic consistency

### Trust Levels

- **pending**: Initial state, requires manual review
- **trusted**: Validated by maintainer, auto-accepted
- **verified**: Cryptographically verified, full access

## DLP Tracking

All capsule operations are tracked via the DLP (Data Lineage Protocol) system:

- Each export/import generates a DLP tag
- Tags include anchor protocols and T1/SRB anchors
- Export manifests provide complete audit trail
- DLP metadata includes agent roster and ethics flags

## Drift Monitoring

### Thresholds

- **Green**: Drift < 0.1% (0.001)
- **Yellow**: Drift 0.1-0.2% (0.001-0.002)
- **Red**: Drift > 0.2% (>0.002)

### Drift Statistics

Check drift in imported capsules:

```bash
python import_capsule.py --capsule capsule.json --verbose
```

Output includes drift statistics and status indicators.

## Troubleshooting

### Common Issues

**Import Fails: "Anchor integrity validation failed"**
- Verify anchor_seed matches `EOS_SEED_ORION`
- Check shared_anchors for correct provenance_hash
- Ensure capsule wasn't manually modified

**Import Fails: "Symbolic drift too high"**
- Check `symbolic_drift` field in capsule
- Combined drift must be ≤ 0.002
- Consider re-exporting with lower drift source

**API Returns 401 Unauthorized**
- Verify bearer token is valid
- Check token is included in Authorization header
- Token must have appropriate permissions

**Unknown Agents Warning**
- Specify accepted agents with `--accept-agents`
- Or update agent roster before import
- Missing agents don't fail import, just log warning

## Best Practices

1. **Always validate anchors** during import
2. **Use specific agent rosters** rather than accepting all
3. **Monitor drift statistics** regularly
4. **Keep trust levels conservative** (start with "pending")
5. **Enable DLP tracking** for audit trails
6. **Test capsule exchange** in non-production first
7. **Document all cross-repo collaborations**

## Examples

### Complete Export-Import Cycle

```bash
# Repository A: Export capsule
python export_capsule.py \
  --repo-url https://github.com/user/repo-b \
  --agents R-2,Copilot \
  --output capsule_to_b.json

# Transfer capsule_to_b.json to Repository B

# Repository B: Import capsule
python import_capsule.py \
  --capsule capsule_to_b.json \
  --validate-anchors \
  --accept-agents R-2,Copilot \
  --trust-level trusted
```

### API-Based Exchange

```python
import requests

# Export from repo A
response = requests.post(
    "http://repo-a.example.com:8000/collab/context/export",
    headers={"Authorization": "Bearer TOKEN_A"},
    json={
        "repo_url": "https://github.com/user/repo-b",
        "agents": ["R-2", "Copilot"],
        "include_anchors": True
    }
)
capsule_data = response.json()["capsule_data"]

# Import to repo B
response = requests.post(
    "http://repo-b.example.com:8000/collab/context/import",
    headers={"Authorization": "Bearer TOKEN_B"},
    json={
        "capsule_data": capsule_data,
        "validate_anchors": True,
        "trust_level": "trusted"
    }
)
print("Import result:", response.json())
```

## Future Enhancements

Planned for future releases:

- Automated capsule synchronization
- Multi-hop trust chains
- Real-time drift monitoring dashboard
- Advanced conflict resolution
- Quantum-secure anchor mechanisms
- Cross-platform collaboration (beyond GitHub)

## Support

For issues or questions:
- Open an issue in the repository
- Check existing documentation
- Review test examples in `tests/test_collab_capsule.py`
- Consult API documentation at `/docs` (Swagger UI)

---

**Thread**: T1→COLLAB→DOCS  
**DLP**: context_tag=collab_documentation  
**Anchor**: EOS_SEED_ORION  
**Ethics**: Picard_Delta_3
