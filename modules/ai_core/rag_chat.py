"""Memory-augmented chat: retrieves relevant memories before LLM call."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


async def rag_chat(
    message: str,
    *,
    context_id: str,
    user_id: str = "default",
    top_k: int = 5,
    max_memory_tokens: int = 2000,
    model: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Chat with memory augmentation.

    1. Retrieves relevant memories for the context_id/message pair
    2. Prepends memory context to the system prompt
    3. Calls the unified AI interface
    4. Stores the response back to memory

    Args:
        message: The current user message.
        context_id: Session / agent context identifier used to scope memories.
        user_id: Tenant / user identifier for cache isolation.
        top_k: Maximum number of memory snippets to retrieve.
        max_memory_tokens: Rough upper-bound on injected memory text (characters).
        model: Optional model name passed through as ``model_preference``.
            Must be a valid ``AIModel`` value; ignored if not recognised.
        metadata: Extra key/value pairs forwarded to the AI request metadata.

    Returns:
        dict with keys:
            - ``response`` (str): LLM response text.
            - ``memories_used`` (int): Number of memories retrieved.
            - ``context_id`` (str): Echo of the supplied context_id.
    """
    # ------------------------------------------------------------------
    # Step 1: Retrieve relevant memories
    # ------------------------------------------------------------------
    memories: List[Dict] = []
    memory_context = ""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        memories = core.retrieve_memories(
            context_id, message, top_k=top_k, user_id=user_id
        )
        if memories:
            snippets = [m.get("content", "") for m in memories[:top_k]]
            # Truncate total injected context to stay within max_memory_tokens
            joined = "\n---\n".join(snippets)
            if len(joined) > max_memory_tokens:
                joined = joined[:max_memory_tokens]
            memory_context = "\n\n[Relevant context from memory]\n" + joined
    except Exception as exc:
        logger.warning("Memory retrieval failed for RAG chat: %s", exc)

    # ------------------------------------------------------------------
    # Step 2: Build augmented prompt
    # ------------------------------------------------------------------
    if memory_context:
        augmented_message = f"{memory_context}\n\n[Current message]\n{message}"
    else:
        augmented_message = message

    # ------------------------------------------------------------------
    # Step 3: Call LLM via UnifiedAIInterface
    # ------------------------------------------------------------------
    response_text = ""
    try:
        from modules.ai_core.unified_ai_interface import AIModel, AIRequest, UnifiedAIInterface

        # Resolve optional model string to AIModel enum value
        model_preference: Optional[AIModel] = None
        if model:
            try:
                model_preference = AIModel(model)
            except ValueError:
                logger.debug("Unrecognised model %r; letting UnifiedAIInterface choose", model)

        interface = UnifiedAIInterface()
        req = AIRequest(
            prompt=augmented_message,
            model_preference=model_preference,
            context_tag=f"rag_chat:{context_id}",
        )
        ai_response = await interface.execute_request(req)
        response_text = ai_response.content
    except Exception:
        logger.exception("LLM call failed in RAG chat")
        raise

    # ------------------------------------------------------------------
    # Step 4: Store the Q&A exchange back to memory
    # ------------------------------------------------------------------
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        core.add_memory(
            context_id,
            f"Q: {message[:500]}\nA: {response_text[:500]}",
            {"importance": 0.6, "tags": ["rag_chat"], "user_id": user_id},
        )
    except Exception as exc:
        logger.debug("Failed to store RAG chat to memory: %s", exc)

    return {
        "response": response_text,
        "memories_used": len(memories),
        "context_id": context_id,
    }
