from typing import Any, List, Optional
from ..memory.claims import SubtitleDecision, VerificationResults, DecisionType, HypothesisRule
from ..evidence.registry import EvidenceRegistry
from ..providers.base import LLMProvider
from ..budget import BudgetManager
from .timing import check_timing
from .injection import check_injection
from .vocab import check_vocab
from .grammar import check_grammar
from .names_numbers import check_names_numbers
from .omissions import check_omissions
from .independent_llm_check import independent_llm_verify

class Verifier:
    """Independent verification pipeline. Deterministic checks first, optional LLM second."""
    
    def __init__(self, rules: Optional[List[HypothesisRule]] = None,
                 verifier_llm: Optional[LLMProvider] = None,
                 budget: Optional[BudgetManager] = None):
        self.rules = rules or []
        self.verifier_llm = verifier_llm
        self.budget = budget
    
    def verify(self, decision: SubtitleDecision, registry: Any) -> SubtitleDecision:
        """Run all verification checks on a subtitle decision."""
        if decision.decision == DecisionType.NOT_PROCESSED_BUDGET:
            return decision
        if not decision.nadi_9_text or decision.nadi_9_text == "INSUFFICIENT_EVIDENCE":
            decision.decision = DecisionType.INSUFFICIENT_EVIDENCE
            return decision

        results = VerificationResults()
        all_issues = []

        # 1. Timing check
        results.timing_valid, timing_issues = check_timing(decision)
        all_issues.extend(timing_issues)

        # 2. Injection check
        results.no_injection, injection_issues = check_injection(decision)
        all_issues.extend(injection_issues)

        # 3. Vocabulary check
        if registry is not None:
            results.vocab_supported, vocab_issues = check_vocab(decision, registry)
            if vocab_issues:
                all_issues.extend([f"Unsupported token: {t}" for t in vocab_issues])
        else:
            results.vocab_supported = True  # Can't check without registry

        # 4. Grammar check
        results.grammar_supported, grammar_issues = check_grammar(decision, self.rules)
        all_issues.extend(grammar_issues)

        # 5. Names and numbers check
        results.names_numbers_preserved, nn_issues = check_names_numbers(decision)
        all_issues.extend(nn_issues)

        # 6. Omissions check
        results.no_omissions, omission_issues = check_omissions(decision)
        all_issues.extend(omission_issues)

        # 7. Independent LLM check (optional, uses DIFFERENT prompt)
        if self.verifier_llm is not None:
            llm_passed, llm_issues = independent_llm_verify(
                decision, self.verifier_llm, self.budget, results
            )
            results.independent_check_passed = llm_passed
            all_issues.extend(llm_issues)

        results.issues = all_issues
        decision.verification_results = results

        # Decision logic
        if not results.no_injection:
            decision.decision = DecisionType.HUMAN_REVIEW
            decision.review_question = "Injection artifacts detected in translation output"
        elif not results.vocab_supported:
            decision.decision = DecisionType.HUMAN_REVIEW
            decision.review_question = f"Unsupported vocabulary found: {', '.join(all_issues)}"
        elif not results.timing_valid:
            decision.decision = DecisionType.HUMAN_REVIEW
            decision.review_question = f"Timing violations: {', '.join(timing_issues)}"
        elif all_issues:
            decision.decision = DecisionType.HUMAN_REVIEW
            decision.review_question = f"Verification issues: {'; '.join(all_issues[:3])}"
        # Don't override AUTO_APPROVE if everything passes

        return decision
