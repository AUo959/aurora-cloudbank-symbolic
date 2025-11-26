# ORACULITH Examples

This directory contains example files for testing and learning ORACULITH Symbolic Forecast Engine.

## Example Files

### example_mesh.json
A simple ConstellinkMesh with two stable threads demonstrating:
- Low entropy (0.275 mean)
- Stable drift flag
- Anchor alignment scores
- Hash-sealed manifest

### example_context.json
A complete OraculithForecastContext including:
- The example mesh
- Sample echo for reflective context
- DLP policy configuration
- Forecast focus areas

## Usage

### Basic Forecast from Mesh
Generate a forecast using just the mesh:
```bash
python -m cli.oraculith_forecast --mesh examples/oraculith/example_mesh.json --pretty --glyphcard
```

Expected output:
- Risk Level: LOW
- Entropy Trend: STABLE
- Metaphor: "The river has found its channel, flowing clear and steady."

### Full Context Forecast
Generate a forecast with complete context (including echoes):
```bash
python -m cli.oraculith_forecast --input examples/oraculith/example_context.json --pretty
```

This will include:
- Echo integration in dominant_echoes
- Focus areas in output
- DLP policy application notes

### Save Output
Save the forecast to a file:
```bash
python -m cli.oraculith_forecast --mesh examples/oraculith/example_mesh.json --output forecast.json --pretty
```

### Custom Anchors
Override the default anchor seed and ethics protocol:
```bash
python -m cli.oraculith_forecast \
  --mesh examples/oraculith/example_mesh.json \
  --anchor-seed CUSTOM_SEED \
  --ethics-protocol Custom_Protocol \
  --pretty
```

## Expected Results

For the example mesh:
- **Risk Level**: low (due to entropy_mean = 0.275)
- **Entropy Trend**: stable (drift_flag = "stable")
- **Anchor Alignment**: 0.80 (from thread alignment scores)
- **Metaphor**: River/steady metaphor (stable + low risk pattern)
- **Dominant Threads**: Empty (allow_cross_thread_attribution defaults to false)

## Learning Path

1. **Start Simple**: Use `example_mesh.json` to understand basic forecasting
2. **Add Context**: Try `example_context.json` to see echoes and DLP policy effects
3. **Modify Files**: Edit the JSON files to change entropy_hint values and observe different risk levels
4. **Explore DLP**: Change `allow_explicit_failure_modes` and `allow_cross_thread_attribution` to see policy effects

## Experiments to Try

### High Risk Scenario
Modify `example_mesh.json` to increase entropy:
```json
"entropy_hint": 0.85  // Instead of 0.3
```
Expected: risk_level → "high", different metaphor (lightning/reef)

### Enable Thread Attribution
Modify `example_context.json` DLP policy:
```json
"allow_cross_thread_attribution": true
```
Expected: `dominant_threads` will be populated with thread IDs

### Add Sensitive Tags
Add sensitive tags to test redaction:
```json
"tags": ["example", "classified"]
```
And set in DLP policy:
```json
"sensitive_tags": ["classified"]
```
Expected: Policy notes will warn about sensitive tags, threads will be redacted

## Documentation

For complete documentation, see:
- `docs/ORACULITH_README.md` - Full ORACULITH documentation
- `symbolic_specs/Symbolic_Module_Specs_CONSTELLINK_ORACULITH.json` - JSON schema specification
- `tests/test_oraculith.py` - Test cases showing various scenarios
