"""Salvage sensor tests: maturity scoring, classification, survey metrics."""

from src.sensors.external.salvage import (
    SalvageCandidate,
    SalvageSensor,
    classify,
    detect_beacon,
    score_maturity,
)


def _rec(path, value=20, signals=None, lines=200, on_manifest=False, ext=".py"):
    return {
        "path": path,
        "value_score": value,
        "signals": signals or [],
        "line_count": lines,
        "size_bytes": lines * 40,
        "sha256": "abc",
        "on_official_manifest": on_manifest,
        "extension": ext,
    }


# -- maturity ---------------------------------------------------------------

def test_mature_artifact_scores_high():
    c = SalvageCandidate.from_record(_rec(
        "intake/engine_v2_5_core.py",
        signals=["test_or_fixture", "code_logic", "contract_or_schema"]))
    assert c.maturity >= 0.6


def test_fragment_scores_low():
    c = SalvageCandidate.from_record(_rec(
        "notes.txt", value=2, signals=[], lines=5, ext=".txt"))
    assert c.maturity < 0.3
    assert c.classification == "debris"


# -- beacons -----------------------------------------------------------------

def test_anchor_marker_is_beacon():
    c = SalvageCandidate.from_record(_rec(
        "draft_logic/EOS_SEED_ORION_relay_notes.md", lines=30, ext=".md"))
    assert detect_beacon(c)
    assert c.classification == "beacon"


def test_governance_signal_with_version_is_beacon():
    c = SalvageCandidate.from_record(_rec(
        "intake/protocol_pack_v0_4.json",
        signals=["governance_or_control_plane"], ext=".json"))
    assert c.is_beacon


# -- classification -----------------------------------------------------------

def test_high_value_mature_unregistered_is_cargo():
    c = SalvageCandidate.from_record(_rec(
        "projects/forge_module_v1_2.py", value=25,
        signals=["test_or_fixture", "code_logic"]))
    assert c.classification == "cargo"


def test_registered_artifact_is_not_salvage():
    c = SalvageCandidate.from_record(_rec(
        "src/core/engine_v1_0.py", value=25,
        signals=["test_or_fixture", "code_logic"], on_manifest=True))
    assert c.classification == "registered"


def test_some_maturity_low_value_is_derelict():
    c = SalvageCandidate.from_record(_rec(
        "old/sketch_v0_1.py", value=5, signals=["code_logic"]))
    assert c.classification == "derelict"


# -- survey metrics ---------------------------------------------------------------

def test_sensor_survey_and_alerts():
    s = SalvageSensor()
    s.ingest_records([
        _rec("projects/forge_v1_2.py", value=25,
             signals=["test_or_fixture", "code_logic"]),         # cargo
        _rec("draft/THREADCORE_capsule_v0_3.json",
             signals=["governance_or_control_plane"], ext=".json"),  # beacon
        _rec("src/registered.py", value=25,
             signals=["code_logic"], on_manifest=True),          # registered
        _rec("scrap.txt", value=1, signals=[], lines=3, ext=".txt"),  # debris
    ])
    s.ingest_repo_divergence({
        "aurora-cloudbank-symbolic-main": {"uncommitted": 47, "unpushed_commits": 0},
    })
    r = s.read()
    assert r.values["salvage_contacts"] == 3.0
    assert r.values["high_value_cargo"] == 1.0
    assert r.values["beacon_signals"] == 1.0
    assert r.values["registry_match_rate"] == 0.25
    assert r.values["uncommitted_in_repos"] == 47.0
    assert any("cargo" in a for a in r.alerts)
    assert any("beacon" in a for a in r.alerts)
    assert any("registry match" in a for a in r.alerts)
    top = r.metadata["top_cargo"]
    assert top and top[0]["path"] == "projects/forge_v1_2.py"


def test_sensor_never_promotes():
    """One-way observation: candidates stay pending_review; the sensor has
    no promotion surface."""
    s = SalvageSensor()
    s.ingest_records([_rec("x_v1_0.py", signals=["code_logic"])])
    assert all(c.promotion_status == "pending_review" for c in s.candidates)
    assert not hasattr(s, "promote")
    assert not hasattr(s, "recover")


def test_empty_survey_is_clean():
    r = SalvageSensor().read()
    assert r.alerts == []
    assert r.values["registry_match_rate"] == 1.0
