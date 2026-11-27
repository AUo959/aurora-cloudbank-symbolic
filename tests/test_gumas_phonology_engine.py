"""Layer tests for the language-neutral phonology engine (modules.gumas.phonology)."""

import json
import shutil

import pytest

from modules.gumas.phonology import Engine, Profile
from modules.gumas.phonology.engine import PROFILES_DIR
from modules.gumas.phonology.rules import Morph, SoundLaw, Word, assign_stress
from modules.gumas.phonology.segments import Inventory
from modules.gumas.phonology.syllables import check, syllabify

VELARI = Engine("velari")
INV = VELARI.profile.inventory
TACTICS = VELARI.profile.tactics


# ---------------------------------------------------------------- segments


def test_parse_prefers_digraph_phonemes():
    assert [p.symbol for p in INV.parse("thessa")] == ["th", "e", "s", "s", "a"]


def test_feature_shifts_resolve_to_inventory_phonemes():
    assert INV.shift(INV["u"], {"back": False}).symbol == "y"
    assert INV.shift(INV["u"], {"high": False}).symbol == "o"
    assert INV.shift(INV["i"], {"round": True}).symbol == "y"
    assert INV.shift(INV["t"], {"continuant": True}).symbol == "th"
    assert INV.shift(INV["w"], {"consonantal": True, "sonorant": False}).symbol == "v"
    with pytest.raises(ValueError):
        INV.shift(INV["k"], {"nasal": True})  # no velar nasal in Velari


def test_inventory_rejects_unknown_features_and_duplicate_bundles():
    with pytest.raises(ValueError):
        Inventory({"x": {"features": {"glottal": True}}})
    with pytest.raises(ValueError):
        Inventory({"x": {"features": {"syllabic": True}}, "z": {"features": {"syllabic": True}}})


# ---------------------------------------------------------------- syllables


def test_syllabify_maximizes_legal_onsets():
    sylls = syllabify(INV.parse("thessketh"), TACTICS)
    assert [s.text() for s in sylls] == ["thes", "sketh"]
    sylls = syllabify(INV.parse("tydren"), TACTICS)
    assert [s.text() for s in sylls] == ["ty", "dren"]


def test_phonotactic_check_flags_illegal_codas():
    assert check(INV.parse("velkonn"), TACTICS) == []
    assert check(INV.parse("velskt"), TACTICS)


# ---------------------------------------------------------------- stress & laws


def _word(*parts):
    pieces = []
    for key, kind in parts:
        pieces.append(Word.from_morph(Morph(key, kind), INV.parse(VELARI.profile.lexicon[key].proto)))
    return Word.join(pieces, formed_at=50)


def test_stress_primary_secondary_and_unstressed_clitics():
    word = _word(("ta", "proclitic"), ("karasa", "root"), ("kuna", "root"))
    stresses = [s for _, s in sorted(assign_stress(word).items())]
    # ta (proclitic) | ka ra sa | ku na
    assert stresses == ["unstressed", "primary", "unstressed", "unstressed", "secondary", "unstressed"]


def test_law_conditions_and_simultaneous_application():
    law = SoundLaw.from_dict({
        "id": "T1", "name": "test apocope", "date": 1,
        "target": {"phoneme": "a"}, "change": {"delete": True},
        "when": {"word_final": True, "stress": "unstressed", "min_syllables": 2},
    })  # fmt: skip
    assert law.apply(_word(("karasa", "root")), INV).phonemic() == "karas"
    assert law.apply(_word(("ta", "root")), INV).phonemic() == "ta"  # one syllable: untouched


def test_law_rejects_unknown_condition():
    with pytest.raises(ValueError):
        SoundLaw.from_dict({"id": "T2", "name": "bad", "date": 1, "target": {}, "change": {"delete": True},
                            "when": {"nearby": True}})  # fmt: skip


# ---------------------------------------------------------------- chronology


