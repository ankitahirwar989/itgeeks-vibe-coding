# The Rulebook That Argues With Itself

> An evidence-first university regulation QA system that knows when the rulebook answers,
> stays silent, or contradicts itself.

This is a Retrieval-Augmented QA system over a fictional university's policy corpus
("Central Institute of Technology and Sciences"). Every answer is grounded in retrieved
source passages, cited by document and section. The system always classifies its response
into exactly one of three states:

- **ANSWERABLE** — the corpus directly and sufficiently answers the question.
- **UNKNOWN** — the corpus does not cover the specific scenario asked about (no hallucinated
  fallback to general knowledge).
- **CONTRADICTION** — two or more corpus passages state incompatible rules for the same
  situation. Both conflicting passages are shown side by side; the system does not silently
  pick a winner.

See [corpus/contradictions.md](corpus/contradictions.md) for the three deliberate
contradictions planted in the corpus, and [evals/questions.jsonl](evals/questions.jsonl) for
the 43-question evaluation set (15 ANSWERABLE / 25 UNKNOWN / 3 CONTRADICTION).

## Architecture

```
question -> [retriever: Gemini embeddings + pgvector cosine search over corpus chunks]
         -> [reasoning engine: Gemini classifies ANSWERABLE / UNKNOWN / CONTRADICTION,
             citing only the retrieved passages, via a strict structured-output schema]
         -> [citation verifier: strips any citation/quote the LLM invented that isn't
             actually backed by the retrieved text; fails safe to UNKNOWN if nothing survives]
         -> QueryResponse (state, answer, evidence/contradictions, citations)
```

Every chunk stored in the vector database is exactly one numbered section of one source
document (e.g. `attendance_policy.md#3.1`, `academic_regulations.pdf#8.2`), so every citation
the system returns points at a single, unambiguous, quotable passage. The reasoning LLM is
never allowed to answer from its own training knowledge — the system prompt forbids it, and
the verifier layer rejects any citation or quote that doesn't actually exist in what was
retrieved, regardless of what the model claims.

## Project layout

```
frontend/     Next.js + TypeScript + Tailwind + shadcn-style UI components
backend/      FastAPI + Pydantic app: ingestion, RAG retrieval, reasoning, citation verification
corpus/       Fictional university policy documents (Markdown + one generated PDF)
evals/        43-question eval set + deterministic scoring script
scripts/      ingest.py, generate_embeddings.py, validate_corpus.py, seed_database.py, generate_pdf.py
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL with the `pgvector` extension (or use `docker-compose`, which provisions this
  automatically via the `pgvector/pgvector:pg16` image)
- A Gemini API key (from [Google AI Studio](https://aistudio.google.com/apikey))

## Quick start (Docker)

```bash
cp .env.example .env
# edit .env and set GEMINI_API_KEY

docker compose up -d db
docker compose run --rm ingest
docker compose up -d backend frontend
```

- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:3000

## Quick start (local, no Docker)

```bash
# 1. Postgres with pgvector must be running locally and match DATABASE_URL in .env

# 2. Backend
cd backend
pip install -r requirements.txt
cp ../.env.example .env   # edit with your GEMINI_API_KEY; must live in backend/ for local runs
cd ..
python scripts/seed_database.py
python scripts/ingest.py
cd backend && uvicorn app.main:app --reload

# 3. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000 and try the three example questions shown in the UI, one for
each state.

## Running the evaluation

```bash
python evals/run_eval.py --mode api --base-url http://localhost:8000
```

Reports state-classification accuracy and citation precision/recall/F1, overall and broken
down by expected state. See [evals/README.md](evals/README.md).

## Validating the corpus

```bash
python scripts/validate_corpus.py
```

Confirms every document parses, the corpus meets the minimum word count, and every citation
referenced in `contradictions.md` and `evals/questions.jsonl` resolves to a real chunk.

## Backend tests

```bash
cd backend
pytest
```

Covers corpus parsing (including a regression test for a PDF word-wrap edge case that could
otherwise fabricate a heading), citation verification, and the reasoning engine's guardrail
behavior (hallucinated citations get stripped; unverifiable contradiction/answer claims fail
safe to UNKNOWN).

## Configuration

All model choices are environment-driven — see `.env.example`. Nothing in the code hard-codes
a Gemini model name; `LLM_MODEL` and `EMBEDDING_MODEL` are read from `backend/app/config.py`
at runtime.

## Deployment

- **Frontend**: deployable to Vercel (`frontend/` as project root; set
  `NEXT_PUBLIC_API_BASE_URL` to your deployed backend URL).
- **Backend**: deployable to Render/Railway/Fly.io using `backend/Dockerfile`.
- **Database**: any PostgreSQL provider with the `pgvector` extension available (Supabase,
  Neon, or a self-hosted `pgvector/pgvector` image).
