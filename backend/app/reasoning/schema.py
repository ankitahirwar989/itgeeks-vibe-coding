from pydantic import BaseModel, Field

from app.schemas.query import AnswerState


class LLMEvidenceItem(BaseModel):
    citation: str
    quote: str
    relevance: str = ""


class LLMContradictionPair(BaseModel):
    citation_a: str
    quote_a: str
    citation_b: str
    quote_b: str
    explanation: str


class LLMVerdict(BaseModel):
    state: AnswerState
    answer: str = Field(
        description=(
            "The final answer to show the user. For UNKNOWN, explain what is missing. "
            "For CONTRADICTION, summarize the conflict instead of picking a side."
        )
    )
    evidence: list[LLMEvidenceItem] = Field(default_factory=list)
    contradictions: list[LLMContradictionPair] = Field(default_factory=list)
    reasoning_notes: str = ""
