"""Personal Access Terminal profiles for mesh routing compatibility."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .manifests import normalize_lookup
from .models import AgentManifest


PERSONNEL_ATTENTION_TAG_RE = re.compile(r"^\{\{@[^{}]+:::.+\}\}$")


def is_personnel_attention_tag(value: str) -> bool:
    """Return true for EVA/HUD Personnel Attention Tag syntax."""

    return bool(PERSONNEL_ATTENTION_TAG_RE.match(value.strip()))


@dataclass
class MeshTerminalRoute:
    """Runtime mesh target attached to a terminal profile."""

    owner_agent_id: Optional[str] = None
    channel_id: str = ""
    route_kind: str = "mesh_agent"
    routable: bool = True

    @classmethod
    def from_dict(cls, payload: Optional[Dict[str, Any]]) -> "MeshTerminalRoute":
        payload = payload or {}
        return cls(
            owner_agent_id=payload.get("owner_agent_id"),
            channel_id=str(payload.get("channel_id", "")),
            route_kind=str(payload.get("route_kind", "mesh_agent")),
            routable=bool(payload.get("routable", True)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PatOverlay:
    """Recovered Personal Access Terminal routing overlay metadata."""

    pat_role: str
    status: str
    visibility: str
    anchor_node: str
    thread: Optional[str] = None
    source_pointers: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PatOverlay":
        return cls(
            pat_role=str(payload.get("pat_role", "")),
            status=str(payload.get("status", "")),
            visibility=str(payload.get("visibility", "")),
            anchor_node=str(payload.get("anchor_node", "")),
            thread=payload.get("thread"),
            source_pointers=list(payload.get("source_pointers", [])),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PersonalTerminalProfile:
    """Terminal profile between CanonRec identity and CloudBank mesh routing."""

    terminal_id: str
    owner_display_name: str
    owner_class: str
    terminal_namespace: str
    owner_agent_id: Optional[str] = None
    canon_entity_id: Optional[str] = None
    canon_preferred_name: str = ""
    canon_layer: str = ""
    canon_type: str = ""
    canon_authority: str = ""
    canon_source: str = ""
    l1_station_layer: str = "L1"
    terminal_type: str = "crew"
    station_context: Dict[str, Any] = field(default_factory=dict)
    mesh_route: MeshTerminalRoute = field(default_factory=MeshTerminalRoute)
    aliases: List[str] = field(default_factory=list)
    source_pointers: List[str] = field(default_factory=list)
    pat_overlay: Optional[PatOverlay] = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PersonalTerminalProfile":
        pat_payload = payload.get("pat_overlay")
        return cls(
            terminal_id=str(payload["terminal_id"]),
            owner_agent_id=payload.get("owner_agent_id"),
            owner_display_name=str(payload.get("owner_display_name", "")),
            owner_class=str(payload.get("owner_class", "")),
            canon_entity_id=payload.get("canon_entity_id"),
            canon_preferred_name=str(payload.get("canon_preferred_name", "")),
            canon_layer=str(payload.get("canon_layer", "")),
            canon_type=str(payload.get("canon_type", "")),
            canon_authority=str(payload.get("canon_authority", "")),
            canon_source=str(payload.get("canon_source", "")),
            l1_station_layer=str(payload.get("l1_station_layer", "L1")),
            terminal_namespace=str(payload.get("terminal_namespace", "")),
            terminal_type=str(payload.get("terminal_type", "crew")),
            station_context=dict(payload.get("station_context", {})),
            mesh_route=MeshTerminalRoute.from_dict(payload.get("mesh_route")),
            aliases=list(payload.get("aliases", [])),
            source_pointers=list(payload.get("source_pointers", [])),
            pat_overlay=PatOverlay.from_dict(pat_payload) if pat_payload else None,
        )

    @property
    def routable(self) -> bool:
        return bool(self.mesh_route.routable and self.mesh_route.owner_agent_id)

    def lookup_values(self) -> List[str]:
        values = [
            self.terminal_id,
            self.terminal_namespace,
            self.owner_display_name,
            self.canon_preferred_name,
            *self.aliases,
        ]
        if self.owner_agent_id:
            values.append(self.owner_agent_id)
        if self.mesh_route.channel_id:
            values.append(self.mesh_route.channel_id)
        if self.pat_overlay and self.pat_overlay.anchor_node:
            values.append(self.pat_overlay.anchor_node)
        return [value for value in values if value]

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["mesh_route"] = self.mesh_route.to_dict()
        payload["pat_overlay"] = self.pat_overlay.to_dict() if self.pat_overlay else None
        payload["routable"] = self.routable
        return payload


@dataclass
class TerminalGroup:
    """Resolved group of terminal profiles sharing one compatibility alias."""

    lookup_key: str
    members: List[PersonalTerminalProfile]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "terminal_id": self.lookup_key,
            "terminal_namespace": self.lookup_key,
            "terminal_group": True,
            "owner_class": "terminal_group",
            "terminal_type": "group",
            "members": [member.to_dict() for member in self.members],
            "member_terminal_ids": [member.terminal_id for member in self.members],
            "mesh_routes": [member.mesh_route.to_dict() for member in self.members if member.routable],
        }


class TerminalDirectory:
    """Lookup index for terminal profiles and compatibility aliases."""

    def __init__(self, profiles: Iterable[PersonalTerminalProfile]) -> None:
        self.profiles: Dict[str, PersonalTerminalProfile] = {profile.terminal_id: profile for profile in profiles}
        self.alias_index: Dict[str, List[str]] = {}
        for profile in self.profiles.values():
            for value in profile.lookup_values():
                key = normalize_lookup(value)
                if not key:
                    continue
                self.alias_index.setdefault(key, [])
                if profile.terminal_id not in self.alias_index[key]:
                    self.alias_index[key].append(profile.terminal_id)

    def list_profiles(self) -> List[PersonalTerminalProfile]:
        return sorted(self.profiles.values(), key=lambda profile: (profile.owner_class, profile.owner_display_name))

    def resolve(self, value: str) -> List[PersonalTerminalProfile]:
        if is_personnel_attention_tag(value):
            raise ValueError("Personnel Attention Tags are not Personal Access Terminal routes")
        key = normalize_lookup(value)
        terminal_ids = self.alias_index.get(key, [])
        return [self.profiles[terminal_id] for terminal_id in terminal_ids]

    def resolve_presented(self, value: str) -> Dict[str, Any]:
        matches = self.resolve(value)
        if not matches:
            raise ValueError(f"Unknown terminal '{value}'")
        if len(matches) == 1:
            return matches[0].to_dict()
        return TerminalGroup(lookup_key=value, members=matches).to_dict()


def load_terminal_directory(registry_dir: Path, manifests: Dict[str, AgentManifest]) -> TerminalDirectory:
    """Load L1 terminal profiles and apply optional PAT overlay metadata."""

    registry_path = registry_dir / "l1_terminal_registry.v1.json"
    if not registry_path.exists():
        return TerminalDirectory([])

    payload = json.loads(registry_path.read_text())
    profiles = [PersonalTerminalProfile.from_dict(item) for item in payload.get("profiles", [])]
    by_agent_id = {profile.owner_agent_id: profile for profile in profiles if profile.owner_agent_id}

    for profile in profiles:
        if profile.owner_agent_id and profile.owner_agent_id in manifests:
            manifest = manifests[profile.owner_agent_id]
            if not profile.owner_display_name:
                profile.owner_display_name = manifest.display_name
            if not profile.mesh_route.owner_agent_id:
                profile.mesh_route.owner_agent_id = manifest.id
            if not profile.mesh_route.channel_id:
                profile.mesh_route.channel_id = manifest.default_channel
            profile.aliases.extend(alias for alias in manifest.aliases if alias not in profile.aliases)
        elif profile.mesh_route.routable:
            profile.mesh_route.routable = False

    overlay_path = registry_dir / "pat_live_subset.v1.json"
    if overlay_path.exists():
        overlay_payload = json.loads(overlay_path.read_text())
        for item in overlay_payload.get("overlays", []):
            owner_agent_id = item.get("owner_agent_id")
            profile = by_agent_id.get(owner_agent_id)
            if profile:
                profile.pat_overlay = PatOverlay.from_dict(item)

    return TerminalDirectory(profiles)
