from typing import Optional, Tuple, List
from ..memory.claims import SubtitleDecision, VerificationResults
from ..providers.base import LLMProvider
from ..budget import BudgetManager, BudgetExhaustedError
import json
import logging

logger = logging.getLogger(__name__)

def independent_llm_verify(
    decision: SubtitleDecision,
    llm: Optional[LLMProvider],
    budget: Optional[BudgetManager],
    deterministic_results: VerificationResults
) -> Tuple[Optional[bool], List[str]]:
    """Run an independent LLM check with a DIFFERENT prompt.
    Compares its judgment against deterministic results to detect
    'verifier agrees with translator's mistake' scenarios.
    Returns (passed_or_None, issues)."""
    
    if llm is None or budget is None:
        return None, ["Independent LLM check skipped: no provider available"]
    
    try:
        budget.spend_model_call()
    except BudgetExhaustedError:
        return None, ["Independent LLM check skipped: budget exhausted"]
    
    # Use a DIFFERENT prompt than the translator
    verify_prompt = (
        f"You are a VERIFICATION agent. You did NOT produce this translation.\n"
        f"Source text: {decision.source_text}\n"
        f"Proposed Nadi-9 translation: {decision.nadi_9_text}\n"
        f"Evidence used: {decision.evidence}\n"
        f"Does this translation look correct based on the evidence? "
        f"Reply with JSON: {{\"passed\": true/false, \"reason\": \"...\"}}\n"
    )
    
    try:
        response = llm.generate(verify_prompt, system_prompt="You are an independent translation verifier.")
        result = json.loads(response)
        llm_passed = result.get("passed", None)
        llm_reason = result.get("reason", "")
        
        issues = []
        # Detect disagreement between deterministic and LLM check
        det_passed = all([
            deterministic_results.vocab_supported,
            deterministic_results.grammar_supported,
            deterministic_results.timing_valid,
            deterministic_results.no_injection
        ])
        
        if llm_passed and not det_passed:
            issues.append(f"WARNING: LLM verifier approved but deterministic checks failed. "
                         f"Possible 'verifier agrees with translator mistake'. LLM reason: {llm_reason}")
        elif not llm_passed and det_passed:
            issues.append(f"LLM verifier disagreed with deterministic pass. LLM reason: {llm_reason}")
        
        return llm_passed, issues
        
    except Exception as e:
        logger.warning(f"Independent LLM check failed: {e}")
        return None, [f"Independent LLM check error: {str(e)}"]