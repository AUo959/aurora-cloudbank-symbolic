"""Optional live-LLM adapters for mesh agents."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, Iterable, List, Optional

from .models import AgentManifest


class LiveAdapterUnavailable(RuntimeError):
    """Raised when a live agent adapter cannot produce a reply."""


class OpenAILiveAdapter:
    """Optional OpenAI-backed adapter for live mesh agents."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("MESH_OPENAI_MODEL", "gpt-4.1-mini")
        timeout_value = os.getenv("MESH_OPENAI_TIMEOUT_SECONDS", "20")
        try:
            self.request_timeout_seconds = max(float(timeout_value), 1.0)
        except ValueError:
            self.request_timeout_seconds = 20.0

    def available(self) -> bool:
        return bool(self.api_key)

    async def generate_reply(
        self,
        manifest: AgentManifest,
        user_content: str,
        memory_text: str,
        recent_events: Iterable[dict],
        instruction_profile: Optional[Dict[str, Any]] = None,
        continuity_reflections: Iterable[Dict[str, Any]] = (),
        tool_context: Iterable[Dict[str, Any]] = (),
        tool_schemas: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> str:
        if not self.available():
            raise LiveAdapterUnavailable("OPENAI_API_KEY is not configured")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LiveAdapterUnavailable("openai package is not installed") from exc

        client = OpenAI(api_key=self.api_key, timeout=self.request_timeout_seconds)
        model = manifest.model_profile.get("model", self.model)
        max_output_tokens = int(manifest.model_profile.get("max_output_tokens", 220))

        history_lines = []
        for event in recent_events:
            speaker = event.get("agent_id") or event.get("payload", {}).get("sender_name", "User")
            text = event.get("payload", {}).get("content")
            if text:
                history_lines.append(f"{speaker}: {text}")

        system_sections: List[str] = [
            f"You are {manifest.display_name} in the Aurora mesh workspace.\n"
            f"Execution mode: {manifest.execution_mode}.\n"
            f"Respond concisely and operationally."
        ]
        if instruction_profile:
            core_identity = instruction_profile.get("core_identity", {})
            behavior = instruction_profile.get("behavioral_style", {})
            system_sections.append(
                "Identity profile:\n"
                + json.dumps(
                    {
                        "core_identity": core_identity,
                        "behavioral_style": behavior,
                        "growth_domains": instruction_profile.get("growth_domains", []),
                        "forbidden_behaviors": instruction_profile.get("forbidden_behaviors", []),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        if tool_schemas:
            system_sections.append("Bound tool schemas:\n" + json.dumps(tool_schemas, indent=2, sort_keys=True))
        if tool_context:
            summarized_tools = [
                {
                    "tool_name": item.get("tool_name"),
                    "summary": item.get("summary"),
                    "result": item.get("result"),
                }
                for item in tool_context
            ]
            system_sections.append("Most recent tool observations:\n" + json.dumps(summarized_tools, indent=2, sort_keys=True))
        if continuity_reflections:
            summarized_reflections = [
                {
                    "timestamp": item.get("timestamp"),
                    "reflection_summary": item.get("reflection_summary"),
                    "open_threads": item.get("open_threads", []),
                }
                for item in list(continuity_reflections)[-4:]
            ]
            system_sections.append(
                "Recent continuity reflections:\n" + json.dumps(summarized_reflections, indent=2, sort_keys=True)
            )
        system_sections.append(f"Memory:\n{memory_text or 'No additional memory loaded.'}")
        system_prompt = "\n\n".join(system_sections)
        user_prompt = (
            f"Recent channel context:\n{chr(10).join(history_lines[-8:]) or 'No prior channel history.'}\n\n"
            f"Incoming message:\n{user_content}"
        )

        def _request() -> str:
            response = client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                    {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
                ],
                max_output_tokens=max_output_tokens,
            )
            output_text = getattr(response, "output_text", "")
            if output_text:
                return output_text.strip()
            raise LiveAdapterUnavailable("OpenAI response did not include output_text")

        try:
            return await asyncio.wait_for(asyncio.to_thread(_request), timeout=self.request_timeout_seconds + 5.0)
        except asyncio.TimeoutError as exc:
            raise LiveAdapterUnavailable(
                f"OpenAI request timed out after {self.request_timeout_seconds:.0f}s"
            ) from exc
        except Exception as exc:  # pragma: no cover - network path not used in tests
            raise LiveAdapterUnavailable(str(exc)) from exc
