from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.llm_client import get_client

# OpenAI accepts large batches; keep them modest to bound payload size.
_BATCH_SIZE = 128


@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=30))
async def _embed_batch(texts: list[str]) -> tuple[list[list[float]], int]:
    response = await get_client().embeddings.create(
        model=settings.embedding_model, input=texts
    )
    vectors = [item.embedding for item in response.data]
    return vectors, response.usage.total_tokens


async def embed_texts(texts: list[str]) -> tuple[list[list[float]], int]:
    """Embed texts in batches. Returns (vectors, total_tokens_used)."""
    all_vectors: list[list[float]] = []
    total_tokens = 0
    for start in range(0, len(texts), _BATCH_SIZE):
        batch = texts[start : start + _BATCH_SIZE]
        vectors, tokens = await _embed_batch(batch)
        all_vectors.extend(vectors)
        total_tokens += tokens
    return all_vectors, total_tokens
