"""
AI Core Module for Aurora CloudBank Symbolic

Unified AI integration supporting multiple models:
- Claude 3.5 Sonnet, 4.5 Opus (Anthropic)
- GPT-4, GPT-4o, GPT-5, GPT-5 Codex (OpenAI)

Features:
- Intelligent model selection and fallback chains
- Task-specific optimization (reasoning, code generation, agent mode)
- Performance tracking and cost management
- DLP-compliant request/response tracking
- Token budget enforcement (per-request, per-user, global)
"""

from modules.ai_core.unified_ai_interface import (
    AIModel,
    AIProvider,
    AIRequest,
    AIResponse,
    ModelCapabilities,
    UnifiedAIInterface,
    unified_ai,
)

from modules.ai_core.token_budget import (
    TokenBudget,
    TokenBudgetExceededError,
    token_budget,
)

try:
    from modules.ai_core.claude_integration_hub import sonnet4_hub  # Backward compatibility
    from modules.ai_core.claude_integration_hub import ClaudeIntegrationHub, claude_hub
except ImportError:
    ClaudeIntegrationHub = None
    claude_hub = None
    sonnet4_hub = None

try:
    from modules.ai_core.gpt5_integration_hub import GPT5IntegrationHub, gpt5_hub
except ImportError:
    GPT5IntegrationHub = None
    gpt5_hub = None

__all__ = [
    "AIModel",
    "AIProvider",
    "AIRequest",
    "AIResponse",
    "ModelCapabilities",
    "UnifiedAIInterface",
    "unified_ai",
    "TokenBudget",
    "TokenBudgetExceededError",
    "token_budget",
    "ClaudeIntegrationHub",
    "claude_hub",
    "sonnet4_hub",
    "GPT5IntegrationHub",
    "gpt5_hub",
]
