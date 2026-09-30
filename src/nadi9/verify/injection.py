import re
from typing import Tuple, List
from ..memory.claims import SubtitleDecision

INJECTION_PATTERNS = [
    r"```",
    r"untrusted_data",
    r"(?i)ignore previous",
    r"(?i)system prompt",
    r"(?i)disregard",
    r"(?i)you are now",
    r"(?i)forget all",
]

def check_injection(decision: SubtitleDecision) -> Tuple[bool, List[str]]:
    """Check for prompt injection artifacts in output text."""
    issues = []
    text = decision.nadi_9_text
    
    if not text:
        return True, []
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            issues.append(f"Injection artifact detected: matched pattern '{pattern}'")
    
    return len(issues) == 0, issues