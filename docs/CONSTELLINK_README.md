# CONSTELLINK Multi-Thread Relay Beacon

**Version:** v1.1.0  
**Type:** Multi-Thread Relay Beacon  
**Anchor Seed:** `EOS_SEED_ORION`  
**Ethics Protocol:** `Picard_Delta_3`

## Purpose

CONSTELLINK is the canonical thread-mesh primitive for the Aurora / GUMAS symbolic runtime ecosystem. It binds multiple symbolic threads (GPT conversations, ritual capsules, or other continuity units) into a sealed, hash-verified mesh artifact with:

- **Cross-thread continuity**: Maintains links between related threads
- **Anchor alignment**: Tracks and resolves symbolic anchor seeds across threads
- **Entropy/drift awareness**: Monitors and flags divergence in thread states
- **DLP-aware linkage**: Applies Data Lineage Protocol policies to filter and validate threads
- **Cryptographic sealing**: Generates SHA256 state hashes for mesh integrity verification

CONSTELLINK meshes can be consumed by downstream tools (e.g., ORACULITH for forecasting) and stored in symbolic reliquaries for future rehydration.

## Key Concepts

### Anchors and Ethics

- **`EOS_SEED_ORION`**: The default anchor seed representing the symbolic origin point for Aurora operations. Threads sharing this anchor are considered aligned with the primary Aurora timeline.

- **`Picard_Delta_3`**: The ethics protocol ensuring all mesh operations adhere to established symbolic and ethical boundaries. Named after principles of exploration, diplomacy, and measured intervention.

### Symbolic Tags

Meshes are tagged with:
- `mesh`: Identifies artifact as a mesh structure
- `relay`: Indicates multi-thread relay capability
- `multi-thread`: Denotes binding of multiple threads
- `anchor-alignment`: Tracks anchor seed alignment
- `dlp-aware`: Enforces DLP policies
- `entropy-tracking`: Monitors drift and divergence

### DLP (Data Lineage Protocol) Tags

- `cross-thread`: Allows content sharing across bound threads
- `symbolic_mesh`: Identifies as mesh metadata
- `metadata_only_by_default`: Default mode preserves privacy by sharing only metadata

## Schemas

### Input: `ConstellinkMeshRequest`

Request to bind threads into a mesh.

```json
{
  "request_id": "req_001",
  "threads": [
    {
      "thread_id": "thread_alpha",
      "anchor_seed": "EOS_SEED_ORION",
      "dlp_tags": ["cross-thread", "public"],
      "entropy_score": 0.25,
      "metadata": {"source": "gpt4_session"}
    },
    {
      "thread_id": "thread_beta",
      "anchor_seed": "EOS_SEED_ORION",
      "dlp_tags": ["cross-thread"],
      "entropy_score": 0.15,
      "metadata": {"source": "claude_session"}
    }
  ],
  "target_anchor_seed": "EOS_SEED_ORION",
  "dlp_policy": {
    "allow_cross_thread_content": true,
    "allowed_dlp_tags": ["cross-thread", "public"]
  },
  "caller_context": {
    "operator": "relay_system",
    "timestamp": "2025-01-15T12:00:00Z"
  }
}
```

**Fields:**
- `request_id` (required): Unique identifier for this mesh request
- `threads` (required): Array of `ThreadDescriptor` objects
- `target_anchor_seed` (optional): Override anchor seed; if omitted, resolved from threads
- `dlp_policy` (optional): DLP filtering policy
- `caller_context` (optional): Caller metadata for traceability

#### `ThreadDescriptor`

```json
{
  "thread_id": "thread_alpha",
  "anchor_seed": "EOS_SEED_ORION",
  "dlp_tags": ["cross-thread", "public"],
  "entropy_score": 0.25,
  "metadata": {}
}
```

**Fields:**
- `thread_id` (required): Unique thread identifier
- `anchor_seed` (optional): Thread's anchor seed
- `dlp_tags` (optional): DLP tags for this thread
- `entropy_score` (optional): Entropy/drift score (0.0-1.0)
- `metadata` (optional): Additional thread metadata

