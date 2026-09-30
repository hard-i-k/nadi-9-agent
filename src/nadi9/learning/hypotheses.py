from typing import List
from ..memory.claims import HypothesisRule, RuleStatus
from ..evidence.registry import EvidenceRegistry
from ..providers.base import LLMProvider
import json

class HypothesisGenerator:
    def __init__(self, llm: LLMProvider, registry: EvidenceRegistry, budget: 'BudgetManager'):
        self.llm = llm
        self.registry = registry
        self.budget = budget

    def generate_rules(self) -> List[HypothesisRule]:
        # Gather grammar notes and examples
        grammar = self.registry.get_by_type('grammar_note')
        examples = self.registry.get_by_type('approved_example')
        
        prompt = "Extract language rules from the following evidence.\n"
        for g in grammar:
            prompt += f"Grammar Note {g.id}: {g.content}\n"
            
        # Simplified: mock generating rules
        self.budget.spend_model_call()
        res = self.llm.generate(prompt, system_prompt="Output JSON list of rules: [{id, statement, category}]")
        
        rules = []
        try:
            data = json.loads(res)
            for r in data:
                rules.append(HypothesisRule(
                    id=r.get("id"),
                    statement=r.get("statement"),
                    category=r.get("category")
                ))
        except:
            pass
        return rules
