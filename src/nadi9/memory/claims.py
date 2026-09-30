from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum

class EvidenceType(str, Enum):
    APPROVED_EXAMPLE = "approved_example"
    INTERVIEW = "interview"
    GRAMMAR_NOTE = "grammar_note"
    DICTIONARY_A = "dictionary_a"
    DICTIONARY_B = "dictionary_b"
    VIEWER_FEEDBACK = "viewer_feedback"
    EXPERT_NOTE = "expert_note"
    EPISODE_TRANSCRIPT = "episode_transcript"

class EvidenceItem(BaseModel):
    id: str
    type: EvidenceType
    content: str
    author: Optional[str] = None
    date: Optional[str] = None
    scope: Optional[str] = None
    precedence_tier: int = 99
    reliability_score: float = 1.0
    reliability_reasons: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=list)

class RuleStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    WEAK = "WEAK"
    CONTRADICTED = "CONTRADICTED"
    UNSUPPORTED = "UNSUPPORTED"

class HypothesisRule(BaseModel):
    id: str
    statement: str
    category: str
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    counterexample_ids: List[str] = Field(default_factory=list)
    status: RuleStatus = RuleStatus.UNSUPPORTED
    confidence: float = 0.0
    confidence_reason: str = ""
    context_conditions: Dict[str, str] = Field(default_factory=dict)

class DecisionType(str, Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_PROCESSED_BUDGET = "NOT_PROCESSED_BUDGET"

class VerificationResults(BaseModel):
    vocab_supported: bool = False
    grammar_supported: bool = False
    names_numbers_preserved: bool = False
    no_omissions: bool = False
    timing_valid: bool = False
    no_injection: bool = False
    independent_check_passed: Optional[bool] = None
    issues: List[str] = Field(default_factory=list)

class Timing(BaseModel):
    start: str
    end: str
    duration_sec: float
    chars_per_sec: float

class SubtitleDecision(BaseModel):
    subtitle_id: str
    source_text: str
    nadi_9_text: str = ""
    confidence: float = 0.0
    confidence_reason: str = ""
    decision: DecisionType = DecisionType.INSUFFICIENT_EVIDENCE
    evidence: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    review_question: Optional[str] = None
    verification_results: Optional[VerificationResults] = None
    timing: Optional[Timing] = None

class ConflictRecord(BaseModel):
    id: str
    description: str
    evidence_ids: List[str]
    resolved: bool = False
    resolution_note: Optional[str] = None
