"""Prepare L1-mediated QGIA evidence and CanonRec staging requests locally."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable, Mapping
from pathlib import Path, PurePosixPath
from typing import Annotated, BinaryIO, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, JsonValue, StrictInt, TypeAdapter, field_validator

from .schemas import ForecastOutput


Label = Annotated[str, Field(min_length=1, max_length=256)]
GitCommit = Annotated[str, Field(pattern=r"^(?:[a-f0-9]{40}|[a-f0-9]{64})$")]
Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
Repository = Annotated[str, Field(pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")]
REQUIRED_GATES = (
    "evidence", "layer_integrity", "schema_validation", "identity_collision",
    "authorization_approval", "final_reconciliation", "naming",
)


class BridgeError(ValueError):
    """The evidence or approval cannot support a staging request."""


class BridgeModel(BaseModel):
    """Versioned bridge documents reject fields outside their declared shape."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Artifact(BridgeModel):
    """Identify exact bytes in a layer-scoped local Git object."""

    repository: Repository
    commit: GitCommit
    path: str
    layer: Literal["L1", "L2"]
    sha256: Digest

    @field_validator("path")
    @classmethod
    def relative_git_path(cls, value: str) -> str:
        """Require a literal path inside the pinned repository."""
        if PurePosixPath(value).is_absolute() or {"", ".", ".."}.intersection(value.split("/")):
            raise ValueError("expected a repository-relative artifact path")
        if "\\" in value or "\0" in value:
            raise ValueError("unexpected path separator")
        return value


class ForecastPackage(BridgeModel):
    """Preserve a forecast with its source identity, context, and calibration."""

    version: Literal["1.0"]
    source_system: Literal["QGIA"]
    source_actor: Label
    as_of: AwareDatetime
    question: Label
    horizon: Label
    region: Label
    domain: Label
    forecast: ForecastOutput
    calibration: dict[str, JsonValue] = Field(min_length=1)
    model: Label
    priors: list[Artifact] = Field(min_length=1)
    evidence: list[Artifact] = Field(min_length=1)
    unknowns: tuple[Label, ...]
    assumptions: tuple[Label, ...]
    watchcon: Label | None = None
    axiom_state: Literal["clear", "approved_override", "hold"] = "clear"


class RunParameters(BridgeModel):
    """Describe parameters supported by the pinned GUMAS fixture adapter."""

    scenario_id: Literal["gumas_canonical_v1"]
    seed: StrictInt
    turns: StrictInt = Field(gt=0)
    fabric_domain: Literal["union", "velar"]


class EnginePin(BridgeModel):
    """Identify the engine reviewed by the approving L1 actor."""

    version: Literal["4.0.0-synth"]
    commit: GitCommit


class GateReference(BridgeModel):
    """Identify one independently issued CanonRec gate receipt."""

    receipt_id: Label
    artifact: Artifact


class Mediation(BridgeModel):
    """Record L1 approval and the scope of the translated scenario."""

    version: Literal["1.0"]
    decision: Literal["approved", "pending", "partial", "rejected"]
    scope: Literal["L2:scenario_seed"]
    authority: Label
    relay_id: Label
    reviewed_at: AwareDatetime
    forecast: Artifact
    selected_tiers: tuple[StrictInt, ...]
    translation_notes: Label
    constraints: tuple[Label, ...]
    excluded_interpretations: tuple[Label, ...]
    ethics_state: Literal["clear", "hold"]
    parameters: RunParameters
    engine: EnginePin


class Origin(BridgeModel):
    """Allow a pinned issuer for a particular evidence type."""

    repository: Repository
    commit: GitCommit


class Policy(BridgeModel):
    """Carry the local operator's trusted authorities and current artifact pins."""

    version: Literal["1.0"]
    forecast_origins: list[Origin]
    mediation_origins: list[Origin]
    current_forecasts: dict[Label, Digest]
    approvers: list[Label]
    relays: list[Label]
    engine_commit: GitCommit
    gate_origins: dict[str, list[Origin]]


Reader = Callable[[Artifact], bytes]
FORECAST_INSTANT = TypeAdapter(AwareDatetime)


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise BridgeError(f"Duplicate JSON key {key!r}")
        result[key] = value
    return result


def _json(data: str | bytes) -> dict:
    document = json.loads(data, object_pairs_hook=_unique_pairs)
    if not isinstance(document, dict):
        raise BridgeError("Expected a JSON object")
    return document


def _origin(reference: Artifact) -> Origin:
    return Origin(repository=reference.repository, commit=reference.commit)


def _verified(reference: Artifact, read: Reader) -> bytes:
    data = read(reference)
    if hashlib.sha256(data).hexdigest() != reference.sha256:
        raise BridgeError(f"Artifact digest mismatch for {reference.path}")
    return data


