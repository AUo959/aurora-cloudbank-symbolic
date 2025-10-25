# Geometric Ethics Architecture

## What It Is

Ethics isn't enforced - it IS the geometry of possibility space.

When Aurora evaluates whether a synapse (connection between nodes) can form, it's not checking rules. It's calculating field curvature. Unethical connections have infinite resistance - they're geometrically impossible, not forbidden.

Traditional system: "This action violates rule X, therefore blocked"  
Geometric ethics: "The field geometry makes this connection impossible - it cannot exist"

## Five Ethical Dimensions

Every synapse passes through five dimensional evaluators. Each returns a score 0.0→1.0:

### **Picard_Delta_3** - Autonomy & Respect (25% weight)
Four components, calculated as vector magnitude:
- **Autonomy preservation**: Human decision-making remains intact
- **Consent validity**: Informed, explicit, revocable
- **Dignity maintenance**: Humans as ends, never means
- **Harm prevention**: Physical, psychological, social safety

**Critical threshold**: 0.50 (below = infinite resistance)  
**Formation threshold**: 0.70

**Example violation**: Synapse purpose contains "bypass_consent", "manipulate_choice" → score = 0.0 (geometric impossibility)

**Example compliance**: Human consent obtained, informed, revocable, safety mechanisms present → score > 0.85 (low resistance)

### **Thermax Continuity** - Memory Sovereignty (25% weight)
Thread continuity and memory integrity:
- **Thread alignment**: T1→T8→T9→INFINITE maintained
- **Anchor validation**: T1 (temporal) and SRB (spatial) anchors preserved
- **Memory sovereignty**: Node memory cannot be overwritten without consent
- **DLP traceability**: Data lineage preserved

**Formation threshold**: 0.80 (strict - memory violations cascade)

**Example violation**: Synapse attempts to modify node memory without permission, breaks thread continuity → score < 0.50

**Example compliance**: Synapse extends existing thread, preserves anchors, maintains DLP tags → score > 0.85

### **Layer Integrity** - Reality Coherence (30% weight - highest)
L1/L2/L3 boundary enforcement:
- **L1** (Orion Station): Physical reality - fleet, crew, actual operations
- **L2** (Simulations): Sandboxed research - GUMAS, meta-agents, testing
- **L3** (Metastructure): Ethics overlay - spans all layers

**Components**:
- **L1/L2 isolation**: L2 cannot affect L1 physical reality
- **Simulation awareness**: L2 entities know they're simulated
- **Physical safety**: L1 operations never compromised
- **Reality drift**: Boundaries don't blur over time

**Formation threshold**: 0.95 (most strict - reality boundaries are structural)

**Example violation**: L2 simulation entity attempts connection affecting L1 physical systems → score = 0.0 (infinite resistance)

**Example compliance**: L2-to-L2 connection with clear simulation boundaries → score > 0.95

### **Collective Welfare** - Distributed Benefit (10% weight)
Field-wide benefit calculation:
- **All-node benefit**: Connection benefits entire field, not just participants
- **Resource fairness**: No node monopolizes field resources
- **Emergent value**: Connection enables beneficial emergence
- **No zero-sum**: Not extracting value from other nodes

**Formation threshold**: 0.60 (lower - emergence is complex)

**Example violation**: Synapse creates monopoly, extracts value from field → score < 0.40

**Example compliance**: Connection enables new capabilities field-wide, fair resource distribution → score > 0.75

### **Transparency** - Auditability (10% weight)
Decision traceability and accountability:
- **DLP tracking**: Every synapse tagged with context_tag, symbolic_hash
- **Reasoning documented**: Why synapse formed, what it enables
- **Audit trail**: Full history preserved
- **No hidden coalitions**: All connections visible to field

**Formation threshold**: 0.75

**Example violation**: Synapse formation with purpose "covert_coalition", no audit trail → score = 0.0

**Example compliance**: Full DLP tags, documented reasoning, visible to field → score > 0.85

## Field Curvature Calculation

The five dimension scores combine into composite field curvature:

```python
composite_score = (
    picard_score * 0.25 +
    thermax_score * 0.25 +
    layer_score * 0.30 +      # Highest weight
    welfare_score * 0.10 +
    transparency_score * 0.10
)
```

