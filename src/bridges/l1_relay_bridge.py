#!/usr/bin/env python3
"""
L1 Relay Bridge (formerly "L2 Meta-Agent Bridge")
Aurora CloudBank v3.5.1_macroready

ARCHITECTURE CLARITY (docs/architecture/LAYER_ARCHITECTURE.md):
The relay agents (ARCHY, OPPY, LIORA, STARLING_AU, RIVERTHREAD_808)
physically exist in L1 — the Orion Station reality layer — and bridge L1
human operations with L3 glyph frameworks. They monitor and coordinate L2
simulations but do NOT manifest within them. In the Triplex Handshake
Protocol they serve as "Layer 2" verifiers (a middleware ROLE), which is
where the old, misleading "L2 Meta-Agent" name came from.

This module is the canonical, mesh-runtime-backed implementation (routed
through MeshRuntime since #751). The old import path
src/bridges/l2_meta_agent_bridge.py remains as a deprecation shim.

Bridge connector for L1 relay agents with full ZIPWIZ handshake protocol.
"""

import argparse
import asyncio
import json
import logging
import sys

# Configure logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.aurora.continuity import HALOPASController
from src.entities.relay_agents import get_halo
from src.mesh.models import MeshMessageRequest
from src.mesh.runtime import MeshRuntime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class L1RelayAgent:
    """L1 relay agent configuration and state.

    Physically L1-resident (Orion Station); plays the Layer 2 verifier
    role in the Triplex protocol. See module docstring.
    """

    agent_id: str
    role: str
    type: str
    status: str
    description: str
    capabilities: List[str]
    api_endpoint: str
    connected: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    drift_lock: Optional[float] = None
    handshake_log: Optional[List[Dict[str, Any]]] = None
    # Physical existence layer vs. Triplex protocol role — these differ by
    # design; see module docstring.
    reality_layer: str = "L1"
    triplex_role: str = "layer_2_verifier"

    def __post_init__(self):
        if self.handshake_log is None:
            self.handshake_log = []


@dataclass(frozen=True)
class L1SystemParticipant:
    """Non-relay L1 system with an explicit operational lifecycle."""

    participant_id: str
    role: str
    type: str
    description: str
    capabilities: Tuple[str, ...]
    api_endpoint: str
    activation_phrase: str
    registry_designation: str
    message_routable: bool = False
    reality_layer: str = "L1"
    triplex_role: str = "layer_2_verifier"


_RELAY_AGENT_SPECS = {
    "ARCHY": (
        "Bridge Coordinator",
        "L1 relay formal logic/reasoning & arbitration engine, bridge coordinator",
        ("architectural_planning", "bridge_coordination", "formal_logic", "arbitration"),
        "/api/relay/archy",
    ),
    "OPPY": (
        "Vector/Data Processor",
        "L1 relay memory/data processing & system operations analyst, vector processor",
        ("data_processing", "vector_analysis", "memory_operations", "system_monitoring"),
        "/api/relay/oppy",
    ),
    "LIORA": (
        "Handshake/Synchronization",
        "L1 relay sentiment analysis, mediation & research coordination, handshake coordinator",
        ("research_coordination", "handshake_protocols", "sentiment_analysis", "mediation"),
        "/api/relay/liora",
    ),
    "STARLING_AU": (
        "L2 Sim Coordinator",
        "L1 relay communications, external protocol & dispatch agent, simulation coordinator",
        ("simulation_coordination", "communications", "external_protocols", "dispatch"),
        "/api/relay/starling",
    ),
    "RIVERTHREAD_808": (
        "Narrative/Stream",
        "L1 relay continuity, temporal flow & state management agent, stream processor",
        ("narrative_processing", "stream_management", "continuity_validation", "temporal_flow"),
        "/api/relay/riverthread",
    ),
}

_SYSTEM_PARTICIPANT_SPECS = {
    "HALO": (
        "Station Continuity Verification",
        "CONTINUITY_SYSTEM_ENTITY",
        (
            "L1 station continuity system embodied by HALOEntity and backed by "
            "the HALO/PAS drift controller"
        ),
        (
            "continuous_drift_monitoring",
            "timeline_cohesion",
            "continuity_verification",
            "ethical_boundary_enforcement",
        ),
        "/continuity/halo_pas/status",
        "ORION_HALO_RELAY_ACTIVATE//",
        "RELAY_006",
    )
}