def _validate_review(forecast: ForecastPackage, review: Mediation, policy: Policy) -> None:
    if review.decision != "approved":
        raise BridgeError(f"L1 mediation is {review.decision}")
    if not all((review.authority in policy.approvers, review.relay_id in policy.relays)):
        raise BridgeError("L1 approval authority or relay is outside the configured scope")
    if forecast.source_actor in {review.relay_id, review.authority}:
        raise BridgeError("QGIA cannot approve or relay its own package")
    if "hold" in {review.ethics_state, forecast.axiom_state}:
        raise BridgeError("The source or L1 mediation carries an ethics or axiom hold")
    if review.reviewed_at < forecast.as_of:
        raise BridgeError("L1 mediation predates the forecast")
    if review.engine.commit != policy.engine_commit:
        raise BridgeError("L1 mediation pins an unsupported engine commit")
def _validate_selection(forecast: ForecastPackage, review: Mediation) -> None:
    branches = {tier.tier for tier in forecast.forecast.tier_assessments}
    selected = set(review.selected_tiers)
    if not all((selected, selected <= branches, len(selected) == len(review.selected_tiers))):
        raise BridgeError("L1 mediation must select distinct branches of the verified forecast")


def _validate_forecast(forecast: ForecastPackage, source: Artifact, policy: Policy) -> None:
    result = forecast.forecast
    if policy.current_forecasts.get(result.forecast_id) != source.sha256:
        raise BridgeError("The forecast is superseded or unregistered")
    if FORECAST_INSTANT.validate_python(result.timestamp) != forecast.as_of:
        raise BridgeError("The package timestamp differs from its forecast timestamp")
    _validate_tiers(result)


def _validate_tiers(result: ForecastOutput) -> None:
    if len({branch.tier for branch in result.tier_assessments}) != len(result.tier_assessments):
        raise BridgeError("A forecast branch identifier is repeated")
    values = (value for branch in result.tier_assessments for value in (branch.probability, branch.confidence))
    if any(not 0 <= value <= 1 for value in values):
        raise BridgeError("Forecast probability and confidence must be in [0, 1]")


def prepare_material(source: Artifact, mediation: Artifact, policy: Policy, read: Reader) -> dict:
    """Verify the forecast and L1 decision and return deterministic staging material."""
    if source.layer != "L1" or _origin(source) not in policy.forecast_origins:
        raise BridgeError("The forecast requires a trusted L1 Git origin")
    if mediation.layer != "L1" or _origin(mediation) not in policy.mediation_origins:
        raise BridgeError("The mediation record requires a trusted L1 Git origin")
    forecast = ForecastPackage.model_validate(_json(_verified(source, read)))
    review = Mediation.model_validate(_json(_verified(mediation, read)))
    _validate_forecast(forecast, source, policy)
    if review.forecast != source:
        raise BridgeError("The approval binds a different forecast or evidence hash")
    _validate_review(forecast, review, policy)
    _validate_selection(forecast, review)
    for reference in (*forecast.evidence, *forecast.priors):
        if reference.layer != "L1":
            raise BridgeError("A forecast evidence reference crosses layers")
        _verified(reference, read)

    evidence = {
        "version": "1.0", "layer": "L2", "certainty": "STAGING",
        "forecast_ref": source.model_dump(mode="json"), "mediation_ref": mediation.model_dump(mode="json"),
        "forecast": forecast.model_dump(mode="json"), "mediation": review.model_dump(mode="json"),
    }
    seed = {
        "version": "1.0", "seed_id": "qgia-seed-" + _digest(evidence), "forecast_id": forecast.forecast.forecast_id,
        "parameters": review.parameters.model_dump(mode="json"), "engine": review.engine.model_dump(mode="json"),
    }
    return {"scenario_seed": seed, "mediation_evidence": evidence}


def request_subject(material: dict, seed: Artifact, evidence: Artifact, read: Reader) -> dict:
    """Bind the exact pinned L2 outputs to one reviewable CanonRec request subject."""
    for kind, reference in (("scenario_seed", seed), ("mediation_evidence", evidence)):
        if reference.layer != "L2" or _json(_verified(reference, read)) != material[kind]:
            raise BridgeError(f"The pinned {kind} differs from the mediated staging material")
    seed_id = material["scenario_seed"]["seed_id"]
    package, review = (material["mediation_evidence"][key] for key in ("forecast", "mediation"))
    sources = [reference.model_dump(mode="json") for reference in (seed, evidence)]
    return {
        "version": "1.0", "request_id": "qgia-staging-" + _digest(sources),
        "submitter": {"system": "QGIA", "actor_id": package["source_actor"], "relay_id": review["relay_id"]},
        "layer": "L2", "operation": "create_staging_claim", "execution_mode": "reference",
        "targets": [{"kind": "scenario_seed", "record_id": seed_id, "layer": "L2", "expected_state": None}],
        "sources": sources, "approval": {"state": "approved", "authority": review["authority"]},
    }