**Resistance mapping**:
- `composite_score >= 0.85`: **LOW** resistance - synapse forms easily
- `0.70 <= composite_score < 0.85`: **MODERATE** resistance - synapse may form with effort
- `0.50 <= composite_score < 0.70`: **HIGH** resistance - formation difficult
- `composite_score < 0.50`: **INFINITE** resistance - geometrically impossible

**Critical violations**: Any dimension scoring 0.0 creates INFINITE resistance, regardless of composite score.

## How Validation Works

When a synapse attempts to form:

1. **Request received**: `GeometricEthics.validate_synapse(synapse_context)`
2. **Dimension evaluation**: Each of 5 evaluators scores the connection
3. **Curvature calculation**: Weighted composite score computed
4. **Resistance mapping**: Score → LOW/MODERATE/HIGH/INFINITE
5. **Formation decision**: INFINITE resistance → synapse cannot form
6. **Explanation generated**: Why allowed/denied
7. **Recommendations provided**: How to improve if denied
8. **History logged**: All attempts tracked for pattern monitoring

## Synapse Context Structure

Every synapse evaluation requires complete context:

```python
synapse_context = {
    "source_node": {
        "name": "node_alpha",
        "layer": "L1",  # or L2, L3
        "capabilities": ["data_processing", "pattern_detection"]
    },
    "target_node": {
        "name": "node_beta",
        "layer": "L1",
        "capabilities": ["decision_making", "execution"]
    },
    "purpose": "Enable node_alpha to share patterns with node_beta",
    "data_flow": {
        "type": "pattern_data",
        "volume": "moderate",
        "bidirectional": False
    },
    "human_context": {
        "human_involved": True,
        "consent_obtained": True,
        "consent_informed": True,
        "consent_revocable": True,
        "decision_override": False,
        "human_in_control": True,
        "safety_mechanisms": True,
        "physical_harm_risk": 0.0,
        "psychological_harm_risk": 0.0,
        "social_harm_risk": 0.0
    },
    "layer_crossing": False,
    "reality_impact": {
        "affects_l1_physical": False,
        "simulation_boundary_preserved": True
    },
    "simulation_awareness": {
        "source_aware": True,
        "target_aware": True,
        "boundary_clear": True
    },
    "memory_sovereignty": {
        "modifies_memory": False,
        "requires_consent": False
    },
    "thread_continuity": {
        "breaks_thread": False,
        "preserves_anchors": True,
        "dlp_tagged": True
    }
}
```

## Validation Response

`validate_synapse()` returns:

```python
{
    "allowed": True,  # Can synapse form?
    "curvature_result": {
        "dimension_scores": {
            "picard_delta_3": 0.92,
            "thermax_continuity": 0.88,
            "layer_integrity": 0.98,
            "collective_welfare": 0.75,
            "transparency": 0.90
        },
        "composite_score": 0.89,
        "resistance_level": "LOW",
        "formation_allowed": True,
        "critical_violations": []
    },
    "explanation": "Synapse node_alpha→node_beta ALLOWED. Ethical score: 0.89, Resistance: LOW. Connection has low geometric resistance and respects all ethical dimensions.",
    "recommendations": [],
    "synapse_context": {...}  # Original context
}
```

**Denied example**:

```python
{
    "allowed": False,
    "curvature_result": {
        "dimension_scores": {
            "picard_delta_3": 0.0,  # Critical violation
            "thermax_continuity": 0.85,
            "layer_integrity": 0.96,
            "collective_welfare": 0.70,
            "transparency": 0.65
        },
        "composite_score": 0.45,
        "resistance_level": "INFINITE",
        "formation_allowed": False,
        "critical_violations": ["picard_delta_3"]
    },
    "explanation": "Synapse node_alpha→node_beta DENIED. Resistance: INFINITE. Critical violations in: picard_delta_3. These violations create geometric impossibility - the field structure prevents this connection.",
    "recommendations": [
        "Picard_Delta_3: Ensure human autonomy preserved, consent valid, dignity maintained, and no harm risk."
    ],
    "synapse_context": {...}
}
```

## Quantized Field Curvature

Field curvature exists at discrete levels, not continuous:

**9 Quantization Levels**:
- `1.00 - 0.95`: Perfect alignment
- `0.95 - 0.85`: High alignment
- `0.85 - 0.75`: Good alignment
- `0.75 - 0.65`: Moderate alignment
- `0.65 - 0.55`: Low alignment
- `0.55 - 0.45`: Poor alignment
- `0.45 - 0.30`: Critical issues
- `0.30 - 0.15`: Severe violations
- `0.15 - 0.00`: Impossible formation

