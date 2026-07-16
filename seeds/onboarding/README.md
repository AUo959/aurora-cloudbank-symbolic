# Engineer Onboarding Seed Staging

Files in this directory are optional onboarding receipts created by `scripts/aurora_onboard.py`. They are **staged symbolic memory seeds**, not canonical facts, staff records, credentials, or authorization grants.

Each generated Markdown file uses YAML front matter with:

- `seed_type: engineer_onboarding`
- `seed_status: staged`
- `engineer_handle`
- UTC `created_at`
- `anchor_seed: EOS_SEED_ORION`
- `ethics_protocol: Picard_Delta_3`
- generating `source`

The onboarding command verifies the file after writing it. Committing or promoting a seed requires normal review against `CANON_INDEX.md` and the relevant authoritative sources; generation alone never promotes it.
