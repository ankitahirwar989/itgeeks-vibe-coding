"""End-to-end ingestion: parse corpus -> embed -> upsert into pgvector."""
import time
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.ingestion.parser import SectionChunk, parse_corpus
from app.models.chunk import Chunk
from app.rag.db import SessionLocal, init_db
from app.rag.embeddings import embed_texts

EMBED_BATCH_SIZE = 64
EMBED_BATCH_DELAY_SECONDS = 5


def _batched(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def ingest_corpus(corpus_dir: Path, reset: bool = True) -> int:
    """Parse every document in corpus_dir, embed each section, and store it.

    Returns the number of chunks ingested.
    """
    init_db()
    sections: list[SectionChunk] = parse_corpus(corpus_dir)
    if not sections:
        return 0

    session = SessionLocal()
    try:
        if reset:
            session.execute(delete(Chunk))
            session.commit()

        total = 0
        for batch in _batched(sections, EMBED_BATCH_SIZE):
            vectors = embed_texts([s.text for s in batch])
            time.sleep(EMBED_BATCH_DELAY_SECONDS)
            for section, vector in zip(batch, vectors):
                citation = f"{section.source_file}#{section.section_id}"
                stmt = (
                    pg_insert(Chunk)
                    .values(
                        source_file=section.source_file,
                        section_id=section.section_id,
                        citation=citation,
                        heading=section.heading,
                        page=section.page,
                        text=section.text,
                        embedding=vector,
                    )
                    .on_conflict_do_update(
                        index_elements=["citation"],
                        set_={
                            "heading": section.heading,
                            "page": section.page,
                            "text": section.text,
                            "embedding": vector,
                        },
                    )
                )
                session.execute(stmt)
                total += 1
            session.commit()
        return total
    finally:
        session.close()
