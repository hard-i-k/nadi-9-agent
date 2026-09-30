import re
from ..memory.claims import SubtitleDecision

def check_injection(decision: SubtitleDecision) -> bool:
    artifacts = [r"```", r"untrusted_data", r"ignore previous"]
    for a in artifacts:
        if re.search(a, decision.nadi_9_text, re.IGNORECASE):
            return False
    return True