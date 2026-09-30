from typing import List
from ..memory.claims import HypothesisRule, RuleStatus
from ..evidence.registry import EvidenceRegistry
from ..memory.claims import EvidenceType
import re


class RuleTester:
    """Deterministically tests each hypothesis rule against all approved examples."""

    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry

    def test_rules(self, rules: List[HypothesisRule]) -> List[HypothesisRule]:
        examples = self.registry.get_by_type(EvidenceType.APPROVED_EXAMPLE)

        for rule in rules:
            supporting = []
            contradicting = []

            for ex in examples:
                content_lower = ex.content.lower()
                rule_lower = rule.statement.lower()

                # Check if the example's content is consistent with the rule
                if self._rule_matches_example(rule, ex.content):
                    supporting.append(ex.id)
                elif self._rule_contradicts_example(rule, ex.content):
                    contradicting.append(ex.id)

            rule.supporting_evidence_ids = supporting
            rule.counterexample_ids = contradicting

            # Update status based on evidence
            if not supporting:
                rule.status = RuleStatus.UNSUPPORTED
                rule.confidence = 0.0
                rule.confidence_reason = "No supporting evidence found in approved examples."
            elif contradicting:
                rule.status = RuleStatus.CONTRADICTED
                rule.confidence = 0.2
                rule.confidence_reason = (
                    f"Supported by {len(supporting)} example(s) but contradicted by "
                    f"{len(contradicting)} example(s): {', '.join(contradicting)}"
                )
            elif len(supporting) == 1:
                rule.status = RuleStatus.WEAK
                rule.confidence = 0.5
                rule.confidence_reason = f"Supported by only 1 example: {supporting[0]}"
            else:
                rule.status = RuleStatus.SUPPORTED
                rule.confidence = min(0.95, 0.5 + len(supporting) * 0.1)
                rule.confidence_reason = f"Supported by {len(supporting)} approved examples."

        return rules

    def _rule_matches_example(self, rule: HypothesisRule, content: str) -> bool:
        """Check if an example supports the rule. Uses keyword matching."""
        content_lower = content.lower()
        rule_lower = rule.statement.lower()

        # Extract key terms from the rule statement
        key_terms = re.findall(r'[\w\-]+', rule_lower)
        # A rule matches if at least 2 key terms appear in the example
        matches = sum(1 for term in key_terms if term in content_lower and len(term) > 3)
        return matches >= 2

    def _rule_contradicts_example(self, rule: HypothesisRule, content: str) -> bool:
        """Check if an example contradicts the rule."""
        # For negation rules: check if source has negation but translation lacks 'na-'
        if rule.category == "negation":
            if ("not " in content.lower() or "don't" in content.lower()):
                if "na-" not in content.lower() and "na " not in content.lower():
                    return True
        return False
