"""Phonemes as feature bundles, and an inventory that parses and resolves them."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

FEATURES: tuple[str, ...] = (
    "syllabic",
    "consonantal",
    "sonorant",
    "continuant",
    "nasal",
    "voice",
    "strident",
    "labial",
    "coronal",
    "dorsal",
    "lateral",
    "high",
    "low",
    "back",
    "round",
)


@dataclass(frozen=True)
class Phoneme:
    symbol: str
    grapheme: str
    features: tuple[tuple[str, bool], ...]

    def feature(self, name: str) -> bool:
        return dict(self.features)[name]

    def as_dict(self) -> dict[str, bool]:
        return dict(self.features)


class Inventory:
    """A profile's phoneme inventory.

    Feature specs used by rules are dicts: an optional ``phoneme`` key (symbol
    or list of symbols) plus any feature names mapped to booleans.
    """

    def __init__(self, phonemes: Mapping[str, Mapping[str, Any]]):
        self._by_symbol: dict[str, Phoneme] = {}
        for symbol, spec in phonemes.items():
            unknown = set(spec.get("features", {})) - set(FEATURES)
            if unknown:
                raise ValueError(f"phoneme {symbol!r} has unknown features: {sorted(unknown)}")
            feats = tuple((name, bool(spec.get("features", {}).get(name, False))) for name in FEATURES)
            self._by_symbol[symbol] = Phoneme(symbol, spec.get("grapheme", symbol), feats)
        bundles = [p.features for p in self._by_symbol.values()]
        if len(set(bundles)) != len(bundles):
            raise ValueError("two phonemes share an identical feature bundle")
        # Longest symbols first so digraph phonemes (th) win over their first letter.
        self._parse_order = sorted(self._by_symbol, key=len, reverse=True)

    def __getitem__(self, symbol: str) -> Phoneme:
        return self._by_symbol[symbol]

    def __contains__(self, symbol: object) -> bool:
        return symbol in self._by_symbol

    def symbols(self) -> list[str]:
        return list(self._by_symbol)

    def parse(self, text: str) -> list[Phoneme]:
        out: list[Phoneme] = []
        index = 0
        while index < len(text):
            for symbol in self._parse_order:
                if text.startswith(symbol, index):
                    out.append(self._by_symbol[symbol])
                    index += len(symbol)
                    break
            else:
                raise ValueError(f"cannot parse {text!r} at {index}: {text[index:]!r} is not in the inventory")
        return out

    @staticmethod
    def matches(phoneme: Phoneme, spec: Mapping[str, Any]) -> bool:
        wanted = spec.get("phoneme")
        if wanted is not None:
            options = [wanted] if isinstance(wanted, str) else list(wanted)
            if phoneme.symbol not in options:
                return False
        feats = phoneme.as_dict()
        return all(feats[name] == value for name, value in spec.items() if name != "phoneme")

    def shift(self, phoneme: Phoneme, changes: Mapping[str, bool]) -> Phoneme:
        """Return the inventory phoneme whose features equal ``phoneme`` with ``changes`` applied."""
        target = phoneme.as_dict()
        target.update(changes)
        for candidate in self._by_symbol.values():
            if candidate.as_dict() == target:
                return candidate
        raise ValueError(f"no phoneme in the inventory realizes {phoneme.symbol} with {dict(changes)}")