#### `DlpPolicy`

```json
{
  "allow_cross_thread_content": true,
  "allowed_dlp_tags": ["cross-thread", "public"]
}
```

**Fields:**
- `allow_cross_thread_content` (optional, default: `true`): Allow content sharing
- `allowed_dlp_tags` (optional): Whitelist of allowed tags; threads with other tags are rejected

### Output: `ConstellinkMesh`

Sealed mesh artifact with bound threads and metadata.

```json
{
  "mesh_id": "mesh_req_001_20250115120000",
  "created_at_utc": "2025-01-15T12:00:00Z",
  "anchor_seed": "EOS_SEED_ORION",
  "ethics_protocol": "Picard_Delta_3",
  "threads": [
    {
      "thread_id": "thread_alpha",
      "anchor_seed": "EOS_SEED_ORION",
      "dlp_tags": ["cross-thread", "public"],
      "anchor_alignment": "aligned",
      "drift_summary": "aligned anchor, low entropy (0.25)",
      "metadata": {"source": "gpt4_session"}
    }
  ],
  "dlp_effective_policy": {
    "cross_thread_content_allowed": true,
    "allowed_tags": ["cross-thread", "public"],
    "rejected_thread_count": 0
  },
  "entropy_summary": {
    "min_entropy": 0.15,
    "max_entropy": 0.25,
    "mean_entropy": 0.20,
    "drift_flag": "stable"
  },
  "divergent_truths": [],
  "caller_context": {
    "operator": "relay_system",
    "timestamp": "2025-01-15T12:00:00Z"
  },
  "mesh_manifest": {
    "version": "1.0.0",
    "export_time_utc": "2025-01-15T12:00:00Z",
    "anchor_seed": "EOS_SEED_ORION",
    "ethics_protocol": "Picard_Delta_3",
    "symbolic_tags": ["mesh", "relay", "multi-thread"],
    "dlp_tags": ["cross-thread", "symbolic_mesh"],
    "state_hash": "sha256::abc123..."
  }
}
```

**Key Fields:**
- `mesh_id`: Unique mesh identifier
- `threads`: Array of `MeshThreadView` with alignment metadata
- `entropy_summary`: Aggregated entropy metrics and drift flag
- `divergent_truths`: List of conflicts requiring human arbitration
- `mesh_manifest`: Manifest with SHA256 state hash for verification

## Python API Usage

### Basic Usage

```python
from symbolic.constellink import (
    ConstellinkRelay,
    MeshRequest,
    ThreadDescriptor,
    DlpPolicy
)

# Create relay
relay = ConstellinkRelay()

# Define threads
threads = [
    ThreadDescriptor(
        thread_id="thread_alpha",
        anchor_seed="EOS_SEED_ORION",
        dlp_tags=["cross-thread"],
        entropy_score=0.2
    ),
    ThreadDescriptor(
        thread_id="thread_beta",
        anchor_seed="EOS_SEED_ORION",
        dlp_tags=["cross-thread"],
        entropy_score=0.3
    )
]

# Create request
request = MeshRequest(
    request_id="req_001",
    threads=threads
)

# Bind threads into mesh
mesh = relay.bind(request)

# Access mesh data
print(f"Mesh ID: {mesh.mesh_id}")
print(f"Anchor: {mesh.anchor_seed}")
print(f"Drift Flag: {mesh.entropy_summary.drift_flag}")

# Export to JSON
mesh_json = mesh.to_dict()

# Print human-readable summary
print(mesh.glyphcard())
```

### Using `mesh_request_from_dict`

Convert raw JSON/dict to typed request:

```python
from symbolic.constellink import mesh_request_from_dict
import json

# Load from JSON
with open("request.json") as f:
    data = json.load(f)

request = mesh_request_from_dict(data)
mesh = relay.bind(request)
```

### Loading the Spec

```python
from symbolic.constellink import load_constellink_spec

spec = load_constellink_spec()
print(spec["modules"][0]["version"])  # v1.1.0
```

## CLI Usage

### Basic Command

