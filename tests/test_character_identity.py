from __future__ import annotations

import copy
import importlib
import json
import sys
from pathlib import Path

import jsonschema
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_DIR = PROJECT_ROOT / "simulation"
if str(SIMULATION_DIR) not in sys.path:
    sys.path.insert(0, str(SIMULATION_DIR))

from character_identity import (  # noqa: E402
    CharacterIdentityError,
    CharacterIdentityRegistry,
    QuarantinedIdentityReference,
)
from character_loader import CharacterLoader  # noqa: E402


REGISTRY_PATH = PROJECT_ROOT / "config" / "l1_character_identity_registry.json"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "character_identity_registry.schema.json"


def _registry_payload() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _write_registry(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "identity-registry.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _roster_section(name: str, identifier: str) -> str:
    return f"""
### 1. **{name}**
- **Role:** Code/Narrative Systems Engineer
- **Title:** Principal Engineer, Narrative Logic Interface
- **Division:** Simulation & Cognitive Systems
- **Clearance:** L3_RESEARCH
- **ID:** {identifier}
- **Contact:** t.qin@orion.station
- **Symbolic Tag:** `s.tag::code.narrative.tobias_qin`
- **Base Speed:** 0.75
- **Specialization Multiplier:** 1.40x
- **Collaboration Bonus:** +15%
"""


@pytest.mark.unit
def test_identity_registry_matches_json_schema():
    registry = _registry_payload()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(registry)


@pytest.mark.unit
def test_tobias_historical_and_current_ids_resolve_to_one_stable_person():
    registry = CharacterIdentityRegistry()

    by_entity = registry.require("ORION.ENTITY.0039")
    assert registry.require("ENG_010") is by_entity
    assert registry.require("SIM_002") is by_entity
    assert registry.require("Tobias Qin") is by_entity
    assert by_entity.current_identifier == "SIM_002"
    assert by_entity.historical_identifiers == ("ENG_010",)
    assert [item.clearance for item in by_entity.identifiers] == [
        "L3_RESEARCH",
        "L3_TECHNICAL",
    ]
    assert [item.division for item in by_entity.identifiers] == [
        "Operations Staff",
        "Simulation & Cognitive Systems",
    ]
    assert by_entity.identifiers[0].superseded_by == "SIM_002"


@pytest.mark.unit
def test_character_loader_resolves_historical_id_without_losing_source_id(
    tmp_path: Path,
):
    roster = tmp_path / "historical-roster.md"
    roster.write_text(
        "# Historical roster\n\n**Version:** 1.1\n"
        + _roster_section("Tobias Qin", "ENG_010"),
        encoding="utf-8",
    )

    loader = CharacterLoader(roster_path=roster)
    profile = loader.get_character("ENG_010")

    assert profile is not None
    assert profile is loader.get_character("SIM_002")
    assert profile is loader.get_character("ORION.ENTITY.0039")
    assert profile.character_id == "SIM_002"
    assert profile.source_character_id == "ENG_010"
    assert profile.stable_entity_key == "ORION.ENTITY.0039"
    assert profile.historical_identifiers == ["ENG_010"]


@pytest.mark.unit
def test_loader_collapses_duplicate_person_before_simulation_consumers(
    tmp_path: Path,
):
    roster = tmp_path / "duplicate-migration-roster.md"
    historical = _roster_section("Tobias Qin Historical", "ENG_010")
    current = _roster_section("Tobias Qin", "SIM_002").replace("### 1.", "### 2.")
    roster.write_text(
        "# Duplicate migration roster\n\n**Version:** 1.4\n" + historical + current,
        encoding="utf-8",
    )

    loader = CharacterLoader(roster_path=roster)

    assert len(loader.get_all_characters()) == 1
    profile = loader.get_all_characters()[0]
    assert profile.name == "Tobias Qin"
    assert profile.source_character_id == "SIM_002"
    assert profile.stable_entity_key == "ORION.ENTITY.0039"
    assert loader.validate_roster() == []


@pytest.mark.unit
def test_karl_sorensen_reference_is_quarantined_not_aliased_or_instantiated(
    tmp_path: Path,
):
    registry = CharacterIdentityRegistry()
    with pytest.raises(QuarantinedIdentityReference) as exc_info:
        registry.resolve("  PROF.   KARL SORENSEN ")
    assert exc_info.value.possible_referent == "ORION.ENTITY.0010"

    roster = tmp_path / "conflicted-roster.md"
    roster.write_text(
        "# Conflicted roster\n\n**Version:** 1.4\n"
        + _roster_section("Prof. Karl Sorensen", "UNKNOWN_KARL"),
        encoding="utf-8",
    )
    loader = CharacterLoader(roster_path=roster)
    assert loader.get_all_characters() == []
    with pytest.raises(QuarantinedIdentityReference):
        loader.get_character("Prof. Karl Sorensen")

    roster.write_text(
        "# Conflicted roster\n\n**Version:** 1.4\n"
        + _roster_section("Prof. Karl Sorensen", "ETH_003"),
        encoding="utf-8",
    )
    loader = CharacterLoader(roster_path=roster)
    assert loader.get_all_characters() == []


@pytest.mark.unit
def test_identity_registry_rejects_assignment_id_shared_by_two_people(
    tmp_path: Path,
):
    payload = _registry_payload()
    second = copy.deepcopy(payload["entities"][1])
    second["identifiers"][0]["identifier"] = "SIM_002"
    second["current_identifier"] = "SIM_002"
    payload["entities"][1] = second

    with pytest.raises(
        CharacterIdentityError,
        match="assignment identifier maps to multiple people",
    ):
        CharacterIdentityRegistry(_write_registry(tmp_path, payload))


@pytest.mark.unit
def test_identity_registry_revision_must_match_staff_provenance(tmp_path: Path):
    payload = _registry_payload()
    payload["authority_boundary"]["authority_revision"] = "0" * 40

    with pytest.raises(
        CharacterIdentityError,
        match="does not match staff provenance",
    ):
        CharacterIdentityRegistry(_write_registry(tmp_path, payload))


@pytest.mark.unit
def test_identity_registry_revision_must_be_lowercase_hex(tmp_path: Path):
    payload = _registry_payload()
    payload["authority_boundary"]["authority_revision"] = "g" * 40

    with pytest.raises(CharacterIdentityError, match="must be a git SHA"):
        CharacterIdentityRegistry(_write_registry(tmp_path, payload))


@pytest.mark.unit
def test_character_loader_supports_package_import():
    module = importlib.import_module("simulation.character_loader")

    assert module.CharacterLoader is not None


@pytest.mark.unit
def test_current_roster_loader_exposes_tobias_identity_history():
    loader = CharacterLoader()
    profile = loader.get_character("ENG_010")

    assert profile is not None
    assert profile.name == "Tobias Qin"
    assert profile.character_id == "SIM_002"
    assert profile.source_character_id == "SIM_002"
    assert profile.stable_entity_key == "ORION.ENTITY.0039"