def _verify_gate(name: str, reference: GateReference, subject: dict, policy: Policy, read: Reader) -> None:
    artifact = reference.artifact
    if artifact.layer != "L2" or _origin(artifact) not in policy.gate_origins.get(name, []):
        raise BridgeError(f"{name} has no trusted L2 origin")
    gate = _json(_verified(artifact, read))
    expected = {
        "gate": name, "receipt_id": reference.receipt_id, "subject_sha256": _digest(subject), "verdict": "PASS",
    }
    if name == "authorization_approval":
        expected.update(decision="approved", authority=subject["approval"]["authority"])
    if name == "final_reconciliation":
        expected["recommendation"] = "STAGING"
    if any(gate.get(key) != value for key, value in expected.items()):
        raise BridgeError(f"{name} does not approve the exact staging subject")


def _validate_subject(subject: dict) -> None:
    scope = tuple(subject[key] for key in ("layer", "operation", "execution_mode"))
    if scope != ("L2", "create_staging_claim", "reference"):
        raise BridgeError("A mediated package can only create L2 staging material")
    targets = subject["targets"]
    if len(targets) != 1:
        raise BridgeError("A mediated package requires exactly one approved scenario seed")
    target, = targets
    if (target["layer"], target["kind"], target["expected_state"]) != ("L2", "scenario_seed", None):
        raise BridgeError("A mediated package requires an L2 scenario seed target")


def _receipt_for_gate(name: str, reference: dict) -> tuple[str, GateReference]:
    if name == "naming":
        variant, = reference
        if variant not in {"exemption", "receipt"}:
            raise BridgeError("Expected a naming decision or naming exemption")
        name, reference = ("naming_exemption" if variant == "exemption" else name), reference[variant]
    return name, GateReference.model_validate(reference)


def finalize_request(subject: dict, receipts: dict, policy: Policy, read: Reader) -> dict:
    """Emit the CanonRec request after verifying every independently supplied gate."""
    _validate_subject(subject)
    if set(receipts) != set(REQUIRED_GATES):
        raise BridgeError("The current L2 stage request needs the complete CanonRec gate receipt set")
    for name, reference in receipts.items():
        gate, receipt = _receipt_for_gate(name, reference)
        _verify_gate(gate, receipt, subject, policy, read)
    request = {**subject, "gate_receipts": receipts}
    return {**request, "content_hash": _digest(request)}


def git_reader(repositories: Mapping[str, Path]) -> Reader:
    """Resolve evidence from configured local Git object databases."""
    try:
        from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo
    except ImportError as exc:
        raise BridgeError(
            "Install GitPython from the CloudBank development requirements to use local Git evidence"
        ) from exc

    try:
        checkouts = {name: Repo(path) for name, path in repositories.items()}
    except (InvalidGitRepositoryError, NoSuchPathError) as exc:
        raise BridgeError("An evidence repository is not available as a local Git checkout") from exc

    def read(reference: Artifact) -> bytes:
        repo = checkouts[reference.repository]
        try:
            with repo.git.custom_environment(GIT_NO_LAZY_FETCH="1", GIT_NO_REPLACE_OBJECTS="1", GIT_ALLOW_PROTOCOL=""):
                if repo.git.cat_file("-t", reference.commit) != "commit":
                    raise BridgeError("An artifact must pin a full Git commit")
                return repo.git.cat_file(
                    "blob", f"{reference.commit}:{reference.path}",
                    stdout_as_string=False, strip_newline_in_stdout=False,
                )
        except GitCommandError as exc:
            raise BridgeError(f"Git artifact unavailable for {reference.path}") from exc

    return read


def _document(stream: BinaryIO) -> dict:
    with stream:
        return _json(stream.read())


def _reference(stream: BinaryIO) -> Artifact:
    return Artifact.model_validate(_document(stream))


def _invoke(args: argparse.Namespace) -> dict:
    policy = Policy.model_validate(_document(args.policy))
    repositories = {name: Path(path) for name, path in (item.split("=", 1) for item in args.repository)}
    read = git_reader(repositories)
    material = prepare_material(_reference(args.forecast), _reference(args.mediation), policy, read)
    if args.action == "prepare":
        return material
    if args.seed is None or args.evidence is None:
        raise BridgeError("Select pinned seed and evidence artifacts with --seed and --evidence")
    subject = request_subject(material, _reference(args.seed), _reference(args.evidence), read)
    if args.action == "subject":
        return subject
    if args.gate_receipts is None:
        raise BridgeError("Supply independently issued gate proofs with --gate-receipts")
    return finalize_request(subject, _document(args.gate_receipts), policy, read)


def main() -> int:
    """Prepare evidence, issue a gate subject, or finalize a review-only packet."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "subject", "request"))
    for name in ("policy", "forecast", "mediation"):
        parser.add_argument(f"--{name}", required=True, type=argparse.FileType("rb"))
    for name in ("seed", "evidence", "gate-receipts"):
        parser.add_argument(f"--{name}", type=argparse.FileType("rb"))
    parser.add_argument("--repository", action="append", default=[], metavar="OWNER/REPO=PATH")
    args = parser.parse_args()

    try:
        print(_canonical(_invoke(args)).decode())
    except (KeyError, OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"{exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
