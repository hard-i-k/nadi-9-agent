from typing import List
from ..memory.claims import SubtitleDecision, DecisionType

def write_final_report(decisions: List[SubtitleDecision], filepath: str):
    total = len(decisions)
    review = sum(1 for d in decisions if d.decision == DecisionType.HUMAN_REVIEW)
    insufficient = sum(1 for d in decisions if d.decision == DecisionType.INSUFFICIENT_EVIDENCE)
    
    recommendation = "RELEASE"
    if review > 0:
        recommendation = "RELEASE WITH REVIEW"
    if insufficient > 0:
        recommendation = "DO NOT RELEASE"

    content = f"# Final Report\n\nRecommendation: {recommendation}\n"
    content += f"Total Lines: {total}\nNeeds Review: {review}\nInsufficient Evidence: {insufficient}\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)