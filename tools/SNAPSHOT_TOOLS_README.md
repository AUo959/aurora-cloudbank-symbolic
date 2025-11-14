# Aurora CloudBank Snapshot & Reliquary Tools

**Quantum-symbolic state management with DLP tracking and ethical anchoring**

Anchor: `EOS_SEED_ORION` | Team: `AUo959-team` | Version: `v0.1.0` | Ethics: `Picard_Delta_3`

---

## ✅ Installation Complete

All snapshot, reliquary, and glyphcard tools are now operational!

### 🎯 Quick Verification

```bash
# Run tests
python3 -m pytest tools/snapshot/tests/test_snapshot.py -v

# Seal a snapshot
python3 -m tools.snapshot.cli seal --manifest sample_manifest.json --state-file sample_state.json --out-dir .snapshots

# Verify snapshot
python3 -m tools.snapshot.cli verify .snapshots/snapshot_*.json

# Generate glyphcard
python3 tools/glyphcard/generate.py .snapshots/snapshot_*.json
```

### 📦 Tools Included

1. **Snapshot Sealer** (`tools/snapshot/`) - Seal, verify, restore quantum-symbolic state
2. **Reliquary Indexer** (`tools/reliquary/`) - Manifest discovery & validation
3. **Glyphcard Generator** (`tools/glyphcard/`) - Visual cards & diffs

See the main tools README for full documentation.
