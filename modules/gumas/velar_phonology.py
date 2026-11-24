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
from .phonology.analysis import Analysis, Analyzer
from .phonology.engine import COMMON, Derivation, Engine, shared_roots

ENGINE = Engine("velari")
ANALYZER = Analyzer(ENGINE)
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


class Dialect(str, Enum):
    COMMON = COMMON
    IMPERIAL = "imperial"
    UNION = "union"


def _dialect(dialect: Dialect | str | None) -> str | None:
    return Dialect(dialect).value if dialect is not None else None


def derive(
    roots: Sequence[str], stratum: Stratum | str = Stratum.ELDER, dialect: Dialect | str | None = None
) -> Derivation:
    return ENGINE.derive(roots, Stratum(stratum).value, dialect=_dialect(dialect))


def fit_attested(*, include_fixtures: bool = False) -> list[dict[str, Any]]:
    return ENGINE.fit_attested(include_fixtures=include_fixtures)


def generate_house_names(
    lineage: Lineage | str,
    *,
    seed: int,
    count: int = 6,
    stratum: Stratum | str | None = None,
    dialect: Dialect | str | None = None,
    registry: Any | None = None,
    weighted: bool = False,
    sporadic: bool = True,
) -> list[Derivation]:
    """House names for a lineage; the dialect defaults to the lineage's own."""
    eras = [Stratum(stratum).value] if stratum else None
    return ENGINE.generate(
        Lineage(lineage).value,
        seed=seed,
        count=count,
        eras=eras,
        dialect=_dialect(dialect),
        registry=registry,
        weighted=weighted,
        sporadic=sporadic,
    )


def generate_given_names(
    *,
    seed: int,
    count: int = 6,
    stratum: Stratum | str | None = None,
    dialect: Dialect | str | None = None,
    registry: Any | None = None,
    weighted: bool = False,
    sporadic: bool = True,
) -> list[Derivation]:
    """Given names: a content root plus a personal suffix."""
    eras = [Stratum(stratum).value] if stratum else None
    return ENGINE.generate_given_names(
        seed=seed,
        count=count,
        eras=eras,
        dialect=_dialect(dialect),
        registry=registry,
        weighted=weighted,
        sporadic=sporadic,
    )


def analyze(written: str) -> Analysis:
    """Reverse-derive a written Velari name: its etymologies, or why it has none."""
    return ANALYZER.analyze(written)


def blind_recovery(*, include_fixtures: bool = True) -> list[dict[str, Any]]:
    return ANALYZER.blind_recovery(include_fixtures=include_fixtures)


def phonotactic_ok(written: str) -> bool:
    """True when a written Velari form parses and satisfies Velari phonotactics."""
    try:
        segments = ENGINE.profile.inventory.parse(written.lower().replace("'", ""))
    except ValueError:
        return False
    return not syllables.check(segments, ENGINE.profile.tactics)


__all__ = [
    "ANALYZER",
    "ENGINE",
    "ENGINE_VERSION",
    "Analysis",
    "Derivation",
    "Dialect",
    "Lineage",
    "Stratum",
    "analyze",
    "blind_recovery",
    "derive",
    "fit_attested",
    "generate_given_names",
    "generate_house_names",
    "phonotactic_ok",
    "shared_roots",
]
