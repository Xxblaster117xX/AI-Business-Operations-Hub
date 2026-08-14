from google.genai import types

from app.config import settings
from app.gemini_client import call_with_retry, get_client


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """Embed a single piece of text with Gemini, returning a fixed-size vector."""
    client = get_client()
    result = call_with_retry(
        lambda: client.models.embed_content(
            model=settings.gemini_embedding_model,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=settings.embedding_dim,
            ),
        )
    )
    return result.embeddings[0].values


def embed_query(text: str) -> list[float]:
    return embed_text(text, task_type="RETRIEVAL_QUERY")
