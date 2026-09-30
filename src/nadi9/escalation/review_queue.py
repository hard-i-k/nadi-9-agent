from typing import List, Dict, Any
from ..memory.claims import SubtitleDecision, DecisionType, ConflictRecord

NEVER_AUTOMATE = [
    "Resolving expert disagreements",
    "Approving status/kinship-sensitive lines with unresolved conflict",
    "Changing source precedence",
    "Releasing when any line is INSUFFICIENT_EVIDENCE",
]

class ReviewQueue:
    def __init__(self):
        self.queue: List[Dict[str, Any]] = []
        self.never_automate_violations: List[str] = []

    def process_decisions(self, decisions: List[SubtitleDecision], conflicts: List[ConflictRecord] = None):
        conflicts = conflicts or []
        unresolved_conflicts = [c for c in conflicts if not c.resolved]
        
        for d in decisions:
            if d.decision in [DecisionType.HUMAN_REVIEW, DecisionType.INSUFFICIENT_EVIDENCE]:
                entry = {
                    "subtitle_id": d.subtitle_id,
                    "source_text": d.source_text,
                    "nadi_9_text": d.nadi_9_text,
                    "confidence": d.confidence,
                    "confidence_reason": d.confidence_reason,
                    "review_question": d.review_question or "Manual review required",
                    "evidence": d.evidence,
                    "conflicts": d.conflicts,
                    "assumptions": d.assumptions,
                    "decision": d.decision.value if hasattr(d.decision, 'value') else str(d.decision),
                    "verification_issues": d.verification_results.issues if d.verification_results else []
                }
                self.queue.append(entry)
            
            # Check NEVER_AUTOMATE rules
            if d.decision == DecisionType.AUTO_APPROVE and d.conflicts:
                for conflict_id in d.conflicts:
                    if any(c.id == conflict_id and not c.resolved for c in conflicts):
                        self.never_automate_violations.append(
                            f"{d.subtitle_id}: Auto-approved despite unresolved conflict {conflict_id}"
                        )
                        d.decision = DecisionType.HUMAN_REVIEW
                        d.review_question = f"Overridden to HUMAN_REVIEW: unresolved conflict {conflict_id}"

    def get_queue(self) -> List[Dict[str, Any]]:
        return self.queue
    
    def has_insufficient_evidence(self, decisions: List[SubtitleDecision]) -> bool:
        return any(d.decision == DecisionType.INSUFFICIENT_EVIDENCE for d in decisions)
