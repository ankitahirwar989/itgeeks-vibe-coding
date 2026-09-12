# Utility image for one-off corpus ingestion (`docker compose run ingest`).
# The backend API itself is built from backend/Dockerfile; the frontend from frontend/Dockerfile.
FROM python:3.11-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/app backend/app
COPY corpus corpus
COPY scripts scripts

CMD ["python", "scripts/ingest.py"]
