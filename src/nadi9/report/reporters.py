import json
from typing import List
from ..memory.claims import SubtitleDecision

class Reporter:
    @staticmethod
    def write_srt(decisions: List[SubtitleDecision], filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            for idx, d in enumerate(decisions, 1):
                f.write(f"{idx}\n")
                if d.timing:
                    f.write(f"{d.timing.start} --> {d.timing.end}\n")
                else:
                    f.write("00:00:00,000 --> 00:00:02,000\n")
                f.write(f"{d.nadi_9_text}\n\n")

    @staticmethod
    def write_jsonl(decisions: List[SubtitleDecision], filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            for d in decisions:
                f.write(d.json() + "\n")

    @staticmethod
    def write_final_report(decisions: List[SubtitleDecision], filepath: str):
        total = len(decisions)
        review = sum(1 for d in decisions if d.decision == "HUMAN_REVIEW")
        insufficient = sum(1 for d in decisions if d.decision == "INSUFFICIENT_EVIDENCE")
        
        recommendation = "RELEASE"
        if review > 0:
            recommendation = "RELEASE WITH REVIEW"
        if insufficient > 0:
            recommendation = "DO NOT RELEASE"

        content = f"# Final Report\n\nRecommendation: {recommendation}\n"
        content += f"Total Lines: {total}\nNeeds Review: {review}\nInsufficient Evidence: {insufficient}\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
