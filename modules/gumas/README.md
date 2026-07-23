# GUMAS L2 Naming Runtime

This package implements the executable naming contract documented as `GUMAS_NAMING_PROTOCOL_v0.1`.

## Responsibilities

- Produce deterministic candidate names from entity, faction, region, register, constraints, and seed.
- Load a CanonRec-exported registry snapshot.
- Reject exact collisions and configurable root, phonetic, or cadence crowding.
- Preserve rejected candidates and collision counts.
- Emit a complete `naming_receipt` for CanonRec admission.
- Permit owner selection from a deterministic shortlist without erasing the generator's audit trail.

## Minting flow

```bash
python scripts/gumas_name_mint.py \
  --entity-type PERSON \
  --entity-id char_example \
  --faction galactic_union \
  --region kharis_sector \
  --registry /tmp/l2_name_registry.json \
  --seed 4718224 \
  --count 6
```

Select a consequential name and emit the final receipt:

```bash
python scripts/gumas_name_mint.py \
  --entity-type PERSON \
  --entity-id char_example \
  --faction galactic_union \
  --region kharis_sector \
  --registry /tmp/l2_name_registry.json \
  --seed 4718224 \
  --count 6 \
  --select 2 \
  --output /tmp/char_example_naming_receipt.json
```

The generator proposes and audits names. CanonRec remains the authority that admits them.
