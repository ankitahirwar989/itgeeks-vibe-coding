"""Deterministic scoring for a single QA system response against a gold record."""
from dataclasses import dataclass


@dataclass
class ScoredResult:
    id: str
    question: str
    expected_state: str
    actual_state: str
    state_correct: bool
    citation_precision: float
    citation_recall: float
    citation_f1: float


def score_citations(expected: list[str], actual: list[str]) -> tuple[float, float, float]:
    expected_set, actual_set = set(expected), set(actual)
    if not expected_set and not actual_set:
        return 1.0, 1.0, 1.0
    if not actual_set:
        return 0.0, 0.0, 0.0
    if not expected_set:
        # No citations expected (e.g. UNKNOWN); penalize any fabricated citation.
        return 0.0, 1.0, 0.0

    true_positives = len(expected_set & actual_set)
    precision = true_positives / len(actual_set)
    recall = true_positives / len(expected_set)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def score_record(record: dict, response: dict) -> ScoredResult:
    expected_state = record["expected_state"]
    actual_state = response.get("state", "")
    expected_citations = record.get("expected_citations", [])
    actual_citations = response.get("citations", [])

    precision, recall, f1 = score_citations(expected_citations, actual_citations)

    return ScoredResult(
        id=record["id"],
        question=record["question"],
        expected_state=expected_state,
        actual_state=actual_state,
        state_correct=expected_state == actual_state,
        citation_precision=precision,
        citation_recall=recall,
        citation_f1=f1,
    )


def summarize(results: list[ScoredResult]) -> dict:
    n = len(results)
    if n == 0:
        return {}
    state_accuracy = sum(r.state_correct for r in results) / n
    avg_f1 = sum(r.citation_f1 for r in results) / n

    by_state: dict[str, dict] = {}
    for state in {"ANSWERABLE", "UNKNOWN", "CONTRADICTION"}:
        subset = [r for r in results if r.expected_state == state]
        if subset:
            by_state[state] = {
                "count": len(subset),
                "state_accuracy": sum(r.state_correct for r in subset) / len(subset),
                "avg_citation_f1": sum(r.citation_f1 for r in subset) / len(subset),
            }

    return {
        "total": n,
        "state_accuracy": state_accuracy,
        "avg_citation_f1": avg_f1,
        "by_state": by_state,
    }
