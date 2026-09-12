from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.rag.embeddings import embed_query


@dataclass
class RetrievedChunk:
    chunk: Chunk
    distance: float

    @property
    def similarity(self) -> float:
        # cosine_distance in pgvector is in [0, 2]; convert to a rough similarity in [0, 1].
        return max(0.0, 1.0 - self.distance / 2.0)


def retrieve(session: Session, question: str, top_k: int = 8) -> list[RetrievedChunk]:
    query_vector = embed_query(question)
    distance = Chunk.embedding.cosine_distance(query_vector)
    stmt = select(Chunk, distance.label("distance")).order_by(distance).limit(top_k)
    rows = session.execute(stmt).all()
    return [RetrievedChunk(chunk=row[0], distance=float(row[1])) for row in rows]
