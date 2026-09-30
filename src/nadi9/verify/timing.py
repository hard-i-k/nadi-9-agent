from ..memory.claims import SubtitleDecision

def check_timing(decision: SubtitleDecision) -> bool:
    if not decision.timing: return False
    if decision.timing.duration_sec < 0.5 or decision.timing.duration_sec > 7.0:
        return False
    if decision.timing.chars_per_sec > 25:
        return False
    if len(decision.nadi_9_text) > 84: # approx 2 lines of 42
        return False
    return True