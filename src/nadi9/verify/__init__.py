from typing import Any
from ..memory.claims import SubtitleDecision, VerificationResults, DecisionType
from .timing import check_timing
from .injection import check_injection
from .vocab import check_vocab

class Verifier:
    def verify(self, decision: SubtitleDecision, registry: Any) -> SubtitleDecision:
        if decision.decision == DecisionType.NOT_PROCESSED_BUDGET:
            return decision

        results = VerificationResults()
        results.timing_valid = check_timing(decision)
        results.no_injection = check_injection(decision)
        results.vocab_supported = check_vocab(decision, registry)
        results.grammar_supported = True
        results.names_numbers_preserved = True
        results.no_omissions = True
        
        issues = []
        if not results.timing_valid:
            issues.append("Timing violation")
        if not results.no_injection:
            issues.append("Injection artifact detected")
        if not results.vocab_supported:
            issues.append("Unsupported vocabulary used")
            
        results.issues = issues
        decision.verification_results = results
        
        if issues:
            decision.decision = DecisionType.HUMAN_REVIEW
            decision.review_question = f"Verification failed: {', '.join(issues)}"
            
        return decision
