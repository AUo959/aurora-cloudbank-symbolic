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
from typing import Any, Callable, Mapping, Sequence

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


# --------------------------------------------------------------------------- condition matching


def _spec_at(word: Word, index: int, spec: Any) -> bool:
    tokens = word.tokens
    if spec == "#":
        return index < 0 or index >= len(tokens)
    if index < 0 or index >= len(tokens):
        return False
    token = tokens[index]
    if spec == "+":
        return isinstance(token, Boundary)
    return isinstance(token, Seg) and Inventory.matches(token.phoneme, spec)


def _sequence(word: Word, start: int, specs: Sequence[Any], step: int) -> bool:
    position = start
    for spec in specs:
        if not _spec_at(word, position, spec):
            return False
        if spec == "#":
            return True
        position += step
    return True


@dataclass(frozen=True)
class _MatchContext:
    word: Word
    index: int
    token: Seg
    stress: Mapping[int, str]
    nuclei: int

    def neighbour(self, offset: int) -> Token | None:
        position = self.index + offset
        if 0 <= position < len(self.word.tokens):
            return self.word.tokens[position]
        return None


def _element_initial(ctx: _MatchContext, value: bool) -> bool:
    return value == (not isinstance(ctx.neighbour(-1), Seg))


def _element_final(ctx: _MatchContext, value: bool) -> bool:
    return value == (not isinstance(ctx.neighbour(+1), Seg))


def _word_final(ctx: _MatchContext, value: bool) -> bool:
    return value == (ctx.neighbour(+1) is None)


def _before(ctx: _MatchContext, specs: Sequence[Any]) -> bool:
    return _sequence(ctx.word, ctx.index + 1, specs, +1)


def _after(ctx: _MatchContext, specs: Sequence[Any]) -> bool:
    return _sequence(ctx.word, ctx.index - 1, specs, -1)


def _stress(ctx: _MatchContext, wanted: str) -> bool:
    actual = ctx.stress.get(ctx.index, "unstressed")
    if wanted == "stressed":
        return actual != "unstressed"
    return actual == wanted


def _min_syllables(ctx: _MatchContext, value: int) -> bool:
    return ctx.nuclei >= int(value)


def _proclitic(ctx: _MatchContext, value: bool) -> bool:
    return value == (ctx.word.morphs[ctx.token.morph].kind == "proclitic")


def _next_segment(ctx: _MatchContext) -> Seg | None:
    """The next segment, looking through morpheme boundaries."""
    for token in ctx.word.tokens[ctx.index + 1 :]:
        if isinstance(token, Seg):
            return token
    return None


def _reduce_triple(ctx: _MatchContext, value: bool) -> bool:
    """The target is the first of a doubled consonant and follows a different consonant (r|nn -> rn)."""
    prev, nxt = ctx.neighbour(-1), _next_segment(ctx)
    doubled = nxt is not None and nxt.phoneme == ctx.token.phoneme
    after_other = isinstance(prev, Seg) and prev.phoneme.feature("consonantal") and prev.phoneme != ctx.token.phoneme
    return value == (doubled and after_other)


CONDITIONS: Mapping[str, Callable[[_MatchContext, Any], bool]] = {
    "element_initial": _element_initial,
    "element_final": _element_final,
    "word_final": _word_final,
    "before": _before,
    "after": _after,
    "stress": _stress,
    "min_syllables": _min_syllables,
    "proclitic": _proclitic,
    "reduce_triple": _reduce_triple,
}


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
        unknown = set(data.get("when", {})) - set(CONDITIONS)
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

    def _matches(self, word: Word, index: int, stress: Mapping[int, str], nuclei: int) -> bool:
        token = word.tokens[index]
        if not isinstance(token, Seg) or not Inventory.matches(token.phoneme, self.target):
            return False
        ctx = _MatchContext(word, index, token, stress, nuclei)
        return all(CONDITIONS[name](ctx, value) for name, value in self.when.items())

    # ------------------------------------------------------------------ application

    def _rewrite(self, token: Seg, inventory: Inventory) -> list[Token]:
        """The tokens that replace one matched segment."""
        change = self.change
        if change.get("delete"):
            return []
        if change.get("geminate"):
            return [token, token]
        if "phoneme" in change:
            return [Seg(inventory[change["phoneme"]], token.morph)]
        if "features" not in change:
            raise ValueError(f"law {self.law_id} has no usable change: {change}")
        try:
            return [Seg(inventory.shift(token.phoneme, change["features"]), token.morph)]
        except ValueError as exc:
            raise ValueError(f"law {self.law_id}: {exc}") from exc

    def apply(self, word: Word, inventory: Inventory) -> Word:
        stress = assign_stress(word)
        nuclei = sum(1 for p in word.segments() if p.feature("syllabic"))
        hits = [i for i in range(len(word.tokens)) if self._matches(word, i, stress, nuclei)]
        if not hits:
            return word
        tokens = list(word.tokens)
        for index in reversed(hits):  # right to left, so earlier indices stay valid
            tokens[index : index + 1] = self._rewrite(tokens[index], inventory)  # type: ignore[arg-type]
        return Word(tokens, list(word.morphs))
