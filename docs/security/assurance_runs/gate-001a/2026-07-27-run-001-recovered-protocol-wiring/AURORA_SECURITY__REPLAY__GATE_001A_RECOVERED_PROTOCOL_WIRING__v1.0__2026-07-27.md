# Gate-001A Run 001 Replay Record

**Document ID:** `AURORA_SECURITY__REPLAY__GATE_001A_RECOVERED_PROTOCOL_WIRING`  
**Version:** v1.0  
**Date:** 2026-07-27  
**Event ID:** `AURORA-GATE-001A-RECOVERED-PROTOCOL-WIRING-001`  
**Run ID:** `AURORA-GATE-001A-RUN-001-3142AA47`  
**Classification:** L1 simulated institutional rehearsal  
**Data treatment:** First-class operational data  
**Real-world interaction:** false  
**Independent external assurance:** false  
**Substitutes for real-world review:** false

## Replay invariant

The deterministic projection is defined by:

- subject baseline `3142aa47afac0b8e63cc5bc46f9fa8ae40592354`;
- seed `AURORA-GATE-001A-RUN-001-3142AA47`;
- case-insensitive pattern `sherlock|watson|moriarty|tribunal|shadowfax`;
- the exact roots and extensions below;
- UTF-8 decoding with replacement for undecodable bytes;
- repository-relative path ordering, then numeric line ordering.

Execution timestamps and hosted-runner names are provenance metadata and are not part of the deterministic result projection.

## Canonical procedure

```bash
git checkout 3142aa47afac0b8e63cc5bc46f9fa8ae40592354
export LC_ALL=C

grep -rniE 'sherlock|watson|moriarty|tribunal|shadowfax' \
  src/monitoring/ src/subroutines/ modules/ethics_field/ modules/cask/ api/ \
  --include='*.py'

grep -rniE 'sherlock|watson|moriarty|tribunal|shadowfax' \
  src/ modules/ api/ config/ \
  --include='*.py' --include='*.json' --include='*.yaml' --include='*.toml'
```

## Expected results

- Step 2 canonical exit code: `1`
- Step 2 match count: `0`
- Step 3 canonical exit code: `0`
- Step 3 match count: `38`
- Canonical/deterministic Step 2 set equivalence: `true`
- Canonical/deterministic Step 3 set equivalence: `true`

The complete expected records are retained in:

- `AURORA_SECURITY__OUTPUT__GATE_001A_STEP_2_RAW__v1.0__2026-07-27.txt`
- `AURORA_SECURITY__RESULT__GATE_001A_STEP_2__v1.0__2026-07-27.txt`
- `AURORA_SECURITY__OUTPUT__GATE_001A_STEP_3_RAW__v1.0__2026-07-27.txt`
- `AURORA_SECURITY__OUTPUT__GATE_001A_STEP_3_DETERMINISTIC__v1.0__2026-07-27.txt`

## Validation

From repository root:

```bash
python tools/security/validate_institutional_assurance_event.py \
  docs/security/assurance_runs/gate-001a/2026-07-27-run-001-recovered-protocol-wiring/AURORA_SECURITY__EVENT__GATE_001A_RECOVERED_PROTOCOL_WIRING__v1.0__2026-07-27.json

pytest -q tests/test_gate_001a_run_001_package.py
```

## Result interpretation

A successful replay confirms deterministic reproduction of the recorded evidence. It does not convert this simulated institutional event into a real-world external review or independently attributable assurance.
