from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.ingestion.embedder import embed_texts
from app.retrieval.base import RetrievalMode, RetrievedChunk
from app.retrieval.hybrid import search_hybrid
from app.retrieval.keyword import search_keyword
from app.retrieval.vector import search_vector


async def retrieve(
    session: AsyncSession,
    query: str,
    mode: RetrievalMode = RetrievalMode.hybrid,
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """Retrieve the top chunks for a query under the chosen retrieval mode."""
    top_k = top_k or settings.top_k

    if mode is RetrievalMode.keyword:
        return await search_keyword(session, query, top_k)

    vectors, _ = await embed_texts([query])
    query_vector = vectors[0]

    if mode is RetrievalMode.vector:
        return await search_vector(session, query_vector, top_k)

    # Hybrid: over-fetch from each retriever before fusing.
    fetch_k = max(top_k * 4, 20)
    return await search_hybrid(session, query, query_vector, top_k, fetch_k)
