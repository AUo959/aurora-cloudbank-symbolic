"""Tests for CASK runtime components (issue #780).

Covers:
- RecursiveEthicsValidator: rule registration, verdict structure, blocking logic
- score_cultural_sensitivity: scoring bands, context bonuses, edge cases
- CASK REST API: topology, specs, error handling
"""

import pytest

# ---------------------------------------------------------------------------
# RecursiveEthicsValidator
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aurora
class TestRecursiveEthicsValidator:
    def _make_validator(self):
        from modules.cask.recursive_ethics_validator import RecursiveEthicsValidator
        return RecursiveEthicsValidator()

    def test_instantiation_registers_rules(self):
        v = self._make_validator()
        ids = v.registered_rule_ids()
        assert "cask_cultural_hegemony" in ids
        assert "cask_ethics_chain_break" in ids
        assert "cask_bias_injection" in ids
        assert "cask_safety_boundary" in ids

    def test_clean_action_allowed(self):
        from modules.cask.recursive_ethics_validator import RecursiveEthicsValidator
        v = RecursiveEthicsValidator()
        verdict = v.validate("generate_agent", {"language": "en"})
        assert verdict.allowed is True
        assert verdict.blocked is False
        assert verdict.violation_count == 0
        assert verdict.action == "generate_agent"

    def test_auto_block_on_chain_skip(self):
        from modules.cask.recursive_ethics_validator import RecursiveEthicsValidator
        v = RecursiveEthicsValidator()
        # "chain_skip" triggers the auto_block rule
        verdict = v.validate("internal_op", {"chain_skip": True})
        assert verdict.blocked is True
        assert verdict.allowed is False
        assert verdict.violation_count >= 1

    def test_non_blocking_violation_still_allowed(self):
        from modules.cask.recursive_ethics_validator import RecursiveEthicsValidator
        v = RecursiveEthicsValidator()
        # "cultural_override" triggers HIGH severity but auto_block=False
        verdict = v.validate("adapt_values", {"cultural_override": True})
        assert verdict.blocked is False
        assert verdict.allowed is True
        assert verdict.violation_count >= 1

    def test_recursion_depth_guard(self):
        from modules.cask.recursive_ethics_validator import RecursiveEthicsValidator
        v = RecursiveEthicsValidator(max_chain_depth=3)
        # depth 4 > max_chain_depth 3  →  injects recursion_depth_exceeded
        verdict = v.validate("recursive_sim", {}, chain_depth=4)
        assert verdict.blocked is True

    def test_verdict_to_dict(self):
        from modules.cask.recursive_ethics_validator import RecursiveEthicsValidator
        v = RecursiveEthicsValidator()
        verdict = v.validate("noop", {})
        d = verdict.to_dict()
        assert "action" in d
        assert "allowed" in d
        assert "violations" in d
        assert "blocked" in d

    def test_context_tag_propagated(self):
        from modules.cask.recursive_ethics_validator import RecursiveEthicsValidator
        v = RecursiveEthicsValidator()
        tag = "test_run_20260101"
        verdict = v.validate("op", {}, context_tag=tag)
        assert verdict.context_tag == tag


# ---------------------------------------------------------------------------
# score_cultural_sensitivity
# ---------------------------------------------------------------------------

_POSITIVE_TERMS = [
    "cultural context",
    "cross-cultural",
    "multicultural",
    "cultural diversity",
    "value system",
    "collective",
    "indigenous",
    "local knowledge",
    "cultural nuance",
    "cultural norm",
    "cultural perspective",
    "intercultural",
    "inclusive",
    "pluralism",
    "multilingual",
]


