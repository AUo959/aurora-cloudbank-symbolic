from modules.reflective_autonomy.autonomic_correction_engine import AutonomicCorrectionEngine
from modules.reflective_autonomy.capsule_linter import CapsuleLinter
from modules.reflective_autonomy.reflective_autonomy_loop import ReflectiveAutonomyLoop
from modules.reflective_autonomy.reflective_monitor_core import (
    AutonomicCorrectionEngine as CoreAutonomicCorrectionEngine,
)
from modules.reflective_autonomy.reflective_monitor_core import CapsuleLinter as CoreCapsuleLinter
from modules.reflective_autonomy.reflective_monitor_core import ReflectiveAutonomyLoop as CoreReflectiveAutonomyLoop


def test_capsule_linter_reexport_matches_core():
    assert CapsuleLinter is CoreCapsuleLinter


def test_autonomic_correction_engine_reexport_matches_core():
    assert AutonomicCorrectionEngine is CoreAutonomicCorrectionEngine


def test_reflective_autonomy_loop_reexport_matches_core():
    assert ReflectiveAutonomyLoop is CoreReflectiveAutonomyLoop
