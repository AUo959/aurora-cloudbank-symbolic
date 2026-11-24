"""Velari (velar_imperium) names: a facade over ``modules.gumas.phonology``.

The language data lives in ``modules/gumas/phonology/profiles/velari/``; the
engine is language-neutral. This module keeps a small Velari-specific API.

The canonical spec is the Velar naming convention on
``canon/L2/entities/polities/polity_velar_imperium.json`` (``naming_conventions``).
The attested corpus in ``profiles/velari/attested.json`` must reproduce exactly.
Root glosses carry ``gloss_status`` and are not canon unless marked so.
Generated names still go through the naming gate; this module proposes forms
and does not admit them.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Sequence

from . import phonology
from .phonology import syllables
from .phonology.engine import Derivation, Engine, shared_roots

ENGINE = Engine("velari")
ENGINE_VERSION = phonology.ENGINE_VERSION


class Lineage(str, Enum):
    NOBLE = "noble"
    MILITARY = "military"
    SCHOLARLY = "scholarly"
    REFORMIST = "reformist"
    OUTWORLD = "outworld"


class Stratum(str, Enum):
    ELDER = "elder"
    MIDDLE = "middle"
    SCRIBAL = "scribal"


def derive(roots: Sequence[str], stratum: Stratum | str = Stratum.ELDER) -> Derivation:
    return ENGINE.derive(roots, Stratum(stratum).value)


def fit_attested(*, include_fixtures: bool = False) -> list[dict[str, Any]]:
    return ENGINE.fit_attested(include_fixtures=include_fixtures)


def generate_house_names(
    lineage: Lineage | str,
    *,
    seed: int,
    count: int = 6,
    stratum: Stratum | str | None = None,
    registry: Any | None = None,
) -> list[Derivation]:
    eras = [Stratum(stratum).value] if stratum else None
    return ENGINE.generate(Lineage(lineage).value, seed=seed, count=count, eras=eras, registry=registry)


def phonotactic_ok(written: str) -> bool:
    """True when a written Velari form parses and satisfies Velari phonotactics."""
    try:
        segments = ENGINE.profile.inventory.parse(written.lower().replace("'", ""))
    except ValueError:
        return False
    return not syllables.check(segments, ENGINE.profile.tactics)


__all__ = [
    "ENGINE",
    "ENGINE_VERSION",
    "Derivation",
    "Lineage",
    "Stratum",
    "derive",
    "fit_attested",
    "generate_house_names",
    "phonotactic_ok",
    "shared_roots",
]
