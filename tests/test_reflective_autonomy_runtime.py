from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from modules.reflective_autonomy.autonomic_correction_engine import AutonomicCorrectionEngine
from modules.reflective_autonomy.capsule_linter import CapsuleLinter
from modules.reflective_autonomy.integration_capsule_threadcore_classifier import ThreadcoreClassifierCapsule
from modules.reflective_autonomy.loom_restore_script import build_resetcore_plan, load_governance_config, run_resetcore
from modules.reflective_autonomy.reflective_autonomy_loop import ReflectiveAutonomyLoop
from modules.reflective_autonomy.sonnet4_reflective_engine import ReflectiveEngine


VALID_THREADCORE_PAYLOAD = {
    "augmentation": "THREADCORE",
    "version": "v3.5.1_macroready",
    "role": "Symbolic Constellation Loom + Reflection Module",
    "threadcore_directives": ["Preserve anchor continuity."],
    "anchor_seed": "EOS_SEED_ORION",
    "ethics_protocol": "Picard_Delta_3",
    "symbolic_drift": "0.0%",
}


class ReflectiveAutonomyRuntimeTests(TestCase):
    def test_capsule_linter_accepts_valid_threadcore_payload(self) -> None:
        result = CapsuleLinter().lint_capsule(VALID_THREADCORE_PAYLOAD, capsule_id="valid")

        self.assertTrue(result.valid)
        self.assertEqual(result.checked_capsules, 1)
        self.assertEqual(result.errors, [])

    def test_capsule_linter_reports_governance_and_schema_findings(self) -> None:
        invalid_payload = {
            "augmentation": "THREADCORE",
            "version": "v3.5.1_macroready",
            "role": "Symbolic Constellation Loom + Reflection Module",
            "anchor_seed": "WRONG_ANCHOR",
            "ethics_protocol": "Wrong_Protocol",
        }

        result = CapsuleLinter().lint_capsule(invalid_payload, capsule_id="invalid")
        codes = {finding.code for finding in result.findings}

        self.assertFalse(result.valid)
        self.assertIn("missing_required_field", codes)
        self.assertIn("invalid_anchor_seed", codes)
        self.assertIn("invalid_ethics_protocol", codes)

    def test_capsule_linter_rejects_non_mapping_payload(self) -> None:
        result = CapsuleLinter().lint_capsule("not a capsule", capsule_id="bad")  # type: ignore[arg-type]

        self.assertFalse(result.valid)
        self.assertEqual(result.errors[0].code, "invalid_capsule_type")

    def test_correction_engine_plans_non_destructive_actions(self) -> None:
        invalid_payload = {
            "augmentation": "THREADCORE",
            "version": "v3.5.1_macroready",
            "role": "Symbolic Constellation Loom + Reflection Module",
            "anchor_seed": "WRONG_ANCHOR",
            "ethics_protocol": "Picard_Delta_3",
        }

        report = AutonomicCorrectionEngine().evaluate_capsule(invalid_payload, capsule_id="invalid")
        actions = {action.action for action in report.actions}

        self.assertFalse(report.approved)
        self.assertIn("restore_governance_value", actions)
        self.assertIn("populate_field", actions)

    def test_reflective_autonomy_loop_writes_audit_receipt(self) -> None:
        invalid_payload = dict(VALID_THREADCORE_PAYLOAD)
        invalid_payload["threadcore_directives"] = []

        with TemporaryDirectory() as tmpdir:
            audit_log = Path(tmpdir) / "audit.log"
            loop = ReflectiveAutonomyLoop(audit_log_path=audit_log)
            receipt = loop.run_cycle(capsules=[invalid_payload])

            self.assertEqual(receipt.status, "attention_required")
            self.assertEqual(receipt.checked_capsules, 1)
            self.assertTrue(audit_log.exists())
            self.assertIn("planned: repair_directives", audit_log.read_text(encoding="utf-8"))

    def test_resetcore_plan_declares_handler_and_dry_run_receipt(self) -> None:
        config = load_governance_config()
        plan = build_resetcore_plan(config)
        result = run_resetcore(dry_run=True)

        self.assertEqual(plan["command"], "RESETCORE")
        self.assertEqual(plan["ethics_protocol"], "Picard_Delta_3")
        self.assertEqual(plan["anchor_seed"], "EOS_SEED_ORION")
        self.assertIn("run_resetcore", plan["handler"])
        self.assertTrue(result["dry_run"])
        self.assertIn(result["receipt"]["status"], {"passed", "attention_required"})

    def test_registered_payloads_have_lint_coverage(self) -> None:
        result = CapsuleLinter().lint_registered_payloads()

        self.assertGreaterEqual(result.checked_capsules, 4)
        self.assertTrue(result.valid)

    def test_classifier_capsule_returns_status_receipt(self) -> None:
        capsule = ThreadcoreClassifierCapsule()
        result = capsule.process("threadcore symbolic anchor vector")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["classification"]["primary_folder"], "SymbolicOps")

    def test_sonnet_reflective_engine_uses_governance_inputs(self) -> None:
        engine = ReflectiveEngine()
        decision = {
            "decision_id": "D-1",
            "rationale": "Preserve capsule integrity.",
            "expected_outcomes": ["lint receipt"],
            "ethical_verified": True,
        }

        result = engine.reflect_on_decision(decision)

        self.assertTrue(result["approved"])
        self.assertEqual(result["missing_fields"], [])
