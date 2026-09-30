from typing import List, Dict, Any
from ..memory.claims import SubtitleDecision, DecisionType, Timing
from ..providers.base import LLMProvider
from ..budget import BudgetManager, BudgetExhaustedError
import json
import logging

logger = logging.getLogger(__name__)

class Translator:
    def __init__(self, llm: LLMProvider, budget: BudgetManager):
        self.llm = llm
        self.budget = budget

    def translate(self, plan: List[Dict[str, Any]], rules: List[Any], registry: Any) -> List[SubtitleDecision]:
        decisions = []
        for line in plan:
            try:
                self.budget.spend_model_call()
                # Mock translation prompt
                prompt = f"Translate: {line['source_text']}"
                res = self.llm.generate(prompt)
                
                try:
                    res_data = json.loads(res)
                except:
                    res_data = {"nadi_9_text": "MOCK", "decision": "HUMAN_REVIEW"}
                    
                dec = SubtitleDecision(
                    subtitle_id=line["id"],
                    source_text=line["source_text"],
                    nadi_9_text=res_data.get("nadi_9_text", ""),
                    confidence=res_data.get("confidence", 0.5),
                    decision=DecisionType(res_data.get("decision", "HUMAN_REVIEW")),
                    timing=Timing(
                        start=line.get("start", "00:00:00,000"),
                        end=line.get("end", "00:00:02,000"),
                        duration_sec=2.0,
                        chars_per_sec=len(res_data.get("nadi_9_text", "")) / 2.0
                    )
                )
                decisions.append(dec)
            except BudgetExhaustedError:
                logger.warning(f"Budget exhausted. Marking {line['id']} as NOT_PROCESSED_BUDGET")
                dec = SubtitleDecision(
                    subtitle_id=line["id"],
                    source_text=line["source_text"],
                    decision=DecisionType.NOT_PROCESSED_BUDGET
                )
                decisions.append(dec)
            except Exception as e:
                logger.error(f"Translation error: {e}")
                dec = SubtitleDecision(
                    subtitle_id=line["id"],
                    source_text=line["source_text"],
                    decision=DecisionType.HUMAN_REVIEW,
                    review_question="Translation tool failed."
                )
                decisions.append(dec)
                
        return decisions
