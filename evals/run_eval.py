"""Run the full evaluation set against a running instance of the QA API (or the qa_service
directly, in-process) and report deterministic scores.

Usage:
    python evals/run_eval.py --mode api --base-url http://localhost:8000
    python evals/run_eval.py --mode inprocess
"""
import argparse
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from scoring import ScoredResult, score_record, summarize  # noqa: E402

QUESTIONS_PATH = Path(__file__).resolve().parent / "questions.jsonl"


def load_questions() -> list[dict]:
    records = []
    with QUESTIONS_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def run_via_api(records: list[dict], base_url: str) -> list[dict]:
    responses = []
    with httpx.Client(base_url=base_url, timeout=60.0) as client:
        for record in records:
            resp = client.post("/api/query", json={"question": record["question"]})
            resp.raise_for_status()
            responses.append(resp.json())
    return responses


def run_inprocess(records: list[dict]) -> list[dict]:
    from app.services.qa_service import ask

    responses = []
    for record in records:
        result = ask(record["question"])
        responses.append(result.model_dump())
    return responses


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["api", "inprocess"], default="api")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent / "results.json"))
    args = parser.parse_args()

    records = load_questions()
    if args.mode == "api":
        responses = run_via_api(records, args.base_url)
    else:
        responses = run_inprocess(records)

    results: list[ScoredResult] = [
        score_record(record, response) for record, response in zip(records, responses)
    ]

    summary = summarize(results)

    print(json.dumps(summary, indent=2))

    failures = [r for r in results if not r.state_correct]
    if failures:
        print(f"\n{len(failures)} state mismatches:")
        for r in failures:
            print(f"  - {r.id}: expected {r.expected_state}, got {r.actual_state} :: {r.question}")

    output = {
        "summary": summary,
        "results": [
            {
                "id": r.id,
                "question": r.question,
                "expected_state": r.expected_state,
                "actual_state": r.actual_state,
                "state_correct": r.state_correct,
                "citation_precision": r.citation_precision,
                "citation_recall": r.citation_recall,
                "citation_f1": r.citation_f1,
            }
            for r in results
        ],
    }
    Path(args.out).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nFull results written to {args.out}")


if __name__ == "__main__":
    main()
