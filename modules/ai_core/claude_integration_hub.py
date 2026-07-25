"""
Enhanced Claude Integration Hub for Aurora CloudBank Symbolic

Supports Claude Opus 5 and Claude Sonnet 5 with intelligent fallback
Maintains backward compatibility with existing Sonnet 4 integration
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from modules.ai_core.unified_ai_interface import AIModel, AIProvider, AIRequest, AIResponse, unified_ai
except ImportError:
    # Graceful fallback for testing
    AIModel = None
    AIProvider = None
    AIRequest = None
    AIResponse = None
    unified_ai = None

logger = logging.getLogger(__name__)


@dataclass
class ClaudeConfig:
    """Configuration for Claude model integration"""

    # Model selection (IDs verified against the Anthropic catalog on 2026-07-25;
    # these take no date suffix)
    preferred_model: str = "claude-opus-5"  # Default to Opus 5
    fallback_model: str = "claude-sonnet-5"  # Fallback to Sonnet 5
    enable_gpt_fallback: bool = True
    gpt_fallback_model: str = "gpt-4o"

    # Performance settings
    max_tokens: int = 16384  # conservative default; Opus 5 supports up to 128k
    temperature: float = 0.7
    top_p: float = 0.9
    context_window: int = 1_000_000  # Opus 5 and Sonnet 5: 1M

    # Safety and ethics
    safety_level: str = "high"
    ethics_protocol: str = "Picard_Delta_3"

    # Feature flags
    enable_code_execution: bool = True  # supported by Opus 5 and Sonnet 5
    enable_vision: bool = True
    enable_function_calling: bool = True
    preserve_legacy_behavior: bool = True  # Maintain legacy Sonnet 4 hub compatibility

    # DLP and tracking
    dlp_tracking: bool = True
    context_tag_prefix: str = "claude"


class ClaudeIntegrationHub:
    """
    Enhanced Claude integration supporting Claude Opus 5 and Claude Sonnet 5

    Key features:
    - Automatic model selection based on availability
    - Intelligent fallback chain: Opus 5 → Sonnet 5 → GPT-4o
    - Context window optimization
    - Code execution support
    - Backward compatible with existing sonnet4_integration_hub
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Claude integration hub"""
        self.config = config or {}
        self.claude_config = self._parse_config()
        self.active_clients: Dict[str, Dict[str, Any]] = {}
        self.performance_stats: Dict[str, Any] = {}
        self._unified_ai = unified_ai if unified_ai else None

        # Check model availability
        self._check_model_availability()

    def _parse_config(self) -> ClaudeConfig:
        """Parse Claude configuration from global config"""
        claude_cfg = self.config.get("claude", {})

        return ClaudeConfig(
            preferred_model=claude_cfg.get("preferred_model", "claude-opus-5"),
            fallback_model=claude_cfg.get("fallback_model", "claude-sonnet-5"),
            enable_gpt_fallback=claude_cfg.get("enable_gpt_fallback", True),
            gpt_fallback_model=claude_cfg.get("gpt_fallback_model", "gpt-4o"),
            max_tokens=claude_cfg.get("max_tokens", 16384),
            temperature=claude_cfg.get("temperature", 0.7),
            top_p=claude_cfg.get("top_p", 0.9),
            safety_level=claude_cfg.get("safety_level", "high"),
            enable_code_execution=claude_cfg.get("enable_code_execution", True),
            enable_vision=claude_cfg.get("enable_vision", True),
            dlp_tracking=claude_cfg.get("dlp_tracking", True),
        )

    def _check_model_availability(self):
        """Check which Claude models are currently available"""
        if not self._unified_ai:
            logger.warning("⚠️  Unified AI interface not available")
            return

        try:
            available = self._unified_ai.get_available_models()

            # Check for Claude Opus 5
            if AIModel and AIModel.CLAUDE_OPUS_5 in available:
                logger.info("✅ Claude Opus 5 available")
                self.claude_opus_available = True
            else:
                logger.info("⏳ Claude Opus 5 not available, will use Sonnet 5")
                self.claude_opus_available = False

            # Check for Claude Sonnet 5
            if AIModel and AIModel.CLAUDE_SONNET_5 in available:
                logger.info("✅ Claude Sonnet 5 available")
                self.claude_sonnet_available = True
            else:
                logger.warning("⚠️  Claude Sonnet 5 not available")
                self.claude_sonnet_available = False

        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            self.claude_opus_available = False
            self.claude_sonnet_available = True  # Assume Sonnet 5 works

    async def execute_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context_tag: str = "claude_request",
        task_type: str = "general",
        **kwargs,
    ) -> Optional[AIResponse]:
        """
        Execute request using optimal Claude model with fallback

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            context_tag: DLP tracking tag
            task_type: Type of task (reasoning, code_generation, mathematical, general)
            **kwargs: Additional parameters

        Returns:
            AI response or None if all models fail
        """
        if not self._unified_ai or not AIRequest:
            logger.error("❌ Unified AI interface not available")
            return None

        # Build fallback chain based on task type and availability
        fallback_chain = self._build_fallback_chain(task_type)

        # Create request
        request = AIRequest(
            prompt=prompt,
            system_prompt=system_prompt or self._get_default_system_prompt(),
            max_tokens=kwargs.get("max_tokens", self.claude_config.max_tokens),
            temperature=kwargs.get("temperature", self.claude_config.temperature),
            top_p=kwargs.get("top_p", self.claude_config.top_p),
            fallback_chain=fallback_chain,
            context_tag=f"{self.claude_config.context_tag_prefix}_{context_tag}",
            dlp_tracking=self.claude_config.dlp_tracking,
            safety_level=self.claude_config.safety_level,
            functions=kwargs.get("functions"),
        )

        try:
            response = await self._unified_ai.execute_request(request, task_type=task_type)

            # Track performance
            self._track_performance(response)

            return response

        except Exception as e:
            logger.error(f"Claude request failed: {e}")
            return None

    def _build_fallback_chain(self, task_type: str) -> list:
        """Build intelligent fallback chain based on task type and availability"""
        if not AIModel:
            return []

        chain = []

        # For reasoning tasks, prefer Opus 5
        if task_type in ["reasoning", "mathematical"]:
            if self.claude_opus_available:
                chain.append(AIModel.CLAUDE_OPUS_5)
            if self.claude_sonnet_available:
                chain.append(AIModel.CLAUDE_SONNET_5)

        # For code generation, prefer Opus 5 (stronger code generation)
        elif task_type == "code_generation":
            if self.claude_opus_available:
                chain.append(AIModel.CLAUDE_OPUS_5)
            if self.claude_sonnet_available:
                chain.append(AIModel.CLAUDE_SONNET_5)

        # For general tasks, use availability order
        else:
            if self.claude_sonnet_available:
                chain.append(AIModel.CLAUDE_SONNET_5)
            if self.claude_opus_available:
                chain.append(AIModel.CLAUDE_OPUS_5)

        # Add GPT fallback if enabled
        if self.claude_config.enable_gpt_fallback:
            chain.append(AIModel.GPT_4O)

        return chain

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for Claude"""
        return (
            "You are Claude, an AI assistant integrated with Aurora CloudBank Symbolic, "
            "a quantum-symbolic computing platform. You have access to advanced reasoning, "
            "code generation, and mathematical capabilities. Maintain Aurora's ethical "
            f"protocols ({self.claude_config.ethics_protocol}) and DLP tracking standards. "
            "Provide precise, well-reasoned responses."
        )

    def _track_performance(self, response: AIResponse):
        """Track performance metrics for model selection optimization"""
        if not response or not response.success:
            return

        model_key = response.model_used.value if response.model_used else "unknown"

        if model_key not in self.performance_stats:
            self.performance_stats[model_key] = {
                "total_requests": 0,
                "total_tokens": 0,
                "avg_latency_ms": 0,
                "success_rate": 1.0,
            }

        stats = self.performance_stats[model_key]
        stats["total_requests"] += 1
        stats["total_tokens"] += response.tokens_used

        # Update rolling average for latency
        n = stats["total_requests"]
        stats["avg_latency_ms"] = (stats["avg_latency_ms"] * (n - 1) + response.latency_ms) / n

    async def enable_claude_45(self) -> Dict[str, bool]:
        """
        Enable the top-tier Claude model (Opus 5).

        The ``_45`` in the name is legacy: it predates the catalog
        reconciliation and is kept because the ``/enable-claude-45`` API route
        and the ``get_global_status()`` response keys are public surface.

        Returns:
            Status dictionary
        """
        if not self._unified_ai or not AIModel:
            return {"error": "Unified AI not available", "enabled": False}

        try:
            self._unified_ai.enable_model(AIModel.CLAUDE_OPUS_5)
            self.claude_opus_available = True

            logger.info("🚀 Claude Opus 5 enabled!")

            return {
                "enabled": True,
                "model": AIModel.CLAUDE_OPUS_5.value,
                "context_window": 1_000_000,
                "max_tokens": 128_000,
                "features": {
                    "code_execution": True,
                    "vision": True,
                    "function_calling": True,
                    "enhanced_reasoning": True,
                },
            }

        except Exception as e:
            logger.error(f"Failed to enable Claude Opus 5: {e}")
            return {"error": str(e), "enabled": False}

    def get_global_status(self) -> Dict[str, Any]:
        """
        Get current Claude integration status

        Returns:
            Status dictionary with model availability and configuration
        """
        return {
            # Key names are legacy public surface; the values now track
            # Claude Sonnet 5 and Claude Opus 5 respectively.
            "claude_35_sonnet_available": self.claude_sonnet_available,
            "claude_45_opus_available": self.claude_opus_available,
            "preferred_model": self.claude_config.preferred_model,
            "fallback_model": self.claude_config.fallback_model,
            "gpt_fallback_enabled": self.claude_config.enable_gpt_fallback,
            "active_clients": len(self.active_clients),
            "performance_stats": self.performance_stats,
            "config": {
                "max_tokens": self.claude_config.max_tokens,
                "context_window": self.claude_config.context_window,
                "temperature": self.claude_config.temperature,
                "safety_level": self.claude_config.safety_level,
                "dlp_tracking": self.claude_config.dlp_tracking,
            },
        }

    # Backward compatibility methods for existing sonnet4_integration_hub users
    async def enable_sonnet4_for_all_clients(self) -> Dict[str, bool]:
        """Legacy method - redirects to new interface"""
        logger.info("⚠️  Using legacy method - consider migrating to execute_request()")
        return await self.enable_claude_45()


# Global instance for easy access
claude_hub = ClaudeIntegrationHub()

# Backward compatibility alias
sonnet4_hub = claude_hub
