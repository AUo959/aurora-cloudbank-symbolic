"""Mission runtime orchestration for the Aurora MCP Shuttle Bay."""

from __future__ import annotations

import json
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration
from src.integrations.shuttle_bay_runtime.assignment import build_assignment_metadata
from src.integrations.shuttle_bay_runtime.catalog import REPO_ROOT, load_catalog_bundle
from src.integrations.shuttle_bay_runtime.inspection import run_postflight_inspection, run_preflight_inspection
from src.integrations.shuttle_bay_runtime.models import MissionRecord, PersistenceMode, PolicyDecision, RoutingAssignment, TrustLane
from src.integrations.shuttle_bay_runtime.policy import evaluate_policy_decision
from src.integrations.shuttle_bay_runtime.resources import (
    list_resource_definitions,
    read_resource_payload,
    resource_uris,
)
from src.integrations.shuttle_bay_runtime.routing import resolve_routing_assignment


class ShuttleBayMissionController:
    """Deterministic mission mediation layer around the agent runtime."""

    def __init__(self, agent_integration: ChatGPTAgentModeIntegration):
        self.agent_integration = agent_integration
        self.catalog = load_catalog_bundle()
        self.journal_path = REPO_ROOT / "data" / "shuttle_bay" / "mission_journal.jsonl"
        self.memory_journal = deque(maxlen=250)
        self.persistence_mode = PersistenceMode.DISK
        self.metrics = {
            "total": 0,
            "executed": 0,
            "denied": 0,
            "failed": 0,
            "review_flagged": 0,
        }
        self.active_missions = 0
        self._lock = Lock()

    def _mission_id(self) -> str:
        return f"MSN-{uuid.uuid4().hex[:12].upper()}"

    def _audit_tag(self, tool_name: str, mission_id: str) -> str:
        return f"MCP::{tool_name}::{mission_id}"

    def _pipeline_ready(self) -> bool:
        return self.catalog.critical_sources_ready()

    def _mission_pipeline_manifest(self) -> Dict[str, Any]:
        return {
            "enabled": True,
            "policy_mode": self.catalog.policy_matrix.get("policy_mode", "policy_first"),
            "assignment_mode": "symbolic_role_first",
            "trust_lanes": [lane.value for lane in TrustLane],
            "resource_uris": resource_uris(),
            "journal_path": "data/shuttle_bay/mission_journal.jsonl",
        }

    def build_manifest(self, tools_info: Dict[str, Any]) -> Dict[str, Any]:
        bridge_core = self.catalog.bridge_core
        return {
            "shuttle_bay": {
                "id": "aurora-mcp-shuttle-bay",
                "version": bridge_core.get("version", "1.0.0"),
                "transport": "http_json_adapter",
                "recommended_routes": {
                    "manifest": "/mcp/shuttle-bay",
                    "tools": "/mcp/shuttle-bay/tools",
                    "execute": "/mcp/shuttle-bay/execute",
                    "session": "/mcp/shuttle-bay/session",
                    "status": "/mcp/shuttle-bay/status",
                },
                "legacy_routes": {
                    "bridge_metadata": "/mcp_bridge",
                    "command_router": "/mcp_bridge/route_command",
                },
            },
            "bridge_core": {
                "module_id": bridge_core.get("module_id"),
                "anchor_seed": bridge_core.get("anchor_seed"),
                "ethics_protocol": bridge_core.get("ethics_protocol"),
                "governance_layer": bridge_core.get("governance_layer"),
                "security_layers": bridge_core.get("security_layers", {}),
                "core_functions": bridge_core.get("core_functions", []),
            },
            "agent_mode": {
                "mode": self.agent_integration.config.get("mode", "chatgpt_agent_mode"),
                "api_schema_version": tools_info.get("api_schema_version", "2024.1"),
                "capabilities": tools_info.get("capabilities", []),
            },
            "security": {
                "network_scope": "loopback_by_default",
                "remote_access_token_env": "AURORA_AGENT_CONTROL_TOKEN",
                "legacy_anchor_required": bridge_core.get("anchor_seed"),
            },
            "mission_pipeline": self._mission_pipeline_manifest(),
            "resources": resource_uris(),
            "tools": tools_info.get("tools", {}),
            "context_tag": "mcp_shuttle_bay_manifest",
        }

    def list_resources(self) -> Dict[str, Any]:
        return list_resource_definitions()

    def read_resource(self, uri: str, tools_info: Dict[str, Any]) -> Dict[str, Any]:
        manifest = self.build_manifest(tools_info)
        payload = read_resource_payload(uri, self.catalog, manifest)
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(payload, default=str),
                }
            ]
        }

    def _augment_status(self, base_status: Dict[str, Any]) -> Dict[str, Any]:
        base_status["bridge_core"] = {
            "module_id": self.catalog.bridge_core.get("module_id"),
            "governance_layer": self.catalog.bridge_core.get("governance_layer"),
        }
        base_status["pipeline_readiness"] = {
            "ready": self._pipeline_ready(),
            "policy_mode": self.catalog.policy_matrix.get("policy_mode", "policy_first"),
            "assignment_mode": "symbolic_role_first",
            "trust_lanes": [lane.value for lane in TrustLane],
            "resource_count": len(resource_uris()),
        }
        base_status["loaded_sources"] = self.catalog.source_status
        base_status["mission_counters"] = dict(self.metrics, active=self.active_missions)
        base_status["degraded_modes"] = {
            "persistence_mode": self.persistence_mode.value,
            "persistence_degraded": self.persistence_mode == PersistenceMode.MEMORY,
            "staff_registry_role_only": not self.catalog.source_status.get("staff_registry", {}).get("loaded", False)
            or not self.catalog.staff_registry.get("crew_registry", {}).get("human_staff", {}),
        }
        base_status["context_tag"] = "mcp_shuttle_bay_status"
        return base_status

    async def get_status(self) -> Dict[str, Any]:
        return self._augment_status(await self.agent_integration.get_agent_status())

    async def _persist_mission(self, mission: MissionRecord) -> None:
        try:
            self.journal_path.parent.mkdir(parents=True, exist_ok=True)
            mission.persistence_mode = PersistenceMode.DISK.value
            with self.journal_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(mission.to_dict(), default=str) + "\n")
            self.persistence_mode = PersistenceMode.DISK
        except Exception:
            mission.persistence_mode = PersistenceMode.MEMORY.value
            self.memory_journal.append(mission.to_dict())
            self.persistence_mode = PersistenceMode.MEMORY

    def _build_denied_response(
        self,
        tool_name: str,
        session_id: Optional[str],
        policy: PolicyDecision,
        routing: RoutingAssignment,
        assignment: Dict[str, Any],
        preflight: Dict[str, Any],
        error: str,
    ) -> Dict[str, Any]:
        postflight = {
            "ok": False,
            "stage": "postflight",
            "checks": [],
            "issues": [error],
            "degraded": [],
            "summary": "Execution blocked before tool invocation.",
        }
        mission = MissionRecord(
            mission_id=self._mission_id(),
            tool_name=tool_name,
            session_id=session_id,
            lane=TrustLane.RED.value,
            tool_domain=policy.tool_domain,
            risk_score=policy.risk_score,
            policy_action="deny",
            review_required=False,
            authority_role=assignment.get("authority_role", routing.authority_role),
            authority_name=assignment.get("authority_name"),
            relay_agent=assignment.get("relay_agent", routing.relay_agent),
            shuttle_id=assignment.get("shuttle_id", routing.shuttle_id),
            oversight_glyphs=list(routing.oversight_glyphs),
            preflight=preflight,
            postflight=postflight,
            audit_tag=self._audit_tag(tool_name, self._mission_id()),
            status="denied",
            execution_success=False,
            persistence_mode=self.persistence_mode.value,
            created_at=datetime.utcnow().isoformat(),
        )
        return {"success": False, "error": error, "mission": mission.mission_envelope(), "dlp_level": "DLP_L1_OK"}

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        tools_registry = self.agent_integration.tools_registry
        mission_id = self._mission_id()

        try:
            routing = resolve_routing_assignment(tool_name, self.catalog)
            policy = evaluate_policy_decision(
                tool_name=tool_name,
                tool_domain=routing.tool_domain,
                lane_hint=routing.lane_hint,
                catalog=self.catalog,
                tool_schema_present=tool_name in tools_registry and bool(tools_registry.get(tool_name, {}).get("parameters")),
            )
        except ValueError as exc:
            policy = PolicyDecision(
                tool_name=tool_name,
                tool_domain="unknown",
                lane=TrustLane.RED,
                risk_score=1.0,
                policy_action="deny",
                review_required=False,
                deny_reasons=[str(exc)],
            )
            routing = RoutingAssignment(
                tool_name=tool_name,
                tool_domain="unknown",
                shuttle_id="",
                relay_agent="",
                authority_role="",
                authority_key="",
                clearance_required="",
            )

        assignment = build_assignment_metadata(routing, self.catalog)

        with self._lock:
            active_snapshot = self.active_missions

        preflight = run_preflight_inspection(
            tool_name=tool_name,
            policy=policy,
            routing=routing,
            catalog=self.catalog,
            tools_registry=tools_registry,
            active_missions=active_snapshot,
        )
        preflight_payload = preflight.to_dict()

        if not preflight.ok or policy.lane == TrustLane.RED:
            error = preflight.summary or "; ".join(policy.deny_reasons) or "Shuttle Bay denied the tool call."
            postflight_payload = {
                "ok": False,
                "stage": "postflight",
                "checks": [],
                "issues": [error],
                "degraded": [],
                "summary": "Execution blocked before tool invocation.",
            }
            mission = MissionRecord(
                mission_id=mission_id,
                tool_name=tool_name,
                session_id=session_id,
                lane=TrustLane.RED.value,
                tool_domain=policy.tool_domain,
                risk_score=policy.risk_score,
                policy_action="deny",
                review_required=False,
                authority_role=assignment.get("authority_role", routing.authority_role),
                authority_name=assignment.get("authority_name"),
                relay_agent=assignment.get("relay_agent", routing.relay_agent),
                shuttle_id=assignment.get("shuttle_id", routing.shuttle_id),
                oversight_glyphs=list(routing.oversight_glyphs),
                preflight=preflight_payload,
                postflight=postflight_payload,
                audit_tag=self._audit_tag(tool_name, mission_id),
                status="denied",
                execution_success=False,
                persistence_mode=self.persistence_mode.value,
                created_at=datetime.utcnow().isoformat(),
            )
            self.metrics["total"] += 1
            self.metrics["denied"] += 1
            await self._persist_mission(mission)
            return {"success": False, "error": error, "mission": mission.mission_envelope(), "dlp_level": "DLP_L1_OK"}

        with self._lock:
            if self.active_missions >= int(
                self.catalog.l1_config.get("l1_command_node", {}).get("fleet_control", {}).get("max_concurrent_missions", 8)
                or 8
            ):
                capacity_error = "Mission capacity exceeded at dispatch time."
                self.metrics["total"] += 1
                self.metrics["denied"] += 1
                denied_postflight = {
                    "ok": False,
                    "stage": "postflight",
                    "checks": [],
                    "issues": [capacity_error],
                    "degraded": [],
                    "summary": "Execution blocked before tool invocation.",
                }
                mission = MissionRecord(
                    mission_id=mission_id,
                    tool_name=tool_name,
                    session_id=session_id,
                    lane=TrustLane.RED.value,
                    tool_domain=policy.tool_domain,
                    risk_score=policy.risk_score,
                    policy_action="deny",
                    review_required=False,
                    authority_role=assignment.get("authority_role", routing.authority_role),
                    authority_name=assignment.get("authority_name"),
                    relay_agent=assignment.get("relay_agent", routing.relay_agent),
                    shuttle_id=assignment.get("shuttle_id", routing.shuttle_id),
                    oversight_glyphs=list(routing.oversight_glyphs),
                    preflight=preflight_payload,
                    postflight=denied_postflight,
                    audit_tag=self._audit_tag(tool_name, mission_id),
                    status="denied",
                    execution_success=False,
                    persistence_mode=self.persistence_mode.value,
                    created_at=datetime.utcnow().isoformat(),
                )
                await self._persist_mission(mission)
                return {
                    "success": False,
                    "error": capacity_error,
                    "mission": mission.mission_envelope(),
                    "dlp_level": "DLP_L1_OK",
                }
            self.active_missions += 1

        try:
            result = await self.agent_integration.execute_tool(
                tool_name=tool_name,
                parameters=parameters,
                session_id=session_id,
            )
        finally:
            with self._lock:
                self.active_missions = max(self.active_missions - 1, 0)

        postflight = run_postflight_inspection(policy=policy, routing=routing, execution_result=result)
        postflight_payload = postflight.to_dict()

        mission = MissionRecord(
            mission_id=mission_id,
            tool_name=tool_name,
            session_id=session_id,
            lane=policy.lane.value,
            tool_domain=policy.tool_domain,
            risk_score=policy.risk_score,
            policy_action=policy.policy_action,
            review_required=policy.review_required,
            authority_role=assignment.get("authority_role", routing.authority_role),
            authority_name=assignment.get("authority_name"),
            relay_agent=assignment.get("relay_agent", routing.relay_agent),
            shuttle_id=assignment.get("shuttle_id", routing.shuttle_id),
            oversight_glyphs=list(routing.oversight_glyphs),
            preflight=preflight_payload,
            postflight=postflight_payload,
            audit_tag=self._audit_tag(tool_name, mission_id),
            status="completed" if result.get("success", False) else "failed",
            execution_success=bool(result.get("success", False)),
            persistence_mode=self.persistence_mode.value,
            created_at=datetime.utcnow().isoformat(),
        )

        self.metrics["total"] += 1
        if policy.review_required:
            self.metrics["review_flagged"] += 1
        if result.get("success", False):
            self.metrics["executed"] += 1
        else:
            self.metrics["failed"] += 1

        await self._persist_mission(mission)

        augmented = dict(result)
        augmented["mission"] = mission.mission_envelope()
        return augmented
