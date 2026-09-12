import json

from google.genai import types

from app.citations.verifier import verify_citation
from app.config import get_settings
from app.rag.embeddings import get_genai_client
from app.rag.retriever import RetrievedChunk
from app.reasoning.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, format_evidence_block
from app.reasoning.schema import LLMVerdict
from app.schemas.query import AnswerState, Citation, ContradictionPair, EvidenceItem, QueryResponse

NO_EVIDENCE_ANSWER = (
    "UNKNOWN — No passage in the rulebook corpus is relevant enough to this question to "
    "answer it. The rulebook does not appear to address this scenario."
)


def _call_llm(question: str, retrieved: list[RetrievedChunk]) -> LLMVerdict:
    settings = get_settings()
    client = get_genai_client()
    evidence_block = format_evidence_block(retrieved)
    user_prompt = USER_PROMPT_TEMPLATE.format(question=question, evidence_block=evidence_block)

    response = client.models.generate_content(
        model=settings.llm_model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=LLMVerdict,
            max_output_tokens=settings.max_output_tokens,
            temperature=0,
        ),
    )
    if response.parsed is not None:
        return response.parsed
    print("RAW LLM RESPONSE:", repr(response.text))
    return LLMVerdict.model_validate(json.loads(response.text))


def _build_citation(chunk_map: dict[str, RetrievedChunk], citation_id: str) -> Citation | None:
    item = chunk_map.get(citation_id)
    if item is None:
        return None
    c = item.chunk
    return Citation(
        citation=c.citation,
        source_file=c.source_file,
        section_id=c.section_id,
        heading=c.heading,
        page=c.page,
        text=c.text,
    )


def answer_question(question: str, retrieved: list[RetrievedChunk]) -> QueryResponse:
    if not retrieved:
        return QueryResponse(
            question=question,
            state=AnswerState.UNKNOWN,
            answer=NO_EVIDENCE_ANSWER,
            evidence=[],
            contradictions=[],
            citations=[],
            retrieved=[],
            reasoning_notes="No evidence was retrieved from the corpus for this question.",
        )

    chunk_map = {item.chunk.citation: item for item in retrieved}
    known_text = {item.chunk.citation: item.chunk.text for item in retrieved}

    verdict = _call_llm(question, retrieved)

    # --- Guardrail pass: drop any evidence item whose citation or quote is not actually
    # backed by the retrieved corpus text. This is what keeps the system "evidence-first"
    # even if the LLM tries to cite something it wasn't given. ---
    verified_evidence: list[EvidenceItem] = []
    for e in verdict.evidence:
        result = verify_citation(e.citation, e.quote, known_text)
        if result.citation_exists and result.quote_supported:
            verified_evidence.append(EvidenceItem(citation=e.citation, quote=e.quote, relevance=e.relevance))

    verified_contradictions: list[ContradictionPair] = []
    for pair in verdict.contradictions:
        r_a = verify_citation(pair.citation_a, pair.quote_a, known_text)
        r_b = verify_citation(pair.citation_b, pair.quote_b, known_text)
        if r_a.citation_exists and r_a.quote_supported and r_b.citation_exists and r_b.quote_supported:
            verified_contradictions.append(
                ContradictionPair(
                    claim_a=EvidenceItem(citation=pair.citation_a, quote=pair.quote_a),
                    claim_b=EvidenceItem(citation=pair.citation_b, quote=pair.quote_b),
                    explanation=pair.explanation,
                )
            )

    state = verdict.state

    # If the model claimed CONTRADICTION but none of its contradiction pairs survive
    # verification, we cannot trust the claim — fail safe to UNKNOWN rather than showing an
    # unverifiable contradiction.
    if state == AnswerState.CONTRADICTION and not verified_contradictions:
        state = AnswerState.UNKNOWN

    # If the model claimed ANSWERABLE but no evidence survives verification, we cannot show
    # an answer with no backing — fail safe to UNKNOWN.
    if state == AnswerState.ANSWERABLE and not verified_evidence:
        state = AnswerState.UNKNOWN

    citations: list[str] = []
    if state == AnswerState.CONTRADICTION:
        for pair in verified_contradictions:
            citations.extend([pair.claim_a.citation, pair.claim_b.citation])
    else:
        citations = [e.citation for e in verified_evidence]
    citations = sorted(set(citations))

    retrieved_citations = [
        c for c in (_build_citation(chunk_map, item.chunk.citation) for item in retrieved) if c
    ]

    answer = verdict.answer
    if state == AnswerState.UNKNOWN and not answer.upper().startswith("UNKNOWN"):
        answer = f"UNKNOWN — {answer}"
    if state == AnswerState.CONTRADICTION and "CONTRADICTION" not in answer.upper():
        answer = f"CONTRADICTION DETECTED — {answer}"

    return QueryResponse(
        question=question,
        state=state,
        answer=answer,
        evidence=verified_evidence if state != AnswerState.CONTRADICTION else [],
        contradictions=verified_contradictions if state == AnswerState.CONTRADICTION else [],
        citations=citations,
        retrieved=retrieved_citations,
        reasoning_notes=verdict.reasoning_notes,
    )
