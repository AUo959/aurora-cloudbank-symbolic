"""Canonical mesh runtime for the Aurora collaboration chamber."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

try:
    from fastapi import WebSocket
except ImportError:  # pragma: no cover - runtime still works without FastAPI installed
    WebSocket = Any  # type: ignore[misc,assignment]

from .live_agents import LiveAdapterUnavailable, OpenAILiveAdapter
from .manifests import build_alias_index, ensure_seed_memory_files, load_manifests, normalize_lookup
from .models import AgentManifest, MeshEvent, MeshMessageRequest


ORION_CORE = {
    "anchor_seed": "EOS_SEED_ORION",
    "ethics_protocol": "Picard_Delta_3",
    "halo_module": "HALO_CONTINUITY_GRAFT_005",
    "version": "v3.5.1_macroready",
}


class MeshStore:
    """SQLite-backed persistence for mesh messages and events."""

    def __init__(self, db_path: Path, transcript_dir: Path) -> None:
        self.db_path = db_path
        self.transcript_dir = transcript_dir
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._connection = sqlite3.connect(str(db_path), check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with self._lock:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS agent_state (
                    agent_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    execution_mode TEXT NOT NULL,
                    manifest_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ready',
                    activated_at TEXT,
                    last_heartbeat TEXT
                );

                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    sender_name TEXT NOT NULL,
                    target_agent_id TEXT,
                    channel_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    agent_id TEXT,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_events_channel_id ON events(channel_id, event_id);
                CREATE INDEX IF NOT EXISTS idx_events_message_id ON events(message_id, event_id);
                """
            )
            self._connection.commit()

    def upsert_manifest(self, manifest: AgentManifest) -> None:
        with self._lock:
            current = self._connection.execute(
                "SELECT status, activated_at, last_heartbeat FROM agent_state WHERE agent_id = ?",
                (manifest.id,),
            ).fetchone()
            status = current["status"] if current else "ready"
            activated_at = current["activated_at"] if current else None
            last_heartbeat = current["last_heartbeat"] if current else None
            self._connection.execute(
                """
                INSERT INTO agent_state (
                    agent_id, display_name, execution_mode, manifest_json, status, activated_at, last_heartbeat
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(agent_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    execution_mode = excluded.execution_mode,
                    manifest_json = excluded.manifest_json,
                    status = excluded.status,
                    activated_at = COALESCE(agent_state.activated_at, excluded.activated_at),
                    last_heartbeat = COALESCE(agent_state.last_heartbeat, excluded.last_heartbeat)
                """,
                (
                    manifest.id,
                    manifest.display_name,
                    manifest.execution_mode,
                    manifest.to_json(),
                    status,
                    activated_at,
                    last_heartbeat,
                ),
            )
            self._connection.commit()

    def set_agent_status(self, agent_id: str, status: str) -> Dict[str, Any]:
        now = utcnow()
        activated_at = now if status == "active" else None
        with self._lock:
            self._connection.execute(
                """
                UPDATE agent_state
                SET status = ?, activated_at = COALESCE(activated_at, ?), last_heartbeat = ?
                WHERE agent_id = ?
                """,
                (status, activated_at, now, agent_id),
            )
            self._connection.commit()
            row = self._connection.execute(
                "SELECT * FROM agent_state WHERE agent_id = ?",
                (agent_id,),
            ).fetchone()
        return dict(row) if row else {}

    def heartbeat(self, agent_id: str) -> Dict[str, Any]:
        now = utcnow()
        with self._lock:
            self._connection.execute(
                "UPDATE agent_state SET last_heartbeat = ?, status = CASE WHEN status = 'disconnected' THEN 'ready' ELSE status END WHERE agent_id = ?",
                (now, agent_id),
            )
            self._connection.commit()
            row = self._connection.execute(
                "SELECT * FROM agent_state WHERE agent_id = ?",
                (agent_id,),
            ).fetchone()
        return dict(row) if row else {}

    def disconnect(self, agent_id: str) -> Dict[str, Any]:
        now = utcnow()
        with self._lock:
            self._connection.execute(
                "UPDATE agent_state SET status = 'disconnected', last_heartbeat = ? WHERE agent_id = ?",
                (now, agent_id),
            )
            self._connection.commit()
            row = self._connection.execute(
                "SELECT * FROM agent_state WHERE agent_id = ?",
                (agent_id,),
            ).fetchone()
        return dict(row) if row else {}

    def list_agent_rows(self) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute("SELECT * FROM agent_state ORDER BY display_name").fetchall()
        return [dict(row) for row in rows]

    def get_agent_row(self, agent_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM agent_state WHERE agent_id = ?",
                (agent_id,),
            ).fetchone()
        return dict(row) if row else None

    def create_message(
        self,
        message_id: str,
        sender_id: str,
        sender_name: str,
        target_agent_id: Optional[str],
        channel_id: str,
        content: str,
        message_type: str,
    ) -> None:
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO messages (
                    message_id, sender_id, sender_name, target_agent_id, channel_id, content, message_type, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (message_id, sender_id, sender_name, target_agent_id, channel_id, content, message_type, utcnow()),
            )
            self._connection.commit()

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._connection.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,)).fetchone()
        return dict(row) if row else None

    def append_event(
        self,
        event_type: str,
        message_id: str,
        channel_id: str,
        agent_id: Optional[str],
        payload: Dict[str, Any],
    ) -> MeshEvent:
        timestamp = utcnow()
        payload_json = json.dumps(payload, sort_keys=True)
        with self._lock:
            cursor = self._connection.execute(
                """
                INSERT INTO events (message_id, channel_id, agent_id, event_type, timestamp, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (message_id, channel_id, agent_id, event_type, timestamp, payload_json),
            )
            self._connection.commit()
            event_id = int(cursor.lastrowid)

        envelope = MeshEvent(
            event_id=event_id,
            event_type=event_type,
            message_id=message_id,
            channel_id=channel_id,
            agent_id=agent_id,
            timestamp=timestamp,
            payload=payload,
        )
        self._append_transcript(channel_id, envelope)
        if event_type == "trace_update":
            self._append_trace(envelope)
        return envelope

    def get_events_after(self, after: int = 0, limit: int = 100) -> Dict[str, Any]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT event_id, message_id, channel_id, agent_id, event_type, timestamp, payload_json
                FROM events
                WHERE event_id > ?
                ORDER BY event_id ASC
                LIMIT ?
                """,
                (after, limit),
            ).fetchall()
        events = [self._row_to_event(row) for row in rows]
        next_cursor = events[-1].event_id if events else after
        return {"events": [event.to_dict() for event in events], "next_cursor": next_cursor}

    def get_channel_history(self, channel_id: str, limit: int = 100) -> Dict[str, Any]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT event_id, message_id, channel_id, agent_id, event_type, timestamp, payload_json
                FROM events
                WHERE channel_id = ?
                ORDER BY event_id DESC
                LIMIT ?
                """,
                (channel_id, limit),
            ).fetchall()
        events = [self._row_to_event(row) for row in reversed(rows)]
        next_cursor = events[-1].event_id if events else 0
        return {"events": [event.to_dict() for event in events], "next_cursor": next_cursor}

    def get_recent_events(self, channel_id: str, limit: int = 12) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT event_id, message_id, channel_id, agent_id, event_type, timestamp, payload_json
                FROM events
                WHERE channel_id = ?
                ORDER BY event_id DESC
                LIMIT ?
                """,
                (channel_id, limit),
            ).fetchall()
        return [self._row_to_event(row).to_dict() for row in reversed(rows)]

    def last_event_id(self) -> int:
        with self._lock:
            row = self._connection.execute("SELECT MAX(event_id) AS event_id FROM events").fetchone()
        return int(row["event_id"] or 0)

    def _row_to_event(self, row: sqlite3.Row) -> MeshEvent:
        payload = json.loads(row["payload_json"]) if row["payload_json"] else {}
        return MeshEvent(
            event_id=int(row["event_id"]),
            event_type=row["event_type"],
            message_id=row["message_id"],
            channel_id=row["channel_id"],
            agent_id=row["agent_id"],
            timestamp=row["timestamp"],
            payload=payload,
        )

    def _append_transcript(self, channel_id: str, event: MeshEvent) -> None:
        path = self.transcript_dir / f"{slugify(channel_id)}.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(event.to_json() + "\n")

    def _append_trace(self, event: MeshEvent) -> None:
        path = self.transcript_dir / "trace.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(event.to_json() + "\n")


