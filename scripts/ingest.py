"""Parse the corpus, embed every section, and load it into pgvector.

Usage:
    python scripts/ingest.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.ingestion.pipeline import ingest_corpus  # noqa: E402

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"


def main():
    count = ingest_corpus(CORPUS_DIR, reset=True)
    print(f"Ingested {count} chunks from {CORPUS_DIR}")


if __name__ == "__main__":
    main()
