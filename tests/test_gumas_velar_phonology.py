import pytest

from modules.gumas.naming import NameRegistry, RegistryEntry
from modules.gumas.velar_phonology import (
    ENGINE,
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
    # Canon lists "Virex Talvaren" and "Tkaras Prime" as aliases.
    assert derive(("tala", "warena"), Stratum.SCRIBAL).informal == "Talvaren"
    assert derive(("ta", "karasa"), Stratum.SCRIBAL).informal == "Tkaras"


def test_formation_era_shapes_the_compound():
    # Same roots, three coinage dates, three historically distinct shapes.
    assert derive(("wela", "kuna"), Stratum.ELDER).formal == "Velkonn"
    assert derive(("wela", "kuna"), Stratum.MIDDLE).formal == "Velakynn"
    assert derive(("wela", "kuna"), Stratum.SCRIBAL).formal == "Vel'kynn"


def test_apostrophe_marks_a_post_reform_junction():
    for stratum in (Stratum.ELDER, Stratum.MIDDLE):
        assert "'" not in derive(("tu", "rena"), stratum).formal
    assert derive(("tu", "rena"), Stratum.SCRIBAL).formal == "Ty'ren"


def test_derivation_is_deterministic_and_dated():
    a = derive(("tala", "warena"), "scribal")
    b = derive(("tala", "warena"), "scribal")
    assert a.receipt() == b.receipt()
    laws = [step["law"] for step in a.trace if "law" in step]
    assert laws == ["VL1", "VL5"]
    dates = [step["date"] for step in a.trace]
    assert dates == sorted(dates)
    assert any(step.get("event") == "compounded" for step in a.trace)
    receipt = a.receipt()
    assert receipt["proto"] == "*tala~warena"
    assert receipt["profile"] == "velari"
    assert receipt["profile_digest"] == ENGINE.profile.digest


@pytest.mark.parametrize("lineage", list(Lineage))
def test_generated_names_carry_canonical_lineage_prefix(lineage):
    names = generate_house_names(lineage, seed=4718224, count=6)
    assert len(names) == 6
    for form in names:
        assert form.formal.startswith(CANON_PREFIX[lineage]), form.formal
        assert form.lineage == lineage.value
        assert form.legal
        assert phonotactic_ok(form.formal)


def test_reformist_names_are_scribal_coinages():
    for form in generate_house_names(Lineage.REFORMIST, seed=11, count=8):
        assert form.era == "scribal"
        assert form.formal.startswith("Rynn'")


def test_generation_is_seed_deterministic():
    first = [f.formal for f in generate_house_names("noble", seed=7, count=5)]
    again = [f.formal for f in generate_house_names("noble", seed=7, count=5)]
    other = [f.formal for f in generate_house_names("noble", seed=8, count=5)]
    assert first == again
    assert first != other


def test_registry_blocks_collision_with_canon_house():
    registry = NameRegistry([RegistryEntry(canonical_name="Velkonn", entity_id="org_house_velkonn")])
    checked = generate_house_names("noble", seed=4718224, count=40, stratum="elder", registry=registry)
    unchecked = generate_house_names("noble", seed=4718224, count=40, stratum="elder")
    assert "Velkonn" in [f.formal for f in unchecked]
    assert "Velkonn" not in [f.formal for f in checked]


def test_shared_roots_identifies_cognates():
    velkonn = derive(("wela", "kuna"))
    velrynn = derive(("wela", "rina"), Stratum.SCRIBAL)
    tyren = derive(("tu", "rena"))
    assert shared_roots(velkonn, velrynn) == {"wela"}
    assert shared_roots(velkonn, tyren) == set()


def test_unknown_root_rejected():
    with pytest.raises(KeyError):
        derive(("wela", "zzz"))


def test_phonotactics():
    assert phonotactic_ok("Velkonn")
    assert phonotactic_ok("Varn")
    assert phonotactic_ok("Tal'Varen")
    assert not phonotactic_ok("Velrsk")  # illegal coda cluster
    assert not phonotactic_ok("Velq")  # q is not in the inventory
