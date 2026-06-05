"""Optional live-LLM adapters for mesh agents."""

from __future__ import annotations

import asyncio
import os
from typing import Iterable

from .models import AgentManifest

# Module-level shared OpenAI client (avoids per-request construction overhead).
# If the package is absent or the env var is missing at import time we fall back
# to per-request construction inside generate_reply so the module stays importable.
_MESH_CLIENT = None
try:
    import httpx
    from openai import OpenAI as _OpenAI

    _MESH_CLIENT = _OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", ""),
        timeout=httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=60.0),
        max_retries=2,
    )
except Exception:
    _MESH_CLIENT = None


class LiveAdapterUnavailable(RuntimeError):
    """Raised when a live agent adapter cannot produce a reply."""


class OpenAILiveAdapter:
    """Optional OpenAI-backed adapter for live mesh agents."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("MESH_OPENAI_MODEL", "gpt-4.1-mini")

    def available(self) -> bool:
        return bool(self.api_key)

    async def generate_reply(
        self,
        manifest: AgentManifest,
        user_content: str,
        memory_text: str,
        recent_events: Iterable[dict],
    ) -> str:
        if not self.available():
            raise LiveAdapterUnavailable("OPENAI_API_KEY is not configured")

        if _MESH_CLIENT is not None:
            client = _MESH_CLIENT
        else:
            try:
                import httpx
                from openai import OpenAI
            except ImportError as exc:
                raise LiveAdapterUnavailable("openai package is not installed") from exc
            client = OpenAI(
                api_key=self.api_key,
                timeout=httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=60.0),
                max_retries=2,
            )
        model = manifest.model_profile.get("model", self.model)
        max_output_tokens = int(manifest.model_profile.get("max_output_tokens", 220))

        history_lines = []
        for event in recent_events:
            speaker = event.get("agent_id") or event.get("payload", {}).get("sender_name", "User")
            text = event.get("payload", {}).get("content")
            if text:
                history_lines.append(f"{speaker}: {text}")

        system_prompt = (
            f"You are {manifest.display_name} in the Aurora mesh workspace.\n"
            f"Execution mode: {manifest.execution_mode}.\n"
            f"Respond concisely and operationally.\n"
            f"Memory:\n{memory_text or 'No additional memory loaded.'}"
        )
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
            return await asyncio.to_thread(_request)
        except Exception as exc:  # pragma: no cover - network path not used in tests
            raise LiveAdapterUnavailable(str(exc)) from exc
