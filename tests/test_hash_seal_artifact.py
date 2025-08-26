"""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
Test suite for hash_seal_artifact.py
Anchor: T3A_DECISION_PR77
Seed: EOS_SEED_ORION
Ethics: Picard_Delta_3
"""

import json
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = "scripts/hash_seal_artifact.py"


def test_hash_and_metadata_generation():
    sample = tempfile.NamedTemporaryFile(delete=False)
    sample.write(b"sample-data-123")
    sample.flush()
    sample.close()

    out_dir = tempfile.mkdtemp()
    _ = subprocess.run(
        [sys.executable, SCRIPT, "--input", sample.name, "--out-dir", out_dir],
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
    try:
        sample.write(b"sample-data-123")
        sample.flush()
        sample.close()

        out_dir = tempfile.mkdtemp()
        _ = subprocess.run(
            [sys.executable, SCRIPT, "--input", sample.name, "--out-dir", out_dir],
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
        assert meta["anchor"] == "T3A_DECISION_PR77"
    finally:
        pathlib.Path(sample.name).unlink()
