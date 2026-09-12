"""Standalone utility: parse the corpus and print embedding stats without writing to the
database. Useful for sanity-checking embedding cost/dimension before running the full
ingest. Usage:

    python scripts/generate_embeddings.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import get_settings  # noqa: E402
from app.ingestion.parser import parse_corpus  # noqa: E402
from app.rag.embeddings import embed_texts  # noqa: E402

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"


def main():
    settings = get_settings()
    sections = parse_corpus(CORPUS_DIR)
    print(f"Parsed {len(sections)} sections from {CORPUS_DIR}")
    if not sections:
        return
    sample = sections[:1]
    vectors = embed_texts([s.text for s in sample])
    print(f"Embedding model: {settings.embedding_model}")
    print(f"Vector dimension returned: {len(vectors[0])} (configured: {settings.embedding_dim})")


if __name__ == "__main__":
    main()
