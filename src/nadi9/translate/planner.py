from typing import List, Dict, Any

class TranslationPlanner:
    def plan(self, episode_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Rank by risk (humor, kinship, etc.)
        def risk_score(line):
            score = 0
            text = line.get("source_text", "").lower()
            if "brother" in text or "sister" in text or "elder" in text:
                score += 5 # Kinship risk
            if line.get("metadata", {}).get("humor", False):
                score += 3
            if line.get("metadata", {}).get("code_switching", False):
                score += 4
            return score
            
        return sorted(episode_lines, key=risk_score, reverse=True)
