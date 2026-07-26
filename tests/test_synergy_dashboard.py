"""
Tests for Component Synergy Dashboard API

DLP: synergy_dashboard_tests
"""

import pytest
from fastapi.testclient import TestClient

# The signals _runtime_health() is allowed to attribute a score to. Kept in
# sync with the health_source docstring on ComponentStatus; anything outside
# this set means a score appeared with no named source behind it.
_RUNTIME_HEALTH_SOURCES = {
    "runtime_import",
    "runtime_routes",
    "runtime_telemetry",
    "static",
}


@pytest.fixture
def test_client():
    """Create test client for API testing"""
    from api.aurora_api import app
    return TestClient(app)


class TestSynergyDashboardAPI:
    """Test suite for synergy dashboard endpoints"""
    
    def test_health_endpoint(self, test_client):
        """Test dashboard health check endpoint"""
        response = test_client.get("/api/synergy/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "synergy_dashboard_api"
        assert "timestamp" in data
        assert "version" in data
    
    def test_get_components(self, test_client):
        """Static topology, enriched with runtime-derived health."""
        response = test_client.get("/api/synergy/components")
        assert response.status_code == 200

        components = response.json()
        assert isinstance(components, list)
        assert len(components) > 0
        
        # Verify component structure
        component = components[0]
        assert "component_id" in component
        assert "name" in component
        assert "category" in component
        assert "description" in component
        assert "endpoints" in component
        assert "status" in component
        assert "telemetry_available" in component
        assert "telemetry_source" in component

        # Health is derived per request from a real signal, and the response
        # says which one. Both fields are always present together.
        assert "health_score" in component
        assert "health_source" in component
        assert component["status"] in {"active", "degraded", "unavailable", "unknown"}
        assert component["health_source"] in _RUNTIME_HEALTH_SOURCES

    def test_get_components_with_filter(self, test_client):
        """status_filter narrows the list to entries with that runtime status."""
        # Filter on a status the registry actually reports right now rather
        # than a hard-coded one — a filter value no component matches returns
        # an empty list, which would make this test pass without exercising
        # anything.
        all_components = test_client.get("/api/synergy/components").json()
        target = all_components[0]["status"]

        response = test_client.get(f"/api/synergy/components?status_filter={target}")
        assert response.status_code == 200

        components = response.json()
        assert isinstance(components, list)
        assert len(components) > 0, f"no component reported status {target!r}"
        for component in components:
            assert component["status"] == target

    def test_components_do_not_report_placeholder_live_health(self, test_client):
        """No component field is filled with a value nothing measured.

        health_score is permitted — it is derived from an import probe, route
        presence, or telemetry, and health_source names which. The fields below
        have no signal behind them at all, so the route must leave them unset
        rather than emit a plausible-looking number.
        """
        response = test_client.get("/api/synergy/components")
        assert response.status_code == 200

        for component in response.json():
            assert component["health_source"] in _RUNTIME_HEALTH_SOURCES
            # telemetry_available claims telemetry specifically, not health
            # generally: it must agree with where the score actually came from.
            assert component["telemetry_available"] == (
                component["health_source"] == "runtime_telemetry"
            )
            assert component["telemetry_source"] == (
                "r2_agent_telemetry"
                if component["health_source"] == "runtime_telemetry"
                else "static_registry"
            )
            assert "last_heartbeat" not in component
            assert "uptime_seconds" not in component
            assert "resource_usage" not in component
    
    def test_get_topology(self, test_client):
        """Test retrieving component topology"""
        response = test_client.get("/api/synergy/topology")
        assert response.status_code == 200
        
        topology = response.json()
        assert "nodes" in topology
        assert "edges" in topology
        assert "clusters" in topology
        assert "timestamp" in topology
        
        # Verify nodes structure
        assert isinstance(topology["nodes"], list)
        assert len(topology["nodes"]) > 0
        
        node = topology["nodes"][0]
        assert "id" in node
        assert "label" in node
        assert "category" in node
        assert "description" in node
        assert "health" in node
        
        # Verify edges structure
        assert isinstance(topology["edges"], list)
        if len(topology["edges"]) > 0:
            edge = topology["edges"][0]
            assert "source" in edge
            assert "target" in edge
            assert "type" in edge
            assert "description" in edge
        
        # Verify clusters structure
        assert isinstance(topology["clusters"], list)
        if len(topology["clusters"]) > 0:
            cluster = topology["clusters"][0]
            assert "id" in cluster
            assert "name" in cluster
            assert "members" in cluster
    
    def test_get_interactions(self, test_client):
        """Test retrieving component interactions"""
        response = test_client.get("/api/synergy/interactions")
        assert response.status_code == 200
        
        interactions = response.json()
        assert isinstance(interactions, list)
        assert len(interactions) > 0
        
        # Verify interaction structure
        interaction = interactions[0]
        assert "source_id" in interaction
        assert "target_id" in interaction
        assert "interaction_type" in interaction
        assert "frequency" in interaction
        assert "last_interaction" in interaction
        assert "latency_ms" in interaction
        assert "success_rate" in interaction
        
        # Verify metrics ranges
        assert interaction["frequency"] > 0
        assert interaction["latency_ms"] > 0
        assert 0 <= interaction["success_rate"] <= 1
    
    def test_get_interactions_with_filter(self, test_client):
        """Test retrieving interactions filtered by component"""
        response = test_client.get("/api/synergy/interactions?component_id=aumemmanager")
        assert response.status_code == 200
        
        interactions = response.json()
        assert isinstance(interactions, list)
        
        # All interactions should involve the specified component
        for interaction in interactions:
            assert (interaction["source_id"] == "aumemmanager" or 
                   interaction["target_id"] == "aumemmanager")
    
    def test_get_synergy_scores(self, test_client):
        """Test retrieving synergy scores"""
        response = test_client.get("/api/synergy/synergy-scores")
        assert response.status_code == 200
        
        scores = response.json()
        assert isinstance(scores, list)
        assert len(scores) > 0
        
        # Verify synergy score structure
        score = scores[0]
        assert "component_pair" in score
        assert "score" in score
        assert "trend" in score
        assert "opportunities" in score
        assert "integration_level" in score
        
        # Verify component pair
        assert isinstance(score["component_pair"], list)
        assert len(score["component_pair"]) == 2
        
        # Verify score range
        assert 0 <= score["score"] <= 100
        
        # Verify trend values
        assert score["trend"] in ["increasing", "stable", "decreasing"]
        
        # Verify integration level
        assert score["integration_level"] in ["none", "partial", "full"]
        
        # Verify opportunities
        assert isinstance(score["opportunities"], list)
    
    def test_get_metrics(self, test_client):
        """Test retrieving dashboard metrics"""
        response = test_client.get("/api/synergy/metrics")
        assert response.status_code == 200
        
        metrics = response.json()
        assert "total_components" in metrics
        assert "active_components" in metrics
        assert "total_interactions" in metrics
        assert "average_synergy_score" in metrics
        assert "system_health" in metrics
        assert "timestamp" in metrics
        
        # Verify metrics values
        assert metrics["total_components"] > 0
        assert metrics["active_components"] >= 0
        assert metrics["active_components"] <= metrics["total_components"]
        assert metrics["total_interactions"] >= 0
        assert 0 <= metrics["average_synergy_score"] <= 100
        assert 0 <= metrics["system_health"] <= 100
    
    def test_component_registry_consistency(self, test_client):
        """Test consistency between components and topology"""
        # Get components
        comp_response = test_client.get("/api/synergy/components")
        components = comp_response.json()
        
        # Get topology
        topo_response = test_client.get("/api/synergy/topology")
        topology = topo_response.json()
        
        # Number of components should match number of nodes
        assert len(components) == len(topology["nodes"])
        
        # Component IDs should match node IDs
        comp_ids = {c["component_id"] for c in components}
        node_ids = {n["id"] for n in topology["nodes"]}
        assert comp_ids == node_ids
    
    def test_interaction_topology_consistency(self, test_client):
        """Test consistency between interactions and topology edges"""
        # Get interactions
        inter_response = test_client.get("/api/synergy/interactions")
        interactions = inter_response.json()
        
        # Get topology
        topo_response = test_client.get("/api/synergy/topology")
        topology = topo_response.json()
        
        # Number of interactions should match number of edges
        assert len(interactions) == len(topology["edges"])
        
        # Source/target pairs should match
        inter_pairs = {(i["source_id"], i["target_id"]) for i in interactions}
        edge_pairs = {(e["source"], e["target"]) for e in topology["edges"]}
        assert inter_pairs == edge_pairs
    
    def test_synergy_score_calculation(self, test_client):
        """Test synergy score calculation logic"""
        response = test_client.get("/api/synergy/synergy-scores")
        scores = response.json()
        
        for score in scores:
            # High scores should have full integration
            if score["score"] >= 80:
                assert score["integration_level"] == "full"
            
            # Low scores should have opportunities
            if score["score"] < 80:
                assert len(score["opportunities"]) > 0


class TestDLPTracking:
    """Test DLP tracking in synergy dashboard"""
    
    def test_dlp_context_tags(self, test_client):
        """Verify DLP tracking is applied to all endpoints"""
        endpoints = [
            "/api/synergy/components",
            "/api/synergy/topology",
            "/api/synergy/interactions",
            "/api/synergy/synergy-scores",
            "/api/synergy/metrics",
        ]
        
        for endpoint in endpoints:
            response = test_client.get(endpoint)
            assert response.status_code == 200
            # DLP tracking happens internally, verify no errors occur


class TestErrorHandling:
    """Test error handling in synergy dashboard"""
    
    def test_invalid_status_filter(self, test_client):
        """Test handling of invalid status filter"""
        # Should return all components if filter doesn't match any
        response = test_client.get("/api/synergy/components?status_filter=invalid")
        assert response.status_code == 200
        components = response.json()
        assert isinstance(components, list)
    
    def test_invalid_component_filter(self, test_client):
        """Test handling of invalid component filter in interactions"""
        response = test_client.get("/api/synergy/interactions?component_id=nonexistent")
        assert response.status_code == 200
        interactions = response.json()
        # Should return empty list for nonexistent component
        assert isinstance(interactions, list)
        assert len(interactions) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
