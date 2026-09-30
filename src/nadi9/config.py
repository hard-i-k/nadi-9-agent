from pydantic import BaseModel, Field
from typing import Dict
from .memory.claims import EvidenceType

class PrecedencePolicy(BaseModel):
    # Lower number = higher precedence
    tiers: Dict[EvidenceType, int] = {
        EvidenceType.APPROVED_EXAMPLE: 1,
        EvidenceType.DICTIONARY_B: 2,
        EvidenceType.GRAMMAR_NOTE: 2,
        EvidenceType.EXPERT_NOTE: 3,
        EvidenceType.INTERVIEW: 4,
        EvidenceType.DICTIONARY_A: 5,
        EvidenceType.VIEWER_FEEDBACK: 6,
        EvidenceType.EPISODE_TRANSCRIPT: 99
    }

class Config(BaseModel):
    max_model_calls: int = 25
    max_tool_calls: int = 50
    precedence: PrecedencePolicy = Field(default_factory=PrecedencePolicy)
    data_dir: str = "fixtures"
    provider: str = "mock"

default_config = Config()
