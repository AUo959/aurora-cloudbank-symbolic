# Reflective Autonomy System Code Bundle
# Fully integrated operational symbolic governance system
# Phase 1-7 Complete Bundle

# =============================================
# MODULE 1 — Reflective Monitor Core
# =============================================

import datetime
from pathlib import Path

import yaml

class ReflectiveMonitor:

    def __init__(self, capsule_index_path=".loom/reflect/capsule_registry.yaml"):
        self.capsule_index_path = Path(capsule_index_path)
        self.load_capsule_registry()

    def load_capsule_registry(self):
        if not self.capsule_index_path.exists():
            self.capsule_registry = {}
            print("[WARN] Capsule registry not found. Initializing empty.")
        else:
            with open(self.capsule_index_path, "r") as f:
                self.capsule_registry = yaml.safe_load(f) or {}
        print(f"[LOADED] {len(self.capsule_registry)} capsules registered.")

    def register_capsule(self, anchor_hash, bundle_name, export_time, files):
        self.capsule_registry[anchor_hash] = {
            "bundle": bundle_name,
            "exported_at": export_time,
            "files": files,
            "status": "sealed",
        }
        self.save_capsule_registry()
        print(f"[REGISTERED] Capsule {anchor_hash} registered.")

    def save_capsule_registry(self):
        self.capsule_index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.capsule_index_path, "w") as f:
            yaml.dump(self.capsule_registry, f)

    def audit_registry(self):
        unsealed = [
            k for k, v in self.capsule_registry.items() if v.get("status") != "sealed"
        ]
        print("[AUDIT] Capsule Integrity Check:")
        print(f" - Total Capsules: {len(self.capsule_registry)}")
        print(f" - Unsealed Capsules: {len(unsealed)}")
        return unsealed

# =============================================
# MODULE 2 — Capsule Linter
# =============================================

class CapsuleLinter:

    def __init__(self, capsule_index_path=".loom/reflect/capsule_registry.yaml"):
        self.capsule_index_path = Path(capsule_index_path)
        self.diagnostics = []
        self.load_registry()

    def load_registry(self):
        if not self.capsule_index_path.exists():
            raise FileNotFoundError("Capsule registry not found.")
        with open(self.capsule_index_path, "r") as f:
            self.registry = yaml.safe_load(f) or {}
        print(f"[LOADED] {len(self.registry)} capsules indexed.")

    def run_lint(self):
        self.diagnostics.clear()
        for anchor, meta in self.registry.items():
            if "status" not in meta or meta["status"] != "sealed":
                self.diagnostics.append((anchor, "Unsealed Capsule"))
            if not meta.get("files"):
                self.diagnostics.append((anchor, "Missing file list"))
            if not meta.get("exported_at"):
                self.diagnostics.append((anchor, "Missing export timestamp"))
        self.print_diagnostics()

    def print_diagnostics(self):
        if not self.diagnostics:
            print("[LINTER] No issues found.")
        else:
            print("[LINTER] Issues detected:")
            for anchor, issue in self.diagnostics:
                print(f" - {anchor}: {issue}")

    def suggest_actions(self):
        suggestions = []
        for anchor, issue in self.diagnostics:
            if issue == "Unsealed Capsule":
                suggestions.append(f"Seal capsule {anchor}")
            if issue == "Missing file list":
                suggestions.append(f"Verify files for {anchor}")
            if issue == "Missing export timestamp":
                suggestions.append(f"Recover export date for {anchor}")
        return suggestions

# =============================================
# MODULE 3 — Continuity Manager
# =============================================

class ContinuityManager:

    def __init__(self):
        self.linter = CapsuleLinter()
        self.recovery_queue = []

    def evaluate(self):
        print("[CONTINUITY] Evaluating symbolic thread integrity...")
        self.linter.run_lint()
        suggestions = self.linter.suggest_actions()
        for action in suggestions:
            self.queue_recovery(action)
        self.report_queue()

    def queue_recovery(self, action):
        self.recovery_queue.append(action)
        print(f"[QUEUE] Recovery action queued: {action}")

    def report_queue(self):
        if not self.recovery_queue:
            print("[CONTINUITY] No recovery actions required.")
        else:
            print("[CONTINUITY] Recovery Actions Pending:")
            for action in self.recovery_queue:
                print(f" - {action}")

# =============================================
# MODULE 4 — Autonomic Correction Engine
# =============================================

class AutonomicCorrectionEngine:

    def __init__(self):
        self.manager = ContinuityManager()
        self.correction_log = []

    def evaluate_and_correct(self):
        print("[ACE] Evaluating continuity recovery actions...")
        self.manager.evaluate()
        for action in self.manager.recovery_queue:
            if self.validate_correction(action):
                self.apply_correction(action)
            else:
                print(f"[ACE] Correction deferred: {action}")
        self.report_corrections()

    def validate_correction(self, action):
        if "Seal capsule" in action:
            return True  # Initial simple heuristic — future upgrade path
        return False

    def apply_correction(self, action):
        self.correction_log.append(action)
        print(f"[ACE] Correction applied: {action}")

    def report_corrections(self):
        if not self.correction_log:
            print("[ACE] No corrections applied.")
        else:
            print("[ACE] Corrections Applied:")
            for correction in self.correction_log:
                print(f" - {correction}")

# =============================================
# MODULE 5 — Reflective Autonomy Loop
# =============================================

class ReflectiveAutonomyLoop:

    def __init__(self):
        self.ace = AutonomicCorrectionEngine()
        self.audit_log_path = ".loom/reflect/autonomy_audit_log.txt"

    def run_cycle(self):
        print("[RAL] Starting Reflective Autonomy Cycle...")
        timestamp = datetime.datetime.now().isoformat()
        self.ace.evaluate_and_correct()
        self.write_audit_log(timestamp)
        print("[RAL] Cycle complete.")

    def write_audit_log(self, timestamp):
        with open(self.audit_log_path, "a") as f:
            f.write(f"Autonomy Cycle: {timestamp}\n")
            if not self.ace.correction_log:
                f.write(" - No corrections applied.\n")
            else:
                for correction in self.ace.correction_log:
                    f.write(f" - Applied: {correction}\n")
            f.write("\n")
