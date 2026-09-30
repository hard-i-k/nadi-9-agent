import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DependencyGraph:
    def __init__(self):
        # Maps evidence/rule ID -> List of subtitle IDs that depend on it
        self.dependencies: Dict[str, List[str]] = {}
        
    def add_dependency(self, source_id: str, subtitle_id: str):
        if source_id not in self.dependencies:
            self.dependencies[source_id] = []
        if subtitle_id not in self.dependencies[source_id]:
            self.dependencies[source_id].append(subtitle_id)

    def get_impacted_subtitles(self, source_id: str) -> List[str]:
        return self.dependencies.get(source_id, [])

class CorrectionHandler:
    def __init__(self, graph: DependencyGraph):
        self.graph = graph
        self.change_log = []

    def handle_correction(self, event: Dict[str, Any]) -> List[str]:
        event_type = event.get("type")
        source_id = event.get("target_id")
        logger.info(f"Applying correction: {event_type} on {source_id}")
        
        impacted = self.graph.get_impacted_subtitles(source_id)
        self.change_log.append({
            "event": event,
            "impacted_subtitles": impacted
        })
        return impacted
