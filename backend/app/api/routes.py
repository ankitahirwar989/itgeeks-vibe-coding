from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.rag.db import get_session
from app.models.chunk import Chunk
from app.schemas.query import QueryRequest, QueryResponse
from app.services.qa_service import ask

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/documents")
def list_documents():
    session = get_session()
    try:
        rows = session.execute(
            select(Chunk.source_file, func.count(Chunk.id)).group_by(Chunk.source_file)
        ).all()
        return {"documents": [{"source_file": r[0], "chunk_count": r[1]} for r in rows]}
    finally:
        session.close()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        return ask(request.question, top_k=request.top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Query failed: {exc}") from exc
