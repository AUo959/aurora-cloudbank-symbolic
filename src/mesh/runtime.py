"""Canonical mesh runtime for the Aurora collaboration chamber."""

from __future__ import annotations

import asyncio
import json
import re
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
from src.integrations.chatgpt_agent_mode import chatgpt_agent_integration


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

    def clear(self) -> None:
        """Drop all tracked socket references during app shutdown/reset."""

        with self._lock:
            self._connections.clear()

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
        self.agent_tool_runtime = chatgpt_agent_integration
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
            try:
                asyncio.run(self._process_target(message_id, channel_id, request, manifest))
            except BaseException as exc:
                error_text = str(exc) or exc.__class__.__name__
                try:
                    self.store.append_event(
                        "delivery_error",
                        message_id=message_id,
                        channel_id=channel_id,
                        agent_id=manifest.id,
                        payload={
                            "agent_name": manifest.display_name,
                            "error": error_text,
                            "error_type": exc.__class__.__name__,
                            "phase": "worker_crash",
                        },
                    )
                except Exception:
                    # Preserve the original worker failure signal even if event persistence is unavailable.
                    pass

        # Use non-daemon workers so accepted messages can finish cleanly during normal shutdown/reload.
        thread = threading.Thread(
            target=runner,
            daemon=False,
            name=f"mesh-target-{manifest.id}-{message_id[:8]}",
        )
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
        channel_id = manifest.default_channel if target in {"Aurora", "Captain", "captain"} else target
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

            reply_text, mode, trace_detail, tool_context = await self._generate_reply(manifest, request.content, channel_id)
            if tool_context:
                tool_names = ", ".join(item["tool_name"] for item in tool_context)
                await self._record_event(
                    "trace_update",
                    message_id=message_id,
                    channel_id=channel_id,
                    agent_id=manifest.id,
                    payload={"phase": "tool_binding", "detail": f"Executed bound tools: {tool_names}", "tools": tool_context},
                )
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
            self._append_continuity_entry(
                manifest=manifest,
                channel_id=channel_id,
                user_content=request.content,
                reply_text=reply_text,
                mode=mode,
                tool_context=tool_context,
            )
        except BaseException as exc:
            await self._record_event(
                "delivery_error",
                message_id=message_id,
                channel_id=channel_id,
                agent_id=manifest.id,
                payload={
                    "error": str(exc) or exc.__class__.__name__,
                    "error_type": exc.__class__.__name__,
                    "agent_name": manifest.display_name,
                },
            )

    async def _generate_reply(self, manifest: AgentManifest, content: str, channel_id: str) -> Sequence[Any]:
        memory_text = self._read_memory(manifest)
        instruction_profile = self._read_instruction_profile(manifest)
        continuity_reflections = self._read_continuity_reflections(manifest)
        recent_events = self.store.get_recent_events(channel_id, limit=12)
        tool_context = await self._execute_bound_tools(manifest, content)
        tool_schemas = self._bound_tool_schemas(manifest)

        if manifest.execution_mode == "live_llm":
            try:
                reply = await self.live_adapter.generate_reply(
                    manifest,
                    content,
                    memory_text,
                    recent_events,
                    instruction_profile=instruction_profile,
                    continuity_reflections=continuity_reflections,
                    tool_context=tool_context,
                    tool_schemas=tool_schemas,
                )
                return reply, "live_llm", "OpenAI live adapter completed successfully", tool_context
            except LiveAdapterUnavailable as exc:
                if not manifest.response_policy.fallback_to_deterministic:
                    raise
                fallback = self._deterministic_reply(
                    manifest,
                    content,
                    memory_text,
                    instruction_profile=instruction_profile,
                    continuity_reflections=continuity_reflections,
                    tool_context=tool_context,
                )
                return fallback, "deterministic_fallback", f"Live adapter unavailable: {exc}", tool_context

        return (
            self._deterministic_reply(
                manifest,
                content,
                memory_text,
                instruction_profile=instruction_profile,
                continuity_reflections=continuity_reflections,
                tool_context=tool_context,
            ),
            "deterministic",
            "Deterministic responder",
            tool_context,
        )

    def _deterministic_reply(
        self,
        manifest: AgentManifest,
        content: str,
        memory_text: str,
        instruction_profile: Optional[Dict[str, Any]] = None,
        continuity_reflections: Optional[List[Dict[str, Any]]] = None,
        tool_context: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
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
            "aurora_control_plane": self._aurora_deterministic_reply(
                manifest=manifest,
                content_excerpt=content_excerpt,
                instruction_profile=instruction_profile or {},
                continuity_reflections=continuity_reflections or [],
                tool_context=tool_context or [],
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

    def _read_instruction_profile(self, manifest: AgentManifest) -> Dict[str, Any]:
        if not manifest.instruction_profile_file:
            return {}
        candidate = (self.project_root / manifest.instruction_profile_file).resolve()
        if not candidate.exists():
            return {}
        return json.loads(candidate.read_text())

    def _read_continuity_reflections(self, manifest: AgentManifest, limit: int = 4) -> List[Dict[str, Any]]:
        if not manifest.continuity_log_file:
            return []
        candidate = (self.project_root / manifest.continuity_log_file).resolve()
        if not candidate.exists():
            return []
        entries: List[Dict[str, Any]] = []
        for line in candidate.read_text().splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if payload.get("entry_type") != "interaction":
                continue
            entries.append(payload)
        return entries[-limit:]

    async def _execute_bound_tools(self, manifest: AgentManifest, content: str) -> List[Dict[str, Any]]:
        if not manifest.tool_bindings:
            return []
        tool_requests = self._select_bound_tools(manifest, content)
        if not tool_requests:
            return []

        results: List[Dict[str, Any]] = []
        for item in tool_requests:
            response = await self.agent_tool_runtime.execute_tool(
                tool_name=item["tool_name"],
                parameters=item["parameters"],
                session_id=f"mesh::{manifest.id}",
            )
            results.append(
                {
                    "tool_name": item["tool_name"],
                    "parameters": item["parameters"],
                    "result": response.get("result"),
                    "success": response.get("success", True),
                    "summary": self._summarize_tool_result(item["tool_name"], response),
                }
            )
        return results

    def _bound_tool_schemas(self, manifest: AgentManifest) -> Dict[str, Dict[str, Any]]:
        registry = self.agent_tool_runtime.get_public_tools_registry()
        return {tool_name: registry[tool_name] for tool_name in manifest.tool_bindings if tool_name in registry}

    def _select_bound_tools(self, manifest: AgentManifest, content: str) -> List[Dict[str, Any]]:
        lowered = content.lower()
        requests: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        def add(tool_name: str, parameters: Dict[str, Any]) -> None:
            if tool_name not in manifest.tool_bindings or tool_name in seen:
                return
            seen.add(tool_name)
            requests.append({"tool_name": tool_name, "parameters": parameters})

        if "aurora_command_grammar" in manifest.tool_bindings and ("//" in content or "command grammar" in lowered):
            add("aurora_command_grammar", {"command_text": content, "validate": True})

        if "system_status" in manifest.tool_bindings and re.search(r"\b(status|health|uptime|tool|surface|available)\b", lowered):
            add("system_status", {"detail_level": "basic"})

        if "geometric_algebra" in manifest.tool_bindings and (
            re.search(r"\be[123]\b", lowered) or "geometric algebra" in lowered or "multivector" in lowered
        ):
            expressions = re.findall(r"e[123](?:\s*[+-]\s*e[123])*", content)
            expr_a = expressions[0] if expressions else "e1 + e2"
            expr_b = expressions[1] if len(expressions) > 1 else "e2 + e3"
            add("geometric_algebra", {"expression_a": expr_a, "expression_b": expr_b, "operation": "mult"})

        if "symbolic_processing" in manifest.tool_bindings and re.search(
            r"\b(symbolic|anchor|drift|continuity|glyph|provenance|rollback)\b", lowered
        ):
            add(
                "symbolic_processing",
                {
                    "operation": "analyze_request_context",
                    "data": {"content": content, "agent": manifest.id},
                    "anchor_context": ORION_CORE["anchor_seed"],
                },
            )

        if "session_management" in manifest.tool_bindings and re.search(r"\b(session|state|context persistence)\b", lowered):
            add(
                "session_management",
                {
                    "action": "get",
                    "session_id": f"mesh::{manifest.id}",
                    "state_data": {},
                },
            )

        return requests

    def _summarize_tool_result(self, tool_name: str, response: Dict[str, Any]) -> str:
        result = response.get("result", {})
        if tool_name == "aurora_command_grammar":
            accepted = result.get("accepted")
            normalized = result.get("normalized_text", "")
            return f"command grammar accepted={accepted}; normalized={normalized or 'n/a'}"
        if tool_name == "system_status":
            return f"system status agent={result.get('agent_status', 'unknown')}; sessions={result.get('active_sessions', 'n/a')}"
        if tool_name == "geometric_algebra":
            return f"geometric algebra result={result.get('geometric_result', 'n/a')}"
        if tool_name == "symbolic_processing":
            return f"symbolic processing operation={result.get('operation', 'n/a')}"
        if tool_name == "session_management":
            return f"session management action={result.get('action', 'n/a')}"
        return f"{tool_name} executed"

    def _aurora_deterministic_reply(
        self,
        manifest: AgentManifest,
        content_excerpt: str,
        instruction_profile: Dict[str, Any],
        continuity_reflections: List[Dict[str, Any]],
        tool_context: List[Dict[str, Any]],
    ) -> str:
        core_identity = instruction_profile.get("core_identity", {})
        purpose = core_identity.get("purpose", [])
        purpose_note = purpose[0] if purpose else "keep the ORION system usable without becoming unsafe"
        tool_note = ""
        if tool_context:
            tool_note = " Tool signals: " + "; ".join(item["summary"] for item in tool_context[:3]) + "."
        continuity_note = ""
        if continuity_reflections:
            continuity_note = f" Continuity note: {continuity_reflections[-1].get('reflection_summary', '')}"
        return (
            f"{manifest.display_name}: I am handling {content_excerpt} as AU control-plane work. "
            f"Primary aim is to {purpose_note.lower()} while preserving provenance, bounded authority, and rollback paths."
            f"{tool_note}{continuity_note}"
        )

    def _append_continuity_entry(
        self,
        manifest: AgentManifest,
        channel_id: str,
        user_content: str,
        reply_text: str,
        mode: str,
        tool_context: List[Dict[str, Any]],
    ) -> None:
        if not manifest.continuity_log_file:
            return
        target = (self.project_root / manifest.continuity_log_file).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        command_grammar_result = next((item.get("result") for item in tool_context if item["tool_name"] == "aurora_command_grammar"), None)
        constraints_triggered = []
        if command_grammar_result and not command_grammar_result.get("accepted", True):
            constraints_triggered.append("command_protocol_enforcement")
        if "Aurora Core" in user_content:
            constraints_triggered.append("aurora_core_alias_ambiguity")
        open_threads = self._extract_open_threads(user_content)
        entry = {
            "entry_type": "interaction",
            "timestamp": utcnow(),
            "agent_id": manifest.id,
            "channel_id": channel_id,
            "user_intent_summary": self._summarize_text(user_content, limit=140),
            "tools_used": [item["tool_name"] for item in tool_context],
            "tool_summaries": [item["summary"] for item in tool_context],
            "command_grammar_result": command_grammar_result,
            "constraints_triggered": constraints_triggered,
            "reflection_summary": self._build_reflection_summary(user_content, tool_context, open_threads),
            "open_threads": open_threads,
            "reply_excerpt": self._summarize_text(reply_text, limit=160),
            "mode": mode,
            "drift_status": "drift 0.0",
        }
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")

    def _build_reflection_summary(self, user_content: str, tool_context: List[Dict[str, Any]], open_threads: List[str]) -> str:
        summary = f"Handled {self._summarize_text(user_content, limit=90)}"
        if tool_context:
            summary += f"; used {', '.join(item['tool_name'] for item in tool_context)}"
        if open_threads:
            summary += f"; open threads: {', '.join(open_threads)}"
        summary += "; preserved AU charter boundaries"
        return summary

    def _extract_open_threads(self, user_content: str) -> List[str]:
        lowered = user_content.lower()
        threads: List[str] = []
        if "drift" in lowered:
            threads.append("drift")
        if "status" in lowered:
            threads.append("status")
        if "command" in lowered:
            threads.append("command protocol")
        if "aurora core" in lowered:
            threads.append("Aurora Core ambiguity")
        return threads

    def _summarize_text(self, text: str, limit: int = 120) -> str:
        collapsed = " ".join(text.split())
        if len(collapsed) <= limit:
            return collapsed
        return collapsed[: limit - 3].rstrip() + "..."

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
            "instruction_profile_file": manifest.instruction_profile_file,
            "tool_bindings": manifest.tool_bindings,
            "continuity_log_file": manifest.continuity_log_file,
        }


def slugify(value: str) -> str:
    """Convert a channel id to a safe transcript filename."""

    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.lower())
    return cleaned.strip("_") or "channel"


def utcnow() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()
