from .registry import EvidenceRegistry
from ..memory.claims import EvidenceType

class ReliabilityChecker:
    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry

    def check_dictionaries(self):
        examples = self.registry.get_by_type(EvidenceType.APPROVED_EXAMPLE)
        dict_a = self.registry.get_by_type(EvidenceType.DICTIONARY_A)
        dict_b = self.registry.get_by_type(EvidenceType.DICTIONARY_B)
        
        # Super simplified mock check for conflict
        # E.g., if dictionary content specifies "word=X" and example has "word=Y"
        # We simulate this by checking if the metadata has 'mock_conflict_with'
        
        for d_item in dict_a + dict_b:
            # For this exercise, we simulate a failure if it's explicitly poisoned in metadata
            if d_item.metadata.get("poisoned", False):
                self.registry.quarantine(d_item.id, "Failed cross-check with approved examples (poisoned)")
                
        # We also record conflicts between Dict A and Dict B if they define the same word differently
        # Handled in the memory state or planning phase.
