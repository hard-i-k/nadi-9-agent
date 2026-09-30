import re
from typing import List, Tuple
from ..memory.claims import SubtitleDecision

def check_names_numbers(decision: SubtitleDecision) -> Tuple[bool, List[str]]:
    """Check that names and numbers from source are preserved in output."""
    issues = []
    source = decision.source_text
    output = decision.nadi_9_text
    
    if not output or output == "INSUFFICIENT_EVIDENCE":
        return True, []
    
    # Extract numbers from source
    source_numbers = set(re.findall(r'\b\d+\b', source))
    output_numbers = set(re.findall(r'\b\d+\b', output))
    
    missing_numbers = source_numbers - output_numbers
    if missing_numbers:
        issues.append(f"Numbers missing from output: {missing_numbers}")
    
    # Extract capitalized proper names (heuristic: capitalized words not at sentence start)
    words = source.split()
    proper_names = set()
    for i, w in enumerate(words):
        clean = re.sub(r'[^\w]', '', w)
        if clean and clean[0].isupper() and i > 0 and len(clean) > 1:
            proper_names.add(clean)
    
    for name in proper_names:
        if name.lower() not in output.lower():
            issues.append(f"Proper name '{name}' missing from output")
    
    return len(issues) == 0, issues