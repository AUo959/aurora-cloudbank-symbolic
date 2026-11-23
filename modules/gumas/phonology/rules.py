"""Words as segment/boundary streams, a stress model, and data-defined sound laws.

A sound law is a dated rewrite. Its JSON form::

    {"id": "VL1", "name": "w-fortition", "date": 100, "era": "Old Velari",
     "target": {"phoneme": "w"},
     "change": {"features": {"consonantal": true, "sonorant": false}},
     "when": {"element_initial": true}}

``change`` is one of ``{"features": {...}}`` (move to the inventory phoneme with
those features), ``{"phoneme": "x"}``, ``{"delete": true}`` or
``{"geminate": true}``.

``when`` conditions (all must hold):

* ``element_initial`` / ``element_final`` / ``word_final``: position in the word
* ``before`` / ``after``: a sequence of specs immediately following/preceding
  the target; a spec is a feature dict, ``"+"`` (any internal boundary) or
  ``"#"`` (word edge)
* ``stress``: ``primary`` | ``secondary`` | ``stressed`` | ``unstressed``
* ``min_syllables``: the whole word has at least this many nuclei
* ``proclitic``: the target belongs to a proclitic morpheme

All matches are found on the input form and applied together, so a law never
feeds itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

from .segments import Inventory, Phoneme


@dataclass(frozen=True)
class Morph:
    key: str
    kind: str  # root | suffix | proclitic
    lineage: str | None = None


@dataclass(frozen=True)
class Seg:
    phoneme: Phoneme
    morph: int  # index into Word.morphs


@dataclass(frozen=True)
class Boundary:
    kind: str  # compound | suffix
    formed_at: int


Token = Seg | Boundary


@dataclass
class Word:
    tokens: list[Token]
    morphs: list[Morph]

    @classmethod
    def from_morph(cls, morph: Morph, segments: Sequence[Phoneme]) -> "Word":
        return cls([Seg(p, 0) for p in segments], [morph])

    @classmethod
    def join(cls, words: Sequence["Word"], formed_at: int) -> "Word":
        tokens: list[Token] = []
        morphs: list[Morph] = []
        for word in words:
            offset = len(morphs)
            if tokens:
                kind = "suffix" if word.morphs[0].kind == "suffix" else "compound"
                tokens.append(Boundary(kind, formed_at))
            tokens.extend(replace(t, morph=t.morph + offset) if isinstance(t, Seg) else t for t in word.tokens)
            morphs.extend(word.morphs)
        return cls(tokens, morphs)

    def phonemic(self) -> str:
        out = []
        for token in self.tokens:
            if isinstance(token, Seg):
                out.append(token.phoneme.symbol)
            else:
                out.append("-" if token.kind == "suffix" else "+")
        return "".join(out)

    def segments(self) -> list[Phoneme]:
        return [t.phoneme for t in self.tokens if isinstance(t, Seg)]


def assign_stress(word: Word) -> dict[int, str]:
    """Stress per token index (vowels only).

    Primary stress falls on the first vowel of the first non-proclitic root;
    every later compound element takes secondary stress on its first vowel.
    Suffixes and proclitics are unstressed.
    """
    stress: dict[int, str] = {}
    seen_morphs: set[int] = set()
    primary_given = False
    for index, token in enumerate(word.tokens):
        if not isinstance(token, Seg) or not token.phoneme.feature("syllabic"):
            continue
        morph = word.morphs[token.morph]
        if morph.kind != "root" or token.morph in seen_morphs:
            stress[index] = "unstressed"
            continue
        seen_morphs.add(token.morph)
        stress[index] = "secondary" if primary_given else "primary"
        primary_given = True
    return stress


@dataclass(frozen=True)
class SoundLaw:
    law_id: str
    name: str
    date: int
    era: str
    description: str
    target: Mapping[str, Any]
    change: Mapping[str, Any]
    when: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SoundLaw":
        allowed = {"element_initial", "element_final", "word_final", "before", "after",
                   "stress", "min_syllables", "proclitic"}  # fmt: skip
        unknown = set(data.get("when", {})) - allowed
        if unknown:
            raise ValueError(f"law {data['id']} uses unknown conditions: {sorted(unknown)}")
        return cls(
            law_id=data["id"],
            name=data["name"],
            date=int(data["date"]),
            era=data.get("era", ""),
            description=data.get("description", ""),
            target=data["target"],
            change=data["change"],
            when=data.get("when", {}),
        )

    # ------------------------------------------------------------------ matching

    def _spec_at(self, word: Word, index: int, spec: Any) -> bool:
        tokens = word.tokens
        if spec == "#":
            return index < 0 or index >= len(tokens)
        if index < 0 or index >= len(tokens):
            return False
        token = tokens[index]
        if spec == "+":
            return isinstance(token, Boundary)
        return isinstance(token, Seg) and Inventory.matches(token.phoneme, spec)

    def _sequence(self, word: Word, start: int, specs: Sequence[Any], step: int) -> bool:
        position = start
        for spec in specs:
            if not self._spec_at(word, position, spec):
                return False
            if spec == "#":
                return True
            position += step
        return True

    def _matches(self, word: Word, index: int, stress: dict[int, str], nuclei: int) -> bool:
        token = word.tokens[index]
        if not isinstance(token, Seg) or not Inventory.matches(token.phoneme, self.target):
            return False
        when = self.when
        prev_token = word.tokens[index - 1] if index > 0 else None
        next_token = word.tokens[index + 1] if index + 1 < len(word.tokens) else None
        if "element_initial" in when and when["element_initial"] != (not isinstance(prev_token, Seg)):
            return False
        if "element_final" in when and when["element_final"] != (not isinstance(next_token, Seg)):
            return False
        if "word_final" in when and when["word_final"] != (next_token is None):
            return False
        if "before" in when and not self._sequence(word, index + 1, when["before"], +1):
            return False
        if "after" in when and not self._sequence(word, index - 1, when["after"], -1):
            return False
        if "stress" in when:
            actual = stress.get(index, "unstressed")
            wanted = when["stress"]
            ok = actual != "unstressed" if wanted == "stressed" else actual == wanted
            if not ok:
                return False
        if "min_syllables" in when and nuclei < int(when["min_syllables"]):
            return False
        if "proclitic" in when and when["proclitic"] != (word.morphs[token.morph].kind == "proclitic"):
            return False
        return True

    # ------------------------------------------------------------------ application

    def apply(self, word: Word, inventory: Inventory) -> Word:
        stress = assign_stress(word)
        nuclei = sum(1 for p in word.segments() if p.feature("syllabic"))
        hits = [i for i in range(len(word.tokens)) if self._matches(word, i, stress, nuclei)]
        if not hits:
            return word
        tokens = list(word.tokens)
        for index in reversed(hits):
            token = tokens[index]
            if not isinstance(token, Seg):
                continue
            if self.change.get("delete"):
                del tokens[index]
            elif self.change.get("geminate"):
                tokens.insert(index + 1, token)
            elif "phoneme" in self.change:
                tokens[index] = Seg(inventory[self.change["phoneme"]], token.morph)
            elif "features" in self.change:
                try:
                    tokens[index] = Seg(inventory.shift(token.phoneme, self.change["features"]), token.morph)
                except ValueError as exc:
                    raise ValueError(f"law {self.law_id}: {exc}") from exc
            else:
                raise ValueError(f"law {self.law_id} has no usable change: {self.change}")
        return Word(tokens, list(word.morphs))
