from typing import Dict, List, Optional
from ..memory.claims import EvidenceItem, EvidenceType
from ..config import PrecedencePolicy

class EvidenceRegistry:
    def __init__(self, precedence_policy: PrecedencePolicy):
        self.items: Dict[str, EvidenceItem] = {}
        self.precedence = precedence_policy
        self.quarantined_ids: set[str] = set()

    def add(self, item: EvidenceItem):
        if item.type in self.precedence.tiers:
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
            self.items[item_id].metadata['quarantine_reason'] = reason

    def get_by_type(self, ev_type: EvidenceType) -> List[EvidenceItem]:
        return [item for item in self.get_all_active() if item.type == ev_type]
