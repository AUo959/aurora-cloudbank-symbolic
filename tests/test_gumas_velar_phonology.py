import pytest

from modules.gumas.naming import NameRegistry, RegistryEntry
from modules.gumas.velar_phonology import (
    ENGINE,
    analyze,
    blind_recovery,
    Dialect,
    Lineage,
    Stratum,
    derive,
    fit_attested,
    generate_given_names,
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


@pytest.mark.parametrize("row", fit_attested(include_fixtures=True), ids=lambda r: f"{r['tier']}:{r['attested']}")
def test_engine_reproduces_corpus_spelling_and_legality(row):
    # match requires the exact spelling, the informal form when given, and phonotactic legality
    assert row["legal"], row
    assert row["match"], row


def test_canon_corpus_rows_are_cited_and_fixtures_are_not_canon():
    canon = fit_attested()
    assert {r["tier"] for r in canon} == {"canon"}
    for row in canon:
        assert row["evidence"] in {"entity", "canon_text"}, row
        assert row["source"]["path"].startswith("canon/L2/"), row
    fixtures = [r for r in fit_attested(include_fixtures=True) if r["tier"] == "fixture"]
    assert {r["attested"] for r in fixtures} == {"Varn", "Thessari"}
    assert all(r["evidence"] is None for r in fixtures)


def test_attested_tkaras_is_phonotactically_legal():
    assert derive(("ta", "karasa"), Stratum.SCRIBAL).legal
    assert phonotactic_ok("T'karas")


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


# ---------------------------------------------------------------- phase 2


def test_ablaut_grades_share_one_radical():
    varn = derive(("warna", "ketha"))
    varen = derive(("tala", "warena"), Stratum.SCRIBAL)
    assert ENGINE.profile.lexicon["warna"].grade == "zero"
    assert ENGINE.profile.lexicon["warena"].grade == "full"
    assert ENGINE.profile.lexicon["warena"].gloss == "guard (full-grade)"
    assert shared_roots(varn, varen) == {"WAR"}  # Varn- and -Varen are kin, not crowding
    assert varen.receipt()["radicals"] == ["tala", "WAR"]


def test_cluster_reduction_only_inside_fused_compounds():
    assert derive(("warna", "nima"), Stratum.ELDER).formal == "Varnim"
    assert derive(("warna", "nima"), Stratum.SCRIBAL).formal == "Varn'nim"
    assert derive(("rina", "nima"), Stratum.SCRIBAL).formal == "Rynn'nim"  # canonical Rynn- survives


def test_hiatus_elision_keeps_middle_era_suffixes_clean():
    assert derive(("dura", "isa"), Stratum.MIDDLE).formal == "Dyris"
    assert derive(("karasa", "ara"), Stratum.MIDDLE).formal == "Karasar"


@pytest.mark.parametrize(
    "roots, stratum, common, imperial, union",
    [
        (("wela", "kuna"), Stratum.SCRIBAL, "Vel'kynn", "Vel'kinn", "Vel'kynn"),
        (("tessa", "ari"), Stratum.ELDER, "Thessari", "Thessari", "Thesari"),
        (("warna", "mora"), Stratum.ELDER, "Varnmor", "Varnmor", "Varnmur"),
    ],
)
def test_dialects_diverge_after_the_split(roots, stratum, common, imperial, union):
    assert derive(roots, stratum).formal == common
    assert derive(roots, stratum, Dialect.IMPERIAL).formal == imperial
    assert derive(roots, stratum, Dialect.UNION).formal == union


def test_dialect_tagged_canon_rows_survive_their_branch():
    tagged = [r for r in fit_attested() if r["dialect"] != "common"]
    assert {(r["attested"], r["dialect"]) for r in tagged} == {
        ("Velkonn", "imperial"),
        ("Tyr", "imperial"),
        ("Tal'Varen", "imperial"),
        ("Rynn", "union"),
        ("Talyx", "imperial"),
        ("Virex", "imperial"),
        ("Jasrek", "imperial"),
        ("Syrr", "imperial"),
        ("Sira", "imperial"),
        ("Nyros", "imperial"),
        ("Thalen", "union"),
        ("Vel-Surak", "union"),
        ("Daeryth", "union"),
    }
    assert all(r["match"] for r in tagged)


def test_lineages_generate_in_their_own_dialect():
    assert {f.dialect for f in generate_house_names(Lineage.REFORMIST, seed=3, count=4)} == {"union"}
    assert {f.dialect for f in generate_house_names(Lineage.NOBLE, seed=3, count=4)} == {"imperial"}
    assert {f.dialect for f in generate_house_names(Lineage.OUTWORLD, seed=3, count=4)} == {"common"}
    forced = generate_house_names(Lineage.NOBLE, seed=3, count=4, dialect=Dialect.COMMON)
    assert {f.dialect for f in forced} == {"common"}


def test_given_names_are_root_plus_personal_suffix():
    names = generate_given_names(seed=4718224, count=12)
    assert len(names) == 12
    assert len({n.informal for n in names}) == 12
    for name in names:
        assert name.legal
        assert name.lineage is None
        assert ENGINE.profile.lexicon[name.roots[1]].kind == "suffix"
        assert name.roots[1] in ENGINE.profile.personal_suffixes
    again = [n.formal for n in generate_given_names(seed=4718224, count=12)]
    assert again == [n.formal for n in names]


def test_given_names_screened_by_registry():
    first = generate_given_names(seed=4718224, count=1)[0].formal
    registry = NameRegistry([RegistryEntry(canonical_name=first, entity_id="char_existing")])
    assert first not in [n.formal for n in generate_given_names(seed=4718224, count=12, registry=registry)]


def test_no_canon_velari_name_is_left_unexplained():
    """The seven canon given names once listed as unexplained now derive and are cited in the corpus."""
    assert ENGINE.profile.unexplained == ()
    corpus = {r["attested"]: r for r in fit_attested()}
    for name in ("Sira", "Syrr", "Talyx", "Virex", "Thalen", "Jasrek", "Jaxx"):
        assert corpus[name]["match"], name
        assert corpus[name]["evidence"] == "entity"


# ---------------------------------------------------------------- phase 3


def test_blind_recovery_finds_every_recorded_etymology():
    rows = {r["name"]: r for r in blind_recovery()}
    assert len(rows) == 22
    assert all(r["recovered"] for r in rows.values())
    # Genuine rival etymologies: different roots spelling the same name.
    rivals = {name: r["rival_roots"] for name, r in rows.items() if r["rival_roots"]}
    assert rivals == {"Tyren": [("tura", "ena")], "Tyr": [("tu", "ra")], "Syrr": [("syra", "ra")]}


def test_junction_marks_date_the_coinage_in_analysis():
    for name in ("Tal'Varen", "T'karas", "Vel'Rynn"):
        eras = {d.era for d in analyze(name).exact}
        assert eras and eras <= {"scribal", "late"}, name  # an apostrophe means coined after the reform
    assert {d.era for d in analyze("T\u2019karas").exact} == {"scribal"}
    assert "elder" in {d.era for d in analyze("Talvaren").exact}  # solid: could be an old fused coinage
    for spelling in ("Vel-Surak", "Vel Surak"):
        assert {(d.era, d.dialect) for d in analyze(spelling).exact} == {("late", "union")}, spelling


@pytest.mark.parametrize(
    "name, status",
    [
        ("Velkonn", "derived"),
        ("Talyx", "derived"),
        ("Jaxx", "derived"),
        ("Thalen", "derived"),
        ("Syrr", "derived"),
        ("Velkon", "near"),
        ("Zhar'keth", "loan"),
        ("Kaelor", "unexplained"),
    ],
)
def test_analysis_status(name, status):
    assert analyze(name).status == status


def test_near_miss_points_at_the_nearest_form():
    distance, nearest = analyze("Velkon").nearest[0]
    assert distance == 1 and nearest.formal == "Velkonn" and nearest.roots == ("wela", "kuna")


def test_loans_are_adapted_not_claimed():
    zhar = analyze("Zhar'keth")
    assert zhar.foreign == ["z"] and zhar.adapted == "sharketh" and not zhar.exact
    assert analyze("Talyx").foreign == []  # x and j are native Velari now


@pytest.mark.parametrize(
    "roots, era, dialect, formal",
    [
        (("iaksa",), "elder", None, "Jaxx"),  # j-hardening, ks > x, x-gemination in one syllable
        (("iasreka",), "elder", None, "Jasrek"),  # j-hardening
        (("tala", "yksa"), "elder", None, "Talyx"),  # ks > x, no gemination in two syllables
        (("wira", "eksa"), "elder", None, "Virex"),
        (("syrda",), "elder", None, "Syrr"),  # rd-assimilation
        (("si", "ra"), "scribal", None, "Sira"),  # late suffix escapes apocope
        (("si", "ra"), "elder", None, "Sir"),  # the same suffix coined early loses its -a
        (("nurusa",), "elder", None, "Nyros"),
        (("daerytha",), "elder", "union", "Daeryth"),  # Union keeps final th (canon)
    ],
)
def test_canon_gap_mechanisms(roots, era, dialect, formal):
    assert ENGINE.derive(roots, era, dialect=dialect).formal == formal


def test_union_hyphenates_post_split_compounds_and_raises_o():
    union = ENGINE.derive(("wela", "soraka"), "late", dialect="union")
    assert (union.formal, union.informal) == ("Vel-Surak", "Vel Surak")
    imperial = ENGINE.derive(("wela", "soraka"), "late", dialect="imperial")
    assert (imperial.formal, imperial.informal) == ("Vel'sorak", "Velsorak")  # apostrophe, no o-raising


def test_sporadic_change_is_recorded_and_opt_in_for_derive():
    plain = derive(("warna", "karasa"))
    struck = ENGINE.derive(("warna", "karasa"), "elder", sporadic=True)
    assert plain.formal == "Varnkaras" and not plain.sporadic
    assert struck.formal == "Varnkalas" and struck.sporadic == ["SP1"]
    assert struck.trace[-1]["sporadic"] == "SP1"


def test_generation_sporadic_is_seeded_and_can_be_disabled():
    # Which candidates are struck depends on the profile digest, so look across seeds rather than at one.
    runs = {seed: generate_house_names(Lineage.REFORMIST, seed=seed, count=13) for seed in range(10)}
    assert any(n.sporadic for names in runs.values() for n in names)
    for seed, names in runs.items():
        again = generate_house_names(Lineage.REFORMIST, seed=seed, count=13)
        assert [n.formal for n in names] == [n.formal for n in again]
        assert all(n.formal.startswith("Rynn'") for n in names)  # dissimilation never touches the first r
        plain = generate_house_names(Lineage.REFORMIST, seed=seed, count=13, sporadic=False)
        assert not any(n.sporadic for n in plain)


def test_weighted_generation_ranks_by_sound():
    names = generate_house_names(Lineage.NOBLE, seed=4718224, count=6, weighted=True)
    scores = [n.euphony for n in names]
    assert scores == sorted(scores, reverse=True)
    assert len(names) == 6 and all(n.legal for n in names)


def test_sound_model_prefers_velari_shapes():
    model = ENGINE.sound_model
    assert model.score("Tal'Varen") > model.score("Xqzzt")
    assert model.score("Velkonn") > model.score("Grubstok")
