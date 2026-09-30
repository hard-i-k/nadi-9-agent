from typing import List, Dict, Any
from ..memory.dependency_graph import DependencyGraph
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CorrectionHandler:
    """Handles correction events by finding impacted subtitles via dependency graph."""

    def __init__(self, graph: DependencyGraph):
        self.graph = graph
        self.change_log: List[Dict[str, Any]] = []

    def handle_correction(self, event: Dict[str, Any]) -> List[str]:
        """Process a correction event. Returns list of impacted subtitle IDs."""
        source_id = event.get("target_id", "")
        event_type = event.get("type", "unknown")
        logger.info(f"Applying correction: {event_type} on {source_id}")

        impacted = self.graph.get_impacted_subtitles(source_id)

        self.change_log.append({
            "event": event,
            "impacted_subtitles": impacted,
            "timestamp": datetime.now().isoformat(),
        })

        return impacted
