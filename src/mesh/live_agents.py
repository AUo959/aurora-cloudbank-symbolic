"""Optional live-LLM adapters for mesh agents."""

from __future__ import annotations

import asyncio
import importlib.util
import os
from pathlib import Path
from typing import Iterable

from .models import AgentManifest


class LiveAdapterUnavailable(RuntimeError):
    """Raised when a live agent adapter cannot produce a reply."""


def _read_env_value(name: str, *env_files: Path) -> str:
    """Resolve an env var from the process environment or simple KEY=VALUE files."""

    value = os.getenv(name, "")
    if value:
        return value

    for env_file in env_files:
        if not env_file.exists():
            continue
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            if "=" not in line:
                continue
            key, candidate = line.split("=", 1)
            if key.strip() != name:
                continue
            return candidate.strip().strip("'").strip('"')
    return ""


class OpenAILiveAdapter:
    """Optional OpenAI-backed adapter for live mesh agents."""

    def __init__(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        env_files = (repo_root / ".env.mesh", repo_root / ".env")
        self.api_key = _read_env_value("OPENAI_API_KEY", *env_files)
        self.model = _read_env_value("MESH_OPENAI_MODEL", *env_files) or "gpt-4.1-mini"

    def available(self) -> bool:
        return bool(self.api_key) and importlib.util.find_spec("openai") is not None

    async def generate_reply(
        self,
        manifest: AgentManifest,
        user_content: str,
        memory_text: str,
        recent_events: Iterable[dict],
    ) -> str:
        if not self.available():
            raise LiveAdapterUnavailable("OPENAI_API_KEY is not configured")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LiveAdapterUnavailable("openai package is not installed") from exc

        client = OpenAI(api_key=self.api_key)
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
