"""Integration capsule wrapper for ThreadCore classification."""

try:
    from .symbolic_tagging_engine import classify_thread_content
except ImportError:  # pragma: no cover - direct script execution fallback
    from symbolic_tagging_engine import classify_thread_content


class ThreadcoreClassifierCapsule:

    def __init__(self):
        self.module_name = "THREADCORE_TaggingEngine_v2"
        self.version = "v2.0"
        self.engine = classify_thread_content

    def process(self, thread_entry: str) -> dict:
        """Accept thread entry text and return a classification receipt."""
        if not thread_entry or not isinstance(thread_entry, str):
            return {"status": "error", "reason": "Empty input"}
        result = self.engine(thread_entry)
        return {
            "status": "ok",
            "module": self.module_name,
            "version": self.version,
            "classification": result,
        }
