from typing import List, Dict, Any
from pydantic import BaseModel
from nadi9.memory.claims import Rule, SubtitleDecision

class ImpactReport(BaseModel):
    affected_rules: List[str]
    affected_subtitles: List[str]
    severity: str

class ImpactAnalyzer:
    def analyze_impact(self, event: Dict[str, Any], graph: Dict[str, List[str]], rules: List[Rule], decisions: List[SubtitleDecision]) -> ImpactReport:
        item_id = event.get("item_id", "")
        event_type = event.get("event_type", "")
        
        affected_rules = []
        affected_subs = []
        
        # Find affected rules
        for rule in rules:
            if item_id in rule.evidence_ids:
                affected_rules.append(rule.id)
        
        # Find affected subtitles (transitive closure)
        queue = [item_id] + affected_rules
        visited = set(queue)
        
        while queue:
            curr = queue.pop(0)
            for sub_id, deps in graph.items():
                if curr in deps and sub_id not in visited:
                    visited.add(sub_id)
                    queue.append(sub_id)
                    affected_subs.append(sub_id)
                    
        severity = "LOW"
        if len(affected_subs) > 10 or event_type == "model_outage":
            severity = "HIGH"
        elif len(affected_subs) > 0 or len(affected_rules) > 0:
            severity = "MEDIUM"
            
        return ImpactReport(
            affected_rules=affected_rules,
            affected_subtitles=affected_subs,
            severity=severity
        )