class WebSocketHub:
    """Very small same-process broadcast hub for mesh events."""

    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._lock = threading.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            recipients = list(self._connections)
        stale: List[WebSocket] = []
        for websocket in recipients:
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)
        if stale:
            with self._lock:
                for websocket in stale:
                    self._connections.discard(websocket)


class MeshRuntime:
    """Single authoritative runtime for routed mesh messages."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.runtime_root = self.project_root / "runtime" / "mesh"
        self.manifest_dir = self.project_root / "config" / "mesh" / "agents"
        self.memory_dir = self.project_root / "config" / "mesh" / "memory"
        ensure_seed_memory_files(self.memory_dir)
        self.store = MeshStore(self.runtime_root / "mesh.db", self.runtime_root / "transcripts")
        self.websocket_hub = WebSocketHub()
        self.live_adapter = OpenAILiveAdapter()
        self.manifests: Dict[str, AgentManifest] = {}
        self.alias_index: Dict[str, str] = {}
        self.reload_manifests()

    def reload_manifests(self) -> None:
        self.manifests = load_manifests(self.manifest_dir)
        self.alias_index = build_alias_index(self.manifests.values())
        for manifest in self.manifests.values():
            self.store.upsert_manifest(manifest)

    def list_agents(self) -> List[Dict[str, Any]]:
        agent_rows = {row["agent_id"]: row for row in self.store.list_agent_rows()}
        records: List[Dict[str, Any]] = []
        for manifest in self.manifests.values():
            row = agent_rows.get(manifest.id, {})
            records.append(self._present_agent(manifest, row))
        return records

    def get_agent(self, agent_id_or_alias: str) -> Dict[str, Any]:
        manifest = self._resolve_manifest(agent_id_or_alias)
        row = self.store.get_agent_row(manifest.id) or {}
        return self._present_agent(manifest, row)

    def activate_agent(self, agent_id_or_alias: str) -> Dict[str, Any]:
        manifest = self._resolve_manifest(agent_id_or_alias)
        row = self.store.set_agent_status(manifest.id, "active")
        return self._present_agent(manifest, row)

    def disconnect_agent(self, agent_id_or_alias: str) -> Dict[str, Any]:
        manifest = self._resolve_manifest(agent_id_or_alias)
        row = self.store.disconnect(manifest.id)
        return self._present_agent(manifest, row)

    def heartbeat(self, agent_id_or_alias: str) -> Dict[str, Any]:
        manifest = self._resolve_manifest(agent_id_or_alias)
        row = self.store.heartbeat(manifest.id)
        return self._present_agent(manifest, row)

    def get_status(self) -> Dict[str, Any]:
        agents = self.list_agents()
        active_agents = [agent for agent in agents if agent["status"] == "active"]
        channels = sorted({channel for manifest in self.manifests.values() for channel in manifest.channels})
        return {
            "mesh_status": "operational",
            "version": ORION_CORE["version"],
            "event_cursor": self.store.last_event_id(),
            "total_agents": len(agents),
            "active_agents": len(active_agents),
            "agents": agents,
            "channels": channels,
            "orion_core": ORION_CORE,
            "live_adapter": {
                "provider": "openai",
                "available": self.live_adapter.available(),
            },
        }

    def get_events_after(self, after: int = 0, limit: int = 100) -> Dict[str, Any]:
        return self.store.get_events_after(after=after, limit=limit)

    def get_channel_history(self, channel_id: str, limit: int = 100) -> Dict[str, Any]:
        return self.store.get_channel_history(channel_id=channel_id, limit=limit)

    async def send_message(self, request: MeshMessageRequest) -> Dict[str, Any]:
        target_agents = self._resolve_targets(request)
        channel_id = self._resolve_channel(request, target_agents)
        message_id = uuid.uuid4().hex
        target_agent_id = target_agents[0].id if len(target_agents) == 1 else None

        self.store.create_message(
            message_id=message_id,
            sender_id=request.sender_id,
            sender_name=request.sender_name,
            target_agent_id=target_agent_id,
            channel_id=channel_id,
            content=request.content,
            message_type=request.type,
        )

        accepted_event = await self._record_event(
            "message_accepted",
            message_id=message_id,
            channel_id=channel_id,
            agent_id=None,
            payload={
                "content": request.content,
                "sender_id": request.sender_id,
                "sender_name": request.sender_name,
                "targets": [agent.id for agent in target_agents],
                "message_type": request.type,
            },
        )
        await self._record_event(
            "trace_update",
            message_id=message_id,
            channel_id=channel_id,
            agent_id=None,
            payload={
                "phase": "message_routed",
                "detail": f"Resolved targets: {', '.join(agent.display_name for agent in target_agents)}",
            },
        )

        for manifest in target_agents:
            self._spawn_target(message_id, channel_id, request, manifest)

        return {
            "success": True,
            "status": "accepted",
            "message_id": message_id,
            "channel_id": channel_id,
            "targets": [agent.id for agent in target_agents],
            "event_id": accepted_event.event_id,
        }

    def _spawn_target(
        self,
        message_id: str,
        channel_id: str,
        request: MeshMessageRequest,
        manifest: AgentManifest,
    ) -> None:
        """Run target processing outside the request event loop."""

        def runner() -> None:
            asyncio.run(self._process_target(message_id, channel_id, request, manifest))

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

    async def inject_agent_message(
        self,
        agent_id_or_alias: str,
        target: str,
        content: str,
        message_type: str = "direct",
    ) -> Dict[str, Any]:
        manifest = self._resolve_manifest(agent_id_or_alias)
        self.heartbeat(manifest.id)
        channel_id = manifest.default_channel if target in {"Aurora", "Pilot", "pilot", "Captain", "captain"} else target
        message_id = uuid.uuid4().hex
        self.store.create_message(
            message_id=message_id,
            sender_id=manifest.id,
            sender_name=manifest.display_name,
            target_agent_id=None,
            channel_id=channel_id,
            content=content,
            message_type=message_type,
        )
        event = await self._record_event(
            "message_accepted",
            message_id=message_id,
            channel_id=channel_id,
            agent_id=manifest.id,
            payload={
                "content": content,
                "sender_id": manifest.id,
                "sender_name": manifest.display_name,
                "targets": [target],
                "message_type": message_type,
            },
        )
        return {
            "success": True,
            "message_id": message_id,
            "channel_id": channel_id,
            "relay_status": "accepted",
            "event_id": event.event_id,
        }

    async def _process_target(
        self,
        message_id: str,
        channel_id: str,
        request: MeshMessageRequest,
        manifest: AgentManifest,
    ) -> None:
        try:
            self.activate_agent(manifest.id)
            await self._record_event(
                "agent_ack",
                message_id=message_id,
                channel_id=channel_id,
                agent_id=manifest.id,
                payload={"agent_name": manifest.display_name, "execution_mode": manifest.execution_mode},
            )
            await asyncio.sleep(max(manifest.typing_profile.delay_ms, 50) / 1000.0)
            await self._record_event(
                "agent_typing",
                message_id=message_id,
                channel_id=channel_id,
                agent_id=manifest.id,
                payload={"agent_name": manifest.display_name, "delay_ms": manifest.typing_profile.delay_ms},
            )

            reply_text, mode, trace_detail = await self._generate_reply(manifest, request.content, channel_id)
            await self._record_event(
                "trace_update",
                message_id=message_id,
                channel_id=channel_id,
                agent_id=manifest.id,
                payload={"phase": "reply_ready", "mode": mode, "detail": trace_detail},
            )
            await self._record_event(
                "agent_reply",
                message_id=message_id,
                channel_id=channel_id,
                agent_id=manifest.id,
                payload={"content": reply_text, "agent_name": manifest.display_name, "mode": mode},
            )
        except Exception as exc:
            await self._record_event(
                "delivery_error",
                message_id=message_id,
                channel_id=channel_id,
                agent_id=manifest.id,
                payload={"error": str(exc), "agent_name": manifest.display_name},
            )

    async def _generate_reply(self, manifest: AgentManifest, content: str, channel_id: str) -> Sequence[str]:
        memory_text = self._read_memory(manifest)
        recent_events = self.store.get_recent_events(channel_id, limit=12)

        if manifest.execution_mode == "live_llm":
            try:
                reply = await self.live_adapter.generate_reply(manifest, content, memory_text, recent_events)
                return reply, "live_llm", "OpenAI live adapter completed successfully"
            except LiveAdapterUnavailable as exc:
                if not manifest.response_policy.fallback_to_deterministic:
                    raise
                fallback = self._deterministic_reply(manifest, content, memory_text)
                return fallback, "deterministic_fallback", f"Live adapter unavailable: {exc}"

        return self._deterministic_reply(manifest, content, memory_text), "deterministic", "Deterministic responder"

    def _deterministic_reply(self, manifest: AgentManifest, content: str, memory_text: str) -> str:
        style = manifest.response_policy.style
        content_excerpt = content.strip().replace("\n", " ")
        if len(content_excerpt) > 180:
            content_excerpt = content_excerpt[:177] + "..."
        memory_excerpt = ""
        if memory_text:
            first_line = next((line.strip() for line in memory_text.splitlines() if line.strip()), "")
            if first_line:
                memory_excerpt = f" Memory anchor: {first_line}."

        templates = {
            "strategic": (
                f"{manifest.display_name}: I'm treating this as a coordination item tied to {content_excerpt}. "
                "Immediate next step is to frame the decision, identify the blocking dependency, and keep the line tight."
            ),
            "analytical": (
                f"{manifest.display_name}: Structurally, {content_excerpt} touches architecture and interface boundaries. "
                "I'd isolate the contract first, then tighten the implementation path."
            ),
            "performance": (
                f"{manifest.display_name}: For {content_excerpt}, I'd check the latency path, the redundant work, and the handoff cost before changing anything."
            ),
            "adaptive": (
                f"{manifest.display_name}: I'm reading {content_excerpt} as a pattern-change request. "
                "Best move is to preserve the current loop, then adapt the rule set around it."
            ),
            "communications": (
                f"{manifest.display_name}: {content_excerpt} needs a cleaner routing contract and a clearer delivery signal so the workspace stays coherent."
            ),
            "continuity": (
                f"{manifest.display_name}: I'd anchor {content_excerpt} to the current thread state first, then update the channel without introducing drift."
            ),
            "general": f"{manifest.display_name}: I've logged {content_excerpt} and I'm responding from the shared mesh context.",
        }
        body = templates.get(style, templates["general"])
        return body + memory_excerpt + " [drift 0.0]"

    async def _record_event(
        self,
        event_type: str,
        message_id: str,
        channel_id: str,
        agent_id: Optional[str],
        payload: Dict[str, Any],
    ) -> MeshEvent:
        event = self.store.append_event(
            event_type=event_type,
            message_id=message_id,
            channel_id=channel_id,
            agent_id=agent_id,
            payload=payload,
        )
        await self.websocket_hub.broadcast(event.to_dict())
        return event

    def _read_memory(self, manifest: AgentManifest) -> str:
        parts: List[str] = []
        for relative_path in manifest.memory_files:
            candidate = (self.project_root / relative_path).resolve()
            if candidate.exists():
                parts.append(candidate.read_text())
        return "\n\n".join(parts).strip()

    def _resolve_targets(self, request: MeshMessageRequest) -> List[AgentManifest]:
        if request.to:
            return [self._resolve_manifest(request.to)]

        if request.channel:
            channel_id = request.channel
            if request.type == "broadcast" or channel_id.startswith("#"):
                targets = [manifest for manifest in self.manifests.values() if channel_id in manifest.channels]
                if targets:
                    return targets
            direct_targets = [manifest for manifest in self.manifests.values() if channel_id == manifest.default_channel]
            if direct_targets:
                return direct_targets
        raise ValueError("Mesh messages require either a target agent or a routable channel")

    def _resolve_channel(self, request: MeshMessageRequest, targets: Iterable[AgentManifest]) -> str:
        if request.channel:
            return request.channel
        first_target = next(iter(targets))
        return first_target.default_channel

    def _resolve_manifest(self, agent_id_or_alias: str) -> AgentManifest:
        direct = self.manifests.get(agent_id_or_alias)
        if direct:
            return direct
        normalized = normalize_lookup(agent_id_or_alias)
        mapped_id = self.alias_index.get(normalized)
        if mapped_id and mapped_id in self.manifests:
            return self.manifests[mapped_id]
        raise ValueError(f"Unknown agent '{agent_id_or_alias}'")

    def _present_agent(self, manifest: AgentManifest, row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        row = row or {}
        return {
            "agent_id": manifest.id,
            "display_name": manifest.display_name,
            "aliases": manifest.aliases,
            "channels": manifest.channels,
            "default_channel": manifest.default_channel,
            "execution_mode": manifest.execution_mode,
            "status": row.get("status", "ready"),
            "activated_at": row.get("activated_at"),
            "last_heartbeat": row.get("last_heartbeat"),
            "response_policy": manifest.response_policy.to_dict(),
            "typing_profile": manifest.typing_profile.to_dict(),
            "model_profile": manifest.model_profile,
            "memory_files": manifest.memory_files,
        }


def slugify(value: str) -> str:
    """Convert a channel id to a safe transcript filename."""

    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.lower())
    return cleaned.strip("_") or "channel"


def utcnow() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()
