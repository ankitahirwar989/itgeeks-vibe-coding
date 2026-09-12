from functools import lru_cache

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_random_exponential

from app.config import get_settings


@lru_cache
def get_genai_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts with the configured Gemini embedding model."""
    if not texts:
        return []
    settings = get_settings()
    client = get_genai_client()
    response = client.models.embed_content(
        model=settings.embedding_model,
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=settings.embedding_dim),
    )
    return [embedding.values for embedding in response.embeddings]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
