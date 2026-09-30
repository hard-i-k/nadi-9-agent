import json
from typing import List, Dict, Any
import logging
from ..memory.dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)

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
