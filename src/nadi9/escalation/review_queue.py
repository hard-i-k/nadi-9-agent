from typing import List
from ..memory.claims import SubtitleDecision, DecisionType

class ReviewQueue:
    def __init__(self):
        self.queue = []

    def process_decisions(self, decisions: List[SubtitleDecision]):
        for d in decisions:
            if d.decision in [DecisionType.HUMAN_REVIEW, DecisionType.INSUFFICIENT_EVIDENCE]:
                self.queue.append({
                    "subtitle_id": d.subtitle_id,
                    "source_text": d.source_text,
                    "nadi_9_text": d.nadi_9_text,
                    "review_question": d.review_question,
                    "status": d.decision.value if hasattr(d.decision, 'value') else str(d.decision)
                })

    def get_queue(self):
        return self.queue
