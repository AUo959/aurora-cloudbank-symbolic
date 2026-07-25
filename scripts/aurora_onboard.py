#!/usr/bin/env python3
"""Human-first, repository-grounded onboarding for Aurora / Orion Station.

The command uses only the Python standard library. All reported system state is
read from files in the current checkout; architecture constants are verified
against the canonical layer document before they are displayed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence, TextIO


RELAY_AGENTS = ("ARCHY", "OPPY", "LIORA", "STARLING_AU", "RIVERTHREAD_808")
L3_FRAMEWORKS = ("Axiomera", "Caelion", "Sentari", "Velatrix", "Glyphon", "Harmion")
SYSTEM_ENTITY = "HALO"
DEFAULT_PYTHON_FLOOR = (3, 11)


@dataclass(frozen=True)
class Check:
    """One evidence-backed onboarding validation."""

    name: str
    status: str
    detail: str
    source: str


class OnboardingError(RuntimeError):
    """Human-readable onboarding failure that must not expose a traceback."""


class AuroraOnboarding:
    """Run the onboarding phases against one repository checkout."""

    def __init__(self, root: Path, stream: TextIO, input_fn: Callable[[str], str]) -> None:
        self.root = root.resolve()
        self.stream = stream
        self.input_fn = input_fn
        self.checks: list[Check] = []
        self.context: dict[str, Any] = {}
        self.state: dict[str, Any] = {}
        self.architecture_text = ""
        self.version = "unknown"
        self.lockpoint = "not recorded"
        self.lockpoint_source = "AURORA_CONTEXT.json"
        self.lockpoint_freshness_warning = ""
        self.ethics: dict[str, Any] = {}
        self.seed: dict[str, Any] | None = None

    def _path(self, relative: str) -> Path:
        path = (self.root / relative).resolve()
        if self.root not in path.parents and path != self.root:
            raise OnboardingError(f"Path escapes repository root: {relative}")
        return path

    def _read_text(self, relative: str) -> str:
        path = self._path(relative)
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise OnboardingError(f"Cannot read {relative}: {exc}") from None

    def _read_json(self, relative: str) -> dict[str, Any]:
        try:
            value = json.loads(self._read_text(relative))
        except json.JSONDecodeError as exc:
            raise OnboardingError(f"Invalid JSON in {relative}: line {exc.lineno}, column {exc.colno}") from None
        if not isinstance(value, dict):
            raise OnboardingError(f"Expected a JSON object in {relative}")
        return value

    def _add_check(self, name: str, status: str, detail: str, source: str) -> None:
        self.checks.append(Check(name=name, status=status, detail=detail, source=source))

    def _python_floor(self) -> tuple[int, int]:
        setup_text = self._read_text("setup.py")
        match = re.search(r"python_requires\s*=\s*[\"']>=\s*(\d+)\.(\d+)", setup_text)
        if not match:
            fallback = f">={DEFAULT_PYTHON_FLOOR[0]}.{DEFAULT_PYTHON_FLOOR[1]}"
            self._add_check(
                "python_requirement_source",
                "warning",
                f"python_requires was not found; using onboarding fallback {fallback}",
                "setup.py",
            )
            return DEFAULT_PYTHON_FLOOR
        return int(match.group(1)), int(match.group(2))

    def _check_python(self) -> None:
        floor = self._python_floor()
        actual = sys.version_info[:2]
        detail = f"Python {actual[0]}.{actual[1]} (repository requires >={floor[0]}.{floor[1]})"
        status = "pass" if actual >= floor else "fail"
        self._add_check("python_version", status, detail, "setup.py")

    def _load_required_sources(self) -> None:
        self.state = self._read_json(".aurora/SIMULATION_STATE.json")
        self.context = self._read_json("AURORA_CONTEXT.json")
        self.architecture_text = self._read_text("docs/architecture/LAYER_ARCHITECTURE.md")
        self._add_check(
            "simulation_state",
            "pass",
            f"Readable JSON; last_updated={self.state.get('last_updated', 'not recorded')}",
            ".aurora/SIMULATION_STATE.json",
        )
        self._add_check(
            "aurora_context",
            "pass",
            f"Readable JSON; generated={self.context.get('document_generated', 'not recorded')}",
            "AURORA_CONTEXT.json",
        )

    def _load_identity(self) -> None:
        manifest = self._read_text("src/api/l1_relay_api.manifest.yaml")
        version_match = re.search(r"Aurora_Continuity_Seal_v([0-9.]+)", manifest)
        if not version_match:
            raise OnboardingError("Continuity version is missing from src/api/l1_relay_api.manifest.yaml")
        self.version = version_match.group(1)
        active_state = self.context.get("active_state", {})
        if isinstance(active_state, dict) and active_state.get("lockpoint"):
            self.lockpoint = str(active_state["lockpoint"])
        freshness = active_state.get("_staleness_warning") if isinstance(active_state, dict) else None
        self.lockpoint_freshness_warning = str(freshness or "")
        detail = f"Aurora continuity v{self.version}; lockpoint={self.lockpoint}"
        if freshness:
            detail += "; lockpoint is a documented context snapshot, not a live-state claim"
        self._add_check(
            "system_identity",
            "pass",
            detail,
            "AURORA_CONTEXT.json + src/api/l1_relay_api.manifest.yaml",
        )

    def _check_architecture(self) -> None:
        expected = (*RELAY_AGENTS, SYSTEM_ENTITY, *L3_FRAMEWORKS, "Triplex Handshake")
        missing = [term for term in expected if term not in self.architecture_text]
        if missing:
            self._add_check(
                "architecture_canon",
                "fail",
                f"Canonical architecture source is missing: {', '.join(missing)}",
                "docs/architecture/LAYER_ARCHITECTURE.md",
            )
            return
        self._add_check(
            "architecture_canon",
            "pass",
            "Five L1 relay agents, HALO continuity system-entity, and six L3 frameworks verified",
            "docs/architecture/LAYER_ARCHITECTURE.md",
        )

    def _check_ethics(self) -> None:
        manifest = self._read_json("QGIA_integration/QUANTUM_FORGE_Axiom_Manifest.json")
        audit_text = self._read_text("QGIA_Integration/04_GUMAS_AuditSchema.md")
        script_text = self._read_text("scripts/activate_l3_ethics.sh")
        binding = manifest.get("ethics_binding")
        context_status = self.context.get("active_modules", {}).get("ethics", {}).get("status")
        rule_match = re.search(r"### (GAE-\d{3} \| [^\n]+).*?- \*\*Trigger condition:\*\* ([^\n]+)", audit_text, re.S)
        self.ethics = {
            "layer_status": str(context_status or "not recorded").upper(),
            "binding": binding,
            "binding_verified": binding == "GUMAS_Thermax",
            "sample_rule": rule_match.group(1) if rule_match else "not available",
            "sample_rule_summary": rule_match.group(2) if rule_match else "not available",
            "activation_source_present": "Picard_Delta_3" in script_text,
            "sources": [
                "AURORA_CONTEXT.json",
                "QGIA_integration/QUANTUM_FORGE_Axiom_Manifest.json",
                "QGIA_Integration/04_GUMAS_AuditSchema.md",
                "scripts/activate_l3_ethics.sh",
            ],
        }
        verified = context_status == "active" and binding == "GUMAS_Thermax" and bool(rule_match)
        self._add_check(
            "ethics_anchor",
            "pass" if verified else "fail",
            f"Ethics layer={self.ethics['layer_status']}; GUMAS_Thermax binding={binding or 'missing'}",
            "AURORA_CONTEXT.json + QGIA_integration/QUANTUM_FORGE_Axiom_Manifest.json",
        )

    def validate(self) -> None:
        """Load every source needed by the uninterrupted onboarding flow."""

        self._check_python()
        self._load_required_sources()
        self._load_identity()
        self._check_architecture()
        self._check_ethics()
        for relative in ("CANON_INDEX.md", "seeds/onboarding/README.md"):
            self._read_text(relative)
        canon_index = self._read_text("CANON_INDEX.md")
        indexed = "seeds/onboarding/README.md" in canon_index
        self._add_check(
            "seed_staging_policy",
            "pass" if indexed else "warning",
            "Engineer seed staging is indexed without automatic canon promotion" if indexed else "Seed staging policy is not indexed",
            "CANON_INDEX.md",
        )

    def _print(self, value: str = "") -> None:
        print(value, file=self.stream)

    def print_environment(self) -> None:
        self._print("\nPhase 1 — Environment Check")
        self._print("-" * 36)
        for check in self.checks:
            icon = "PASS" if check.status == "pass" else check.status.upper()
            self._print(f"[{icon}] {check.name}: {check.detail}")
        self._print(f"Aurora v{self.version} | Orion Station | {self.lockpoint}")
        if self.lockpoint_freshness_warning:
            self._print(f"Freshness warning from AURORA_CONTEXT.json: {self.lockpoint_freshness_warning}")
        else:
            self._print("Note: the lockpoint is read from AURORA_CONTEXT.json; no freshness warning is recorded.")

    def print_architecture(self) -> None:
        layers = self.context.get("architecture_layers", {})
        self._print("\nPhase 2 — Layer Architecture Tour")
        self._print("-" * 36)
        for layer in ("L1", "L2", "L3"):
            self._print(f"{layer}: {layers.get(layer, 'Not recorded in AURORA_CONTEXT.json')}")
        self._print(f"L1 relay agents: {', '.join(RELAY_AGENTS)}")
        self._print(f"L1 continuity system-entity: {SYSTEM_ENTITY} (verifies continuity; does not relay messages)")
        self._print(f"L3 glyph frameworks: {', '.join(L3_FRAMEWORKS)}")
        self._print("Triplex: L3 glyph validation → L1 verifier step → L1 human consent.")

    def print_ethics(self) -> None:
        self._print("\nPhase 3 — Ethics Anchor Live Demo (read-only)")
        self._print("-" * 36)
        verified = "VERIFIED" if self.ethics.get("binding_verified") else "UNVERIFIED"
        self._print(f"Ethics layer: {self.ethics.get('layer_status')} | GUMAS_Thermax binding: {verified}")
        self._print(f"Sample audit rule: {self.ethics.get('sample_rule')}")
        self._print(f"Trigger: {self.ethics.get('sample_rule_summary')}")

    @staticmethod
    def _slug(handle: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", handle.lower()).strip("-")
        return (slug or "engineer")[:48]

    def write_seed(self, handle: str) -> dict[str, Any]:
        clean_handle = handle.strip()
        if not clean_handle:
            raise OnboardingError("Engineer handle cannot be empty")
        if len(clean_handle) > 80:
            raise OnboardingError("Engineer handle must be 80 characters or fewer")
        now = datetime.now(timezone.utc)
        receipt_time = now.replace(microsecond=0)
        relative = Path("seeds/onboarding") / f"engineer-{self._slug(clean_handle)}-{now:%Y%m%dT%H%M%S%fZ}.md"
        path = self._path(relative.as_posix())
        path.parent.mkdir(parents=True, exist_ok=True)
        content = self._seed_content(clean_handle, receipt_time)
        try:
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)
        except OSError as exc:
            raise OnboardingError(f"Cannot write {relative.as_posix()}: {exc}") from None
        if path.read_text(encoding="utf-8") != content:
            raise OnboardingError(f"Seed verification failed for {relative.as_posix()}")
        self.seed = {
            "path": relative.as_posix(),
            "status": "staged",
            "created_at": receipt_time.isoformat().replace("+00:00", "Z"),
            "canon_policy": "seeds/onboarding/README.md",
            "verified": True,
        }
        return self.seed

    @staticmethod
    def _seed_content(handle: str, now: datetime) -> str:
        created_at = now.isoformat().replace("+00:00", "Z")
        return (
            "---\n"
            "seed_type: engineer_onboarding\n"
            "seed_status: staged\n"
            f"engineer_handle: {json.dumps(handle, ensure_ascii=False)}\n"
            f"created_at: {created_at}\n"
            "anchor_seed: EOS_SEED_ORION\n"
            "ethics_protocol: Picard_Delta_3\n"
            "source: scripts/aurora_onboard.py\n"
            "---\n\n"
            "# Engineer Onboarding Memory Seed\n\n"
            "This seed records completion of the repository onboarding flow. It is staged, not canonical, until reviewed.\n"
        )

    def prompt_for_seed(self) -> None:
        self._print("\nPhase 4 — Symbolic Memory Seed Write (optional)")
        self._print("-" * 36)
        if self.exit_code() == 1:
            self._print("Skipped because environment validation failed. No repository files were written.")
            return
        answer = self.input_fn("Write your engineer handle to the memory vault? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            self._print("Skipped. No repository files were written.")
            return
        handle = self.input_fn("Engineer handle: ")
        seed = self.write_seed(handle)
        self._print(f"Seed written and verified: {seed['path']}")
        self._print("Status: staged; CANON_INDEX.md points to the review policy, not automatic promotion.")

    def status(self) -> str:
        statuses = {check.status for check in self.checks}
        if "fail" in statuses:
            return "fail"
        if "warning" in statuses:
            return "partial"
        return "pass"

    def exit_code(self) -> int:
        status = self.status()
        if status == "fail":
            return 1
        if status == "partial":
            return 2
        return 0

    def agent_report(self, elapsed: float) -> dict[str, Any]:
        code = self.exit_code()
        return {
            "schema_version": "1.0.0",
            "mode": "agent",
            "status": self.status(),
            "exit_code": code,
            "system": {
                "identity": self.context.get("system_identity", {}).get("name", "Aurora"),
                "continuity_version": self.version,
                "station": "Orion Station",
                "lockpoint": self.lockpoint,
                "lockpoint_source": self.lockpoint_source,
            },
            "checks": [asdict(check) for check in self.checks],
            "architecture": {
                "layers": self.context.get("architecture_layers", {}),
                "l1_relay_agents": list(RELAY_AGENTS),
                "l1_continuity_system_entity": SYSTEM_ENTITY,
                "l3_glyph_frameworks": list(L3_FRAMEWORKS),
            },
            "ethics": self.ethics,
            "memory_seed": self.seed,
            "elapsed_seconds": round(elapsed, 3),
            "next_steps": ["CANON_INDEX.md", ".aurora/SIMULATION_STATE.json", "docs/architecture/"],
        }

    def print_completion(self, elapsed: float) -> None:
        code = self.exit_code()
        self._print("\nPhase 5 — Completion Report")
        self._print("-" * 36)
        self._print(f"Elapsed time: {elapsed:.2f}s")
        if code == 1:
            self._print("❌ Onboarding incomplete. Resolve the failed environment checks above.")
            return
        self._print("✅ Onboarding complete. You are now a verified Orion Station crew member.")
        if self.status() == "partial":
            self._print("Non-fatal warnings were recorded; review them before implementation work.")
        self._print("Next: CANON_INDEX.md | .aurora/SIMULATION_STATE.json | docs/architecture/")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aurora / Orion Station engineer onboarding")
    parser.add_argument("--skip-interactive", action="store_true", help="Run validation without prompts")
    parser.add_argument("--agent", action="store_true", help="Emit one JSON status object and suppress prose")
    return parser


def _error_report(message: str, agent: bool, stream: TextIO) -> None:
    if agent:
        json.dump(
            {
                "schema_version": "1.0.0",
                "mode": "agent",
                "status": "fail",
                "exit_code": 1,
                "error": message,
            },
            stream,
            indent=2,
        )
        stream.write("\n")
    else:
        print(f"❌ Onboarding could not continue: {message}", file=stream)


def _run_onboarding(
    app: AuroraOnboarding,
    args: argparse.Namespace,
    started: float,
    input_fn: Callable[[str], str],
) -> int:
    app.validate()
    if args.agent:
        json.dump(app.agent_report(time.perf_counter() - started), app.stream, indent=2)
        app.stream.write("\n")
        return app.exit_code()
    app.print_environment()
    if not args.skip_interactive:
        choice = input_fn("Press ENTER to tour the layer architecture, or SKIP to proceed: ").strip().upper()
        if choice != "SKIP":
            app.print_architecture()
    app.print_ethics()
    if not args.skip_interactive:
        app.prompt_for_seed()
    elapsed = time.perf_counter() - started
    app.print_completion(elapsed)
    return app.exit_code()


def main(
    argv: Sequence[str] | None = None,
    *,
    repo_root: Path | None = None,
    stream: TextIO | None = None,
    input_fn: Callable[[str], str] = input,
) -> int:
    args = build_parser().parse_args(argv)
    output = stream or sys.stdout
    root = repo_root or Path(__file__).resolve().parents[1]

    # No terminal attached (piped, redirected, CI, container) means the
    # interactive prompts can never be answered. Degrade to the same path as
    # --skip-interactive rather than failing on EOF, so `make onboard` in a
    # non-tty context still produces a useful report. Only applies when reading
    # from real stdin — an injected input_fn supplies its own answers.
    if (
        not args.skip_interactive
        and not args.agent
        and input_fn is input
        and not sys.stdin.isatty()
    ):
        args.skip_interactive = True
        print(
            "ℹ️  No interactive terminal detected — running in non-interactive mode "
            "(equivalent to --skip-interactive).",
            file=output,
        )
    started = time.perf_counter()
    app = AuroraOnboarding(root=root, stream=output, input_fn=input_fn)
    try:
        return _run_onboarding(app, args, started, input_fn)
    except (OnboardingError, EOFError, KeyboardInterrupt) as exc:
        message = str(exc) or "onboarding interrupted"
        _error_report(message, args.agent, output)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
