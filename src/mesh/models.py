"""Dataclass models for the mesh runtime."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TypingProfile:
    """Basic typing cadence configuration for live chamber playback."""

    delay_ms: int = 450

    @classmethod
    def from_dict(cls, payload: Optional[Dict[str, Any]]) -> "TypingProfile":
        payload = payload or {}
        return cls(delay_ms=int(payload.get("delay_ms", 450)))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResponsePolicy:
    """Fallback and style settings for an agent manifest."""

    style: str = "general"
    fallback_to_deterministic: bool = True
    signature: str = ""

    @classmethod
    def from_dict(cls, payload: Optional[Dict[str, Any]]) -> "ResponsePolicy":
        payload = payload or {}
        return cls(
            style=str(payload.get("style", "general")),
            fallback_to_deterministic=bool(payload.get("fallback_to_deterministic", True)),
            signature=str(payload.get("signature", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentManifest:
    """Authoritative configuration for a routable agent."""

    id: str
    display_name: str
    aliases: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)
    default_channel: str = ""
    execution_mode: str = "deterministic"
    model_profile: Dict[str, Any] = field(default_factory=dict)
    typing_profile: TypingProfile = field(default_factory=TypingProfile)
    response_policy: ResponsePolicy = field(default_factory=ResponsePolicy)
    memory_files: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "AgentManifest":
        return cls(
            id=str(payload["id"]),
            display_name=str(payload["display_name"]),
            aliases=list(payload.get("aliases", [])),
            channels=list(payload.get("channels", [])),
            default_channel=str(payload.get("default_channel", "")),
            execution_mode=str(payload.get("execution_mode", "deterministic")),
            model_profile=dict(payload.get("model_profile", {})),
            typing_profile=TypingProfile.from_dict(payload.get("typing_profile")),
            response_policy=ResponsePolicy.from_dict(payload.get("response_policy")),
            memory_files=list(payload.get("memory_files", [])),
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["typing_profile"] = self.typing_profile.to_dict()
        payload["response_policy"] = self.response_policy.to_dict()
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


@dataclass
class MeshMessageRequest:
    """Canonical request body for user-originated mesh messages."""

    content: str
    to: Optional[str] = None
    channel: Optional[str] = None
    # Canon (ORION.ROLE.PILOT, owner-ruled 2026-06-11): the user-interface
    # role is Pilot; "captain" is the accepted legacy alias from early sessions.
    sender_id: str = "pilot"
    sender_name: str = "Pilot"
    type: str = "direct"

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "MeshMessageRequest":
        return cls(
            content=str(payload["content"]),
            to=payload.get("to"),
            channel=payload.get("channel"),
            sender_id=str(payload.get("sender_id", "pilot")),
            sender_name=str(payload.get("sender_name", "Pilot")),
            type=str(payload.get("type", "direct")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeshEvent:
    """Normalized event envelope for HTTP and WebSocket consumers."""

    event_id: int
    event_type: str
    message_id: str
    channel_id: str
    timestamp: str
    agent_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)
