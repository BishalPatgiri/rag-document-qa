from functools import lru_cache

from openai import AsyncOpenAI

from app.config import settings


@lru_cache
def get_client() -> AsyncOpenAI:
    """Shared AsyncOpenAI client, created lazily so the app boots without a key."""
    return AsyncOpenAI(api_key=settings.openai_api_key)
