from typing import List, Dict, Any
from ..evidence.registry import EvidenceRegistry
from ..memory.claims import HypothesisRule


class PlannedLine:
    """A line from the episode with its risk assessment."""
    def __init__(self, data: Dict[str, Any], risk_score: int, risk_reasons: List[str]):
        self.data = data
        self.risk_score = risk_score
        self.risk_reasons = risk_reasons


class TranslationPlanner:
    """Ranks episode lines by risk and plans budget allocation."""

    def plan(self, lines: List[Dict[str, Any]], registry: EvidenceRegistry = None,
             rules: List[HypothesisRule] = None) -> List[PlannedLine]:
        planned = []
        for line in lines:
            score, reasons = self._assess_risk(line, registry)
            planned.append(PlannedLine(data=line, risk_score=score, risk_reasons=reasons))

        # Sort by risk (highest first) to spend budget on risky lines first
        planned.sort(key=lambda p: p.risk_score, reverse=True)
        return planned

    def _assess_risk(self, line: Dict[str, Any], registry: EvidenceRegistry = None) -> tuple:
        score = 0
        reasons = []
        text = line.get("source_text", "").lower()
        meta = line.get("metadata", {})

        # Kinship terms
        if any(w in text for w in ["brother", "sister", "elder", "younger", "father", "mother"]):
            score += 5
            reasons.append("Contains kinship terms")

        # Metadata flags
        if meta.get("kinship"):
            score += 5
            reasons.append("Marked as kinship scene")
        if meta.get("humor"):
            score += 3
            reasons.append("Contains humor")
        if meta.get("code_switching"):
            score += 4
            reasons.append("Code-switching detected")
        if meta.get("ambiguous"):
            score += 4
            reasons.append("Ambiguous phrase")
        if meta.get("status_dependent"):
            score += 5
            reasons.append("Status-dependent meaning")

        # Unknown vocabulary check
        if registry:
            words = text.split()
            for w in words:
                if len(w) > 3 and not registry.find_by_word(w):
                    score += 1
                    reasons.append(f"Unknown word: {w}")

        if not reasons:
            reasons.append("Standard line")

        return score, reasons
