"""Reverse derivation: from a written name back to the etymologies that produce it.

The analyzer derives every one- and two-element form the lexicon allows, in
every era and dialect, and indexes them by spelling. A name is then:

* ``derived``     - at least one etymology reproduces it exactly
* ``loan``        - it uses letters the language lacks; the loan map gives how a
                    native speaker would hear it (a hypothesis, never a canon claim)
* ``near``        - no exact etymology, but one within ``near_distance`` edits
* ``unexplained`` - none of the above

``blind_recovery`` checks the analyzer against the corpus: for each attested
name, without being told its etymology, does the analysis include the recorded
roots and era, and how many rival etymologies also fit?
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any, Iterator

from .engine import COMMON, Derivation, Engine
from .phonaesthetics import normalize


@dataclass
class Analysis:
    written: str
    status: str
    exact: list[Derivation] = field(default_factory=list)
    nearest: list[tuple[int, Derivation]] = field(default_factory=list)
    foreign: list[str] = field(default_factory=list)
    adapted: str | None = None

    def summary(self) -> dict[str, Any]:
        return {
            "written": self.written,
            "status": self.status,
            "etymologies": [_etymology(d) for d in self.exact],
            "nearest": [{"distance": dist, **_etymology(d)} for dist, d in self.nearest],
            "foreign_letters": self.foreign,
            "loan_adapted": self.adapted,
        }


def _etymology(d: Derivation) -> dict[str, Any]:
    return {"form": d.formal, "roots": list(d.roots), "era": d.era, "dialect": d.dialect, "gloss": d.gloss}


class Analyzer:
    def __init__(self, engine: Engine, near_distance: int = 2):
        self.engine = engine
        self.near_distance = near_distance
        self._index: dict[str, list[Derivation]] | None = None

    @classmethod
    def shared(cls, engine: Engine) -> "Analyzer":
        """One analyzer per profile version: the index (every derivable form) is costly to build."""
        key = (engine.profile.name, engine.profile.digest)
        if key not in _SHARED:
            _SHARED[key] = cls(engine)
        return _SHARED[key]

    # ------------------------------------------------------------------ index

    @property
    def index(self) -> dict[str, list[Derivation]]:
        if self._index is None:
            self._index = {}
            for roots, era, dialect in self._combinations():
                derived = self.engine.derive(roots, era, dialect=dialect)
                self._index.setdefault(normalize(derived.formal), []).append(derived)
        return self._index

    def _combinations(self) -> Iterator[tuple[tuple[str, ...], str, str]]:
        dialects = [COMMON, *sorted(self.engine.profile.dialects)]
        eras = list(self.engine.profile.eras)
        return itertools.product(self._shapes(), eras, dialects)

    def _shapes(self) -> list[tuple[str, ...]]:
        """Single roots, and pairs of a root or proclitic followed by a root or suffix."""
        heads = self._keys("root")
        leaders = heads + self._keys("proclitic")
        tails = heads + self._keys("suffix")
        return [(h,) for h in heads] + list(itertools.product(leaders, tails))

    def _keys(self, kind: str) -> list[str]:
        return [k for k, r in self.engine.profile.lexicon.items() if r.kind == kind]

    # ------------------------------------------------------------------ analysis

    def analyze(self, written: str, nearest: int = 3) -> Analysis:
        key = normalize(written)
        exact = _dedupe([d for d in self.index.get(key, []) if _spelled_as(d, written)])
        if exact:
            return Analysis(written, "derived", exact=exact)
        foreign = self.foreign_letters(key)
        if foreign:
            return Analysis(written, "loan", foreign=foreign, adapted=self.adapt_loan(key))
        close = self._nearest(key, nearest)
        status = "near" if close and close[0][0] <= self.near_distance else "unexplained"
        return Analysis(written, status, nearest=close)

    def foreign_letters(self, written: str) -> list[str]:
        native = set("".join(self.engine.profile.inventory.symbols()))
        return sorted({ch for ch in normalize(written) if ch.isalpha() and ch not in native})

    def adapt_loan(self, written: str) -> str:
        """How a native speaker would hear a borrowed spelling (profile ``loan_map``)."""
        loan_map = self.engine.profile.loan_map
        return "".join(loan_map.get(ch, ch) for ch in normalize(written))

    def _nearest(self, key: str, limit: int) -> list[tuple[int, Derivation]]:
        scored = sorted((_distance(key, form), form) for form in self.index)
        return [(dist, self.index[form][0]) for dist, form in scored[:limit]]

    # ------------------------------------------------------------------ validation

    def blind_recovery(self, *, include_fixtures: bool = True) -> list[dict[str, Any]]:
        """Recover each corpus name's recorded etymology from its spelling alone."""
        rows = list(self.engine.profile.attested)
        if include_fixtures:
            rows += list(self.engine.profile.fixtures)
        return [self._recover(row) for row in rows]

    def _recover(self, row: dict[str, Any]) -> dict[str, Any]:
        """Recovered = the recorded roots and era are among the exact etymologies.

        ``rival_roots``: different roots that spell the same name (a true rival
        etymology). ``other_eras``: the recorded roots coined in another era also
        spell it, so the era cannot be read off the form.
        """
        analysis = self.analyze(row["formal"])
        roots, era = tuple(row["roots"]), row["era"]
        found = any((d.roots, d.era) == (roots, era) for d in analysis.exact)
        return {
            "name": row["formal"],
            "recovered": found,
            "rival_roots": sorted({d.roots for d in analysis.exact} - {roots}),
            "other_eras": sorted({d.era for d in analysis.exact if d.roots == roots and d.era != era}),
        }


_SHARED: dict[tuple[str, str], "Analyzer"] = {}


def _spelled_as(derived: Derivation, written: str) -> bool:
    """Junction marks date a coinage, so a formal spelling (apostrophe or hyphen) must match exactly.

    A spaced spelling must match the informal register (Vel Surak); a solid spelling may be either the
    informal register or an older fused coinage.
    """
    text = written.replace("\u2019", "'").lower()
    if "'" in text or "-" in text:
        return derived.formal.lower() == text
    if " " in text:
        return derived.informal.lower() == text
    return True


def _dedupe(derivations: list[Derivation]) -> list[Derivation]:
    """One entry per (roots, era); dialects that agree on the form collapse to the first."""
    seen: set[tuple[tuple[str, ...], str | None]] = set()
    out = []
    for d in derivations:
        if (d.roots, d.era) not in seen:
            seen.add((d.roots, d.era))
            out.append(d)
    return out


def _distance(a: str, b: str) -> int:
    """Levenshtein edit distance."""
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]
