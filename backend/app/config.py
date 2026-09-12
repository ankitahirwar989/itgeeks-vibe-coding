from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolved as an absolute path (backend/.env) so config loads the same way regardless of
# whether the process's cwd is the repo root (scripts/*.py) or backend/ (uvicorn).
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://rulebook:rulebook@localhost:5432/rulebook_qa"

    # Gemini
    gemini_api_key: str = ""
    llm_model: str = "gemini-2.0-flash"
    embedding_model: str = "text-embedding-004"
    embedding_dim: int = 768

    # Retrieval / reasoning
    retrieval_top_k: int = 8
    contradiction_similarity_floor: float = 0.15
    max_output_tokens: int = 1200

    # API
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
