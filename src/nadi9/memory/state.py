from typing import List, Dict, Any, Optional
from ..memory.claims import HypothesisRule, SubtitleDecision, ConflictRecord, StateSnapshot
from ..evidence.registry import EvidenceRegistry
from .dependency_graph import DependencyGraph
from datetime import datetime


class PipelineState:
    """Tracks the entire pipeline state with versioning for auditability."""

    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry
        self.rules: List[HypothesisRule] = []
        self.conflicts: List[ConflictRecord] = []
        self.decisions: Dict[str, SubtitleDecision] = {}
        self.dependency_graph = DependencyGraph()
        self.change_log: List[Dict[str, Any]] = []
        self._version = 0

    def set_rules(self, rules: List[HypothesisRule]):
        self.rules = rules
        self._version += 1

    def set_conflicts(self, conflicts: List[ConflictRecord]):
        self.conflicts = conflicts
        self._version += 1

    def add_decision(self, decision: SubtitleDecision):
        self.decisions[decision.subtitle_id] = decision
        self._version += 1

    def record_change(self, what: str, why: str, old: str, new: str):
        self.change_log.append({
            "what": what,
            "why": why,
            "old": old,
            "new": new,
            "version": self._version,
            "timestamp": datetime.now().isoformat(),
        })
        self._version += 1

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(
            version=self._version,
            timestamp=datetime.now().isoformat(),
            active_rule_count=len(self.rules),
            active_conflict_count=len(self.conflicts),
            budget_model_calls=0,
            budget_tool_calls=0,
        )

    def get_version(self) -> int:
        return self._version