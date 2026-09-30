from typing import Any
from ..memory.claims import SubtitleDecision

def check_vocab(decision: SubtitleDecision, registry: Any) -> bool:
    if "UNSUPPORTED_WORD" in decision.nadi_9_text:
        return False
    return True