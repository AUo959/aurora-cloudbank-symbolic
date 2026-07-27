#!/usr/bin/env python3
"""Install the validated Gate-001A Run 001 package from staged archive chunks."""

from __future__ import annotations

import base64
import hashlib
import io
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_DIR = Path(__file__).with_name(".gate001a_payload")
EXPECTED_ARCHIVE_SHA256 = "24bf5a734d4c35b483ce024a4a0980be7441e3f2b7fdfe80a169679bceaa6a5b"
VERIFICATION = ROOT / "docs/security/recovered_protocol_wiring_verification.md"
OLD_STATUS = "**Status:** ⏳ PENDING — Gate-001A and Gate-001B records are maintained separately"
NEW_STATUS = (
    "**Status:** ⚠️ Gate-001A Run 001 FINDING — deterministic capability PASS; "
    "subject finding tracked in issue #1361; Gate-001B remains PENDING"
)
LATEST_EVENT = (
    "**Latest Gate-001A event:** "
    "`AURORA-GATE-001A-RECOVERED-PROTOCOL-WIRING-001` · "
    "baseline `3142aa47afac0b8e63cc5bc46f9fa8ae40592354` · "
    "report `docs/security/assurance_runs/gate-001a/"
    "2026-07-27-run-001-recovered-protocol-wiring/"
    "AURORA_SECURITY__REPORT__GATE_001A_RECOVERED_PROTOCOL_WIRING__v1.0__2026-07-27.md`"
)


def main() -> None:
    chunks = sorted(PAYLOAD_DIR.glob("part*.b64"), key=lambda path: path.name)
    if not chunks:
        raise SystemExit("No staged Gate-001A payload chunks found")

    encoded = b"".join(path.read_bytes().strip() for path in chunks)
    archive = base64.b64decode(encoded, validate=True)
    observed = hashlib.sha256(archive).hexdigest()
    if observed != EXPECTED_ARCHIVE_SHA256:
        raise SystemExit(
            f"Gate-001A archive digest mismatch: expected {EXPECTED_ARCHIVE_SHA256}, observed {observed}"
        )

    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        root_resolved = ROOT.resolve()
        for member in bundle.infolist():
            target = (ROOT / member.filename).resolve()
            if target != root_resolved and root_resolved not in target.parents:
                raise SystemExit(f"Unsafe archive member: {member.filename}")
        bundle.extractall(ROOT)

    text = VERIFICATION.read_text(encoding="utf-8")
    if OLD_STATUS not in text:
        raise SystemExit("Expected pending Gate-001 status line was not found")
    updated = text.replace(OLD_STATUS, f"{NEW_STATUS}  \n{LATEST_EVENT}", 1)
    VERIFICATION.write_text(updated, encoding="utf-8")

    print(f"Installed {len(bundle.infolist())} Gate-001A package members")
    print(f"Archive SHA-256: {observed}")


if __name__ == "__main__":
    main()
