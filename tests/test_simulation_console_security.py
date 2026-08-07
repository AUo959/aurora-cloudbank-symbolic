from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
CONSOLE = ROOT / "static" / "aurora-simulation-console.html"
CHECK = TestCase()


def _sha256_source(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return f"'sha256-{base64.b64encode(digest).decode('ascii')}'"


def test_console_csp_allows_only_hashed_inline_content():
    html = CONSOLE.read_text(encoding="utf-8")
    csp_match = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', html)
    CHECK.assertIsNotNone(csp_match)
    csp = csp_match.group(1)

    CHECK.assertNotIn("'unsafe-inline'", csp)
    CHECK.assertNotIn("'unsafe-hashes'", csp)

    style_blocks = re.findall(r"<style>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    script_blocks = re.findall(r"<script>(.*?)</script>", html, re.DOTALL | re.IGNORECASE)
    event_handlers = set(re.findall(r'\son[a-z]+="([^"]+)"', html, re.IGNORECASE))
    bound_actions = set(re.findall(r'data-console-action="([^"]+)"', html))
    CHECK.assertEqual(len(style_blocks), 1)
    CHECK.assertEqual(len(script_blocks), 1)
    CHECK.assertFalse(event_handlers)
    CHECK.assertEqual(
        bound_actions,
        {
            "clearCollaboration",
            "computeGeometricProduct",
            "computeMultiple",
            "exploreRelationships",
            "generateMultipleVectors",
            "generateQuantumVector",
            "loadOperatorSnapshot",
            "loadSynergyComponents",
            "performSymbolicReasoning",
            "shareDiscovery",
        },
    )

    for inline_source in [*style_blocks, *script_blocks]:
        CHECK.assertIn(_sha256_source(inline_source), csp)
    for action in bound_actions:
        CHECK.assertRegex(script_blocks[0], rf"\b{action},")


def test_console_uses_web_crypto_for_display_randomness():
    html = CONSOLE.read_text(encoding="utf-8")
    CHECK.assertNotIn("Math.random", html)
    CHECK.assertIn("window.crypto.getRandomValues", html)
