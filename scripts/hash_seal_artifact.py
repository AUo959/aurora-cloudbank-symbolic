#!/usr/bin/env python3
"""
T3A_DECISION_PR77
Seed: EOS_SEED_ORION
Ethics: Picard_Delta_3
Purpose:
  Generic hashing & seal generation for artifacts (glyphcards, manifests, split reports).
Usage:
  python scripts/hash_seal_artifact.py --input docs/glyphcards/PR77_BASELINE.md --out-dir artifacts/seals
Outputs:
  - <artifact_name>.sha256 containing SHA256 and filename.
  - JSON metadata sidecar with anchor + seed + ethics + DLP + timestamp + version.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import sys

ANCHOR = "T3A_DECISION_PR77"
SEED = "EOS_SEED_ORION"
ETHICS = "Picard_Delta_3"
DLP = "L1_OK"
SCHEMA_VERSION = "1.0.0"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description="Generate hash seal + metadata for an artifact.")
    ap.add_argument("--input", required=True, help="Path to artifact file.")
    ap.add_argument("--out-dir", default="artifacts/seals", help="Directory to store seal outputs.")
    ap.add_argument("--anchor", default=ANCHOR)
    ap.add_argument("--seed", default=SEED)
    ap.add_argument("--ethics", default=ETHICS)
    ap.add_argument("--dlp", default=DLP)
    ap.add_argument("--label", default=None, help="Optional label for grouping.")
    args = ap.parse_args()

    artifact = pathlib.Path(args.input)
    if not artifact.exists():
        print(f"[ERROR] Artifact not found: {artifact}", file=sys.stderr)
        sys.exit(2)

    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    digest = sha256_file(artifact)
    seal_filename = artifact.name + ".sha256"
    seal_path = out_dir / seal_filename
    with seal_path.open("w") as f:
        f.write(f"{digest}  {artifact.name}\n")

    meta = {
        "anchor": args.anchor,
        "seed": args.seed,
        "ethics": args.ethics,
        "dlp": args.dlp,
        "artifact": str(artifact),
        "artifact_size_bytes": artifact.stat().st_size,
        "sha256": digest,
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z'),
        "schema_version": SCHEMA_VERSION,
        "label": args.label,
        "tool": "hash_seal_artifact.py"
    }
    meta_path = out_dir / (artifact.name + ".metadata.json")
    with meta_path.open("w") as f:
        json.dump(meta, f, indent=2)

    print(f"[OK] Seal generated for {artifact} -> {seal_path}")
    print(digest)


if __name__ == "__main__":
    main()
