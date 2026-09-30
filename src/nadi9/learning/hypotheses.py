from typing import List, Dict, Any
from ..memory.claims import HypothesisRule, RuleStatus
from ..evidence.registry import EvidenceRegistry
from ..memory.claims import EvidenceType
from ..providers.base import LLMProvider
from ..budget import BudgetManager, BudgetExhaustedError
import json
import logging
import re

logger = logging.getLogger(__name__)


class HypothesisGenerator:
    """Extracts candidate language rules from evidence, then optionally uses LLM."""

    def __init__(self, llm: LLMProvider, registry: EvidenceRegistry, budget: BudgetManager):
        self.llm = llm
        self.registry = registry
        self.budget = budget

    def generate_rules(self) -> List[HypothesisRule]:
        rules: List[HypothesisRule] = []

        # 1. Deterministic extraction from grammar notes
        grammar_items = self.registry.get_by_type(EvidenceType.GRAMMAR_NOTE)
        for item in grammar_items:
            extracted = self._extract_from_grammar(item)
            rules.extend(extracted)

        # 2. Optional LLM-based extraction (spend budget carefully)
        try:
            self.budget.spend_model_call()
            examples = self.registry.get_by_type(EvidenceType.APPROVED_EXAMPLE)
            prompt = "Extract language rules from the following evidence.\n"
            for g in grammar_items[:5]:
                prompt += f"Grammar: {g.content}\n"
            for e in examples[:10]:
                prompt += f"Example: {e.content}\n"

            res = self.llm.generate(prompt, system_prompt="Output JSON list of rules")
            try:
                data = json.loads(res)
                if isinstance(data, list):
                    for r in data:
                        rule = HypothesisRule(
                            id=r.get("id", f"llm-{len(rules)}"),
                            statement=r.get("statement", r.get("description", "")),
                            category=r.get("category", "general"),
                        )
                        # LLM-proposed rules start as UNSUPPORTED until tested
                        rule.status = RuleStatus.UNSUPPORTED
                        rules.append(rule)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to parse LLM rules: {e}")
        except BudgetExhaustedError:
            logger.warning("Budget exhausted during hypothesis generation")

        return rules

    def _extract_from_grammar(self, item) -> List[HypothesisRule]:
        """Extract rules deterministically from grammar note content."""
        rules = []
        content = item.content.lower()

        # Look for common grammar patterns
        patterns = {
            "word_order": [r"(SOV|SVO|VSO|subject.*object.*verb|verb.*final)"],
            "tense": [r"(past tense|future tense|tense mark|-(va|ki))"],
            "negation": [r"(negat|prefix.*na-|na-.*prefix)"],
            "respect": [r"(respect|elder|-(jin|jina)|honorific|polite)"],
            "kinship": [r"(kinship|brother|sister|family|thama|kisa)"],
        }

        for category, pats in patterns.items():
            for pat in pats:
                if re.search(pat, content):
                    rule = HypothesisRule(
                        id=f"grammar-{category}-{item.id}",
                        statement=item.content,
                        category=category,
                        supporting_evidence_ids=[item.id],
                    )
                    rules.append(rule)
                    break

        return rules
