# Evaluation

`questions.jsonl` contains 43 hand-written evaluation questions against the corpus in `../corpus`:

- 15 `ANSWERABLE`
- 25 `UNKNOWN`
- 3 `CONTRADICTION`

`expected_answers.jsonl` holds a short gold-answer summary per question id, for human review.

## Running

Make sure the backend is ingested and running (see the root `README.md`), then:

```bash
python evals/run_eval.py --mode api --base-url http://localhost:8000
```

Or run against the reasoning pipeline directly, in-process (requires `GEMINI_API_KEY` and a
reachable Postgres/pgvector instance, but not a running FastAPI server):

```bash
python evals/run_eval.py --mode inprocess
```

## What is scored

For every question, `evals/scoring.py` deterministically compares the system's response to the
gold record on two axes:

1. **State accuracy** — did the system return the correct one of `ANSWERABLE` / `UNKNOWN` /
   `CONTRADICTION`?
2. **Citation precision/recall/F1** — do the citations the system returned match the
   `expected_citations` for the question? For `UNKNOWN` questions, `expected_citations` is
   empty, so any citation returned is scored as a fabrication.

The script prints an overall summary and a per-state breakdown, and writes full per-question
results to `evals/results.json`.
