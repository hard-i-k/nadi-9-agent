from typing import List
from ..memory.claims import SubtitleDecision

def write_srt(decisions: List[SubtitleDecision], filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        for idx, d in enumerate(decisions, 1):
            f.write(f"{idx}\n")
            if d.timing:
                f.write(f"{d.timing.start} --> {d.timing.end}\n")
            else:
                f.write("00:00:00,000 --> 00:00:02,000\n")
            f.write(f"{d.nadi_9_text}\n\n")