def test_compounds_evolve_separately_before_formation():
    middle = VELARI.derive(("wela", "kuna"), "middle")
    events = [step.get("event") or step["law"] for step in middle.trace]
    assert events.index("compounded") > events.index("VL3")  # fronting hit kuna while it stood alone
    assert middle.phonemic == "vela+kynn"


def test_explicit_formation_date_overrides_era():
    late = VELARI.derive(("wela", "kuna"), formed_at=850)
    assert late.formal == "Vel'kynn"
    assert late.formed_at == 850


def test_unknown_era_rejected():
    with pytest.raises(KeyError):
        VELARI.derive(("wela", "kuna"), "future")


# ---------------------------------------------------------------- profiles


def test_profile_digest_changes_with_data(tmp_path):
    copy = tmp_path / "velari"
    shutil.copytree(PROFILES_DIR / "velari", copy)
    original = Profile.load(copy).digest
    lexicon = json.loads((copy / "lexicon.json").read_text())
    lexicon["roots"]["sela"]["gloss"] = "starlight"
    (copy / "lexicon.json").write_text(json.dumps(lexicon))
    assert Profile.load(copy).digest != original


def test_profile_rejects_ambiguous_chronology(tmp_path):
    copy = tmp_path / "velari"
    shutil.copytree(PROFILES_DIR / "velari", copy)
    chronology = json.loads((copy / "chronology.json").read_text())
    chronology["laws"][1]["date"] = chronology["laws"][0]["date"]
    (copy / "chronology.json").write_text(json.dumps(chronology))
    with pytest.raises(ValueError):
        Profile.load(copy)


def test_profile_rejects_roots_outside_inventory(tmp_path):
    copy = tmp_path / "velari"
    shutil.copytree(PROFILES_DIR / "velari", copy)
    lexicon = json.loads((copy / "lexicon.json").read_text())
    lexicon["roots"]["qova"] = {"proto": "qova", "gloss": "x", "gloss_status": "draft"}
    (copy / "lexicon.json").write_text(json.dumps(lexicon))
    with pytest.raises(ValueError):
        Profile.load(copy)


# ---------------------------------------------------------------- phase 2: lexicon, dialects, conditions


def _mutated_profile(tmp_path, part, mutate):
    copy = tmp_path / "velari"
    shutil.copytree(PROFILES_DIR / "velari", copy)
    data = json.loads((copy / f"{part}.json").read_text())
    mutate(data)
    (copy / f"{part}.json").write_text(json.dumps(data))
    return copy


@pytest.mark.parametrize(
    "mutate",
    [
        lambda lx: lx["roots"]["warna"]["derive"].update(radical="NOPE"),
        lambda lx: lx["roots"]["warna"]["derive"].update(grade="lengthened"),
        lambda lx: lx["generative_content_roots"].append("missing_root"),
        lambda lx: lx["personal_suffixes"].append("kuna"),
    ],
    ids=["unknown-radical", "unknown-grade", "undefined-reference", "suffix-not-suffix"],
)
def test_lexicon_rejects_broken_references(tmp_path, mutate):
    with pytest.raises(ValueError):
        Profile.load(_mutated_profile(tmp_path, "lexicon", mutate))


def test_dialect_laws_must_postdate_the_split(tmp_path):
    def early(ch):
        ch["dialects"]["branches"]["union"]["laws"][0]["date"] = 990

    with pytest.raises(ValueError):
        Profile.load(_mutated_profile(tmp_path, "chronology", early))


def test_common_is_reserved_and_unknown_dialects_rejected(tmp_path):
    def reserve(ch):
        ch["dialects"]["branches"]["common"] = {"laws": []}

    with pytest.raises(ValueError):
        Profile.load(_mutated_profile(tmp_path, "chronology", reserve))
    with pytest.raises(KeyError):
        VELARI.derive(("wela", "kuna"), dialect="nythran")


