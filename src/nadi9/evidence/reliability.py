import re
import logging
from typing import List, Tuple
from .registry import EvidenceRegistry
from ..memory.claims import EvidenceType, ConflictRecord

logger = logging.getLogger(__name__)


class ReliabilityChecker:
    """Cross-checks dictionaries against approved examples, detects conflicts and poisoned entries."""

    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry

    def check_all(self) -> Tuple[List[ConflictRecord], List[str]]:
        """Run all reliability checks. Returns (conflicts, quarantined_ids)."""
        quarantined_ids: List[str] = []
        conflicts: List[ConflictRecord] = []

        # 1. Quarantine poisoned entries
        for item in list(self.registry.items.values()):
            if item.metadata.get("poisoned", False):
                self.registry.quarantine(item.id, "Failed cross-check: metadata.poisoned=True")
                quarantined_ids.append(item.id)
                logger.warning(f"Quarantined {item.id}: poisoned entry")

        # 2. Find conflicts between Dictionary A and Dictionary B
        dict_a = self.registry.get_by_type(EvidenceType.DICTIONARY_A)
        dict_b = self.registry.get_by_type(EvidenceType.DICTIONARY_B)

        def extract_word_and_nadi9(content: str):
            """Parse 'word: X | nadi9: Y' format."""
            word_match = re.search(r'word:\s*(\w+)', content, re.IGNORECASE)
            nadi9_match = re.search(r'nadi9:\s*([\w\-]+)', content, re.IGNORECASE)
            if word_match and nadi9_match:
                return word_match.group(1).lower(), nadi9_match.group(1).lower()
            return None, None

        # Build word -> (item, nadi9_translation) maps
        a_map = {}
        for item in dict_a:
            word, nadi9 = extract_word_and_nadi9(item.content)
            if word and nadi9:
                a_map[word] = (item, nadi9)

        b_map = {}
        for item in dict_b:
            word, nadi9 = extract_word_and_nadi9(item.content)
            if word and nadi9:
                b_map[word] = (item, nadi9)

        # Find words present in both with different translations
        for word in set(a_map.keys()) & set(b_map.keys()):
            item_a, trans_a = a_map[word]
            item_b, trans_b = b_map[word]
            if trans_a != trans_b:
                conflict = ConflictRecord(
                    id=f"conflict:{word}:{item_a.id}_vs_{item_b.id}",
                    description=f"Dictionary conflict for '{word}': A says '{trans_a}', B says '{trans_b}'",
                    evidence_ids=[item_a.id, item_b.id]
                )
                conflicts.append(conflict)
                self.registry.add_conflict(conflict)
                logger.info(f"Conflict detected: {conflict.description}")

        # 3. Cross-check dictionary entries against approved examples
        examples = self.registry.get_by_type(EvidenceType.APPROVED_EXAMPLE)
        for word, (item, nadi9_word) in {**a_map, **b_map}.items():
            support_count = sum(1 for ex in examples if nadi9_word in ex.content.lower())
            item.reliability_score = min(1.0, support_count * 0.25)
            if support_count > 0:
                item.reliability_reasons.append(f"Confirmed by {support_count} approved example(s)")
            else:
                item.reliability_reasons.append("No confirmation in approved examples")

        return conflicts, quarantined_ids
