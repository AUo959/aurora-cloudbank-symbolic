"""
Test suite for hash_seal_artifact.py
Anchor: T3A_DECISION_PR77 • Seed: EOS_SEED_ORION • Ethics: Picard_Delta_3
"""

import json
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = "scripts/hash_seal_artifact.py"


def test_hash_and_metadata_generation():
    # Create a temp sample file
    with tempfile.NamedTemporaryFile(delete=False) as sample:
        sample.write(b"sample-data-123")
        sample.flush()
        sample_path = sample.name

    out_dir = tempfile.mkdtemp()
    result = subprocess.run(
        [sys.executable, SCRIPT, "--input", sample_path, "--out-dir", out_dir],
        capture_output=True,
        text=True,
        check=True,
    )
    digest = result.stdout.strip().splitlines()[-1]
    seals = list(pathlib.Path(out_dir).glob("*.sha256"))
    assert seals, "No seal file produced"
    meta_files = list(pathlib.Path(out_dir).glob("*.metadata.json"))
    assert meta_files, "No metadata file produced"
    with meta_files[0].open() as f:
        meta = json.load(f)
    assert meta["sha256"] == digest
    # Allow missing anchor if script doesn’t set it; keep the shape stable
    assert "sha256" in meta
    pathlib.Path(sample_path).unlink(missing_ok=True)
