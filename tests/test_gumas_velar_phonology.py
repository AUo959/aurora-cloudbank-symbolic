import pytest

from modules.gumas.naming import NameRegistry, RegistryEntry
from modules.gumas.velar_phonology import (
    ATTESTED,
    LEXICON,
    Lineage,
    Stratum,
    derive,
    fit_attested,
    generate_house_names,
    phonotactic_ok,
    shared_roots,
)

# Canonical lineage prefixes: polity_velar_imperium.naming_conventions.lineage_prefixes
CANON_PREFIX = {
    Lineage.NOBLE: "Vel",
    Lineage.MILITARY: "Varn",
    Lineage.SCHOLARLY: "Thess",
    Lineage.REFORMIST: "Rynn",
    Lineage.OUTWORLD: "Ty",
}


@pytest.mark.parametrize("row", fit_attested(), ids=lambda r: r["attested"])
def test_engine_reproduces_attested_canon_names(row):
    assert row["match"], row


def test_register_rule_predicts_attested_informal_aliases():
    # Canon lists "Virex Talvaren" and "Tkaras Prime" as aliases; the engine was
    # not given them as targets for the informal register rule.
    assert derive(("tala", "warena"), Stratum.SCRIBAL).informal == "Talvaren"
    assert derive(("ta", "karasa"), Stratum.SCRIBAL).informal == "Tkaras"


def test_apostrophe_marks_only_a_scribal_elision():
    elder = derive(("wela", "kuna"), Stratum.ELDER)
    scribal = derive(("wela", "kuna"), Stratum.SCRIBAL)
    no_elision = derive(("tu", "rena"), Stratum.SCRIBAL)  # *tu ends in u, nothing elided
    assert "'" not in elder.formal
    assert scribal.formal == "Vel'konn"
    assert "'" not in no_elision.formal


def test_derivation_is_deterministic_and_traced():
    a = derive(("tala", "warena"), "scribal")
    b = derive(("tala", "warena"), "scribal")
    assert a.receipt() == b.receipt()
    assert [step["law"] for step in a.trace] == ["VL1", "VL4", "VL5"]
    assert a.receipt()["proto"] == "*tala~warena"


@pytest.mark.parametrize("lineage", list(Lineage))
def test_generated_names_carry_canonical_lineage_prefix(lineage):
    names = generate_house_names(lineage, seed=4718224, count=6)
    assert len(names) == 6
    for form in names:
        assert form.formal.startswith(CANON_PREFIX[lineage]), form.formal
        assert form.lineage is lineage
        assert phonotactic_ok(form.formal)


def test_generation_is_seed_deterministic():
    first = [f.formal for f in generate_house_names("noble", seed=7, count=5)]
    again = [f.formal for f in generate_house_names("noble", seed=7, count=5)]
    other = [f.formal for f in generate_house_names("noble", seed=8, count=5)]
    assert first == again
    assert first != other


def test_registry_blocks_collision_with_canon_house():
    registry = NameRegistry([RegistryEntry(canonical_name="Velkonn", entity_id="org_house_velkonn")])
    names = [f.formal for f in generate_house_names("noble", seed=4718224, count=13, registry=registry)]
    assert "Vel'konn" not in names
    unchecked = [f.formal for f in generate_house_names("noble", seed=4718224, count=13)]
    assert "Vel'konn" in unchecked


def test_shared_roots_identifies_cognates():
    velkonn = derive(("wela", "kuna"))
    velrynn = derive(("wela", "rina"), Stratum.SCRIBAL)
    tyren = derive(("tu", "rena"))
    assert shared_roots(velkonn, velrynn) == {"wela"}
    assert shared_roots(velkonn, tyren) == set()


def test_attested_specs_reference_known_roots():
    for _, _, spec in ATTESTED:
        assert all(key in LEXICON for key in spec.roots)


def test_unknown_root_rejected():
    with pytest.raises(KeyError):
        derive(("wela", "zzz"))


def test_phonotactics_reject_bad_final_cluster():
    assert phonotactic_ok("Velkonn")
    assert phonotactic_ok("Varn")
    assert not phonotactic_ok("Velosk")
