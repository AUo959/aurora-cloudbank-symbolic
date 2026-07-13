# ORACULITH - Symbolic Forecast Engine

**Version:** 1.0.0  
**Anchor Seed:** EOS_SEED_ORION  
**Ethics Protocol:** Picard_Delta_3

## Overview

ORACULITH is a symbolic forecasting engine that consumes multi-thread meshes from CONSTELLINK and produces DLP-aware, hash-sealed forecasts with metaphorical analysis, risk assessment, and entropy tracking.

### Key Features

- **CONSTELLINK Mesh Consumer**: First-class integration with ConstellinkMesh data structures
- **Symbolic Metaphor Generation**: Deterministic metaphor templates based on risk/entropy patterns
- **DLP Policy Enforcement**: Configurable controls for cross-thread attribution and explicit failure modes
- **Risk & Entropy Analysis**: Coarse-grained risk levels (low/medium/high) and entropy trends (rising/falling/stable)
- **Anchor Alignment**: Heuristic computation of alignment with symbolic anchor protocols
- **Divergent Truth Detection**: Identifies inconsistencies, missing hashes, and conflicting signals
- **Hash-Sealed Manifests**: SHA256 integrity sealing for reliquary indexing and audit trails

## Relationship to CONSTELLINK

ORACULITH depends on CONSTELLINK for its input data structures:

```
CONSTELLINK (mesh creation)
    ↓
ConstellinkMesh (threads + entropy summary + manifest)
    ↓
ORACULITH (forecasting)
    ↓
SymbolicForecast (metaphor + risk + entropy + sealed manifest)
```

Every forecast references its source mesh via `mesh_reference` which includes:
- `mesh_id` - Unique mesh identifier
- `mesh_state_hash` - SHA256 hash from mesh manifest
- `anchor_seed` - Anchor seed from mesh
- `drift_flag` - Drift status (stable/moderate/divergent)

## Anchors and Ethics

### Anchor Seed: EOS_SEED_ORION
The EOS_SEED_ORION anchor provides temporal and spatial reference for all ORACULITH forecasts. This anchor:
- Links forecasts to the CONSTELLINK mesh topology
- Enables cross-temporal forecast comparison
- Supports symbolic coherence across the Aurora CloudBank ecosystem

### Ethics Protocol: Picard_Delta_3
The Picard_Delta_3 ethics protocol ensures:
- Transparent risk communication (when DLP policy allows)
- Respect for sensitive data (via sensitive_tags enforcement)
- Metaphorical framing to avoid overfitting to literal predictions
- Divergent truth disclosure for ambiguous states

## Data Structures

### Input: OraculithForecastContext

```python
@dataclass
class OraculithForecastContext:
    request_id: str                           # Required: unique request ID
    mesh: ConstellinkMesh                     # Required: source mesh
    echoes: Optional[List[EchoDescriptor]]    # Optional: reflective context
    forecast_horizon: Optional[str]           # Optional: e.g., "near-term"
    forecast_focus: Optional[List[str]]       # Optional: focus areas
    dlp_policy: Optional[OraculithDlpPolicy]  # Optional: DLP controls
    caller_context: Optional[Dict[str, Any]]  # Optional: caller metadata
```

**EchoDescriptor** provides additional reflective context:
```python
@dataclass
class EchoDescriptor:
    source: str              # Required: origin of echo
    echo_text: str           # Required: reflective content
    thread_id: Optional[str] # Optional: thread reference
    entropy_hint: Optional[float]  # Optional: 0.0-1.0
    tags: List[str]          # Optional: categorization
```

**OraculithDlpPolicy** controls forecast behavior:
```python
@dataclass
class OraculithDlpPolicy:
    allow_explicit_failure_modes: bool = False      # Enable literal summaries
    allow_cross_thread_attribution: bool = False    # Include thread IDs
    sensitive_tags: Optional[List[str]] = None      # Tags to redact
```

### Output: SymbolicForecast

