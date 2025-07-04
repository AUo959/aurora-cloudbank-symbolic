"""Stub ethics governor component."""
from __future__ import annotations

from typing import Any

from .base_component import Opal2Component


class EthicsGovernor(Opal2Component):
    """Very simple ethics filter."""

    name = "ethics"
    description = "Reject outputs containing forbidden keywords"
    capabilities = ["content_filter"]

    def __init__(self, banned: list[str] | None = None) -> None:
        super().__init__()
        if banned is None:
            banned = ["forbidden"]
        self.banned = [w.lower() for w in banned]

    def process(self, data: Any) -> Any:
        """Raise an error if ``data`` contains banned terms."""
        if isinstance(data, str):
            lowered = data.lower()
            if any(b in lowered for b in self.banned):
                raise ValueError("Ethics violation detected")
        return data