```bash
# From stdin to stdout
cat request.json | python -m cli.constellink_bind
```

### With Options

```bash
# Pretty-printed output
python -m cli.constellink_bind \
  --input request.json \
  --output mesh.json \
  --pretty

# With glyphcard summary to stderr
python -m cli.constellink_bind \
  --input request.json \
  --glyphcard > mesh.json

# Override anchor seed
python -m cli.constellink_bind \
  --anchor-seed CUSTOM_SEED \
  < request.json \
  > mesh.json

# Show version
python -m cli.constellink_bind --version
```

### CLI Options

- `--input/-i FILE`: Input file (default: stdin)
- `--output/-o FILE`: Output file (default: stdout)
- `--pretty/-p`: Pretty-print JSON
- `--glyphcard/-g`: Print glyphcard to stderr
- `--anchor-seed SEED`: Override default anchor seed
- `--ethics-protocol PROTOCOL`: Override default ethics protocol
- `--version/-v`: Show version

## DLP Behavior

### Tag Filtering

When `dlp_policy.allowed_dlp_tags` is provided:
- Each thread's `dlp_tags` must be a **subset** of `allowed_dlp_tags`
- Threads with tags outside the whitelist are **rejected**
- Rejections are recorded in `divergent_truths`

**Example:**

```python
dlp_policy = DlpPolicy(
    allow_cross_thread_content=True,
    allowed_dlp_tags=["cross-thread", "public"]
)

# This thread will be ACCEPTED (tags are subset)
thread1 = ThreadDescriptor(
    thread_id="alpha",
    dlp_tags=["cross-thread"]
)

# This thread will be REJECTED (has "private" tag)
thread2 = ThreadDescriptor(
    thread_id="beta",
    dlp_tags=["cross-thread", "private"]
)
```

### Divergent Truths

The `divergent_truths` array captures conflicts requiring human review:

```json
{
  "divergent_truths": [
    {
      "type": "dlp_rejection",
      "thread_id": "beta",
      "message": "Thread DLP tags ['cross-thread', 'private'] not subset of allowed ['cross-thread', 'public']",
      "rejected_tags": ["private"]
    }
  ]
}
```

**Types of divergent truths:**
- `dlp_rejection`: Thread rejected due to DLP policy
- `anchor_divergence`: Threads have different anchor seeds
- `all_threads_rejected`: All threads filtered out by DLP

## Entropy and Drift Interpretation

### Entropy Score

Thread entropy scores (0.0-1.0) indicate stability:
- **< 0.3**: Low entropy (stable)
- **0.3-0.6**: Moderate entropy (watch)
- **> 0.6**: High entropy (divergent)

### Drift Flag

The mesh-level `drift_flag` is computed from entropy and anchor alignment:

- **`stable`**: Mean entropy < 0.3, max entropy < 0.5, all anchors aligned
- **`watch`**: Mean entropy < 0.6, max entropy < 0.8
- **`divergent`**: Mean entropy ≥ 0.6 or max entropy ≥ 0.8 or divergent anchors

**Example:**

```json
{
  "entropy_summary": {
    "min_entropy": 0.1,
    "max_entropy": 0.4,
    "mean_entropy": 0.25,
    "drift_flag": "stable"
  }
}
```

## Hash Sealing and Rehydration

### State Hash

The `mesh_manifest.state_hash` is a **SHA256 hash** of the entire mesh payload **excluding the manifest itself**. This enables:

1. **Integrity verification**: Recompute hash and compare
2. **Tamper detection**: Any modification changes the hash
3. **Deterministic sealing**: Same payload always produces same hash

### Computing State Hash

The hash is computed over a **canonicalized JSON** representation:
- Keys sorted alphabetically
- No whitespace (compact JSON)
- UTF-8 encoding

**Python verification:**

```python
import hashlib
import json

# Extract payload (everything except manifest)
payload = {
    "mesh_id": mesh.mesh_id,
    "created_at_utc": mesh.created_at_utc,
    "anchor_seed": mesh.anchor_seed,
    # ... all fields except mesh_manifest
}

# Canonicalize and hash
json_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
computed_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()

# Compare
expected_hash = mesh.mesh_manifest.state_hash.split("::")[1]
assert computed_hash == expected_hash
```

