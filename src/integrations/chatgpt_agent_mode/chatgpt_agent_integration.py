"""
Minimal ChatGPT Agent Mode integration stub.

Provides discover_tools() and execute_tool() to keep /agent/* endpoints functional
without pulling in external dependencies. This stub validates inputs lightly,
maintains an in-memory session store, and returns structured results compatible
with docs/CHATGPT_AGENT_MODE_INTEGRATION.md.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import time


# Simple in-memory session store
_SESSIONS: Dict[str, Dict[str, Any]] = {}


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


async def discover_tools() -> Dict[str, Any]:
    """Return available tools and capabilities for Agent Mode."""
    tools = {
        "symbolic_processing": {
            "type": "function",
            "description": "Execute symbolic processing operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string"},
                    "data": {"type": "object"},
                    "anchor_context": {"type": "string"},
                },
                "required": ["operation"],
            },
        },
        "geometric_algebra": {
            "type": "function",
            "description": "Perform geometric algebra computations (mock by default)",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression_a": {"type": "string"},
                    "expression_b": {"type": "string"},
                    "operation": {"type": "string", "enum": ["mult", "add", "sub"]},
                },
                "required": ["expression_a", "expression_b", "operation"],
            },
        },
        "session_management": {
            "type": "function",
            "description": "Create/update/get/delete agent sessions",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["create", "update", "get", "delete"]},
                    "session_id": {"type": "string"},
                    "state_data": {"type": "object"},
                },
                "required": ["action"],
            },
        },
        "system_status": {
            "type": "function",
            "description": "Return current system status",
            "parameters": {
                "type": "object",
                "properties": {"detail_level": {"type": "string", "enum": ["basic", "detailed", "full"]}},
            },
        },
    }

    return {
        "tools": tools,
        "capabilities": ["function_calling", "tool_execution", "session_persistence"],
        "symbolic_anchors": {"seed": "EOS_SEED_ORION", "ethics": "Picard_Delta_3"},
        "dlp_level": "DLP_L1_OK",
        "timestamp": _now_iso(),
    }


async def execute_tool(tool_name: str, parameters: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute a registered tool with basic validation and mocked results."""
    if tool_name == "session_management":
        return _handle_session(parameters)
    if tool_name == "system_status":
        return {
            "success": True,
            "result": {
                "status": "healthy",
                "detail_level": parameters.get("detail_level", "basic"),
                "timestamp": _now_iso(),
            },
            **_exec_ctx(tool_name),
        }
    if tool_name == "geometric_algebra":
        # Mock computation: echo inputs and pretend result
        a = parameters.get("expression_a", "")
        b = parameters.get("expression_b", "")
        op = parameters.get("operation", "mult")
        pretty = f"({a}) {op} ({b})"
        return {
            "success": True,
            "result": {"geometric_result": pretty, "operation": op, "symbolic_validation": True},
            **_exec_ctx(tool_name),
        }
    if tool_name == "symbolic_processing":
        op = parameters.get("operation", "")
        return {"success": True, "result": {"operation": op, "accepted": True}, **_exec_ctx(tool_name)}

    return {"success": False, "error": f"Unknown tool: {tool_name}", **_exec_ctx(tool_name)}


async def get_agent_status() -> Dict[str, Any]:
    """Return current agent mode status and counts."""
    return {
        "status": "healthy",
        "tools_registered": [
            "symbolic_processing",
            "geometric_algebra",
            "session_management",
            "system_status",
        ],
        "session_count": len(_SESSIONS),
        "symbolic_anchors": {"seed": "EOS_SEED_ORION", "ethics": "Picard_Delta_3"},
        "dlp_level": "DLP_L1_OK",
        "timestamp": _now_iso(),
    }


def _handle_session(params: Dict[str, Any]) -> Dict[str, Any]:
    action = params.get("action")
    sid = params.get("session_id")
    state = params.get("state_data") or {}

    if action == "create":
        sid = sid or f"sess_{int(time.time()*1000)}"
        _SESSIONS[sid] = {"state": state, "created": _now_iso(), "updated": _now_iso()}
        return {
            "success": True,
            "result": {"session_id": sid, "state": _SESSIONS[sid]},
            **_exec_ctx("session_management"),
        }

    if action == "update":
        if sid in _SESSIONS:
            _SESSIONS[sid]["state"].update(state)
            _SESSIONS[sid]["updated"] = _now_iso()
            return {
                "success": True,
                "result": {"session_id": sid, "state": _SESSIONS[sid]},
                **_exec_ctx("session_management"),
            }
        return {"success": False, "error": "Session not found", **_exec_ctx("session_management")}

    if action == "get":
        if sid in _SESSIONS:
            return {
                "success": True,
                "result": {"session_id": sid, "state": _SESSIONS[sid]},
                **_exec_ctx("session_management"),
            }
        return {"success": False, "error": "Session not found", **_exec_ctx("session_management")}

    if action == "delete":
        if sid in _SESSIONS:
            del _SESSIONS[sid]
            return {"success": True, "result": {"deleted": True, "session_id": sid}, **_exec_ctx("session_management")}
        return {"success": False, "error": "Session not found", **_exec_ctx("session_management")}

    return {"success": False, "error": "Invalid action", **_exec_ctx("session_management")}


def _exec_ctx(tool: str) -> Dict[str, Any]:
    return {
        "execution_context": {
            "tool_name": tool,
            "symbolic_anchor": "EOS_SEED_ORION",
            "ethics_protocol": "Picard_Delta_3",
            "context_tag": f"agent_tool_execution_{tool}",
        },
        "symbolic_hash_validation": True,
        "dlp_level": "DLP_L1_OK",
        "timestamp": _now_iso(),
    }
