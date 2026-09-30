import os
import json
import glob
from .registry import EvidenceRegistry
from .sanitizer import Sanitizer
from ..memory.claims import EvidenceItem, EvidenceType

class EvidenceLoader:
    def __init__(self, registry: EvidenceRegistry, data_dir: str):
        self.registry = registry
        self.data_dir = data_dir

    def load_all(self):
        # We assume JSON files in data_dir representing different evidence types
        # e.g., approved_examples.json, dictionary_a.json, etc.
        for filepath in glob.glob(os.path.join(self.data_dir, "*.json")):
            self._load_file(filepath)
            
    def _load_file(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    for item_data in data:
                        self._process_item(item_data, filepath)
                elif isinstance(data, dict) and "items" in data:
                    for item_data in data["items"]:
                        self._process_item(item_data, filepath)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

    def _process_item(self, data: dict, source_file: str):
        content = data.get("content", "")
        item_id = data.get("id", f"auto-{len(self.registry.items)}")
        
        if not Sanitizer.check(content, item_id):
            # Quarantined at load time
            return
            
        item = EvidenceItem(
            id=item_id,
            type=EvidenceType(data.get("type", "expert_note")),
            content=content,
            author=data.get("author"),
            date=data.get("date"),
            scope=data.get("scope"),
            metadata=data.get("metadata", {})
        )
        self.registry.add(item)
