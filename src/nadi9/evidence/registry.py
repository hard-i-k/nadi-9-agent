from typing import List, Dict, Any, Optional, Set
from ..memory.claims import EvidenceItem, EvidenceType, ConflictRecord
from ..config import PrecedencePolicy
import re


class EvidenceRegistry:
    """Central registry for all evidence items with precedence, quarantine, and conflict tracking."""

    def __init__(self, precedence_policy: Optional[PrecedencePolicy] = None):
        self.items: Dict[str, EvidenceItem] = {}
        self.precedence = precedence_policy
        self.quarantined_ids: Set[str] = set()
        self.conflicts: Dict[str, ConflictRecord] = {}

    def add(self, item: EvidenceItem):
        if self.precedence and item.type in self.precedence.tiers:
            item.precedence_tier = self.precedence.tiers[item.type]
        self.items[item.id] = item

    def get(self, item_id: str) -> Optional[EvidenceItem]:
        if item_id in self.quarantined_ids:
            return None
        return self.items.get(item_id)

    def get_all_active(self) -> List[EvidenceItem]:
        return [item for item in self.items.values() if item.id not in self.quarantined_ids]

    def quarantine(self, item_id: str, reason: str):
        if item_id in self.items:
            self.quarantined_ids.add(item_id)
            self.items[item_id].metadata["quarantine_reason"] = reason

    def get_by_type(self, ev_type: EvidenceType) -> List[EvidenceItem]:
        return [item for item in self.get_all_active() if item.type == ev_type]

    def find_by_word(self, word: str) -> List[EvidenceItem]:
        """Search active evidence for items containing a specific word."""
        word_lower = word.lower()
        return [item for item in self.get_all_active() if word_lower in item.content.lower()]

    def add_conflict(self, conflict: ConflictRecord):
        self.conflicts[conflict.id] = conflict

    def get_conflicts_for(self, item_id: str) -> List[ConflictRecord]:
        return [c for c in self.conflicts.values() if item_id in c.evidence_ids]

    def get_all_conflicts(self) -> List[ConflictRecord]:
        return list(self.conflicts.values())

    def get_stats(self) -> Dict[str, Any]:
        stats: Dict[str, Any] = {"total": len(self.items), "quarantined": len(self.quarantined_ids), "by_type": {}}
        for item in self.items.values():
            t = item.type.value if hasattr(item.type, 'value') else str(item.type)
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
        stats["conflicts"] = len(self.conflicts)
        return stats
