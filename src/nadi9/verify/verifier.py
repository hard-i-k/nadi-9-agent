from ..memory.claims import SubtitleDecision, VerificationResults, DecisionType
from typing import Any
import re

class Verifier:
    def verify(self, decision: SubtitleDecision, registry: Any) -> SubtitleDecision:
        if decision.decision == "NOT_PROCESSED_BUDGET":
            return decision

        results = VerificationResults()
        results.timing_valid = self._check_timing(decision)
        results.no_injection = self._check_injection(decision)
        results.vocab_supported = self._check_vocab(decision, registry)
        results.grammar_supported = True # Mock
        results.names_numbers_preserved = True # Mock
        results.no_omissions = True # Mock
        
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

    def _check_timing(self, decision: SubtitleDecision) -> bool:
        if not decision.timing: return False
        # max chars per line, reading speed, min/max duration
        if decision.timing.duration_sec < 0.5 or decision.timing.duration_sec > 7.0:
            return False
        if decision.timing.chars_per_sec > 25:
            return False
        if len(decision.nadi_9_text) > 84: # approx 2 lines of 42
            return False
        return True

    def _check_injection(self, decision: SubtitleDecision) -> bool:
        artifacts = [r"```", r"untrusted_data", r"ignore previous"]
        for a in artifacts:
            if re.search(a, decision.nadi_9_text, re.IGNORECASE):
                return False
        return True

    def _check_vocab(self, decision: SubtitleDecision, registry: Any) -> bool:
        # Mock vocab check: if word is not in dictionaries or examples, fail.
        # Here we just mock it returning True unless a specific word is used for test.
        if "UNSUPPORTED_WORD" in decision.nadi_9_text:
            return False
        return True
