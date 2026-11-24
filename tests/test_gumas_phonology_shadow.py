"""Shadow mode must observe NameService without changing a single output byte."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from modules.gumas.naming import NameEntityType, NameRegistry, NameRequest, NameService, RegistryEntry
from modules.gumas.phonology_shadow import PhonologyShadow, name_words

REPO_ROOT = Path(__file__).resolve().parents[1]


def _request(entity_id: str, faction: str = "velar_imperium", **kwargs) -> NameRequest:
    return NameRequest(entity_type=NameEntityType.PERSON, entity_id=entity_id, faction_context=faction, **kwargs)


def _registry() -> NameRegistry:
    return NameRegistry([RegistryEntry(canonical_name="Velkonn", entity_id="org_house_velkonn")])


@pytest.mark.parametrize("faction", ["velar_imperium", "galactic_union", "vorran_clans"])
@pytest.mark.parametrize("seed", [1, 42, 4718224])
def test_resolution_and_receipt_identical_with_shadow(faction, seed):
    plain = NameService(_registry()).resolve(_request("char_x", faction, seed_hint=seed))
    shadow = PhonologyShadow()
    watched = NameService(_registry(), shadow=shadow).resolve(_request("char_x", faction, seed_hint=seed))
    assert watched.to_dict() == plain.to_dict()
    assert watched.naming_receipt() == plain.naming_receipt()


def test_candidate_shortlist_identical_with_shadow():
    request = _request("char_y", seed_hint=7, candidate_count=4)
    plain = NameService(_registry()).resolve_candidates(request)
    shadow = PhonologyShadow()
    watched = NameService(_registry(), shadow=shadow).resolve_candidates(request)
    assert [r.to_dict() for r in watched] == [r.to_dict() for r in plain]
    assert len(shadow.observations) == 4


def test_shadow_observes_only_profiled_factions():
    shadow = PhonologyShadow()
    service = NameService(NameRegistry(), shadow=shadow)
    service.resolve(_request("char_union", "galactic_union", seed_hint=3))
    service.resolve(_request("char_velar", seed_hint=3))
    assert [obs.entity_id for obs in shadow.observations] == ["char_velar"]
    assert shadow.observations[0].profile == "velari"


def test_observation_reads_every_name_word_and_proposes_an_alternative():
    shadow = PhonologyShadow()
    resolution = NameService(NameRegistry(), shadow=shadow).resolve(_request("char_z", seed_hint=11))
    obs = shadow.observations[0]
    assert obs.name == resolution.canonical_name
    assert [w["word"] for w in obs.words] == name_words(resolution.canonical_name)
    assert {w["status"] for w in obs.words} <= {"derived", "near", "loan", "unexplained"}
    alternative = obs.engine_alternative
    assert alternative["house"]["formal"].startswith("Vel")  # noble lineage by default
    assert alternative["name"] == f"{alternative['given']['formal']} {alternative['house']['formal']}"


def test_lineage_constraint_steers_the_alternative():
    shadow = PhonologyShadow()
    request = _request("char_r", seed_hint=5, constraints={"lineage": "reformist"})
    NameService(NameRegistry(), shadow=shadow).resolve(request)
    assert shadow.observations[0].engine_alternative["house"]["formal"].startswith("Rynn'")


def test_advisories_are_notes_not_findings():
    shadow = PhonologyShadow()
    request = _request("char_forced", constraints={"candidate": "Zhar'keth of House Daeryth"})
    resolution = NameService(NameRegistry(), shadow=shadow).resolve(request)
    codes = {note["code"] for note in shadow.observations[0].advisories}
    assert "loan_spelling" in codes  # zh is not Velari
    assert resolution.signature["warnings"] == []  # nothing reached the registry gate


def test_name_words_drop_english_framing():
    assert name_words("Sel'or of House Veyr") == ["Sel'or", "Veyr"]
    assert name_words("Tal’Varen") == ["Tal'Varen"]


def test_shadow_errors_are_recorded_not_raised():
    class Broken:
        def analyze(self, word):
            raise RuntimeError("analyzer down")

    shadow = PhonologyShadow()
    shadow._analyzers["velari"] = Broken()
    plain = NameService(NameRegistry()).resolve(_request("char_e", seed_hint=9))
    watched = NameService(NameRegistry(), shadow=shadow).resolve(_request("char_e", seed_hint=9))
    assert watched.to_dict() == plain.to_dict()
    assert shadow.observations[0].error == "RuntimeError: analyzer down"
    assert shadow.report()["errors"] == 1


def test_report_tallies_statuses_and_advisories():
    shadow = PhonologyShadow()
    for seed in range(10):
        NameService(NameRegistry(), shadow=shadow).resolve(_request(f"char_{seed}", seed_hint=seed))
    report = shadow.report()
    assert report["observed"] == 10 and report["errors"] == 0
    assert sum(report["word_status"].values()) == sum(len(o["words"]) for o in report["observations"])


def _mint(*extra: str) -> str:
    cmd = [sys.executable, "scripts/gumas_name_mint.py", "--entity-type", "PERSON", "--entity-id", "char_mint",
           "--faction", "velar_imperium", "--seed", "4718224", "--count", "3", *extra]  # fmt: skip
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}  # the script imports modules.* from the repo root
    return subprocess.run(cmd, cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=True).stdout


def test_mint_script_stdout_unchanged_by_shadow_flag(tmp_path):
    report_path = tmp_path / "shadow.json"
    assert _mint("--phonology-shadow", str(report_path)) == _mint()
    report = json.loads(report_path.read_text())
    assert report["observed"] == 3 and report["errors"] == 0