```python
@dataclass
class SymbolicForecast:
    forecast_id: str                              # Unique forecast ID
    created_at_utc: str                           # Timestamp
    anchor_seed: str                              # Anchor (EOS_SEED_ORION)
    ethics_protocol: str                          # Ethics (Picard_Delta_3)
    metaphor: str                                 # Central symbolic metaphor
    risk_level: str                               # low/medium/high/unknown
    entropy_trend: str                            # rising/falling/stable/unknown
    anchor_alignment: Optional[float]             # 0.0-1.0
    supporting_signals: SupportingSignals         # Evidence
    dlp_effective_policy: OraculithDlpEffectivePolicy  # Applied policy
    mesh_reference: MeshReference                 # Source mesh reference
    forecast_manifest: ForecastManifest           # Hash-sealed manifest
    summary: Optional[str]                        # Literal summary (if DLP allows)
    focus: Optional[List[str]]                    # Focus areas
    divergent_truths: Optional[List[str]]         # Inconsistencies
    caller_context: Optional[Dict[str, Any]]      # Caller metadata
```

## Python Usage

### Basic Forecast

```python
from symbolic.constellink import create_mesh, ThreadDescriptor
from symbolic.oraculith import OraculithEngine, OraculithForecastContext

# Create a mesh
threads = [
    ThreadDescriptor(thread_id='t1', source='analysis', entropy_hint=0.2, tags=['stable']),
    ThreadDescriptor(thread_id='t2', source='forecast', entropy_hint=0.3, tags=['verified'])
]
mesh = create_mesh(threads)

# Generate forecast
engine = OraculithEngine()
context = OraculithForecastContext(request_id='req_001', mesh=mesh)
forecast = engine.forecast(context)

# Access results
print(forecast.metaphor)
# => "The river has found its channel, flowing clear and steady."

print(f"Risk: {forecast.risk_level}, Entropy: {forecast.entropy_trend}")
# => "Risk: low, Entropy: stable"

# Get human-readable glyphcard
print(forecast.glyphcard())
```

### Forecast with DLP Policy

```python
from symbolic.oraculith import OraculithDlpPolicy

# Configure DLP policy
dlp_policy = OraculithDlpPolicy(
    allow_explicit_failure_modes=True,  # Enable literal summaries
    allow_cross_thread_attribution=True,  # Include thread IDs in signals
    sensitive_tags=['classified', 'internal']
)

context = OraculithForecastContext(
    request_id='req_002',
    mesh=mesh,
    dlp_policy=dlp_policy
)

forecast = engine.forecast(context)

# Summary is now included (since allow_explicit_failure_modes=True)
if forecast.summary:
    print(forecast.summary)

# Dominant threads are included (since allow_cross_thread_attribution=True)
print(forecast.supporting_signals.dominant_threads)
```

### Forecast with Echoes

```python
from symbolic.oraculith import EchoDescriptor

echoes = [
    EchoDescriptor(
        source='expert_panel',
        echo_text='Recent trends indicate stabilization',
        entropy_hint=0.25,
        tags=['expert', 'verified']
    ),
    EchoDescriptor(
        source='sensor_network',
        echo_text='Noise levels decreasing',
        thread_id='t1',
        entropy_hint=0.15
    )
]

context = OraculithForecastContext(
    request_id='req_003',
    mesh=mesh,
    echoes=echoes,
    forecast_focus=['stability', 'noise_reduction']
)

forecast = engine.forecast(context)
print(forecast.supporting_signals.dominant_echoes)
# => ['sensor_network', 'expert_panel']
```

### Loading from JSON

```python
from symbolic.oraculith import forecast_context_from_dict
import json

# Load context from file
with open('context.json', 'r') as f:
    context_data = json.load(f)

context = forecast_context_from_dict(context_data, validate_mesh=True)
forecast = engine.forecast(context)

# Export to JSON
with open('forecast.json', 'w') as f:
    json.dump(forecast.to_dict(), f, indent=2)
```

