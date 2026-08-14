import time
from functools import lru_cache
from typing import Callable, TypeVar

from google import genai
from google.genai.errors import ServerError

from app.config import settings

T = TypeVar("T")


@lru_cache
def get_client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def call_with_retry(fn: Callable[[], T], retries: int = 3, base_delay: float = 2.0) -> T:
    """Gemini's free tier returns transient 503s ('high demand') fairly often —
    retry with exponential backoff before giving up."""
    last_error: ServerError | None = None
    for attempt in range(retries):
        try:
            return fn()
        except ServerError as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(base_delay * (2**attempt))
    raise last_error
