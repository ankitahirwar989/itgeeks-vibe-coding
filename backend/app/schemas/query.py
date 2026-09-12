from enum import Enum

from pydantic import BaseModel, Field


class AnswerState(str, Enum):
    ANSWERABLE = "ANSWERABLE"
    UNKNOWN = "UNKNOWN"
    CONTRADICTION = "CONTRADICTION"


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class Citation(BaseModel):
    citation: str  # e.g. "attendance_policy.md#3.1"
    source_file: str
    section_id: str
    heading: str = ""
    page: int | None = None
    text: str


class EvidenceItem(BaseModel):
    citation: str
    quote: str
    relevance: str = ""


class ContradictionPair(BaseModel):
    claim_a: EvidenceItem
    claim_b: EvidenceItem
    explanation: str


class QueryResponse(BaseModel):
    question: str
    state: AnswerState
    answer: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    contradictions: list[ContradictionPair] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    retrieved: list[Citation] = Field(default_factory=list)
    reasoning_notes: str = ""
