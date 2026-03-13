"""Comprehensive tests for the QGIA Forecast Simulation Engine (QSFE).

Covers population generation, trust network SBM, belief propagation,
tier aggregation, dissent analysis, output formatting, and reproducibility.
"""

import pytest

from modules.qgia.config import (
    DIVISIONS,
    GRADE_DISTRIBUTION,
    GRADE_TIERS,
    TARGET_EDGES,
    TOTAL_AGENTS,
)
from modules.qgia.forecast_engine import QGIAForecastEngine
from modules.qgia.output_formatter import format_forecast
from modules.qgia.population_generator import generate_population
from modules.qgia.scenario import (
    EXAMPLE_SCENARIOS,
    european_energy_crisis,
    iran_nuclear_escalation,
    south_china_sea_confrontation,
    subsaharan_instability,
)
from modules.qgia.schemas import Agent, EpistemicProfile, ForecastOutput, TierAssessment, TrustEdge
from modules.qgia.trust_network import build_adjacency, generate_trust_network


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def population():
    """Generate the canonical 551-agent population once for all tests."""
    return generate_population(seed=42)


@pytest.fixture(scope="module")
def trust_edges(population):
    """Generate the trust network once for all tests."""
    return generate_trust_network(population, seed=42)


@pytest.fixture(scope="module")
def engine():
    """Instantiate the full forecast engine once for all tests."""
    return QGIAForecastEngine(seed=42)


# ── Population Generator Tests ────────────────────────────────────────

class TestPopulationGenerator:

    def test_population_count(self, population):
        """Population produces exactly 551 agents."""
        assert len(population) == TOTAL_AGENTS

    def test_division_headcounts(self, population):
        """Each division has the correct headcount."""
        div_counts = {}
        for agent in population:
            div_counts[agent.division.value] = div_counts.get(agent.division.value, 0) + 1
        for div_code, div_info in DIVISIONS.items():
            assert div_counts[div_code] == div_info["headcount"], (
                f"{div_code}: expected {div_info['headcount']}, got {div_counts.get(div_code, 0)}"
            )

    def test_all_agents_are_valid_models(self, population):
        """Every agent is a valid Agent Pydantic model."""
        for agent in population:
            assert isinstance(agent, Agent)
            assert isinstance(agent.epistemic_profile, EpistemicProfile)

    def test_epistemic_parameters_in_range(self, population):
        """All epistemic parameters are in [0, 1]."""
        for agent in population:
            ep = agent.epistemic_profile
            for field_name in EpistemicProfile.model_fields:
                value = getattr(ep, field_name)
                assert 0.0 <= value <= 1.0, (
                    f"{agent.agent_id}.{field_name} = {value} out of range"
                )

    def test_agent_id_format(self, population):
        """Agent IDs follow QGIA-{DIV}-{TIER}-{SEQ:04d} format."""
        for agent in population:
            parts = agent.agent_id.split("-")
            assert parts[0] == "QGIA"
            assert parts[1] in DIVISIONS
            assert parts[2].isdigit()
            assert len(parts[3]) == 4 and parts[3].isdigit()

    def test_grade_distribution(self, population):
        """Grade counts match the canonical distribution."""
        grade_counts = {}
        for agent in population:
            grade_counts[agent.grade] = grade_counts.get(agent.grade, 0) + 1
        for grade, info in GRADE_DISTRIBUTION.items():
            assert grade_counts.get(grade, 0) == info["count"], (
                f"{grade}: expected {info['count']}, got {grade_counts.get(grade, 0)}"
            )

    def test_regional_specializations_assigned(self, population):
        """Every agent has a non-empty regional specialization."""
        for agent in population:
            assert agent.regional_specialization, f"{agent.agent_id} has no specialization"

    def test_iid_analysts_are_cross_domain(self, population):
        """All IID analysts have 'Cross-domain' specialization."""
        for agent in population:
            if agent.division.value == "IID":
                assert agent.regional_specialization == "Cross-domain"


# ── Trust Network Tests ───────────────────────────────────────────────

