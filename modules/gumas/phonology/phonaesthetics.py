"""How much a written name sounds like the attested names of its language.

A letter-bigram model trained only on canon evidence: the canon corpus forms
(formal and informal) and the canon given names the rules cannot yet derive.
Those given names are still real Velari names, so they are evidence of how
Velari sounds even where the sound laws do not reach them.

The score is the mean log-probability per bigram, with add-k smoothing. Higher
is more Velari-sounding. It ranks candidates; it never admits or rejects one.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Iterable

START, END = "^", "$"


def normalize(written: str) -> str:
    """Spelling key: lowercase, without junction marks (apostrophe, hyphen) or the space of a split informal form."""
    return "".join(ch for ch in written.lower() if ch not in "'\u2019- ")


class SoundModel:
    def __init__(self, words: Iterable[str], alphabet: Iterable[str], k: float = 0.5):
        self.words = tuple(normalize(w) for w in words)
        letters = set("".join(alphabet)) | set("".join(self.words))
        self.symbols = frozenset(letters | {END})
        self.k = k
        self.pairs: Counter[tuple[str, str]] = Counter()
        self.firsts: Counter[str] = Counter()
        for word in self.words:
            for a, b in _bigrams(word):
                self.pairs[(a, b)] += 1
                self.firsts[a] += 1

    def probability(self, a: str, b: str) -> float:
        return (self.pairs[(a, b)] + self.k) / (self.firsts[a] + self.k * len(self.symbols))

    def score(self, written: str) -> float:
        grams = _bigrams(normalize(written))
        return sum(math.log(self.probability(a, b)) for a, b in grams) / len(grams)


def _bigrams(word: str) -> list[tuple[str, str]]:
    padded = START + word + END
    return list(zip(padded, padded[1:]))
