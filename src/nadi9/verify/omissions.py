from typing import List, Tuple
from ..memory.claims import SubtitleDecision

def check_omissions(decision: SubtitleDecision) -> Tuple[bool, List[str]]:
    """Check for significant omissions or additions vs source."""
    issues = []
    source = decision.source_text
    output = decision.nadi_9_text
    
    if not output or output == "INSUFFICIENT_EVIDENCE":
        return True, []
    
    source_words = len(source.split())
    output_words = len(output.split())
    
    # If output is dramatically shorter, flag potential omission
    if source_words > 3 and output_words < source_words * 0.3:
        issues.append(f"Possible omission: source has {source_words} words but output has only {output_words}")
    
    # If output is dramatically longer, flag potential addition
    if source_words > 0 and output_words > source_words * 3:
        issues.append(f"Possible addition: source has {source_words} words but output has {output_words}")
    
    return len(issues) == 0, issues