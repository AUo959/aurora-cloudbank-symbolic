from tempfile import TemporaryDirectory
from unittest import TestCase

from modules.nexus.emergence.consciousness_emergence_enhanced import EnhancedConsciousnessProtocol
from modules.nexus.emergence.vector_binding import (
    ECHOCHAIN_LINKS,
    ECHOCHAIN_LOOPSET,
    LOCKPOINT_REFERENCE,
    PHASE6_ANCHOR,
    VECTOR_STATE,
    load_vector_binding_contract,
    startup_assert_phase6_vector_binding,
    verify_phase6_vector_binding,
)


class Phase6VectorBindingTests(TestCase):
    def test_contract_contains_phase6_vector_identifiers(self) -> None:
        contract = load_vector_binding_contract()

        self.assertEqual(contract["phase_anchor"], PHASE6_ANCHOR)
        self.assertEqual(contract["vector_state"], VECTOR_STATE)
        self.assertEqual(contract["lockpoint_reference"], LOCKPOINT_REFERENCE)
        self.assertEqual(contract["echochain"]["loopset"], ECHOCHAIN_LOOPSET)
        self.assertEqual(contract["echochain"]["linked"], list(ECHOCHAIN_LINKS))

    def test_startup_assertion_verifies_runtime_bindings(self) -> None:
        receipt = startup_assert_phase6_vector_binding()

        self.assertTrue(receipt.valid)
        self.assertEqual(receipt.errors, [])
        self.assertIn("modules/nexus/emergence/consciousness_emergence_enhanced.py", receipt.checked_files)
        self.assertIn(".nexus/emergence/protocols/PROT-1758781014.405975.json", receipt.checked_files)

    def test_enhanced_protocol_exposes_vector_binding(self) -> None:
        with TemporaryDirectory() as tmpdir:
            protocol = EnhancedConsciousnessProtocol(snapshot_directory=tmpdir)

            self.assertEqual(protocol.anchor, PHASE6_ANCHOR)
            self.assertEqual(protocol.vector_state, VECTOR_STATE)
            self.assertEqual(protocol.lockpoint_reference, LOCKPOINT_REFERENCE)
            self.assertEqual(protocol.echochain_loopset, ECHOCHAIN_LOOPSET)
            self.assertEqual(protocol.echochain_links, list(ECHOCHAIN_LINKS))

    def test_verification_receipt_is_machine_readable(self) -> None:
        receipt = verify_phase6_vector_binding().to_dict()

        self.assertTrue(receipt["valid"])
        self.assertEqual(receipt["bindings"]["vector_state"], VECTOR_STATE)
        self.assertEqual(receipt["bindings"]["echochain"]["loopset"], ECHOCHAIN_LOOPSET)
