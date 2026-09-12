"""Sanity-check the corpus and the eval dataset before ingesting or grading anything.

Checks:
  1. Every document in corpus/ parses into at least one citable section.
  2. Total corpus word count is at least 6,000 words.
  3. Every citation referenced in contradictions.md exists as a real parsed chunk.
  4. Every `expected_citations` entry in evals/questions.jsonl exists as a real parsed chunk.

Usage:
    python scripts/validate_corpus.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.ingestion.parser import parse_corpus  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = ROOT / "corpus"
QUESTIONS_PATH = ROOT / "evals" / "questions.jsonl"
CONTRADICTIONS_PATH = CORPUS_DIR / "contradictions.md"

CITATION_RE = re.compile(r"[\w\-]+\.(?:md|pdf)#[\w.\-]+")


def main() -> int:
    errors: list[str] = []

    sections = parse_corpus(CORPUS_DIR)
    known_citations = {s.citation for s in sections}
    total_words = sum(len(s.text.split()) for s in sections)

    print(f"Parsed {len(sections)} chunks, ~{total_words} words total.")
    if total_words < 6000:
        errors.append(f"Corpus has only ~{total_words} words; minimum required is 6,000.")

    if CONTRADICTIONS_PATH.exists():
        text = CONTRADICTIONS_PATH.read_text(encoding="utf-8")
        found = set(CITATION_RE.findall(text))
        for citation in found:
            if citation not in known_citations:
                errors.append(f"contradictions.md references unknown citation: {citation}")
        print(f"contradictions.md references {len(found)} citation-like strings.")
    else:
        errors.append("contradictions.md is missing.")

    if QUESTIONS_PATH.exists():
        states = {"ANSWERABLE": 0, "UNKNOWN": 0, "CONTRADICTION": 0}
        with QUESTIONS_PATH.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                state = record.get("expected_state")
                if state not in states:
                    errors.append(f"questions.jsonl line {line_no}: invalid expected_state {state!r}")
                    continue
                states[state] += 1
                for citation in record.get("expected_citations", []):
                    if citation not in known_citations:
                        errors.append(
                            f"questions.jsonl line {line_no} ({record.get('id')}): "
                            f"unknown expected citation {citation!r}"
                        )
        print(f"questions.jsonl state counts: {states}")
    else:
        errors.append("evals/questions.jsonl is missing.")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\nCorpus and eval dataset validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