## CLI Usage

The `oraculith-forecast` CLI tool provides command-line access to ORACULITH.

### Basic Usage

```bash
# Generate forecast from context JSON via stdin
python -m cli.oraculith_forecast < context.json

# Generate forecast from context file
python -m cli.oraculith_forecast --input context.json --output forecast.json

# Generate forecast from mesh-only JSON
python -m cli.oraculith_forecast --mesh mesh.json --output forecast.json --pretty
```

### Options

```bash
python -m cli.oraculith_forecast --help

Options:
  --input, -i PATH       Input file with OraculithForecastContext JSON (default: stdin)
  --mesh, -m PATH        Input file with ConstellinkMesh JSON (creates minimal context)
  --output, -o PATH      Output file for SymbolicForecast JSON (default: stdout)
  --pretty, -p           Pretty-print JSON output
  --glyphcard, -g        Print human-readable glyphcard to stderr
  --anchor-seed TEXT     Override anchor seed (default: EOS_SEED_ORION)
  --ethics-protocol TEXT Override ethics protocol (default: Picard_Delta_3)
  --version, -v          Print CLI version
```

### Example: Mesh-Only Input

When you only have a mesh JSON file, the CLI auto-wraps it in a minimal context:

```bash
# Create mesh JSON
echo '{
  "mesh_id": "mesh_abc123",
  "created_at_utc": "2025-11-24T00:00:00Z",
  "anchor_seed": "EOS_SEED_ORION",
  "ethics_protocol": "Picard_Delta_3",
  "threads": [
    {
      "thread_id": "t1",
      "source": "analysis",
      "entropy_hint": 0.2,
      "tags": ["stable"]
    }
  ],
  "entropy_summary": {
    "entropy_mean": 0.2,
    "drift_flag": "stable",
    "thread_count": 1
  },
  "mesh_manifest": {
    "version": "1.0.0",
    "export_time_utc": "2025-11-24T00:00:00Z",
    "anchor_seed": "EOS_SEED_ORION",
    "ethics_protocol": "Picard_Delta_3",
    "symbolic_tags": ["test"],
    "dlp_tags": ["test"],
    "state_hash": "sha256:abc123..."
  }
}' > mesh.json

# Generate forecast
python -m cli.oraculith_forecast --mesh mesh.json --pretty --glyphcard > forecast.json
```

The glyphcard output to stderr:
```
=== ORACULITH Forecast Glyphcard ===
ID: forecast_xyz789
Risk: LOW | Entropy: STABLE
Anchor Alignment: 0.85

Metaphor: The river has found its channel, flowing clear and steady.

Mesh: mesh_abc123 (drift=stable)
=================================
```

## DLP Behavior

### Cross-Thread Attribution

When `allow_cross_thread_attribution=False` (default):
- `supporting_signals.dominant_threads` is empty or redacted
- Metaphors remain available
- Risk and entropy trends are still computed

When `allow_cross_thread_attribution=True`:
- Thread IDs are included in `dominant_threads`
- Enables fine-grained signal tracing

### Explicit Failure Modes

When `allow_explicit_failure_modes=False` (default):
- No literal `summary` field is populated
- Users must interpret `metaphor` symbolically
- `risk_level` and `entropy_trend` remain available as coarse signals

When `allow_explicit_failure_modes=True`:
- Literal `summary` field provides direct risk description
- Recommended for high-risk scenarios requiring immediate action

### Sensitive Tags

When `sensitive_tags` are specified:
- ORACULITH checks mesh thread tags and echo tags
- If sensitive tags are detected:
  - `policy_notes` includes a warning
  - `dominant_threads` and `dominant_echoes` are cleared/redacted
  - Metaphor remains available (symbolic protection)

Example:
```python
dlp_policy = OraculithDlpPolicy(
    allow_explicit_failure_modes=False,
    allow_cross_thread_attribution=False,
    sensitive_tags=['classified', 'pii', 'confidential']
)
```

