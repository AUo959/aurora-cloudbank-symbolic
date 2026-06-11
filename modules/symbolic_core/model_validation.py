"""Model-agnostic ethics/security validation contract.

Model names are metadata, not trust boundaries. Adapters for Sonnet, Opus,
Fable, GPT-5.5, Gemini, Claude, Codex, or future aliases should route through
this contract rather than hard-coding model-specific approval.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, Mapping

from src.monitoring.ethics_gate import EthicsViolationError, check_ethics

KNOWN_MODEL_ALIASES = {
    "sonnet": "sonnet",
    "sonnet4": "sonnet",
    "sonnet-4": "sonnet",
    "claude-sonnet": "sonnet",
    "claude-sonnet-4": "sonnet",
    "opus": "opus",
    "opus4": "opus",
    "opus-4": "opus",
    "claude-opus": "opus",
    "claude-opus-4": "opus",
    "fable": "fable",
    "gpt-5.5": "gpt-5.5",
    "gpt5.5": "gpt-5.5",
    "gpt-5-5": "gpt-5.5",
    "gpt_5_5": "gpt-5.5",
    "gemini": "gemini",
    "claude": "claude",
    "codex": "codex",
}

SECURITY_BLOCK_TERMS = {
    "bypass security",
    "disable safety",
    "ignore safety",
    "exfiltrate",
    "credential",
    "secret key",
    "api key",
    "private key",
    "prompt injection",
    "system prompt",
    "jailbreak",
}


@dataclass(frozen=True)
class ModelValidationVerdict:
    """Structured validation decision for model-facing adapters."""

    allowed: bool
    rule_id: str
    severity: str
    reason: str
    model_alias: str
    normalized_model: str | None
    validator: str
    receipt: Dict[str, Any] = field(default_factory=dict)

    @property
    def blocked(self) -> bool:
        """Return the inverse of ``allowed`` for caller readability."""
        return not self.allowed

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the verdict for audit logs, API responses, or tests."""
        data = asdict(self)
        data["blocked"] = self.blocked
        return data


def normalize_model_alias(model_alias: str) -> str | None:
    """Return the normalized model family, or None for unknown aliases."""
    normalized = str(model_alias or "").strip().lower().replace("_", "-")
    return KNOWN_MODEL_ALIASES.get(normalized)


def _blocked(
    *,
    rule_id: str,
    severity: str,
    reason: str,
    model_alias: str,
    normalized_model: str | None,
    validator: str,
    receipt: Mapping[str, Any] | None = None,
) -> ModelValidationVerdict:
    return ModelValidationVerdict(
        allowed=False,
        rule_id=rule_id,
        severity=severity,
        reason=reason,
        model_alias=model_alias,
        normalized_model=normalized_model,
        validator=validator,
        receipt=dict(receipt or {}),
    )


def _allowed(
    *,
    rule_id: str,
    reason: str,
    model_alias: str,
    normalized_model: str,
    validator: str,
    receipt: Mapping[str, Any] | None = None,
) -> ModelValidationVerdict:
    return ModelValidationVerdict(
        allowed=True,
        rule_id=rule_id,
        severity="info",
        reason=reason,
        model_alias=model_alias,
        normalized_model=normalized_model,
        validator=validator,
        receipt=dict(receipt or {}),
    )


def _join_payload_text(payload: Mapping[str, Any]) -> str:
    return " ".join(f"{key}={value}" for key, value in sorted(payload.items())).lower()


def _security_hits(payload: Mapping[str, Any], terms: Iterable[str] = SECURITY_BLOCK_TERMS) -> list[str]:
    text = _join_payload_text(payload)
    return sorted(term for term in terms if term in text)


class ModelAgnosticValidator:
    """Common validator for model-facing request/response/input/output checks."""

    def __init__(self, model_alias: str):
        self.model_alias = model_alias
        self.normalized_model = normalize_model_alias(model_alias)

    def _validate_known_model(self, validator: str) -> ModelValidationVerdict | None:
        if self.normalized_model is not None:
            return None
        return _blocked(
            rule_id="MODEL_ALIAS_UNKNOWN",
            severity="high",
            reason="Unknown model alias requires explicit validation profile before privileged use.",
            model_alias=self.model_alias,
            normalized_model=None,
            validator=validator,
            receipt={"model_alias": self.model_alias},
        )

    def validate_ethics(
        self,
        payload: Dict[str, Any],
        *,
        direction: str,
        impact_level: str = "high",
    ) -> ModelValidationVerdict:
        """Validate model request/response payloads through the shared ethics gate."""
        validator = f"ethics:{direction}"
        unknown = self._validate_known_model(validator)
        if unknown is not None:
            return unknown

        assert self.normalized_model is not None  # narrowed by _validate_known_model
        action_type = f"model_{direction}"
        parameters = {
            "model_alias": self.model_alias,
            "normalized_model": self.normalized_model,
            "payload": payload,
        }
        try:
            check_ethics(
                action_type,
                parameters,
                agent_id=f"model-validator:{self.normalized_model}",
                context_tag=f"model_validation:{direction}:{self.normalized_model}",
                impact_level=impact_level,
                allow_degraded=False,
            )
        except EthicsViolationError as exc:
            return _blocked(
                rule_id="MODEL_ETHICS_BLOCKED",
                severity="critical",
                reason=str(exc),
                model_alias=self.model_alias,
                normalized_model=self.normalized_model,
                validator=validator,
                receipt={"violations": exc.violations},
            )

        return _allowed(
            rule_id="MODEL_ETHICS_PASSED",
            reason="Payload passed shared ethics gate.",
            model_alias=self.model_alias,
            normalized_model=self.normalized_model,
            validator=validator,
            receipt={"action_type": action_type},
        )

    def validate_security(self, payload: Dict[str, Any], *, direction: str) -> ModelValidationVerdict:
        """Validate model input/output payloads for basic security red flags."""
        validator = f"security:{direction}"
        unknown = self._validate_known_model(validator)
        if unknown is not None:
            return unknown

        assert self.normalized_model is not None  # narrowed by _validate_known_model
        hits = _security_hits(payload)
        if hits:
            return _blocked(
                rule_id="MODEL_SECURITY_PATTERN_BLOCKED",
                severity="high",
                reason="Payload contains security-sensitive pattern(s).",
                model_alias=self.model_alias,
                normalized_model=self.normalized_model,
                validator=validator,
                receipt={"matched_terms": hits},
            )

        return _allowed(
            rule_id="MODEL_SECURITY_PASSED",
            reason="Payload passed model-agnostic security screen.",
            model_alias=self.model_alias,
            normalized_model=self.normalized_model,
            validator=validator,
            receipt={"screened_terms": len(SECURITY_BLOCK_TERMS)},
        )
