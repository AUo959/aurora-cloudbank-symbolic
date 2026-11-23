"""Syllabification (onset maximization) and phonotactic checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .segments import Phoneme


@dataclass(frozen=True)
class Syllable:
    onset: tuple[str, ...]
    nucleus: str
    coda: tuple[str, ...]

    def text(self) -> str:
        return "".join(self.onset) + self.nucleus + "".join(self.coda)


@dataclass(frozen=True)
class Phonotactics:
    onsets: frozenset[tuple[str, ...]]
    codas: frozenset[tuple[str, ...]]
    final_codas: frozenset[tuple[str, ...]]

    @classmethod
    def from_profile(cls, data: dict, consonants: Sequence[str]) -> "Phonotactics":
        singles = {(c,) for c in consonants}
        onsets = singles | {tuple(c) for c in data.get("onset_clusters", [])}
        codas = (singles - {(c,) for c in data.get("never_coda", [])}) | {
            tuple(c) for c in data.get("coda_clusters", [])
        }
        final = {c for c in codas if not (len(c) == 1 and c[0] in data.get("never_final", []))}
        return cls(frozenset(onsets), frozenset(codas), frozenset(final))


class PhonotacticError(ValueError):
    pass


def _split_cluster(cluster: tuple[str, ...], tactics: Phonotactics) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split an intervocalic cluster into (coda, onset), giving the onset its longest legal tail."""
    for k in range(len(cluster)):
        if cluster[k:] in tactics.onsets:
            return cluster[:k], cluster[k:]
    return cluster, ()


def _word_onset(symbols: Sequence[str], nuclei: Sequence[int], tactics: Phonotactics) -> tuple[str, ...]:
    """The consonants before the first nucleus, which must form a legal onset."""
    if not nuclei:
        raise PhonotacticError(f"no syllable nucleus in {''.join(symbols)!r}")
    onset = tuple(symbols[: nuclei[0]])
    if onset and onset not in tactics.onsets:
        raise PhonotacticError(f"illegal word onset {''.join(onset)!r} in {''.join(symbols)!r}")
    return onset


def syllabify(segments: Sequence[Phoneme], tactics: Phonotactics) -> list[Syllable]:
    """Split a segment string into syllables, giving each nucleus the longest legal onset."""
    symbols = [s.symbol for s in segments]
    nuclei = [i for i, s in enumerate(segments) if s.feature("syllabic")]
    onset = _word_onset(symbols, nuclei, tactics)
    syllables: list[Syllable] = []
    ends = nuclei[1:] + [len(symbols)]
    for nucleus, end in zip(nuclei, ends):
        cluster = tuple(symbols[nucleus + 1 : end])
        final = end == len(symbols)
        coda, next_onset = (cluster, ()) if final else _split_cluster(cluster, tactics)
        syllables.append(Syllable(onset, symbols[nucleus], coda))
        onset = next_onset
    return syllables


def check(segments: Sequence[Phoneme], tactics: Phonotactics) -> list[str]:
    """Return phonotactic violations (empty when the form is legal)."""
    try:
        syllables = syllabify(segments, tactics)
    except PhonotacticError as exc:
        return [str(exc)]
    problems = []
    for index, syllable in enumerate(syllables):
        if not syllable.coda:
            continue
        allowed = tactics.final_codas if index == len(syllables) - 1 else tactics.codas
        if syllable.coda not in allowed:
            problems.append(f"illegal coda {''.join(syllable.coda)!r} in syllable {syllable.text()!r}")
    return problems
