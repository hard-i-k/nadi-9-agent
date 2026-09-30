from typing import List
from ..memory.claims import HypothesisRule, RuleStatus
from ..evidence.registry import EvidenceRegistry
from ..memory.claims import EvidenceType

class RuleTester:
    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry

    def test_rules(self, rules: List[HypothesisRule]) -> List[HypothesisRule]:
        examples = self.registry.get_by_type(EvidenceType.APPROVED_EXAMPLE)
        
        for rule in rules:
            # Deterministic test mock
            # In a real scenario, this would apply NLP or regex to check if the rule holds in the example
            # For this exercise, we'll use metadata from the mock rule to simulate this
            supported_by = []
            contradicted_by = []
            
            for ex in examples:
                if ex.id in rule.statement: # extremely naive mock logic
                    supported_by.append(ex.id)
                elif "contradicts:" + ex.id in rule.statement:
                    contradicted_by.append(ex.id)
                    
            rule.supporting_evidence_ids = supported_by
            rule.counterexample_ids = contradicted_by
            
            # Simulated rule unsupported logic
            if not rule.supporting_evidence_ids:
                rule.status = RuleStatus.UNSUPPORTED
                rule.confidence = 0.0
                rule.confidence_reason = "No supporting evidence found in approved examples."
            elif rule.counterexample_ids:
                rule.status = RuleStatus.CONTRADICTED
                rule.confidence = 0.2
                rule.confidence_reason = f"Contradicted by {len(rule.counterexample_ids)} examples."
            else:
                rule.status = RuleStatus.SUPPORTED
                rule.confidence = 0.9
                rule.confidence_reason = f"Supported by {len(rule.supporting_evidence_ids)} examples."
                
        return rules
