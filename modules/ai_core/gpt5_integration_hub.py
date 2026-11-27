"""
OpenAI Integration Hub for Aurora CloudBank Symbolic

Defaults to GPT-6.1 Sol. GPT5IntegrationHub is retained as a compatibility name.
Specialized for code generation, reasoning, and agent mode interactions
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from modules.ai_core.unified_ai_interface import AIModel, AIProvider, AIRequest, AIResponse, unified_ai
except ImportError:
    # Graceful fallback
    AIModel = None
    AIProvider = None
    AIRequest = None
    AIResponse = None
    unified_ai = None

logger = logging.getLogger(__name__)


@dataclass
class GPTConfig:
    """Configuration for GPT model integration"""

    # Model selection
    preferred_model: str = "gpt-6.1-sol"
    codex_model: str = "gpt-6.1-sol"
    fallback_model: str = "gpt-6.1-sol"

    # Performance settings
    max_tokens: int = 32768  # Conservative Responses output budget
    temperature: float = 0.7
    top_p: float = 0.9
    context_window: int = 1_050_000  # Current OpenAI API context limit

    # Code generation settings
    code_temperature: float = 0.3  # Lower for deterministic code
    code_top_p: float = 0.95

    # Agent mode settings
    enable_agent_mode: bool = True
    enable_function_calling: bool = True
    enable_parallel_calls: bool = True

    # Safety and tracking
    safety_level: str = "high"
    dlp_tracking: bool = True
    context_tag_prefix: str = "gpt"


class GPT5IntegrationHub:
    """
    Current OpenAI integration hub; class name retained for compatibility.

    Key features:
    - Direct GPT-6.1 Sol / GPT-6 Astra support
    - Current model routing for code generation
    - ChatGPT Agent Mode integration
    - Function calling and parallel execution
    - Intelligent routing based on task type
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize GPT integration hub"""
        self.config = config or {}
        self.gpt_config = self._parse_config()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.agent_tools: Dict[str, Any] = {}
        self._unified_ai = unified_ai if unified_ai else None

        # Check model availability
        self._check_model_availability()

    def _parse_config(self) -> GPTConfig:
        """Parse GPT configuration from global config"""
        gpt_cfg = self.config.get("gpt", {})

        return GPTConfig(
            preferred_model=gpt_cfg.get("preferred_model", "gpt-6.1-sol"),
            codex_model=gpt_cfg.get("codex_model", "gpt-6.1-sol"),
            fallback_model=gpt_cfg.get("fallback_model", "gpt-6.1-sol"),
            max_tokens=gpt_cfg.get("max_tokens", 32768),
            temperature=gpt_cfg.get("temperature", 0.7),
            top_p=gpt_cfg.get("top_p", 0.9),
            code_temperature=gpt_cfg.get("code_temperature", 0.3),
            enable_agent_mode=gpt_cfg.get("enable_agent_mode", True),
            enable_function_calling=gpt_cfg.get("enable_function_calling", True),
            dlp_tracking=gpt_cfg.get("dlp_tracking", True),
        )

    def _check_model_availability(self):
        """Report configured catalog availability, not account entitlement."""
        available = self._unified_ai.get_available_models() if self._unified_ai else []
        self.gpt5_available = bool(AIModel and AIModel.GPT_5 in available)
        self.gpt5_codex_available = bool(AIModel and AIModel.GPT_5_CODEX in available)
        self.gpt4o_available = bool(AIModel and AIModel.GPT_4O in available)
        self.current_openai_available = bool(AIModel and AIModel.GPT_6_1_SOL in available)

    async def execute_code_generation(
        self,
        prompt: str,
        language: str = "python",
        context_tag: str = "code_gen",
        **kwargs,
    ) -> Optional[AIResponse]:
        """
        Execute code generation request using optimal model (prefers Codex)

        Args:
            prompt: Code generation prompt
            language: Programming language
            context_tag: DLP tracking tag
            **kwargs: Additional parameters

        Returns:
            AI response with generated code
        """
        if not self._unified_ai or not AIRequest:
            logger.error("❌ Unified AI interface not available")
            return None

        # Build system prompt for code generation
        system_prompt = (
            f"You are an expert {language} programmer integrated with Aurora CloudBank Symbolic. "
            "Generate clean, efficient, well-documented code following best practices. "
            "Include type hints, error handling, and DLP tracking where appropriate."
        )

        # Build fallback chain preferring Codex for code tasks
        fallback_chain = self._build_codex_fallback_chain()

        request = AIRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=kwargs.get("max_tokens", self.gpt_config.max_tokens),
            temperature=self.gpt_config.code_temperature,  # Lower temp for code
            top_p=self.gpt_config.code_top_p,
            fallback_chain=fallback_chain,
            context_tag=f"{self.gpt_config.context_tag_prefix}_code_{context_tag}",
            dlp_tracking=self.gpt_config.dlp_tracking,
            reasoning_effort=kwargs.get("reasoning_effort", "medium"),
        )

        try:
            response = await self._unified_ai.execute_request(request, task_type="code_generation")
            return response
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return None

    async def execute_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context_tag: str = "reasoning",
        **kwargs,
    ) -> Optional[AIResponse]:
        """
        Execute reasoning/analysis request

        Args:
            prompt: Reasoning prompt
            system_prompt: Optional system context
            context_tag: DLP tracking tag
            **kwargs: Additional parameters

        Returns:
            AI response with reasoning
        """
        if not self._unified_ai or not AIRequest:
            logger.error("❌ Unified AI interface not available")
            return None

        fallback_chain = self._build_reasoning_fallback_chain()

        request = AIRequest(
            prompt=prompt,
            system_prompt=system_prompt or self._get_default_system_prompt(),
            max_tokens=kwargs.get("max_tokens", self.gpt_config.max_tokens),
            temperature=kwargs.get("temperature", self.gpt_config.temperature),
            top_p=kwargs.get("top_p", self.gpt_config.top_p),
            fallback_chain=fallback_chain,
            context_tag=f"{self.gpt_config.context_tag_prefix}_{context_tag}",
            dlp_tracking=self.gpt_config.dlp_tracking,
            reasoning_effort=kwargs.get("reasoning_effort", "medium"),
        )

        try:
            response = await self._unified_ai.execute_request(request, task_type="reasoning")
            return response
        except Exception as e:
            logger.error(f"Reasoning request failed: {e}")
            return None

    async def execute_agent_action(
        self,
        prompt: str,
        functions: Optional[List[Dict[str, Any]]] = None,
        context_tag: str = "agent",
        **kwargs,
    ) -> Optional[AIResponse]:
        """
        Execute agent mode action with function calling

        Args:
            prompt: Agent prompt
            functions: Available functions for agent
            context_tag: DLP tracking tag
            **kwargs: Additional parameters

        Returns:
            AI response with potential function calls
        """
        if not self._unified_ai or not AIRequest:
            logger.error("❌ Unified AI interface not available")
            return None

        if not self.gpt_config.enable_agent_mode:
            logger.warning("⚠️  Agent mode disabled in configuration")
            return None

        fallback_chain = self._build_agent_fallback_chain()

        request = AIRequest(
            prompt=prompt,
            system_prompt=self._get_agent_system_prompt(),
            max_tokens=kwargs.get("max_tokens", self.gpt_config.max_tokens),
            temperature=kwargs.get("temperature", 0.5),  # Moderate temp for agents
            fallback_chain=fallback_chain,
            functions=functions or self.agent_tools.get("functions", []),
            context_tag=f"{self.gpt_config.context_tag_prefix}_agent_{context_tag}",
            dlp_tracking=self.gpt_config.dlp_tracking,
            reasoning_effort=kwargs.get("reasoning_effort", "medium"),
        )

        try:
            response = await self._unified_ai.execute_request(request, task_type="general")
            return response
        except Exception as e:
            logger.error(f"Agent action failed: {e}")
            return None

    def _configured_chain(self, preferred: str) -> list:
        """Honor current configuration and exclude disabled legacy models."""
        if not AIModel or not self._unified_ai:
            return []
        available = self._unified_ai.get_available_models()
        chain = []
        for name in (preferred, self.gpt_config.fallback_model):
            model = AIModel(name)
            if model in available and model not in chain:
                chain.append(model)
        return chain

    def _build_codex_fallback_chain(self) -> list:
        return self._configured_chain(self.gpt_config.codex_model)

    def _build_reasoning_fallback_chain(self) -> list:
        return self._configured_chain(self.gpt_config.preferred_model)

    def _build_agent_fallback_chain(self) -> list:
        return self._configured_chain(self.gpt_config.preferred_model)

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for GPT"""
        return (
            "You are an advanced AI assistant integrated with Aurora CloudBank Symbolic, "
            "a quantum-symbolic computing platform. You have access to powerful reasoning, "
            "code generation, and analytical capabilities. Provide clear, accurate, and "
            "well-structured responses while maintaining Aurora's ethical protocols and "
            "DLP tracking standards."
        )

    def _get_agent_system_prompt(self) -> str:
        """Get system prompt for agent mode"""
        return (
            "You are an AI agent with function calling capabilities, integrated with "
            "Aurora CloudBank Symbolic. You can use provided tools to accomplish complex "
            "tasks. Analyze the user's request, determine the appropriate sequence of "
            "function calls, and execute them efficiently. Maintain Aurora's ethical "
            "protocols and provide clear explanations of your actions."
        )

    async def enable_gpt5(self) -> Dict[str, bool]:
        """
        Enable GPT-5 (when available)

        Returns:
            Status dictionary
        """
        if not self._unified_ai or not AIModel:
            return {"error": "Unified AI not available", "enabled": False}

        try:
            self._unified_ai.enable_model(AIModel.GPT_5)
            self.gpt5_available = True

            logger.info("🚀 GPT-5 enabled!")

            return {
                "enabled": True,
                "model": "gpt-5",
                "context_window": 1_000_000,
                "max_tokens": 32768,
                "features": {
                    "function_calling": True,
                    "vision": True,
                    "code_execution": True,
                    "parallel_calls": True,
                },
            }

        except Exception as e:
            logger.error(f"Failed to enable GPT-5: {e}")
            return {"error": str(e), "enabled": False}

    async def enable_gpt5_codex(self) -> Dict[str, bool]:
        """
        Enable GPT-5 Codex (when available)

        Returns:
            Status dictionary
        """
        if not self._unified_ai or not AIModel:
            return {"error": "Unified AI not available", "enabled": False}

        try:
            self._unified_ai.enable_model(AIModel.GPT_5_CODEX)
            self.gpt5_codex_available = True

            logger.info("🚀 GPT-5 Codex enabled!")

            return {
                "enabled": True,
                "model": "gpt-5-codex",
                "context_window": 1_000_000,
                "max_tokens": 32768,
                "features": {
                    "advanced_code_generation": True,
                    "code_execution": True,
                    "multi_language_support": True,
                    "function_calling": True,
                },
            }

        except Exception as e:
            logger.error(f"Failed to enable GPT-5 Codex: {e}")
            return {"error": str(e), "enabled": False}

    def get_global_status(self) -> Dict[str, Any]:
        """
        Get current GPT integration status

        Returns:
            Status dictionary with model availability and configuration
        """
        return {
            "current_openai_available": self.current_openai_available,
            "gpt4o_available": self.gpt4o_available,
            "gpt5_available": self.gpt5_available,
            "gpt5_codex_available": self.gpt5_codex_available,
            "preferred_model": self.gpt_config.preferred_model,
            "codex_model": self.gpt_config.codex_model,
            "fallback_model": self.gpt_config.fallback_model,
            "agent_mode_enabled": self.gpt_config.enable_agent_mode,
            "active_sessions": len(self.active_sessions),
            "config": {
                "max_tokens": self.gpt_config.max_tokens,
                "context_window": self.gpt_config.context_window,
                "temperature": self.gpt_config.temperature,
                "code_temperature": self.gpt_config.code_temperature,
                "dlp_tracking": self.gpt_config.dlp_tracking,
            },
        }

    def register_agent_tools(self, tools: Dict[str, Any]):
        """Register tools for agent mode function calling"""
        self.agent_tools = tools
        logger.info(f"✅ Registered {len(tools.get('functions', []))} agent tools")


# Global instance for easy access
gpt5_hub = GPT5IntegrationHub()