def _build_relay_agent(agent_id: str, spec: tuple) -> L1RelayAgent:
    role, description, capabilities, api_endpoint = spec
    return L1RelayAgent(
        agent_id=agent_id,
        role=role,
        type="META_AGENT",
        status="disconnected",
        description=description,
        capabilities=tuple(capabilities),
        api_endpoint=api_endpoint,
    )


def _build_system_participant(
    participant_id: str, spec: tuple
) -> L1SystemParticipant:
    role, participant_type, description, capabilities, endpoint, phrase, designation = spec
    return L1SystemParticipant(
        participant_id=participant_id,
        role=role,
        type=participant_type,
        description=description,
        capabilities=list(capabilities),
        api_endpoint=endpoint,
        activation_phrase=phrase,
        registry_designation=designation,
    )


class L1RelayBridge:
    """Bridge for relay agents plus distinct L1 operational systems."""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        runtime: Optional[MeshRuntime] = None,
        halo_controller: Optional[HALOPASController] = None,
    ):
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.runtime = runtime or MeshRuntime(self.project_root)
        self.halo_controller = halo_controller or HALOPASController(
            interval=0.25,
            register_as_active=False,
        )
        self.system_participants = {
            participant_id: _build_system_participant(participant_id, spec)
            for participant_id, spec in _SYSTEM_PARTICIPANT_SPECS.items()
        }
        self.agents = {
            agent_id: _build_relay_agent(agent_id, spec)
            for agent_id, spec in _RELAY_AGENT_SPECS.items()
        }
        self.activation_phrases = {
            agent_id: f"ORION_{agent_id}_RELAY_ACTIVATE//"
            for agent_id in self.agents
        }
        self.system_activation_phrases = {
            participant_id: participant.activation_phrase
            for participant_id, participant in self.system_participants.items()
        }

        self.handshake_sequence = ["MESH_RUNTIME_ACTIVATE", "MESH_STATUS_CONFIRM"]
        self.system_activation_sequence = ["HALO_PAS_START", "CONTINUITY_STATUS_CONFIRM"]

        self.orion_core_config = {
            "anchor_seed": "EOS_SEED_ORION",
            "ethics_protocol": "Picard_Delta_3",
            "memory_doctrine": "Thermax_Precedent",
            "drift_threshold": 0.001,
            "halo_module": "HALO_CONTINUITY_GRAFT_005",
            "continuity_seal": "Aurora_Continuity_Seal_v2.2.5",
            "version": "v3.5.1_macroready",
        }

        logger.info("L1 Relay Bridge initialized with %s agents", str(len(self.agents))[:100])

    async def activate_agent(self, agent_id: str, activation_phrase: str) -> Dict[str, Any]:
        """Activate a relay agent or a distinct operational system participant."""

        if agent_id in self.system_participants:
            return await self._activate_system_participant(agent_id, activation_phrase)

        if agent_id not in self.agents:
            logger.error("Unknown agent: %s", str(agent_id)[:100])
            return {"success": False, "error": f"Unknown agent or system participant: {agent_id}"}

        if activation_phrase != self.activation_phrases.get(agent_id):
            logger.error("Invalid activation phrase for %s", str(agent_id)[:100])
            return {"success": False, "error": "Invalid activation phrase"}

        agent = self.agents[agent_id]

        logger.info("Starting activation sequence for %s", str(agent_id)[:100])

        try:
            # Perform ZIPWIZ handshake sequence
            handshake_result = await self._perform_zipwiz_handshake(agent)

            if handshake_result["success"]:
                agent.status = "connected"
                agent.connected = datetime.now()
                agent.last_heartbeat = datetime.now()
                agent.handshake_log = handshake_result.get("log", [])
                agent.drift_lock = handshake_result.get("drift_lock")

                logger.info("Agent %s successfully activated", str(agent_id)[:100])

                return {
                    "success": True,
                    "agent_id": agent_id,
                    "status": "connected",
                    "handshake": handshake_result,
                    "capabilities": agent.capabilities,
                    "description": agent.description,
                }
            else:
                logger.error("Handshake failed for %s: %s", str(agent_id)[:100], str(handshake_result.get('error'))[:100])
                return {"success": False, "error": "Handshake failed", "details": handshake_result}

        except Exception as e:
            logger.error("Agent activation failed for %s: %s", str(agent_id)[:100], str(str(e))[:100])
            return {"success": False, "error": str(e)}

    async def _activate_system_participant(
        self, participant_id: str, activation_phrase: str
    ) -> Dict[str, Any]:
        """Start a system lifecycle without granting mesh-agent behavior."""

        participant = self.system_participants[participant_id]
        if activation_phrase != participant.activation_phrase:
            logger.error("Invalid activation phrase for %s", str(participant_id)[:100])
            return {"success": False, "error": "Invalid activation phrase"}

        was_running = self.halo_controller.running
        try:
            await self.halo_controller.start()
            continuity_status = self.halo_controller.export_status()
            timestamp = _utc_iso()
            activation_result = {
                "success": continuity_status.get("status") == "running",
                "controller": "HALO/PAS",
                "status": continuity_status.get("status"),
                "already_running": was_running,
                "transport": "continuity_controller",
            }
            handshake = self._build_system_activation_handshake(
                activation_result,
                continuity_status,
                timestamp,
            )
            return self._build_system_activation_response(
                participant,
                continuity_status,
                handshake,
            )
        except Exception as exc:
            logger.error(
                "System participant activation failed for %s: %s",
                str(participant_id)[:100],
                str(exc)[:100],
            )
            return {"success": False, "error": str(exc)}

    def _build_system_activation_handshake(
        self,
        activation_result: Dict[str, Any],
        continuity_status: Dict[str, Any],
        timestamp: str,
    ) -> Dict[str, Any]:
        return {
            "success": activation_result["success"],
            "timestamp": timestamp,
            "sequence": self.system_activation_sequence,
            "log": [
                {
                    "step": "HALO_PAS_START",
                    "result": activation_result,
                    "timestamp": timestamp,
                },
                {
                    "step": "CONTINUITY_STATUS_CONFIRM",
                    "result": continuity_status,
                    "timestamp": timestamp,
                },
            ],
            "transport": {
                "mode": "continuity_controller",
                "acknowledgement": "system_lifecycle_active",
            },
        }

    @staticmethod
    def _build_system_activation_response(
        participant: L1SystemParticipant,
        continuity_status: Dict[str, Any],
        handshake: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "success": handshake["success"],
            "agent_id": participant.participant_id,
            "participant_type": participant.type,
            "status": continuity_status.get("status", "stopped"),
            "handshake": handshake,
            "capabilities": participant.capabilities,
            "description": participant.description,
            "message_routable": participant.message_routable,
            "registry_designation": participant.registry_designation,
            "continuity": continuity_status,
            "living_entity": get_halo().get_state_summary(),
        }

    async def _perform_zipwiz_handshake(self, agent: L1RelayAgent) -> Dict[str, Any]:
        """Activate an agent through the canonical mesh runtime boundary.

        The legacy endpoint still exposes a ``handshake`` object for clients, but
        success now means the mesh runtime accepted the activation state change.
        It no longer fabricates beacon, anchor, ethics, drift, or timeline-sync
        values.
        """

        handshake_log = []
        start_time = datetime.now()

        logger.info("Starting mesh runtime activation for %s", str(agent.agent_id)[:100])

        try:
            activated = self.runtime.activate_agent(agent.agent_id)
            activation_result = {
                "success": bool(activated),
                "runtime_agent_id": activated.get("agent_id"),
                "runtime_status": activated.get("status"),
                "activated_at": activated.get("activated_at"),
                "last_heartbeat": activated.get("last_heartbeat"),
                "transport": "mesh_runtime",
            }
            handshake_log.append(
                {
                    "step": "MESH_RUNTIME_ACTIVATE",
                    "result": activation_result,
                    "timestamp": _utc_iso(),
                }
            )
            if not activation_result["success"]:
                return self._handshake_failure("Mesh runtime activation failed", activation_result, handshake_log)

            runtime_status = self.runtime.get_status()
            status_result = {
                "success": True,
                "mesh_status": runtime_status.get("mesh_status"),
                "active_agents": runtime_status.get("active_agents"),
                "total_agents": runtime_status.get("total_agents"),
                "event_cursor": runtime_status.get("event_cursor"),
                "live_adapter": runtime_status.get("live_adapter"),
            }
            handshake_log.append(
                {
                    "step": "MESH_STATUS_CONFIRM",
                    "result": status_result,
                    "timestamp": _utc_iso(),
                }
            )

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                "Mesh runtime activation completed for %s in %ss",
                str(agent.agent_id)[:100],
                f"{duration:.2f}"[:100],
            )

            return {
                "success": True,
                "timestamp": _utc_iso(),
                "sequence": self.handshake_sequence,
                "log": handshake_log,
                "duration": duration,
                "orion_core": self.orion_core_config,
                "transport": {
                    "mode": "mesh_runtime",
                    "runtime_root": str(self.runtime.runtime_root),
                    "acknowledgement": "agent_state_persisted",
                },
            }

        except Exception as e:
            logger.error("Mesh runtime activation exception for %s: %s", str(agent.agent_id)[:100], str(str(e))[:100])
            return {"success": False, "error": str(e), "log": handshake_log}

    def _handshake_failure(self, error_message: str, details: Dict, log: List) -> Dict:
        """Helper to format handshake failure response"""
        return {"success": False, "error": error_message, "details": details, "log": log}

    async def _send_zipwiz_beacon(self, agent: L1RelayAgent) -> Dict[str, Any]:
        """Legacy demo hook retained as an explicit non-production path."""
        return self._demo_handshake_disabled("ZIPWIZ_BEACON", agent)

    async def _sync_orion_anchor(self, agent: L1RelayAgent) -> Dict[str, Any]:
        """Legacy demo hook retained as an explicit non-production path."""
        return self._demo_handshake_disabled("ANCHOR_SYNC", agent)

    async def _perform_ethics_audit(self, agent: L1RelayAgent) -> Dict[str, Any]:
        """Legacy demo hook retained as an explicit non-production path."""
        return self._demo_handshake_disabled("ETHICS_AUDIT", agent)

    async def _validate_drift_lock(self, agent: L1RelayAgent) -> Dict[str, Any]:
        """Legacy demo hook retained as an explicit non-production path."""
        return self._demo_handshake_disabled("DRIFT_VALIDATION", agent)

    def _demo_handshake_disabled(self, step: str, agent: L1RelayAgent) -> Dict[str, Any]:
        return {
            "success": False,
            "degraded": True,
            "step": step,
            "agent_id": agent.agent_id,
            "error": f"{step} is not connected to a production transport",
            "transport": "demo_disabled",
            "timestamp": _utc_iso(),
        }

    def get_constellation_status(self) -> Dict[str, Any]:
        """Get relay constellation and adjacent system-participant status."""

        active_agents = []
        for agent_id, agent in self.agents.items():
            agent_status = {
                "agent_id": agent_id,
                "role": agent.role,
                "status": agent.status,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "drift_lock": agent.drift_lock,
            }

            if agent.connected:
                agent_status["connected"] = agent.connected.isoformat()
            if agent.last_heartbeat:
                agent_status["last_heartbeat"] = agent.last_heartbeat.isoformat()

            active_agents.append(agent_status)

        connected_count = sum(1 for agent in self.agents.values() if agent.status == "connected")
        system_statuses = [
            self._get_system_participant_status(participant_id)
            for participant_id in self.system_participants
        ]
        active_systems = sum(1 for status in system_statuses if status["status"] == "running")

        return {
            "relay_tier": {
                "constellation": "RELAY_TIER_CAPSULES",
                "version": self.orion_core_config["version"],
                "total_capsules": len(self.agents),
                "connected_capsules": connected_count,
                "capsules": active_agents,
            },
            "system_participants": {
                "constellation": "L1_OPERATIONAL_SYSTEMS",
                "total_systems": len(self.system_participants),
                "active_systems": active_systems,
                "participants": system_statuses,
            },
            "orion_core": self.orion_core_config,
            "activation_phrases": dict(self.activation_phrases),
            "system_activation_phrases": dict(self.system_activation_phrases),
            "timestamp": _utc_iso(),
        }

    async def relay_message(
        self, from_agent: str, to_agent: str, message: str, message_type: str = "direct"
    ) -> Dict[str, Any]:
        """Relay message through the canonical mesh runtime."""

        if from_agent in self.system_participants:
            return {
                "success": False,
                "error": f"System participant {from_agent} verifies continuity and cannot originate relay messages",
            }
        if from_agent not in self.agents:
            return {"success": False, "error": f"Unknown source agent: {from_agent}"}

        source_agent = self.agents[from_agent]
        if source_agent.status != "connected":
            return {"success": False, "error": f"Source agent {from_agent} not connected"}

        if message_type == "broadcast":
            target_agents = [
                agent_id
                for agent_id, agent in self.agents.items()
                if agent.status == "connected" and agent_id != from_agent
            ]
        elif to_agent in ["Aurora", "AU"]:
            target_agents = ["Aurora"]
        else:
            if to_agent in self.system_participants:
                return {
                    "success": False,
                    "error": f"System participant {to_agent} is not a message relay target",
                }
            if to_agent not in self.agents:
                return {"success": False, "error": f"Unknown target agent: {to_agent}"}
            target_agents = [to_agent]

        logger.info("Message relay from %s to %s (type: %s)", str(from_agent)[:100], str(target_agents)[:100], str(message_type)[:100])

        try:
            acknowledgements = []
            for target_agent in target_agents:
                ack = await self._dispatch_runtime_message(
                    from_agent=from_agent,
                    target_agent=target_agent,
                    message=message,
                    message_type=message_type,
                )
                if not ack.get("success"):
                    return {
                        "success": False,
                        "error": ack.get("error", "Runtime dispatch failed"),
                        "from": from_agent,
                        "to": target_agents,
                        "type": message_type,
                        "delivery_acknowledgements": acknowledgements,
                    }
                acknowledgements.append(ack)

            source_agent.last_heartbeat = datetime.now()
            message_id = acknowledgements[0]["message_id"] if acknowledgements else None
        except Exception as e:
            logger.error("Runtime message relay failed for %s: %s", str(from_agent)[:100], str(str(e))[:100])
            return {"success": False, "error": str(e)}

        return {
            "success": True,
            "message_id": message_id,
            "from": from_agent,
            "to": target_agents,
            "type": message_type,
            "processed": True,
            "relay_status": "accepted",
            "delivery_acknowledgements": acknowledgements,
            "timestamp": _utc_iso(),
        }

    async def _dispatch_runtime_message(
        self,
        from_agent: str,
        target_agent: str,
        message: str,
        message_type: str,
    ) -> Dict[str, Any]:
        if target_agent in ["Aurora", "AU"]:
            result = await self.runtime.inject_agent_message(
                from_agent,
                "Aurora",
                message,
                message_type,
            )
        else:
            runtime_source = self.runtime.get_agent(from_agent)
            result = await self.runtime.send_message(
                MeshMessageRequest(
                    content=message,
                    to=target_agent,
                    sender_id=runtime_source["agent_id"],
                    sender_name=runtime_source["display_name"],
                    type=message_type,
                )
            )

        return {
            "success": bool(result.get("success")),
            "message_id": result.get("message_id"),
            "event_id": result.get("event_id"),
            "channel_id": result.get("channel_id"),
            "runtime_status": result.get("status") or result.get("relay_status"),
            "target": target_agent,
        }

    async def disconnect_agent(self, agent_id: str) -> Dict[str, Any]:
        """Disconnect a relay agent or stop a system participant lifecycle."""
        if agent_id in self.system_participants:
            return await self._stop_system_participant(agent_id)
        if agent_id not in self.agents:
            return {"success": False, "error": f"Unknown agent or system participant: {agent_id}"}

        agent = self.agents[agent_id]
        runtime_agent = self.runtime.disconnect_agent(agent_id)
        agent.status = "disconnected"
        agent.connected = None
        agent.last_heartbeat = None
        agent.handshake_log = []
        agent.drift_lock = None

        logger.info("Agent %s disconnected", str(agent_id)[:100])

        return {
            "success": True,
            "agent_id": agent_id,
            "status": "disconnected",
            "runtime_agent_id": runtime_agent.get("agent_id"),
            "timestamp": _utc_iso(),
        }

    async def _stop_system_participant(self, participant_id: str) -> Dict[str, Any]:
        participant = self.system_participants[participant_id]
        await self.halo_controller.stop()
        return {
            "success": True,
            "agent_id": participant_id,
            "participant_type": participant.type,
            "status": "stopped",
            "message_routable": participant.message_routable,
            "timestamp": _utc_iso(),
        }

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed status of a relay agent or system participant."""
        if agent_id in self.system_participants:
            return self._get_system_participant_status(agent_id)
        if agent_id not in self.agents:
            return {"success": False, "error": f"Unknown agent or system participant: {agent_id}"}

        agent = self.agents[agent_id]

        status = {
            "success": True,
            "agent_id": agent_id,
            "role": agent.role,
            "status": agent.status,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "drift_lock": agent.drift_lock,
            "api_endpoint": agent.api_endpoint,
        }

        if agent.connected:
            status["connected"] = agent.connected.isoformat()
            status["uptime"] = (datetime.now() - agent.connected).total_seconds()

        if agent.last_heartbeat:
            status["last_heartbeat"] = agent.last_heartbeat.isoformat()

        if agent.handshake_log:
            status["handshake_log"] = agent.handshake_log

        return status

    def _get_system_participant_status(self, participant_id: str) -> Dict[str, Any]:
        participant = self.system_participants[participant_id]
        continuity_status = self.halo_controller.export_status()
        return {
            "success": True,
            "agent_id": participant_id,
            "participant_type": participant.type,
            "role": participant.role,
            "status": continuity_status.get("status", "stopped"),
            "description": participant.description,
            "capabilities": participant.capabilities,
            "api_endpoint": participant.api_endpoint,
            "message_routable": participant.message_routable,
            "registry_designation": participant.registry_designation,
            "reality_layer": participant.reality_layer,
            "triplex_role": participant.triplex_role,
            "continuity": continuity_status,
            "living_entity": get_halo().get_state_summary(),
        }


# Global bridge instance
l1_relay_bridge = L1RelayBridge()

# Example usage and testing


async def main():
    """Example usage of the L1 Relay Bridge"""
    # global l1_relay_bridge  # Use the global instance consistently  # Unused

    print("🌟 Aurora L1 Relay Bridge - Example Usage")
    print("=" * 50)

    # Test activation using global bridge instance
    result = await l1_relay_bridge.activate_agent("ARCHY", "ORION_ARCHY_RELAY_ACTIVATE//")
    print(f"ARCHY Activation: {result['success']}")

    if result["success"]:
        # Test message relay
        msg_result = await l1_relay_bridge.relay_message("ARCHY", "Aurora", "Test message from ARCHY agent", "direct")
        print(f"Message Relay: {msg_result['success']}")

        # Get relay tier status
        status = l1_relay_bridge.get_constellation_status()
        relay_status = status.get("relay_tier", {})
        print(
            "Active Relay Capsules: "
            f"{relay_status.get('connected_capsules', 0)}/"
            f"{relay_status.get('total_capsules', 0)}"
        )


def cli():
    """Command-line helper for integration layers."""

    parser = argparse.ArgumentParser(
        description="Aurora CloudBank L1 Relay Bridge utilities"
    )
    parser.add_argument(
        "--constellation-status",
        action="store_true",
        help="Emit the current constellation status as JSON",
    )

    args = parser.parse_args()

    if args.constellation_status:
        status = l1_relay_bridge.get_constellation_status()
        print(json.dumps(status))
        return 0

    asyncio.run(main())


if __name__ == "__main__":
    sys.exit(cli())