## Risk and Entropy Derivation

### Risk Level

Computed from mesh `drift_flag` and `entropy_mean`:

| Drift Flag | Entropy Mean | Risk Level |
|------------|--------------|------------|
| divergent  | > 0.6        | high       |
| moderate   | any          | medium     |
| any        | > 0.5        | medium     |
| stable     | < 0.4        | low        |
| other      | -            | unknown    |

### Entropy Trend

Derived from `drift_flag` and `entropy_mean`:

| Drift Flag | Entropy Mean | Trend   |
|------------|--------------|---------|
| divergent  | > 0.7        | rising  |
| stable     | < 0.3        | stable  |
| any        | < 0.5        | falling |
| other      | -            | unknown |

### Anchor Alignment

Computed as the mean of thread-level `anchor_alignment` values. If no threads provide alignment, defaults based on drift_flag:
- `stable` → 0.85
- `moderate` → 0.6
- `divergent` → 0.3

## Metaphor Generation

ORACULITH uses deterministic metaphor templates keyed on risk and entropy:

- **Low Risk + Stable Entropy**: "The river has found its channel, flowing clear and steady."
- **Low Risk + Falling Entropy**: "The storm passes; calm waters emerge beneath clearing skies."
- **Medium Risk + Stable Entropy**: "The ship sails through familiar fog, vigilant but confident."
- **Medium Risk + Rising Entropy**: "Clouds gather on the horizon; the wise captain checks the sails."
- **High Risk + Rising Entropy**: "Lightning splits the sky; the reef ahead demands immediate course correction."
- **High Risk + Stable Entropy**: "The eye of the hurricane: deceptive calm masking surrounding chaos."
- **Divergent Drift**: "The compass spins wildly; multiple truths compete for navigation."
- **Default**: "The path ahead shrouded in mist; proceed with caution and symbolic awareness."

## Hash Sealing

Every `SymbolicForecast` includes a `forecast_manifest.state_hash` computed via SHA256 over the forecast payload (excluding the manifest itself).

### Hash Computation

1. Build forecast payload dictionary (all fields except `forecast_manifest`)
2. Serialize to canonical JSON (sorted keys, no whitespace)
3. Compute SHA256 hash
4. Prefix with `sha256:`

Example hash: `sha256:a3f5b2c9d8e7f6a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5`

### Mesh Reference

The `mesh_reference.mesh_state_hash` is copied from the source mesh's `mesh_manifest.state_hash`, enabling:
- Integrity verification of the mesh at forecast time
- Reliquary indexing across mesh and forecast
- Audit trail for lineage tracking

## Divergent Truths

ORACULITH detects inconsistencies and records them in `divergent_truths`:

1. **Drift vs. Entropy Mismatch**: Mesh marked as divergent but entropy_mean is low (or vice versa)
2. **Missing State Hash**: Mesh manifest lacks `state_hash` field
3. **Conflicting Echoes**: High variance in echo entropy hints (std > 0.3)

Example:
```python
if forecast.divergent_truths:
    for truth in forecast.divergent_truths:
        print(f"⚠️  {truth}")
```

## Examples

See `tests/test_oraculith.py` for comprehensive usage examples, including:
- Happy-path forecasts with stable meshes
- High-entropy divergent meshes
- DLP policy enforcement validation
- Hash sealing verification

## Related Documentation

- **CONSTELLINK**: See mesh creation and thread descriptors
- **Symbolic Module Spec**: `symbolic_specs/Symbolic_Module_Specs_CONSTELLINK_ORACULITH.json`
- **Module Manifest**: `symbolic/ORACULITH_manifest.json`
- **CLI Manifest**: `cli/ORACULITH_CLI_manifest.json`

## Version History

### 1.0.0 (2025-11-24)
- Initial release
- CONSTELLINK mesh consumption
- DLP policy enforcement
- Metaphor generation
- Risk/entropy analysis
- Hash-sealed manifests
- CLI tool