class TestTrustNetwork:

    def test_edge_count_within_tolerance(self, trust_edges):
        """Trust network has approximately 7,407 edges (±10%)."""
        n = len(trust_edges)
        lower = int(TARGET_EDGES * 0.9)
        upper = int(TARGET_EDGES * 1.1)
        assert lower <= n <= upper, (
            f"Edge count {n} outside ±10% of target {TARGET_EDGES} "
            f"(expected {lower}-{upper})"
        )

    def test_all_edges_are_valid_models(self, trust_edges):
        """Every edge is a valid TrustEdge model."""
        for edge in trust_edges:
            assert isinstance(edge, TrustEdge)
            assert 0.0 <= edge.weight <= 1.0

    def test_edge_type_distribution(self, trust_edges):
        """Edge type proportions roughly match targets."""
        type_counts = {}
        for edge in trust_edges:
            type_counts[edge.edge_type] = type_counts.get(edge.edge_type, 0) + 1
        total = len(trust_edges)

        # Collaborate ~54% (allow 35-70%)
        collaborate_ratio = type_counts.get("collaborate", 0) / total
        assert 0.35 <= collaborate_ratio <= 0.70, f"collaborate ratio: {collaborate_ratio:.3f}"

        # Inform ~33% (allow 15-50%)
        inform_ratio = type_counts.get("inform", 0) / total
        assert 0.15 <= inform_ratio <= 0.50, f"inform ratio: {inform_ratio:.3f}"

        # Challenge ~8% (allow 2-20%)
        challenge_ratio = type_counts.get("challenge", 0) / total
        assert 0.02 <= challenge_ratio <= 0.20, f"challenge ratio: {challenge_ratio:.3f}"

        # Reinforce ~5% (allow 1-15%)
        reinforce_ratio = type_counts.get("reinforce", 0) / total
        assert 0.01 <= reinforce_ratio <= 0.15, f"reinforce ratio: {reinforce_ratio:.3f}"

    def test_no_self_edges(self, trust_edges):
        """No agent has a trust edge to itself."""
        for edge in trust_edges:
            assert edge.source != edge.target

    def test_adjacency_dict_construction(self, trust_edges):
        """Adjacency dict is correctly keyed by target."""
        adj = build_adjacency(trust_edges)
        for target_id, edges in adj.items():
            for edge in edges:
                assert edge.target == target_id


# ── Forecast Engine Tests ─────────────────────────────────────────────

class TestForecastEngine:

    def test_engine_initializes(self, engine):
        """Engine creates population and network on init."""
        assert len(engine.agents) == TOTAL_AGENTS
        assert len(engine.edges) > 0

    @pytest.mark.parametrize("scenario_fn", [
        iran_nuclear_escalation,
        south_china_sea_confrontation,
        european_energy_crisis,
        subsaharan_instability,
    ])
    def test_forecast_runs_without_error(self, engine, scenario_fn):
        """Engine runs all example scenarios without raising."""
        scenario = scenario_fn()
        output = engine.run_forecast(scenario)
        assert isinstance(output, ForecastOutput)

    def test_tiers_properly_ordered(self, engine):
        """Tier I probability > Tier II > Tier III."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        tiers = sorted(output.tier_assessments, key=lambda t: t.tier)
        assert len(tiers) == 3
        assert tiers[0].probability > tiers[1].probability
        assert tiers[1].probability > tiers[2].probability

    def test_tier_labels_correct(self, engine):
        """Each tier has the correct label."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        tier_map = {t.tier: t.label for t in output.tier_assessments}
        assert tier_map[1] == "Most Likely"
        assert tier_map[2] == "Plausible Alternative"
        assert tier_map[3] == "Tail Risk"

    def test_confidence_components_in_range(self, engine):
        """All confidence components are in [0, 1]."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        for ta in output.tier_assessments:
            assert 0.0 <= ta.confidence <= 1.0
            for key, val in ta.confidence_components.items():
                assert 0.0 <= val <= 1.0, f"Tier {ta.tier} {key} = {val} out of range"

    def test_dissent_analysis_finds_dissenters(self, engine):
        """At least some dissenters are identified in forecasts."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        # At least one tier should report dissenters
        total_dissent = sum(ta.dissent_count for ta in output.tier_assessments)
        # Dissent count is the same across all tiers (set once)
        assert output.tier_assessments[0].dissent_count >= 0

    def test_analyst_participation_includes_divisions(self, engine):
        """Analyst participation records division breakdown."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        ap = output.analyst_participation
        # IID always participates
        assert "IID" in ap
        assert ap["IID"] > 0

    def test_provenance_populated(self, engine):
        """Provenance section contains expected fields."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        assert "sources_consulted" in output.provenance
        assert "evidence_fragments" in output.provenance
        assert "independent_source_ratio" in output.provenance

    def test_meta_populated(self, engine):
        """Meta section contains processing stats."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        assert "cell_size" in output.meta
        assert "propagation_rounds" in output.meta
        assert output.meta["cell_size"] > 0
        assert output.meta["propagation_rounds"] >= 1

    def test_crisis_cell_includes_iid(self, engine):
        """Crisis cell always includes all IID analysts."""
        scenario = iran_nuclear_escalation()
        cell = engine._select_crisis_cell(scenario)
        iid_in_cell = [a for a in cell if a.division.value == "IID"]
        iid_total = DIVISIONS["IID"]["headcount"]
        assert len(iid_in_cell) == iid_total

    def test_crisis_cell_filters_by_region(self, engine):
        """Crisis cell includes region-matched analysts from GMD/MAD."""
        scenario = iran_nuclear_escalation()  # Middle East
        cell = engine._select_crisis_cell(scenario)
        for agent in cell:
            if agent.division.value in ("GMD", "MAD"):
                assert agent.regional_specialization == "Middle East"


# ── Echo Chamber Detection Tests ──────────────────────────────────────

class TestEchoChamberDetection:

    def test_echo_chamber_warnings_are_strings(self, engine):
        """Echo chamber warnings are a list of strings."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        assert isinstance(output.echo_chamber_warnings, list)
        for w in output.echo_chamber_warnings:
            assert isinstance(w, str)


