import os
import json
import logging
from typing import Dict
from .registry import EvidenceRegistry
from .sanitizer import Sanitizer
from ..memory.claims import EvidenceItem, EvidenceType

logger = logging.getLogger(__name__)

# Map filename stems to evidence types
FILE_TYPE_MAP = {
    "approved_examples": EvidenceType.APPROVED_EXAMPLE,
    "dictionary_a": EvidenceType.DICTIONARY_A,
    "dictionary_b": EvidenceType.DICTIONARY_B,
    "grammar_notes": EvidenceType.GRAMMAR_NOTE,
    "expert_notes": EvidenceType.EXPERT_NOTE,
    "viewer_feedback": EvidenceType.VIEWER_FEEDBACK,
    "interviews": EvidenceType.INTERVIEW,
    "injection_test": EvidenceType.VIEWER_FEEDBACK,  # loaded as feedback, should be caught by sanitizer
}


class EvidenceLoader:
    """Loads all evidence files from a data directory into the registry."""

    def __init__(self, registry: EvidenceRegistry, data_dir: str):
        self.registry = registry
        self.data_dir = data_dir
        self.load_summary: Dict[str, int] = {"loaded": 0, "quarantined": 0}

    def load_all(self) -> Dict[str, int]:
        """Load all evidence JSON files. Returns summary of loaded/quarantined counts."""
        for filename, ev_type in FILE_TYPE_MAP.items():
            filepath = os.path.join(self.data_dir, f"{filename}.json")
            if os.path.exists(filepath):
                self._load_file(filepath, ev_type)

        logger.info(f"Evidence loaded: {self.load_summary}")
        return self.load_summary

    def _load_file(self, filepath: str, default_type: EvidenceType):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    for item_data in data:
                        self._process_item(item_data, default_type)
                elif isinstance(data, dict):
                    if "items" in data:
                        for item_data in data["items"]:
                            self._process_item(item_data, default_type)
                    else:
                        self._process_item(data, default_type)
            except Exception as e:
                logger.error(f"Error loading {filepath}: {e}")

    def _process_item(self, data: dict, default_type: EvidenceType):
        content = data.get("content", "")
        item_id = data.get("id", f"auto-{len(self.registry.items)}")

        # Sanitize: check for prompt injection
        if not Sanitizer.check(content, item_id):
            self.load_summary["quarantined"] = self.load_summary.get("quarantined", 0) + 1
            logger.warning(f"Quarantined {item_id}: prompt injection detected")
            return

        # Determine type
        raw_type = data.get("type", default_type.value if hasattr(default_type, 'value') else str(default_type))
        try:
            ev_type = EvidenceType(raw_type)
        except ValueError:
            ev_type = default_type

        item = EvidenceItem(
            id=item_id,
            type=ev_type,
            content=content,
            author=data.get("author"),
            date=data.get("date"),
            scope=data.get("scope"),
            metadata=data.get("metadata", {}),
        )
        self.registry.add(item)
        self.load_summary["loaded"] = self.load_summary.get("loaded", 0) + 1
