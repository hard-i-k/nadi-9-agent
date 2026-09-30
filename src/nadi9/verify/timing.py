from typing import Tuple, List
from ..memory.claims import SubtitleDecision
import re

def parse_srt_time(t: str) -> float:
    """Parse SRT timestamp to seconds."""
    match = re.match(r'(\d+):(\d+):(\d+)[,\.](\d+)', t)
    if match:
        h, m, s, ms = match.groups()
        return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
    return 0.0

def check_timing(decision: SubtitleDecision) -> Tuple[bool, List[str]]:
    """Check subtitle timing constraints."""
    issues = []
    if not decision.timing:
        issues.append("No timing information")
        return False, issues
    
    # Duration check
    if decision.timing.duration_sec < 0.5:
        issues.append(f"Duration too short: {decision.timing.duration_sec}s (min 0.5s)")
    if decision.timing.duration_sec > 7.0:
        issues.append(f"Duration too long: {decision.timing.duration_sec}s (max 7.0s)")
    
    # Reading speed check (max 25 chars/sec)
    if decision.timing.chars_per_sec > 25:
        issues.append(f"Reading speed too fast: {decision.timing.chars_per_sec} chars/sec (max 25)")
    
    # Line length check (max 42 chars per line, max 2 lines)
    text = decision.nadi_9_text
    lines = text.split('\n')
    if len(lines) > 2:
        issues.append(f"Too many subtitle lines: {len(lines)} (max 2)")
    for i, line in enumerate(lines):
        if len(line) > 42:
            issues.append(f"Line {i+1} too long: {len(line)} chars (max 42)")
    
    # Total character check
    if len(text) > 84:
        issues.append(f"Total text too long: {len(text)} chars (max 84 for 2 lines)")
    
    return len(issues) == 0, issues