from typing import List, Dict, Any
from ..memory.claims import SubtitleDecision, DecisionType, Timing
from ..evidence.registry import EvidenceRegistry
from ..evidence.sanitizer import Sanitizer
from ..memory.dependency_graph import DependencyGraph
from ..providers.base import LLMProvider
from ..budget import BudgetManager, BudgetExhaustedError
from .planner import PlannedLine
import json
import logging

logger = logging.getLogger(__name__)


class Translator:
    """Produces timed subtitle proposals per line, tracking evidence usage."""

    def __init__(self, llm: LLMProvider, budget: BudgetManager,
                 dep_graph: DependencyGraph = None):
        self.llm = llm
        self.budget = budget
        self.dep_graph = dep_graph or DependencyGraph()

    def translate(self, plan: List[PlannedLine], rules: List[Any],
                  registry: EvidenceRegistry) -> List[SubtitleDecision]:
        decisions = []
        for planned in plan:
            line = planned.data
            try:
                self.budget.spend_model_call()

                # Build prompt with evidence
                relevant_evidence = registry.find_by_word(line.get("source_text", "").split()[0]) if line.get("source_text") else []

                prompt = f"Translate: {line['source_text']}"

                # Wrap evidence as untrusted data
                for ev in relevant_evidence[:5]:
                    wrapped = Sanitizer.wrap_for_prompt(ev.content)
                    prompt += f"\nEvidence {ev.id}: {wrapped}"

                res = self.llm.generate(prompt)

                try:
                    res_data = json.loads(res)
                except (json.JSONDecodeError, Exception):
                    res_data = {"nadi_9_text": "", "decision": "HUMAN_REVIEW",
                               "confidence": 0.3, "confidence_reason": "Failed to parse LLM response"}

                # Build timing
                start = line.get("start", "00:00:00,000")
                end = line.get("end", "00:00:02,000")
                nadi_text = res_data.get("nadi_9_text", "")
                duration = self._parse_duration(start, end)
                cps = len(nadi_text) / max(duration, 0.1)

                # Parse decision
                raw_decision = res_data.get("decision", "HUMAN_REVIEW")
                try:
                    decision_type = DecisionType(raw_decision)
                except ValueError:
                    decision_type = DecisionType.HUMAN_REVIEW

                # Build evidence list
                evidence_ids = res_data.get("evidence", [])
                if not evidence_ids:
                    evidence_ids = [ev.id for ev in relevant_evidence[:5]]

                dec = SubtitleDecision(
                    subtitle_id=line["id"],
                    source_text=line["source_text"],
                    nadi_9_text=nadi_text,
                    confidence=res_data.get("confidence", 0.5),
                    confidence_reason=res_data.get("confidence_reason",
                                                    f"Based on {len(evidence_ids)} evidence items"),
                    decision=decision_type,
                    evidence=evidence_ids,
                    assumptions=res_data.get("assumptions", []),
                    conflicts=res_data.get("conflicts", []),
                    review_question=res_data.get("review_question"),
                    timing=Timing(
                        start=start, end=end,
                        duration_sec=duration, chars_per_sec=cps
                    ),
                )

                # Track dependencies
                for ev_id in evidence_ids:
                    self.dep_graph.add_dependency(ev_id, line["id"])

                decisions.append(dec)

            except BudgetExhaustedError:
                logger.warning(f"Budget exhausted at {line['id']}")
                dec = SubtitleDecision(
                    subtitle_id=line["id"],
                    source_text=line["source_text"],
                    decision=DecisionType.NOT_PROCESSED_BUDGET,
                    confidence_reason="Model call budget exhausted",
                )
                decisions.append(dec)

            except Exception as e:
                logger.error(f"Translation error for {line.get('id', '?')}: {e}")
                dec = SubtitleDecision(
                    subtitle_id=line.get("id", "unknown"),
                    source_text=line.get("source_text", ""),
                    decision=DecisionType.HUMAN_REVIEW,
                    review_question=f"Translation failed: {str(e)}",
                    confidence_reason="Translation tool failure",
                )
                decisions.append(dec)

        return decisions

    def _parse_duration(self, start: str, end: str) -> float:
        """Parse SRT timestamps and return duration in seconds."""
        import re
        def to_sec(t):
            m = re.match(r'(\d+):(\d+):(\d+)[,.](\d+)', t)
            if m:
                h, mi, s, ms = m.groups()
                return int(h)*3600 + int(mi)*60 + int(s) + int(ms)/1000
            return 0.0
        return max(0.1, to_sec(end) - to_sec(start))