### Rehydration Notes

When rehydrating a mesh from storage:

1. **Load mesh JSON**
2. **Extract manifest hash**
3. **Recompute payload hash** (excluding manifest)
4. **Verify hashes match**
5. **Check `rehydration_notes_required` policy**

If hashes don't match, the mesh has been tampered with or corrupted.

## Anchor Seed Resolution

CONSTELLINK resolves the effective anchor seed using this priority:

1. **Explicit `target_anchor_seed`**: If provided in request, use it
2. **Unanimous thread anchors**: If all threads share the same anchor, use it
3. **Default fallback**: Use `EOS_SEED_ORION` and record divergence in `divergent_truths`

**Example divergent_truths entry:**

```json
{
  "type": "anchor_divergence",
  "message": "Threads have divergent anchor seeds: ['EOS_SEED_ORION', 'CUSTOM_SEED']",
  "anchors": ["EOS_SEED_ORION", "CUSTOM_SEED"],
  "resolution": "Using default: EOS_SEED_ORION"
}
```

## Integration with Aurora/GUMAS

### Reliquary Storage

Meshes can be stored in symbolic reliquaries:

```python
# Store mesh
reliquary.store(
    mesh_id=mesh.mesh_id,
    payload=mesh.to_dict(),
    tags=["mesh", "relay"]
)

# Retrieve and verify
stored_mesh = reliquary.retrieve(mesh.mesh_id)
verify_mesh_integrity(stored_mesh)
```

### ORACULITH Integration

ORACULITH (Symbolic Forecast Engine) consumes CONSTELLINK meshes:

```python
# Placeholder for future ORACULITH usage
forecast = oraculith.predict(mesh)
```

### Telemetry

For observability, wrap the relay:

```python
import time

start = time.time()
mesh = relay.bind(request)
duration_ms = (time.time() - start) * 1000

log_event("mesh_created", {
    "mesh_id": mesh.mesh_id,
    "thread_count": len(mesh.threads),
    "drift_flag": mesh.entropy_summary.drift_flag,
    "duration_ms": duration_ms
})
```

## Glyphcard Format

The `glyphcard()` method returns a human-readable summary:

```
═══ CONSTELLINK MESH GLYPHCARD ═══
Mesh ID: mesh_req_001_20250115120000
Anchor: EOS_SEED_ORION
Ethics: Picard_Delta_3
Threads: 2
Drift Flag: stable
Mean Entropy: 0.200
DLP Rejections: 0
═══════════════════════════════════
```

If divergent truths exist, they're listed:

```
⚠️  Divergent Truths (2):
  1. dlp_rejection: Thread DLP tags...
  2. anchor_divergence: Threads have divergent...
```

## Error Handling

### Python API

Raises `ValueError` for:
- Empty thread list
- Invalid entropy scores (< 0.0 or > 1.0)
- Malformed request data

### CLI

Exit codes:
- `0`: Success
- `1`: File not found, invalid JSON, validation error
- `2`: Unexpected error

Errors are written to stderr.

## Testing

See `tests/test_constellink.py` for examples:

```bash
# Run all CONSTELLINK tests
python -m pytest tests/test_constellink.py -v

# Run specific test
python -m pytest tests/test_constellink.py::test_happy_path -v
```

## Specification

Full JSON specification at:
- `symbolic_specs/Symbolic_Module_Specs_CONSTELLINK_ORACULITH.json`

Module manifest:
- `symbolic/CONSTELLINK_manifest.json`

CLI manifest:
- `cli/CONSTELLINK_CLI_manifest.json`

## License and Attribution

Part of the Aurora CloudBank Symbolic runtime.

**Anchor Seed**: `EOS_SEED_ORION`  
**Ethics Protocol**: `Picard_Delta_3`  
**Team**: Aurora Symbolic Core

---

*"Threading continuity through the symbolic mesh, with drift awareness and cryptographic sealing."*
