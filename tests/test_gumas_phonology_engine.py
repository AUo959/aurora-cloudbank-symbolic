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