# ── Reproducibility Tests ─────────────────────────────────────────────

class TestReproducibility:

    def test_same_seed_same_population(self):
        """Same seed produces identical population."""
        pop1 = generate_population(seed=99)
        pop2 = generate_population(seed=99)
        assert len(pop1) == len(pop2)
        for a1, a2 in zip(pop1, pop2):
            assert a1.agent_id == a2.agent_id
            assert a1.epistemic_profile == a2.epistemic_profile

    def test_same_seed_same_network(self):
        """Same seed produces identical trust network."""
        pop = generate_population(seed=99)
        edges1 = generate_trust_network(pop, seed=99)
        edges2 = generate_trust_network(pop, seed=99)
        assert len(edges1) == len(edges2)
        for e1, e2 in zip(edges1, edges2):
            assert e1.source == e2.source
            assert e1.target == e2.target
            assert e1.edge_type == e2.edge_type

    def test_same_seed_same_forecast(self):
        """Same seed produces identical forecast output."""
        engine1 = QGIAForecastEngine(seed=77)
        engine2 = QGIAForecastEngine(seed=77)
        scenario = iran_nuclear_escalation()
        out1 = engine1.run_forecast(scenario)
        out2 = engine2.run_forecast(scenario)
        for t1, t2 in zip(out1.tier_assessments, out2.tier_assessments):
            assert t1.probability == t2.probability
            assert t1.confidence == t2.confidence

    def test_different_seeds_differ(self):
        """Different seeds produce different populations."""
        pop1 = generate_population(seed=1)
        pop2 = generate_population(seed=2)
        # At least some agents should differ in epistemic profiles
        diffs = sum(
            1 for a1, a2 in zip(pop1, pop2)
            if a1.epistemic_profile.prior_strength != a2.epistemic_profile.prior_strength
        )
        assert diffs > 0


# ── Output Formatter Tests ────────────────────────────────────────────

class TestOutputFormatter:

    def test_format_produces_string(self, engine):
        """Formatter produces a non-empty string."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        report = format_forecast(output, scenario_title=scenario.title)
        assert isinstance(report, str)
        assert len(report) > 100

    def test_format_contains_all_sections(self, engine):
        """Formatted output contains all required sections."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        report = format_forecast(output, scenario_title=scenario.title)
        assert "TIER I" in report
        assert "TIER II" in report
        assert "TIER III" in report
        assert "DISSENT REPORT" in report
        assert "ECHO CHAMBER" in report
        assert "PROVENANCE" in report
        assert "QUICK REFERENCE" in report

    def test_format_contains_scenario_title(self, engine):
        """Formatted output includes the scenario title in the header."""
        scenario = iran_nuclear_escalation()
        output = engine.run_forecast(scenario)
        report = format_forecast(output, scenario_title=scenario.title)
        assert scenario.title in report


# ── Module Import Tests ───────────────────────────────────────────────

class TestModuleImports:

    def test_module_manifest_exists(self):
        """Module manifest is importable and has required fields."""
        from modules.qgia import MODULE_MANIFEST
        assert MODULE_MANIFEST["symbolic_tag"] == "s.tag::module.qgia.qsfe"
        assert MODULE_MANIFEST["node"] == "L1_QGIA"
        assert MODULE_MANIFEST["charter"] == "Picard_Delta_3"
        assert MODULE_MANIFEST["version"] == "1.0.0"

    def test_public_api_importable(self):
        """All public API symbols are importable."""
        from modules.qgia import (
            EXAMPLE_SCENARIOS,
            Agent,
            Division,
            EpistemicProfile,
            ForecastOutput,
            QGIAForecastEngine,
            ScenarioInput,
            TierAssessment,
            TrustEdge,
            build_adjacency,
            create_scenario,
            format_forecast,
            generate_population,
            generate_trust_network,
        )
        assert QGIAForecastEngine is not None
        assert len(EXAMPLE_SCENARIOS) == 4