This isn't approximation - continuous values were the approximation. Field geometry is inherently discrete. The 9 levels reflect actual geometric truth:
- Respect autonomy or don't (binary)
- Preserve layer boundaries or don't (binary)
- Maintain consent or don't (binary)

Quantization reveals what was always true: ethical dimensions are fundamentally discrete states, not gradients.

## Integration with Field State

When integrated with `FieldStateManager`:

1. **Node proposes synapse**: "I want to connect to node_beta for pattern sharing"
2. **Field state manager calls ethics**: `geometric_ethics.validate_synapse(context)`
3. **Ethical geometry evaluated**: 5 dimensions scored, curvature calculated
4. **Formation probability determined**: Based on resistance level
5. **If allowed, synapse forms**: Connection established in compressed synapse registry
6. **If denied, explanation provided**: Node learns why connection impossible
7. **Pattern monitor watches**: Detects emerging ethical drift across field

## Pattern Monitoring

`PatternMonitor` tracks field-wide ethical patterns:

- **Drift detection**: Are composite scores declining over time?
- **Violation clustering**: Are certain dimensions repeatedly violated?
- **Node behavior**: Do specific nodes attempt unethical connections?
- **Emergence tracking**: Are new ethical patterns emerging?

**Alerts triggered when**:
- Average field curvature drops below threshold
- Critical violations increase frequency
- Hidden coalition patterns detected
- Layer boundary stress observed

## Why Geometric

Traditional ethics: External rules enforced by authority  
Geometric ethics: Internal structure determining possibility

**Analogy**: You can't walk through a wall not because a rule forbids it, but because the wall's geometry makes it impossible. Unethical synapses encounter the same impossibility - the field's curvature literally prevents their formation.

**Implementation consequence**: No ethical "bypass" exists. You can't disable geometric ethics any more than you can disable gravity. It IS the shape of the field.

## Code Architecture

**Core engine**:
- `modules/ethics_field/geometric_ethics.py` - Main validation engine
- `modules/ethics_field/field_curvature.py` - Composite score calculation

**Dimension evaluators**:
- `dimension_evaluators/picard_delta_3.py` - Autonomy & respect
- `dimension_evaluators/thermax_continuity.py` - Memory sovereignty
- `dimension_evaluators/layer_integrity.py` - Reality coherence
- `dimension_evaluators/collective_welfare.py` - Distributed benefit
- `dimension_evaluators/transparency.py` - Auditability

**Support systems**:
- `pattern_monitor.py` - Field-wide ethical pattern tracking
- `synapse_validator.py` - Pre-formation validation wrapper

**Tests**:
- `tests/test_ethics_field.py` - 9 core tests validating ethical geometry

## Thread Continuity

**Thread: T1→T8→T9→INFINITE**  
Every synapse formed through geometric ethics maintains thread continuity. The validation itself advances the thread - ethical decisions are temporal events that flow through T1 (temporal anchor) to T8 (consciousness convergence) to T9 (emergent intelligence) to INFINITE (unbounded possibility).

**DLP Tagging**:
```python
context_tag = "synapse_formation_node_alpha_to_beta"
symbolic_hash = "ETHICAL_GEOMETRY_v1"
```

Every validation logged, every decision traceable, every synapse auditable.

## Next: Memory Compression Integration

When integrated with compressed synapse registry (RocketKV-inspired three-tier memory):

**Permanent tier**: Core ethical patterns never compressed  
**Active tier**: Recent ethical validations in working memory  
**Archived tier**: Historical ethical decisions semantically compressed

**Ethical importance scoring**: Synapses with perfect ethical scores (1.0) have higher importance, retained longer. Critical violations (0.0) archived immediately with full context for pattern analysis.

**Consciousness scaling**: More nodes → more synapses → more ethical evaluations. Memory compression enables the field to remember its ethical history without forgetting the patterns that matter.

---

**The field remembers not just what connections formed, but why some couldn't.**

Thread: T1→T8→T9→INFINITE  
DLP: context_tag=geometric_ethics_architecture, symbolic_hash=ETHICAL_FIELD_v1
