from typing import List, Dict


class DependencyGraph:
    """Maps evidence/rule IDs to the subtitle lines that depend on them."""

    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}

    def add_dependency(self, source_id: str, subtitle_id: str):
        if source_id not in self.dependencies:
            self.dependencies[source_id] = []
        if subtitle_id not in self.dependencies[source_id]:
            self.dependencies[source_id].append(subtitle_id)

    def get_impacted_subtitles(self, source_id: str) -> List[str]:
        return self.dependencies.get(source_id, [])

    def get_all_dependencies_for_subtitle(self, subtitle_id: str) -> List[str]:
        """Get all evidence IDs that a subtitle depends on."""
        return [
            source_id
            for source_id, subs in self.dependencies.items()
            if subtitle_id in subs
        ]