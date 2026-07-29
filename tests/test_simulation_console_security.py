from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSOLE = ROOT / "static" / "aurora-simulation-console.html"


def _sha256_source(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return f"'sha256-{base64.b64encode(digest).decode('ascii')}'"


def test_console_csp_allows_only_hashed_inline_content():
    html = CONSOLE.read_text(encoding="utf-8")
    csp_match = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', html)
    assert csp_match is not None
    csp = csp_match.group(1)

    assert "'unsafe-inline'" not in csp
    assert "'unsafe-hashes'" in csp

    style_blocks = re.findall(r"<style>(.*?)</style>", html, re.DOTALL)
    script_blocks = re.findall(r"<script>(.*?)</script>", html, re.DOTALL)
    event_handlers = set(re.findall(r'\son[a-z]+="([^"]+)"', html))
    assert len(style_blocks) == 1
    assert len(script_blocks) == 1
    assert event_handlers

    for inline_source in [*style_blocks, *script_blocks, *event_handlers]:
        assert _sha256_source(inline_source) in csp


def test_console_uses_web_crypto_for_display_randomness():
    html = CONSOLE.read_text(encoding="utf-8")
    assert "Math.random" not in html
    assert "window.crypto.getRandomValues" in html
