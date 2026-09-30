from typing import List
from ..memory.claims import SubtitleDecision

def write_jsonl(decisions: List[SubtitleDecision], filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        for d in decisions:
            f.write(d.json() + "\n")