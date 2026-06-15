import unittest

from modules.quantum_forge import (
    ForgeRouteDecision,
    ForgeScope,
    ForgeTaskRequest,
    QuantumAgentForgePolicy,
    RetentionCriteria,
    RetentionOutcome,
    StandingCoverage,
)


def _task(risk_level=0.2):
    return ForgeTaskRequest(
        task_id="task-001",
        task_class="novel_analysis",
        required_capabilities=["domain_research", "synthesis"],
        domain_tags=["L2", "forge"],
        risk_level=risk_level,
    )


class TestQuantumForgeLifecyclePolicy(unittest.TestCase):
    def test_standing_department_coverage_prevents_spawn(self):
        policy = QuantumAgentForgePolicy()
        request = _task()
        coverage = StandingCoverage(department="GUMAS_RESEARCH")

        self.assertIs(policy.evaluate_route(request, coverage), ForgeRouteDecision.ROUTE_TO_DEPARTMENT)
        authorization = policy.authorize_spawn(request, coverage)
        self.assertFalse(authorization.authorized)
        self.assertIs(authorization.route_decision, ForgeRouteDecision.ROUTE_TO_DEPARTMENT)

    def test_prior_retained_spec_prevents_new_spawn(self):
        policy = QuantumAgentForgePolicy()
        request = _task()
        coverage = StandingCoverage(prior_spec_id="spec-existing")

        self.assertIs(policy.evaluate_route(request, coverage), ForgeRouteDecision.INSTANTIATE_FROM_SPEC)
        authorization = policy.authorize_spawn(request, coverage)
        self.assertFalse(authorization.authorized)

    def test_direct_aurora_competency_prevents_spawn(self):
        policy = QuantumAgentForgePolicy()
        request = _task()
        coverage = StandingCoverage(direct_competency=True, direct_handler="aurora_core")

        self.assertIs(policy.evaluate_route(request, coverage), ForgeRouteDecision.HANDLE_DIRECTLY)
        authorization = policy.authorize_spawn(request, coverage)
        self.assertFalse(authorization.authorized)

    def test_no_existing_coverage_routes_to_quantum_agent_spawn(self):
        policy = QuantumAgentForgePolicy()
        request = _task()

        self.assertIs(policy.evaluate_route(request, StandingCoverage()), ForgeRouteDecision.SPAWN_QUANTUM_AGENT)
        authorization = policy.authorize_spawn(request, StandingCoverage())
        self.assertTrue(authorization.authorized)
        self.assertEqual(["domain_research", "synthesis"], authorization.allowed_capabilities)

    def test_high_risk_spawn_requires_pilot_acknowledgment(self):
        policy = QuantumAgentForgePolicy(high_risk_threshold=0.7)
        request = _task(risk_level=0.9)

        denied = policy.authorize_spawn(request, StandingCoverage(), pilot_acknowledged=False)
        self.assertFalse(denied.authorized)
        self.assertEqual(["domain_research", "synthesis"], denied.denied_capabilities)

        allowed = policy.authorize_spawn(request, StandingCoverage(), pilot_acknowledged=True)
        self.assertTrue(allowed.authorized)
        self.assertTrue(allowed.pilot_acknowledged)

    def test_lifecycle_record_is_bounded_temporary_and_transparent(self):
        policy = QuantumAgentForgePolicy()
        request = _task()
        authorization = policy.authorize_spawn(request, StandingCoverage())

        record = policy.record_spawn(
            request,
            authorization,
            scope=ForgeScope.BOUNDED_MULTI_STEP,
            forge_id="forge-test-001",
        )

        self.assertEqual("forge-test-001", record.forge_id)
        self.assertEqual(["domain_research", "synthesis"], record.capabilities)
        self.assertIs(record.scope, ForgeScope.BOUNDED_MULTI_STEP)
        self.assertTrue(record.temporary)
        self.assertTrue(record.active)
        self.assertTrue(record.pilot_informed)
        self.assertEqual("spawn_recorded", record.execution_log[0]["event"])

    def test_capability_expansion_without_aurora_authorization_is_denied(self):
        policy = QuantumAgentForgePolicy()
        request = _task()
        record = policy.record_spawn(request, policy.authorize_spawn(request), forge_id="forge-test-002")

        expansion = policy.request_capability_expansion(
            record.forge_id,
            ["external_tooling"],
            aurora_authorized=False,
        )

        self.assertFalse(expansion.authorized)
        self.assertEqual(["external_tooling"], expansion.denied_capabilities)
        self.assertEqual(["domain_research", "synthesis"], record.capabilities)

    def test_dissolution_retains_log_and_clears_active_status(self):
        policy = QuantumAgentForgePolicy()
        request = _task()
        record = policy.record_spawn(request, policy.authorize_spawn(request), forge_id="forge-test-003")

        dissolved = policy.dissolve(record.forge_id, retention_required=True, log_summary="task complete")

        self.assertFalse(dissolved.active)
        self.assertTrue(dissolved.retention_required)
        self.assertIsNotNone(dissolved.dissolved_at)
        self.assertEqual("dissolved", dissolved.execution_log[-1]["event"])

    def test_retention_review_maps_outputs_to_protocol_outcomes(self):
        cases = [
            (RetentionCriteria(novel_concept=True), RetentionOutcome.STORE_AS_SPEC),
            (RetentionCriteria(module_candidate=True), RetentionOutcome.PROMOTE_TO_MODULE),
            (RetentionCriteria(reusable=True), RetentionOutcome.ARCHIVE),
            (RetentionCriteria(), RetentionOutcome.DISCARD),
        ]
        for criteria, expected in cases:
            with self.subTest(expected=expected):
                policy = QuantumAgentForgePolicy()
                request = _task()
                record = policy.record_spawn(request, policy.authorize_spawn(request), forge_id="forge-test-004")

                review = policy.review_retention(
                    record.forge_id,
                    output_summary="Useful forge result",
                    rationale="covered by retention threshold",
                    criteria=criteria,
                )

                self.assertIs(review.outcome, expected)
                if expected in {RetentionOutcome.STORE_AS_SPEC, RetentionOutcome.PROMOTE_TO_MODULE}:
                    self.assertIsNotNone(review.spec_id)
                else:
                    self.assertIsNone(review.spec_id)
                self.assertEqual("EOS_SEED_ORION", review.anchor)
                self.assertEqual("Picard_Delta_3", review.ethics_clearance)

    def test_pilot_override_controls_retention_outcome(self):
        policy = QuantumAgentForgePolicy()
        request = _task()
        record = policy.record_spawn(request, policy.authorize_spawn(request), forge_id="forge-test-005")

        review = policy.review_retention(
            record.forge_id,
            output_summary="Novel but intentionally discarded",
            rationale="pilot chose not to retain",
            criteria=RetentionCriteria(
                novel_concept=True,
                pilot_override=RetentionOutcome.DISCARD,
            ),
        )

        self.assertIs(review.outcome, RetentionOutcome.DISCARD)
        self.assertTrue(review.pilot_override)


if __name__ == "__main__":
    unittest.main()