def test_laws_for_appends_branch_laws_in_date_order():
    imperial = VELARI.laws_for("imperial")
    assert imperial[: len(VELARI.profile.laws)] == VELARI.profile.laws
    assert [law.law_id for law in imperial[len(VELARI.profile.laws) :]] == ["VI1"]
    assert VELARI.laws_for(None) == VELARI.laws_for("common") == VELARI.profile.laws


def test_reduce_triple_condition():
    law = SoundLaw.from_dict({
        "id": "T3", "name": "test reduction", "date": 1,
        "target": {"consonantal": True}, "change": {"delete": True}, "when": {"reduce_triple": True},
    })  # fmt: skip
    pieces = [Word.from_morph(Morph(k, "root"), INV.parse(p)) for k, p in (("a", "varn"), ("b", "nim"))]
    assert law.apply(Word.join(pieces, formed_at=50), INV).phonemic() == "var+nim"
    pieces = [Word.from_morph(Morph(k, "root"), INV.parse(p)) for k, p in (("a", "rynn"), ("b", "nim"))]
    assert law.apply(Word.join(pieces, formed_at=50), INV).phonemic() == "rynn+nim"  # nn after a vowel stays


# ---------------------------------------------------------------- phase 3: sporadic, loans, analysis helpers


def test_preceded_anywhere_by_condition():
    law = SoundLaw.from_dict({
        "id": "T4", "name": "test dissimilation", "date": 1,
        "target": {"phoneme": "r"}, "change": {"features": {"lateral": True}},
        "when": {"preceded_anywhere_by": {"phoneme": "r"}},
    })  # fmt: skip
    assert law.apply(_word(("karasa", "root")), INV).phonemic() == "karasa"  # one r: untouched
    assert law.apply(_word(("warna", "root"), ("karasa", "root")), INV).phonemic() == "warna+kalasa"


def test_loan_map_drops_note_keys():
    assert "_note" not in VELARI.profile.loan_map
    assert VELARI.profile.loan_map["z"] == "s"
    assert (
        "x" not in VELARI.profile.loan_map and "j" not in VELARI.profile.loan_map
    )  # native since the canon-gaps phase


def test_zero_sporadic_rate_never_strikes(tmp_path):
    def off(ch):
        ch["sporadic"]["rate"] = 0.0

    engine = Engine(Profile.load(_mutated_profile(tmp_path, "chronology", off)))
    names = engine.generate("reformist", seed=4718224, count=8)
    assert not any(n.sporadic for n in names)


def test_edit_distance():
    from modules.gumas.phonology.analysis import _distance

    assert _distance("syrr", "syr") == 1
    assert _distance("thalen", "talen") == 1
    assert _distance("", "abc") == 3


# ---------------------------------------------------------------- canon gaps: new conditions and orthography


def test_max_syllables_condition():
    law = SoundLaw.from_dict({
        "id": "T5", "name": "test", "date": 1, "target": {"phoneme": "a"}, "change": {"delete": True},
        "when": {"word_final": True, "max_syllables": 1},
    })  # fmt: skip
    assert law.apply(_word(("ta", "root")), INV).phonemic() == "t"
    assert law.apply(_word(("tala", "root")), INV).phonemic() == "tala"


def test_new_phonemes_come_from_feature_shifts():
    assert INV.shift(INV["i"], {"syllabic": False, "consonantal": True}).symbol == "j"
    assert INV.shift(INV["k"], {"strident": True}).symbol == "x"
    assert INV.shift(INV["d"], {"sonorant": True, "continuant": True}).symbol == "r"
    assert INV.shift(INV["o"], {"high": True}).symbol == "u"


def test_junction_marks_load_in_date_order_with_dialects():
    marks = VELARI.profile.junction_marks
    assert [(m.name, m.date, m.mark, m.dialect) for m in marks] == [
        ("scribal_reform", 800, "'", None),
        ("union_hyphenation", 1000, "-", "union"),
    ]
