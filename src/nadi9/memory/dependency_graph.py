from typing import List, Dict

class DependencyGraph:
    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}
        
    def add_dependency(self, source_id: str, subtitle_id: str):
        if source_id not in self.dependencies:
            self.dependencies[source_id] = []
        if subtitle_id not in self.dependencies[source_id]:
            self.dependencies[source_id].append(subtitle_id)

    def get_impacted_subtitles(self, source_id: str) -> List[str]:
        return self.dependencies.get(source_id, [])