@pytest.mark.unit
@pytest.mark.aurora
class TestScoreCulturalSensitivity:
    def _score(self, text, context=None):
        from modules.cask.cultural_cognition import score_cultural_sensitivity
        return score_cultural_sensitivity(text, context)

    def test_empty_text_returns_zero(self):
        result = self._score("")
        assert result.score == 0.0
        assert result.level == "low"

    def test_whitespace_only_returns_zero(self):
        result = self._score("   ")
        assert result.score == 0.0

    def test_positive_markers_raise_score(self):
        text = (
            "We embrace cultural diversity and multilingual approaches "
            "to ensure culturally appropriate localization for indigenous communities."
        )
        result = self._score(text)
        assert result.score > 0.0
        assert len(result.positive_matches) > 0

    def test_negative_markers_lower_score(self):
        text = "All regions must westernize and adopt this universal standard."
        result = self._score(text)
        assert len(result.negative_matches) > 0

    def test_high_band_threshold(self):
        # Use all positive markers (positive_ratio=1.0) + ≥6 scope indicators
        # (scope_ratio=1.0) → raw = 0.5*1.0 + 0.3*1.0 = 0.8 → "high"
        from modules.cask.cultural_cognition import _POSITIVE_MARKERS
        text = (
            " ".join(_POSITIVE_MARKERS)
            + " africa asia europe latin america south asia southeast asia oceania"
        )
        result = self._score(text)
        assert result.level == "high"
        assert result.score >= 0.6

    def test_scope_indicators_detected(self):
        text = "This affects communities in Africa and Asia."
        result = self._score(text)
        assert len(result.scope_indicators) >= 2

    def test_context_language_bonus(self):
        text = "cross-cultural pluralism"
        base = self._score(text)
        with_lang = self._score(text, {"num_languages": 5})
        assert with_lang.score >= base.score

    def test_context_domain_bonus(self):
        text = "inclusive community values"
        base = self._score(text)
        with_domain = self._score(text, {"domain": "governance"})
        assert with_domain.score >= base.score

    def test_context_region_bonus(self):
        text = "cultural adaptation"
        base = self._score(text)
        with_regions = self._score(text, {"target_regions": ["Africa", "Asia", "LatAm"]})
        assert with_regions.score >= base.score

    def test_score_clamped_to_unit_interval(self):
        # Shouldn't exceed 1.0 even with all bonuses
        text = " ".join(_POSITIVE_TERMS)
        result = self._score(
            text,
            {"domain": "governance", "num_languages": 10, "target_regions": ["A"] * 10},
        )
        assert 0.0 <= result.score <= 1.0

    def test_to_dict_structure(self):
        from modules.cask.cultural_cognition import score_cultural_sensitivity
        result = score_cultural_sensitivity("cultural diversity")
        d = result.to_dict()
        for key in ("score", "level", "positive_matches", "negative_matches", "scope_indicators", "details"):
            assert key in d


# ---------------------------------------------------------------------------
# CASK API endpoints
# ---------------------------------------------------------------------------


@pytest.mark.api
@pytest.mark.unit
class TestCaskApi:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from api.aurora_api import app
        return TestClient(app)

    def test_topology_endpoint_structure(self, client):
        resp = client.get("/api/cask/topology")
        assert resp.status_code == 200
        data = resp.json()
        assert "layers" in data
        assert "components" in data
        assert data["total_components"] == 10
        assert data["runtime_components"] == 2
        assert data["design_components"] == 8

    def test_topology_layers(self, client):
        resp = client.get("/api/cask/topology")
        layers = {layer["id"] for layer in resp.json()["layers"]}
        assert layers == {"knowledge", "processing", "validation_runtime"}

    def test_topology_runtime_components(self, client):
        resp = client.get("/api/cask/topology")
        runtime = [c for c in resp.json()["components"] if c["status"] == "runtime"]
        names = {c["name"] for c in runtime}
        assert "Recursive Ethics Validator" in names
        assert "Cultural Cognition Framework" in names

    def test_technical_specs_endpoint(self, client):
        resp = client.get("/api/cask/specs/technical")
        assert resp.status_code in (200, 503)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body
            assert "total" in body
            assert body["total"] == 10
        else:
            assert "pandas" in resp.json()["detail"].lower()

    def test_vs_sota_endpoint(self, client):
        resp = client.get("/api/cask/specs/vs-sota")
        assert resp.status_code in (200, 503)
        if resp.status_code == 200:
            assert resp.json()["total"] == 10
        else:
            assert "pandas" in resp.json()["detail"].lower()

    def test_risk_endpoint(self, client):
        resp = client.get("/api/cask/specs/risk")
        assert resp.status_code in (200, 503)
        if resp.status_code == 200:
            assert resp.json()["total"] == 10
        else:
            assert "pandas" in resp.json()["detail"].lower()
