import app.reasoning.engine as engine_module
from app.config import get_settings
from app.models.chunk import Chunk
from app.rag.retriever import RetrievedChunk
from app.reasoning.schema import LLMContradictionPair, LLMEvidenceItem, LLMVerdict
from app.schemas.query import AnswerState


def _chunk(citation, section_id, source_file, text, heading="", page=None):
    return Chunk(
        source_file=source_file,
        section_id=section_id,
        citation=citation,
        heading=heading or citation,
        page=page,
        text=text,
        embedding=[0.0] * get_settings().embedding_dim,
    )


def _retrieved(chunk):
    return RetrievedChunk(chunk=chunk, distance=0.1)


def test_answerable_with_hallucinated_citation_is_stripped_and_falls_back_to_unknown(monkeypatch):
    real_chunk = _chunk(
        "attendance_policy.md#3.1", "3.1", "attendance_policy.md", "Students must maintain 75% attendance."
    )
    retrieved = [_retrieved(real_chunk)]

    fake_verdict = LLMVerdict(
        state="ANSWERABLE",
        answer="The requirement is 75%.",
        evidence=[LLMEvidenceItem(citation="made_up_file.md#9.9", quote="anything", relevance="x")],
        contradictions=[],
        reasoning_notes="",
    )
    monkeypatch.setattr(engine_module, "_call_llm", lambda q, r: fake_verdict)

    result = engine_module.answer_question("What attendance is required?", retrieved)

    assert result.state == AnswerState.UNKNOWN
    assert result.citations == []


def test_answerable_with_real_citation_and_supported_quote_passes_through(monkeypatch):
    real_chunk = _chunk(
        "attendance_policy.md#3.1",
        "3.1",
        "attendance_policy.md",
        "Students must maintain at least 75% attendance in each registered course.",
    )
    retrieved = [_retrieved(real_chunk)]

    fake_verdict = LLMVerdict(
        state="ANSWERABLE",
        answer="Students must maintain at least 75% attendance.",
        evidence=[
            LLMEvidenceItem(
                citation="attendance_policy.md#3.1",
                quote="Students must maintain at least 75% attendance",
                relevance="direct rule",
            )
        ],
        contradictions=[],
        reasoning_notes="",
    )
    monkeypatch.setattr(engine_module, "_call_llm", lambda q, r: fake_verdict)

    result = engine_module.answer_question("What attendance is required?", retrieved)

    assert result.state == AnswerState.ANSWERABLE
    assert result.citations == ["attendance_policy.md#3.1"]
    assert len(result.evidence) == 1


def test_contradiction_with_one_unsupported_side_falls_back_to_unknown(monkeypatch):
    chunk_a = _chunk("attendance_policy.md#3.1", "3.1", "attendance_policy.md", "75% attendance required, no exceptions.")
    chunk_b = _chunk("academic_regulations.pdf#8.2", "8.2", "academic_regulations.pdf", "Medical exemption allows 60% attendance.")
    retrieved = [_retrieved(chunk_a), _retrieved(chunk_b)]

    fake_verdict = LLMVerdict(
        state="CONTRADICTION",
        answer="These conflict.",
        evidence=[],
        contradictions=[
            LLMContradictionPair(
                citation_a="attendance_policy.md#3.1",
                quote_a="75% attendance required, no exceptions.",
                citation_b="academic_regulations.pdf#8.2",
                quote_b="this text does not appear anywhere in the source chunk",
                explanation="conflict",
            )
        ],
        reasoning_notes="",
    )
    monkeypatch.setattr(engine_module, "_call_llm", lambda q, r: fake_verdict)

    result = engine_module.answer_question("Attendance with medical certificate?", retrieved)

    assert result.state == AnswerState.UNKNOWN


def test_verified_contradiction_passes_through(monkeypatch):
    chunk_a = _chunk("attendance_policy.md#3.1", "3.1", "attendance_policy.md", "75% attendance required, no exceptions.")
    chunk_b = _chunk("academic_regulations.pdf#8.2", "8.2", "academic_regulations.pdf", "Medical exemption allows 60% attendance.")
    retrieved = [_retrieved(chunk_a), _retrieved(chunk_b)]

    fake_verdict = LLMVerdict(
        state="CONTRADICTION",
        answer="These conflict.",
        evidence=[],
        contradictions=[
            LLMContradictionPair(
                citation_a="attendance_policy.md#3.1",
                quote_a="75% attendance required, no exceptions.",
                citation_b="academic_regulations.pdf#8.2",
                quote_b="Medical exemption allows 60% attendance.",
                explanation="conflict",
            )
        ],
        reasoning_notes="",
    )
    monkeypatch.setattr(engine_module, "_call_llm", lambda q, r: fake_verdict)

    result = engine_module.answer_question("Attendance with medical certificate?", retrieved)

    assert result.state == AnswerState.CONTRADICTION
    assert set(result.citations) == {"attendance_policy.md#3.1", "academic_regulations.pdf#8.2"}
    assert len(result.contradictions) == 1


def test_no_retrieved_evidence_returns_unknown():
    result = engine_module.answer_question("Some question with no matches", [])
    assert result.state == AnswerState.UNKNOWN
    assert result.citations == []
