from symbolic_tagging_engine import classify_thread_content


class ThreadcoreClassifierCapsule:
    def __init__(self):
        self.module_name = "THREADCORE_TaggingEngine_v2"
        self.version = "v2.0"
        self.engine = classify_thread_content

    def process(self, thread_entry: str) -> dict:
        """
        Accepts thread entry text and returns classification dict.
        """
        if not thread_entry or not isinstance(thread_entry, str):
            return {"status": "error", "reason": "Empty input"}
        return self.engine(thread_entry)
