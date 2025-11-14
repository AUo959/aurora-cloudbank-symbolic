"""
Unified AI Interface for Aurora CloudBank Symbolic

Multi-model AI abstraction layer supporting:
- Claude 3.5 Sonnet, 4.5 Opus
- GPT-4, GPT-4o, GPT-5 (Codex)
- Intelligent fallback chains
- Runtime model selection
- Performance tracking and optimization
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class AIModel(Enum):
    """Supported AI models with version tracking"""

    # Claude family
    CLAUDE_35_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_45_OPUS = "claude-4-5-opus-20250115"  # Expected model identifier

    # GPT family
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4O = "gpt-4o"
    GPT_5 = "gpt-5"  # Expected model identifier
    GPT_5_CODEX = "gpt-5-codex"  # Expected Codex variant


@dataclass
class ModelCapabilities:
    """Capabilities profile for each AI model"""

    model: AIModel
    provider: AIProvider
    context_window: int
    max_output_tokens: int
    supports_function_calling: bool = True
    supports_vision: bool = False
    supports_code_execution: bool = False
    reasoning_strength: int = 5  # 1-10 scale
    code_generation_strength: int = 5  # 1-10 scale
    mathematical_strength: int = 5  # 1-10 scale
    cost_per_1k_tokens: float = 0.0  # USD
    latency_avg_ms: int = 1000
    available: bool = True


@dataclass
class AIRequest:
    """Unified request structure for AI interactions"""

    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    model_preference: Optional[AIModel] = None
    fallback_chain: List[AIModel] = field(default_factory=list)
    functions: Optional[List[Dict[str, Any]]] = None
    context_tag: str = "aurora_ai_request"
    dlp_tracking: bool = True
    safety_level: str = "high"
    stream: bool = False


@dataclass
class AIResponse:
    """Unified response structure from AI models"""

    content: str
    model_used: AIModel
    provider: AIProvider
    tokens_used: int
    latency_ms: float
    success: bool = True
    error: Optional[str] = None
    function_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_tag: str = "aurora_ai_response"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class UnifiedAIInterface:
    """
    Unified interface for multi-model AI interactions

    Features:
    - Automatic model selection based on task requirements
    - Intelligent fallback chains for reliability
    - Performance tracking and optimization
    - Cost management and budgeting
    - DLP-compliant request/response tracking
    """

    # Model capabilities registry
    CAPABILITIES: Dict[AIModel, ModelCapabilities] = {
        AIModel.CLAUDE_35_SONNET: ModelCapabilities(
            model=AIModel.CLAUDE_35_SONNET,
            provider=AIProvider.ANTHROPIC,
            context_window=200_000,
            max_output_tokens=8192,
            supports_function_calling=True,
            supports_vision=True,
            reasoning_strength=9,
            code_generation_strength=8,
            mathematical_strength=9,
            cost_per_1k_tokens=0.003,
            latency_avg_ms=800,
        ),
        AIModel.CLAUDE_45_OPUS: ModelCapabilities(
            model=AIModel.CLAUDE_45_OPUS,
            provider=AIProvider.ANTHROPIC,
            context_window=500_000,
            max_output_tokens=16384,
            supports_function_calling=True,
            supports_vision=True,
            supports_code_execution=True,
            reasoning_strength=10,
            code_generation_strength=9,
            mathematical_strength=10,
            cost_per_1k_tokens=0.015,  # Expected pricing
            latency_avg_ms=1200,
            available=False,  # Not yet released
        ),
        AIModel.GPT_4: ModelCapabilities(
            model=AIModel.GPT_4,
            provider=AIProvider.OPENAI,
            context_window=8192,
            max_output_tokens=4096,
            supports_function_calling=True,
            reasoning_strength=8,
            code_generation_strength=7,
            mathematical_strength=8,
            cost_per_1k_tokens=0.03,
            latency_avg_ms=1500,
        ),
        AIModel.GPT_4O: ModelCapabilities(
            model=AIModel.GPT_4O,
            provider=AIProvider.OPENAI,
            context_window=128_000,
            max_output_tokens=4096,
            supports_function_calling=True,
            supports_vision=True,
            reasoning_strength=9,
            code_generation_strength=8,
            mathematical_strength=8,
            cost_per_1k_tokens=0.005,
            latency_avg_ms=600,
        ),
        AIModel.GPT_5: ModelCapabilities(
            model=AIModel.GPT_5,
            provider=AIProvider.OPENAI,
            context_window=1_000_000,  # Expected
            max_output_tokens=32768,  # Expected
            supports_function_calling=True,
            supports_vision=True,
            supports_code_execution=True,
            reasoning_strength=10,
            code_generation_strength=10,
            mathematical_strength=10,
            cost_per_1k_tokens=0.02,  # Expected pricing
            latency_avg_ms=1000,
            available=False,  # Not yet released
        ),
        AIModel.GPT_5_CODEX: ModelCapabilities(
            model=AIModel.GPT_5_CODEX,
            provider=AIProvider.OPENAI,
            context_window=1_000_000,  # Expected
            max_output_tokens=32768,  # Expected
            supports_function_calling=True,
            supports_vision=True,
            supports_code_execution=True,
            reasoning_strength=9,
            code_generation_strength=10,
            mathematical_strength=9,
            cost_per_1k_tokens=0.025,  # Expected pricing
            latency_avg_ms=900,
            available=False,  # Not yet released
        ),
    }

    # Default fallback chains for different task types
    FALLBACK_CHAINS = {
        "reasoning": [
            AIModel.CLAUDE_45_OPUS,
            AIModel.GPT_5,
            AIModel.CLAUDE_35_SONNET,
            AIModel.GPT_4O,
        ],
        "code_generation": [
            AIModel.GPT_5_CODEX,
            AIModel.GPT_5,
            AIModel.CLAUDE_45_OPUS,
            AIModel.CLAUDE_35_SONNET,
            AIModel.GPT_4O,
        ],
        "mathematical": [
            AIModel.CLAUDE_45_OPUS,
            AIModel.CLAUDE_35_SONNET,
            AIModel.GPT_5,
            AIModel.GPT_4,
        ],
        "general": [
            AIModel.GPT_4O,
            AIModel.CLAUDE_35_SONNET,
            AIModel.GPT_5,
            AIModel.CLAUDE_45_OPUS,
        ],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize unified AI interface"""
        self.config = config or {}
        self.anthropic_client = None
        self.openai_client = None
        self.performance_metrics: Dict[AIModel, List[float]] = {}
        self.usage_stats: Dict[AIModel, Dict[str, int]] = {}
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize AI provider clients with graceful degradation"""
        # Try Anthropic
        try:
            import anthropic

            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=self.config.get("anthropic_api_key", "")
            )
            logger.info("✅ Anthropic client initialized")
        except ImportError:
            logger.warning("⚠️  Anthropic library not available - install: pip install anthropic>=0.40.0")
        except Exception as e:
            logger.warning(f"⚠️  Anthropic client initialization failed: {e}")

        # Try OpenAI
        try:
            import openai

            self.openai_client = openai.AsyncOpenAI(api_key=self.config.get("openai_api_key", ""))
            logger.info("✅ OpenAI client initialized")
        except ImportError:
            logger.warning("⚠️  OpenAI library not available - install: pip install openai>=1.50.0")
        except Exception as e:
            logger.warning(f"⚠️  OpenAI client initialization failed: {e}")

    async def select_optimal_model(
        self, request: AIRequest, task_type: str = "general"
    ) -> AIModel:
        """
        Select optimal model based on request requirements and task type

        Args:
            request: AI request with preferences
            task_type: Type of task (reasoning, code_generation, mathematical, general)

        Returns:
            Selected AI model
        """
        # Use explicit preference if provided and available
        if request.model_preference:
            caps = self.CAPABILITIES.get(request.model_preference)
            if caps and caps.available:
                return request.model_preference

        # Use fallback chain if provided
        if request.fallback_chain:
            for model in request.fallback_chain:
                caps = self.CAPABILITIES.get(model)
                if caps and caps.available:
                    return model

        # Use task-specific fallback chain
        fallback = self.FALLBACK_CHAINS.get(task_type, self.FALLBACK_CHAINS["general"])
        for model in fallback:
            caps = self.CAPABILITIES.get(model)
            if caps and caps.available:
                return model

        # Final fallback to any available model
        for model, caps in self.CAPABILITIES.items():
            if caps.available:
                return model

        raise RuntimeError("No AI models available")

    async def execute_request(
        self, request: AIRequest, task_type: str = "general"
    ) -> AIResponse:
        """
        Execute AI request with automatic model selection and fallback

        Args:
            request: AI request specification
            task_type: Type of task for optimal model selection

        Returns:
            AI response with metadata
        """
        model = await self.select_optimal_model(request, task_type)
        caps = self.CAPABILITIES[model]

        try:
            if caps.provider == AIProvider.ANTHROPIC:
                return await self._execute_anthropic(request, model)
            elif caps.provider == AIProvider.OPENAI:
                return await self._execute_openai(request, model)
            else:
                raise ValueError(f"Unknown provider: {caps.provider}")

        except Exception as e:
            logger.error(f"Model {model.value} failed: {e}")

            # Try fallback chain
            fallback = request.fallback_chain or self.FALLBACK_CHAINS.get(
                task_type, self.FALLBACK_CHAINS["general"]
            )

            for fallback_model in fallback:
                if fallback_model == model:
                    continue  # Skip the failed model

                fallback_caps = self.CAPABILITIES.get(fallback_model)
                if not fallback_caps or not fallback_caps.available:
                    continue

                try:
                    logger.info(f"Trying fallback model: {fallback_model.value}")
                    if fallback_caps.provider == AIProvider.ANTHROPIC:
                        return await self._execute_anthropic(request, fallback_model)
                    elif fallback_caps.provider == AIProvider.OPENAI:
                        return await self._execute_openai(request, fallback_model)
                except Exception as fallback_error:
                    logger.error(f"Fallback model {fallback_model.value} failed: {fallback_error}")
                    continue

            # All models failed
            return AIResponse(
                content="",
                model_used=model,
                provider=caps.provider,
                tokens_used=0,
                latency_ms=0,
                success=False,
                error=f"All models failed. Last error: {str(e)}",
                context_tag=request.context_tag,
            )

    async def _execute_anthropic(self, request: AIRequest, model: AIModel) -> AIResponse:
        """Execute request using Anthropic API"""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")

        start_time = asyncio.get_event_loop().time()

        messages = [{"role": "user", "content": request.prompt}]

        response = await self.anthropic_client.messages.create(
            model=model.value,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            system=request.system_prompt or "",
            messages=messages,
        )

        latency = (asyncio.get_event_loop().time() - start_time) * 1000

        return AIResponse(
            content=response.content[0].text if response.content else "",
            model_used=model,
            provider=AIProvider.ANTHROPIC,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            latency_ms=latency,
            context_tag=request.context_tag,
            metadata={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "stop_reason": response.stop_reason,
            },
        )

    async def _execute_openai(self, request: AIRequest, model: AIModel) -> AIResponse:
        """Execute request using OpenAI API"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")

        start_time = asyncio.get_event_loop().time()

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        kwargs = {
            "model": model.value,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
        }

        if request.functions:
            kwargs["tools"] = [
                {"type": "function", "function": func} for func in request.functions
            ]

        response = await self.openai_client.chat.completions.create(**kwargs)

        latency = (asyncio.get_event_loop().time() - start_time) * 1000

        return AIResponse(
            content=response.choices[0].message.content or "",
            model_used=model,
            provider=AIProvider.OPENAI,
            tokens_used=response.usage.total_tokens,
            latency_ms=latency,
            context_tag=request.context_tag,
            metadata={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "finish_reason": response.choices[0].finish_reason,
            },
        )

    def get_model_capabilities(self, model: AIModel) -> ModelCapabilities:
        """Get capabilities for a specific model"""
        return self.CAPABILITIES[model]

    def get_available_models(self) -> List[AIModel]:
        """Get list of currently available models"""
        return [model for model, caps in self.CAPABILITIES.items() if caps.available]

    def enable_model(self, model: AIModel):
        """Enable a model (e.g., when Claude 4.5 or GPT-5 become available)"""
        if model in self.CAPABILITIES:
            self.CAPABILITIES[model].available = True
            logger.info(f"✅ Model {model.value} enabled")

    def disable_model(self, model: AIModel):
        """Disable a model (e.g., for maintenance or cost control)"""
        if model in self.CAPABILITIES:
            self.CAPABILITIES[model].available = False
            logger.info(f"⚠️  Model {model.value} disabled")


# Global instance for easy access
unified_ai = UnifiedAIInterface()
