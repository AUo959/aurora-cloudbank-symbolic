"""Every declared requirement must carry an upper bound (#1366).

An unbounded `>=` floor admits the next breaking major on any fresh resolve.
That is not hypothetical here: `mcp>=1.28.1` admitted `mcp 2.0.0`, whose
handler-registration API is incompatible, and the failure was misdiagnosed as
"1.28.1 lacks Server.list_tools" (#1384) because the installed package was
never 1.28.1.

This test makes the policy self-enforcing instead of a one-off cleanup.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIREMENT_FILES = ["requirements.txt", "requirements-test.txt"]

# Packages deliberately left unbounded, each with a stated reason. Adding an
# entry here is a decision; leaving a package out of it is not.
EXEMPT = {
    # certifi is the CA trust store, versioned CalVer. An upper bound would
    # freeze the certificate bundle at a release boundary, which is a security
    # regression rather than a protection: stale roots are the failure mode.
    "certifi": "CA trust store on CalVer; pinning would freeze the cert bundle",
}


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def declared_requirements(path: Path) -> list[tuple[int, str, str]]:
    """Yield (line_number, package, full_spec) for real requirement lines."""
    found = []
    for number, raw in enumerate(path.read_text().splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        name = re.split(r"[\[><=!~;\s]", line)[0]
        if name:
            found.append((number, normalize(name), line))
    return found


@pytest.mark.parametrize("filename", REQUIREMENT_FILES)
def test_requirement_file_is_readable(filename: str) -> None:
    """Guards the rest of this file against silently testing nothing."""
    path = REPO_ROOT / filename
    assert path.exists(), f"{filename} is missing"
    assert declared_requirements(path), f"{filename} declares no requirements"


@pytest.mark.parametrize("filename", REQUIREMENT_FILES)
def test_every_requirement_has_an_upper_bound(filename: str) -> None:
    path = REPO_ROOT / filename
    unbounded = [
        f"{filename}:{number} {spec}"
        for number, name, spec in declared_requirements(path)
        if name not in EXEMPT and "<" not in spec and "==" not in spec
    ]
    assert not unbounded, (
        "These requirements admit the next breaking major on a fresh resolve:\n  "
        + "\n  ".join(unbounded)
        + "\n\nAdd an upper bound (usually the next major), or add the package to "
        "EXEMPT in this test with a written reason."
    )


def test_exemptions_are_documented_and_real() -> None:
    """An exemption must name a package that is actually declared."""
    declared = set()
    for filename in REQUIREMENT_FILES:
        declared |= {name for _, name, _ in declared_requirements(REPO_ROOT / filename)}
    for package, reason in EXEMPT.items():
        assert reason.strip(), f"{package} is exempt with no stated reason"
        assert package in declared, (
            f"{package} is exempt but no longer declared; remove the exemption"
        )


def test_certifi_is_still_unbounded() -> None:
    """Pins the reasoning, so a future sweep does not 'fix' it back."""
    text = (REPO_ROOT / "requirements.txt").read_text()
    line = next(
        (ln for ln in text.splitlines() if ln.strip().startswith("certifi")), ""
    )
    assert line, "certifi is no longer declared"
    assert "<" not in line.split("#", 1)[0], (
        "certifi must stay unbounded: it is the CA trust store, and an upper "
        "bound freezes the certificate bundle. See EXEMPT in this file."
    )
