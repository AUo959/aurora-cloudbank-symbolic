from modules.gumas.naming import (
    NameEntityType,
    NameRegistry,
    NameRequest,
    NameService,
    RegistryEntry,
    cadence_signature,
    normalize_name,
    phonetic_key,
)


def test_deterministic_resolution():
    request = NameRequest(
        entity_type=NameEntityType.PERSON,
        entity_id="char_test_001",
        faction_context="galactic_union",
        seed_hint=42,
    )
    first = NameService(NameRegistry()).resolve(request)
    second = NameService(NameRegistry()).resolve(request)
    assert first.canonical_name == second.canonical_name
    assert first.signature == second.signature


def test_exact_collision_is_rejected():
    registry = NameRegistry([RegistryEntry("Arian Kelm", "existing")])
    service = NameService(registry)
    request = NameRequest(
        entity_type=NameEntityType.PERSON,
        entity_id="new",
        constraints={"candidate": "Arian Kelm"},
        seed_hint=1,
    )
    try:
        service.resolve(request)
    except RuntimeError:
        pass
    else:
        raise AssertionError("exact collision should exhaust forced candidate")


def test_phonetic_crowding_detected():
    registry = NameRegistry([RegistryEntry("Lyra Voss", "lyra_voss")])
    findings = registry.evaluate("Lira Vos")
    assert any(item["kind"] in {"phonetic", "root"} for item in findings)


def test_receipt_contains_registry_and_signature():
    registry = NameRegistry([RegistryEntry("Tessa Korr", "tessa_korr")])
    result = NameService(registry).resolve(
        NameRequest(
            entity_type=NameEntityType.SHIP,
            entity_id="vessel_test",
            seed_hint=99,
        )
    )
    receipt = result.naming_receipt()
    assert receipt["protocol"] == "GUMAS_NAMING_PROTOCOL_v0.1"
    assert receipt["registry_digest"]
    assert receipt["signature"]["normalized"] == normalize_name(
        result.canonical_name
    )
    assert receipt["signature"]["phonetic_key"] == phonetic_key(
        result.canonical_name
    )
    assert receipt["signature"]["cadence"] == cadence_signature(
        result.canonical_name
    )
