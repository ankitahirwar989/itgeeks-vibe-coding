"""Create the pgvector extension and tables, without ingesting any data.

Usage:
    python scripts/seed_database.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.rag.db import init_db  # noqa: E402


def main():
    init_db()
    print("Database schema initialized (pgvector extension + tables created).")


if __name__ == "__main__":
    main()
