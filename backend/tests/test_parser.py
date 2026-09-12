from pathlib import Path

from app.ingestion.parser import parse_corpus

CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "corpus"


def _by_citation(chunks):
    return {c.citation: c for c in chunks}


def test_parses_all_documents_with_no_duplicate_citations():
    chunks = parse_corpus(CORPUS_DIR)
    citations = [c.citation for c in chunks]
    assert len(citations) == len(set(citations)), "citations must be unique across the corpus"
    assert len(chunks) > 50


def test_contradiction_1_sources_parse_with_conflicting_thresholds():
    chunks = _by_citation(parse_corpus(CORPUS_DIR))
    a = chunks["attendance_policy.md#3.1"]
    b = chunks["academic_regulations.pdf#8.2"]
    assert "75%" in a.text
    assert "under no circumstances" in a.text.lower()
    assert "60%" in b.text
    assert b.page == 2


def test_contradiction_2_sources_parse_with_conflicting_deadlines():
    chunks = _by_citation(parse_corpus(CORPUS_DIR))
    a = chunks["fee_deadlines.md#13.2"]
    b = chunks["rulebook.md#2.2"]
    assert "15 July" in a.text
    assert "will not be accepted" in a.text
    assert "31 July" in b.text
    assert "shall not be cancelled" in b.text


def test_contradiction_3_sources_parse_with_conflicting_scholarship_rules():
    chunks = _by_citation(parse_corpus(CORPUS_DIR))
    a = chunks["scholarship_policy.md#15.3"]
    b = chunks["academic_regulations.pdf#12.3"]
    assert "suspended" in a.text.lower()
    assert "retains" in b.text.lower()
    assert b.page == 6


def test_no_spurious_headings_from_wrapped_body_text():
    """Regression test: a hand-wrapped PDF body sentence that references another section
    number (e.g. "...described in Section\\n14.2 of the Fee Payment policy...") must never be
    split into its own heading/chunk."""
    chunks = _by_citation(parse_corpus(CORPUS_DIR))
    re_exam = chunks["academic_regulations.pdf#10.2"]
    assert "14.2 of the Fee Payment policy" in re_exam.text

    all_chunks = parse_corpus(CORPUS_DIR)
    bad = [c for c in all_chunks if c.heading.startswith("14.2 of the")]
    assert not bad
