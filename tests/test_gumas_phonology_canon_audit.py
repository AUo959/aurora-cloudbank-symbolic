"""The canon audit script, run on a small synthetic canon tree."""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "gumas_phonology_canon_audit.py"
_spec = importlib.util.spec_from_file_location("gumas_phonology_canon_audit", SCRIPT)
canon_audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(canon_audit)


def _write(root: Path, rel: str, record: dict) -> None:
    path = root / "canon" / "L2" / "entities" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record), encoding="utf-8")


@pytest.fixture
def canon(tmp_path):
    _write(tmp_path, "species/species_velari.json", {
        "entity_id": "species_velari", "entity_kind": "species", "name": "Velari", "certainty": "CANON",
        "distribution": "Velari-heritage world Vel-Surak sits in the Union.",
    })  # fmt: skip
    _write(tmp_path, "organizations/org_house_velkonn.json", {
        "entity_id": "org_house_velkonn", "entity_kind": "organization", "name": "House Velkonn",
        "certainty": "CANON", "faction_bindings": ["velar_imperium"], "aliases": ["house_velkonn"],
    })  # fmt: skip
    _write(tmp_path, "characters/char_syrr_velkonn.json", {
        "entity_id": "char_syrr_velkonn", "entity_kind": "character", "name": "Dr. Syrr Velkonn",
        "certainty": "CANON", "organization_ids": ["org_house_velkonn"],
    })  # fmt: skip
    _write(tmp_path, "locations/loc_vel_surak.json", {
        "entity_id": "loc_vel_surak", "entity_kind": "location", "name": "Vel-Surak", "certainty": "CANON",
        "faction_bindings": ["galactic_union"],
    })  # fmt: skip
    _write(tmp_path, "characters/char_mara_velthis.json", {
        "entity_id": "char_mara_velthis", "entity_kind": "character", "name": "Captain Mara Velthis",
        "certainty": "CANON", "faction_bindings": ["galactic_union"],
    })  # fmt: skip
    _write(tmp_path, "characters/char_draft.json", {
        "entity_id": "char_draft", "entity_kind": "character", "name": "Talyx Draft", "certainty": "STAGING",
    })  # fmt: skip
    return tmp_path


def test_population_and_link_basis(canon):
    report = canon_audit.audit(canon, english=frozenset())
    assert report["records"] == {"velar": 4, "control": 1}  # the STAGING record is excluded
    assert report["link_basis"] == {"binding": 3, "named-velari": 1, "control": 1}
    assert report["velar_orgs"] == ["org_house_velkonn"]


def test_words_are_classified_and_framing_set_aside(canon):
    report = canon_audit.audit(canon, english=frozenset())
    by_word = {r["word"]: r for r in report["words"]}
    assert by_word["Velkonn"]["status"] == "derived" and by_word["Velkonn"]["tier"] == "velar"
    assert by_word["Syrr"]["status"] == "near"
    assert by_word["Mara"]["tier"] == "control"
    assert "Captain" not in by_word and "Dr" not in by_word
    assert "record-id:house_velkonn" in report["set_aside"]
    assert "Vel" in by_word and "Surak" in by_word  # the hyphen splits Vel-Surak


def test_distance_stats_cover_native_words_only(canon):
    report = canon_audit.audit(canon, english=frozenset())
    velar = report["nearest_distance"]["velar"]
    native = [r for r in report["words"] if r["tier"] == "velar" and r["status"] != "loan"]
    assert velar["native_words"] == len(native)
    assert velar["distance_0"] == sum(r["status"] == "derived" for r in native)


def test_set_aside_reasons():
    english = frozenset({"world", "house"})
    assert canon_audit.set_aside_reason("IV", english) == "roman"
    assert canon_audit.set_aside_reason("Khalrix-3", english) == "number"
    assert canon_audit.set_aside_reason("Warlords", english) == "title"
    assert canon_audit.set_aside_reason("Worlds", english) == "english"
    assert canon_audit.set_aside_reason("Velkonn", english) is None
    assert canon_audit.set_aside_reason("Tal'Varen", english) is None


def test_name_words_split_dashes_and_typographic_apostrophes():
    assert canon_audit.name_words("T’karas Prime") == ["T'karas", "Prime"]
    assert canon_audit.name_words("Union–Imperium Border") == ["Union", "Imperium", "Border"]


# ---------------------------------------------------------------- unreadable input is never silent


def test_clean_tree_is_complete(canon):
    report = canon_audit.audit(canon, english=frozenset())
    assert report["complete"] is True
    assert report["unreadable"] == []


def test_malformed_record_is_reported_not_skipped(canon):
    bad = canon / "canon" / "L2" / "entities" / "characters" / "char_broken.json"
    bad.write_text('{"entity_id": "char_broken", "name": "Velkonn", ', encoding="utf-8")
    report = canon_audit.audit(canon, english=frozenset())
    assert report["complete"] is False
    assert [u["path"] for u in report["unreadable"]] == ["characters/char_broken.json"]
    assert report["unreadable"][0]["error"].startswith("JSONDecodeError")
    assert report["records"] == {"velar": 4, "control": 1}  # readable records are still counted


def test_valid_non_record_json_is_out_of_scope_not_unreadable(canon):
    (canon / "canon" / "L2" / "entities" / "index.json").write_text("[1, 2, 3]", encoding="utf-8")
    report = canon_audit.audit(canon, english=frozenset())
    assert report["complete"] is True


def _run_main(monkeypatch, canon, out):
    monkeypatch.setattr("sys.argv", ["audit", "--canon-root", str(canon), "--out", str(out)])
    monkeypatch.setattr(canon_audit, "english_words", lambda: frozenset())
    return canon_audit.main()


def test_main_exits_nonzero_on_incomplete_audit(canon, tmp_path, monkeypatch, capsys):
    out = tmp_path / "report.json"
    assert _run_main(monkeypatch, canon, out) == 0
    (canon / "canon" / "L2" / "entities" / "characters" / "char_broken.json").write_text("{", encoding="utf-8")
    assert _run_main(monkeypatch, canon, out) == 1
    assert json.loads(out.read_text())["complete"] is False  # the report is still written
    assert "audit incomplete: 1 unreadable canon file(s): characters/char_broken.json" in capsys.readouterr().err
