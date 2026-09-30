from typing import List, Tuple
from ..memory.claims import SubtitleDecision, HypothesisRule, RuleStatus

def check_grammar(decision: SubtitleDecision, rules: List[HypothesisRule]) -> Tuple[bool, List[str]]:
    """Check if the translation follows SUPPORTED grammar rules.
    Returns (all_pass, list_of_issues)."""
    issues = []
    supported_rules = [r for r in rules if r.status == RuleStatus.SUPPORTED]
    
    text = decision.nadi_9_text.lower()
    source = decision.source_text.lower()
    
    for rule in supported_rules:
        # Check negation rule
        if rule.category == "negation":
            if "not" in source or "don't" in source or "no " in source:
                if "na-" not in text and "na" not in text.split():
                    issues.append(f"Negation rule {rule.id} may be violated: source has negation but output lacks 'na-' prefix")
        
        # Check tense markers
        if rule.category == "tense":
            if any(w in source for w in ["was", "did", "came", "went", "had"]):
                if "-va" not in text:
                    issues.append(f"Past tense rule {rule.id} may be violated: source is past tense but output lacks '-va' marker")
            if any(w in source for w in ["will", "shall", "going to"]):
                if "-ki" not in text:
                    issues.append(f"Future tense rule {rule.id} may be violated: source is future tense but output lacks '-ki' marker")
        
        # Check respect markers
        if rule.category == "respect":
            if any(w in source for w in ["elder", "senior", "respected"]):
                if "-jin" not in text and "jin" not in text:
                    issues.append(f"Respect rule {rule.id} may be violated: elder address lacks '-jin' suffix")
    
    return len(issues) == 0, issues