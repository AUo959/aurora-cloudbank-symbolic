"""Regression: HTTP error details must not expose internal exception strings (Issue #783)."""
import re
from pathlib import Path
import pytest


@pytest.mark.unit
def test_no_detail_str_e_in_source():
    """Ensure no file in api/, modules/, src/ leaks exception detail via str(e)."""
    skip_files = {"fastapi_security.py", "error_helpers.py"}
    pattern = re.compile(r'detail\s*=\s*(?:str\(e\)|f["\'].*\{(?:str\()?e(?:\))?\}.*["\'])')
    offenders = []
    for root in (Path("api"), Path("modules"), Path("src")):
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if path.name in skip_files:
                continue
            text = path.read_text(errors="replace")
            if pattern.search(text):
                offenders.append(str(path))
    assert offenders == [], f"detail=str(e) leak found in: {offenders}"
