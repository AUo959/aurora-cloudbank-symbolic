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
import uuid
import hashlib


# Simple in-memory session store
_SESSIONS: Dict[str, Dict[str, Any]] = {}
DEFAULT_PII_REDACTION = {
    "enabled": True,
    "strategy": "mask",
    "mask": "***",
    "fields": ["full_name", "email", "phone", "account_number"],
}


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
            "description": "Create/update/get/delete/share/fork agent sessions",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["create", "update", "get", "delete", "share", "fork"]},
                    "session_id": {"type": "string"},
                    "state_data": {"type": "object"},
                    "share_token": {"type": "string"},
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

    def _anchor_for_state(payload: Dict[str, Any]) -> Dict[str, str]:
        metadata_anchor = payload.get("metadata_anchor") or payload.get("metadata") or {}
        return {
            "anchor_seed": metadata_anchor.get("anchor_seed", "T1-SESSION-FLOW-START"),
            "context_tag": "agent_session_state",
        }

    def _with_defaults(payload: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**payload}
        merged.setdefault("pii_redaction", DEFAULT_PII_REDACTION)
        merged.setdefault("metadata_anchor", _anchor_for_state(payload))
        return merged

    def _redact(payload: Dict[str, Any]) -> Dict[str, Any]:
        redaction = payload.get("pii_redaction", DEFAULT_PII_REDACTION)
        if not redaction.get("enabled", True):
            return {**payload, "pii_redaction": redaction}

        masked: Dict[str, Any] = {}
        for key, value in payload.items():
            if key in redaction.get("fields", []):
                masked[key] = redaction.get("mask", "***")
            else:
                masked[key] = value
        masked["pii_redaction"] = redaction
        return masked

    if action == "create":
        sid = sid or f"sess_{int(time.time()*1000)}"
        state_with_defaults = _with_defaults(state)
        _SESSIONS[sid] = {
            "state": state_with_defaults,
            "created": _now_iso(),
            "updated": _now_iso(),
        }
        return {
            "success": True,
            "result": {"session_id": sid, "state": _SESSIONS[sid]},
            **_exec_ctx("session_management"),
        }

    if action == "update":
        if sid in _SESSIONS:
            _SESSIONS[sid]["state"].update(_with_defaults(state))
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

    if action == "share":
        if sid in _SESSIONS:
            shared = _SESSIONS[sid]
            share_token = hashlib.sha256(f"{sid}-T1-SESSION-FLOW".encode()).hexdigest()[:16]
            redacted_state = _redact(shared["state"])
            return {
                "success": True,
                "result": {
                    "session_id": sid,
                    "share_token": share_token,
                    "shared_state": {
                        "state": redacted_state,
                        "metadata_anchor": redacted_state.get("metadata_anchor"),
                    },
                },
                **_exec_ctx("session_management"),
            }
        return {"success": False, "error": "Session not found", **_exec_ctx("session_management")}

    if action == "fork":
        if sid in _SESSIONS:
            share_token = params.get("share_token")
            if not share_token:
                return {"success": False, "error": "share_token required", **_exec_ctx("session_management")}

            base_state = _redact(_SESSIONS[sid]["state"])
            forked_id = f"fork_{uuid.uuid4()}"
            forked_state = _with_defaults({**base_state, "forked_from": sid, "share_token": share_token})
            _SESSIONS[forked_id] = {
                "state": forked_state,
                "created": _now_iso(),
                "updated": _now_iso(),
            }
            return {
                "success": True,
                "result": {"session_id": forked_id, "state": _SESSIONS[forked_id]},
                **_exec_ctx("session_management"),
            }
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
