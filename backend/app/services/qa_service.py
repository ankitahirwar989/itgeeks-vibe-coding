from app.config import get_settings
from app.rag.db import get_session
from app.rag.retriever import retrieve
from app.reasoning.engine import answer_question
from app.schemas.query import QueryResponse


def ask(question: str, top_k: int | None = None) -> QueryResponse:
    settings = get_settings()
    k = top_k or settings.retrieval_top_k
    session = get_session()
    try:
        retrieved = retrieve(session, question, top_k=k)
        return answer_question(question, retrieved)
    finally:
        session.close()
