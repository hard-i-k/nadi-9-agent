from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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
    """A single piece of evidence with a stable ID and metadata."""
    id: str
    type: EvidenceType
    content: str
    author: Optional[str] = None
    date: Optional[str] = None
    scope: Optional[str] = None
    precedence_tier: int = 99
    reliability_score: float = 1.0
    reliability_reasons: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RuleStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    WEAK = "WEAK"
    CONTRADICTED = "CONTRADICTED"
    UNSUPPORTED = "UNSUPPORTED"


class HypothesisRule(BaseModel):
    """A language rule extracted from evidence, tested against examples."""
    id: str
    statement: str
    category: str  # word_order, tense, negation, respect, kinship, code_switching
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
    """Results from the independent verification pipeline."""
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
    """Full decision record for a single subtitle line. This is the required output format."""
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
    """Record of a disagreement between two evidence sources."""
    id: str
    description: str
    evidence_ids: List[str]
    resolved: bool = False
    resolution_note: Optional[str] = None


class StateSnapshot(BaseModel):
    """Versioned snapshot of pipeline state for auditability."""
    version: int
    timestamp: str
    active_rule_count: int
    active_conflict_count: int
    budget_model_calls: int
    budget_tool_calls: int
