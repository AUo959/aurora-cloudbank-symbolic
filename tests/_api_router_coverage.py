"""
Deterministic router-coverage helpers for tests/test_api_router_coverage.py.

Kept separate from the test file (no `test_` prefix) so it can be imported
and unit-tested against synthetic source, not just the real
api/aurora_api.py — see test_api_router_coverage.py's regression fixtures.

Approach: static AST analysis of `app.include_router(...)` call sites in
api/aurora_api.py, not runtime introspection of the live app's registered
routes. This repo's routers are heavily gated behind optional-dependency
try/except blocks (Redis, OpenAI, PyTorch, etc.) — which routers actually
end up on `app.routes` depends on what's installed/configured in whatever
environment runs the test, not on what's declared in source. AST analysis
of the include_router() call sites is deterministic regardless of that.

This does NOT attempt to resolve prefixes for routers whose APIRouter(...)
prefix is defined in another file — that mapping is maintained by hand in
ROUTER_SYMBOL_TO_INVENTORY_ID below and cross-checked, not inferred, since
static cross-file prefix resolution is out of scope for what this needs to
catch (an added/removed include_router call, not a changed prefix value).
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List


def extract_include_router_symbols(source: str) -> List[str]:
    """Return the source-text of each first positional arg to an
    `app.include_router(...)` call, in file order, duplicates included.

    Handles both plain identifiers (`app.include_router(FOO_ROUTER)`) and
    call expressions (`app.include_router(build_sensor_router(_x)), prefix=...)`)
    by rendering the argument back to source text via ast.unparse.
    """
    tree = ast.parse(source)
    symbols: List[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "include_router"):
            continue
        if not (isinstance(func.value, ast.Name) and func.value.id == "app"):
            continue
        if not node.args:
            continue
        symbols.append(ast.unparse(node.args[0]))

    return symbols


def extract_include_router_symbols_from_file(path: Path) -> List[str]:
    return extract_include_router_symbols(path.read_text(encoding="utf-8"))
