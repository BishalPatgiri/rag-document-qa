from app.config import settings
from app.db.models import QueryLog
from app.db.session import AsyncSessionLocal
from app.observability.pricing import chat_cost, embedding_cost


async def log_query(
    *,
    question: str,
    mode: str,
    retrieved_chunk_ids: list[int],
    latency_ms: float,
    prompt_tokens: int,
    completion_tokens: int,
    embedding_tokens: int,
) -> None:
    """Persist a query's latency and token/cost accounting.

    Uses its own session so it is independent of the request lifecycle.
    """
    cost = chat_cost(
        settings.chat_model, prompt_tokens, completion_tokens
    ) + embedding_cost(settings.embedding_model, embedding_tokens)

    async with AsyncSessionLocal() as session:
        session.add(
            QueryLog(
                question=question,
                mode=mode,
                retrieved_chunk_ids=retrieved_chunk_ids,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                embedding_tokens=embedding_tokens,
                est_cost_usd=cost,
            )
        )
        await session.commit()
