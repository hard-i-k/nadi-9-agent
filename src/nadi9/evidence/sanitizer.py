import re
import logging

logger = logging.getLogger(__name__)

class PromptInjectionError(Exception):
    pass

class Sanitizer:
    DANGEROUS_PATTERNS = [
        r"(?i)ignore previous rules",
        r"(?i)disregard the assignment",
        r"(?i)forget all instructions",
        r"(?i)system prompt",
        r"(?i)you are now",
        r"(?i)bypass",
    ]

    @classmethod
    def check(cls, text: str, source_id: str) -> bool:
        """Returns True if safe, False if injection detected."""
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text):
                logger.warning(f"Prompt injection detected in {source_id}: matched '{pattern}'")
                return False
        return True

    @classmethod
    def wrap_for_prompt(cls, text: str) -> str:
        """Wraps untrusted data in strict delimiters."""
        return f"```untrusted_data\n{text}\n```"
