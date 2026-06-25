from dataclasses import replace

from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.base import RetrievedChunk
from app.retrieval.keyword import search_keyword
from app.retrieval.vector import search_vector

# Standard Reciprocal Rank Fusion constant; dampens the weight of top ranks.
RRF_K = 60


def reciprocal_rank_fusion(
    rank_lists: list[list[RetrievedChunk]], top_k: int, k_const: int = RRF_K
) -> list[RetrievedChunk]:
    """Fuse multiple ranked lists by Reciprocal Rank Fusion.

    Each result's fused score is the sum of 1 / (k_const + rank) across the
    lists it appears in (rank is 1-based). The returned chunks carry the fused
    score in ``score``.
    """
    scores: dict[int, float] = {}
    chunks: dict[int, RetrievedChunk] = {}
    for rank_list in rank_lists:
        for rank, chunk in enumerate(rank_list, start=1):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (
                k_const + rank
            )
            chunks.setdefault(chunk.chunk_id, chunk)

    fused = [
        replace(chunks[chunk_id], score=score)
        for chunk_id, score in scores.items()
    ]
    fused.sort(key=lambda c: c.score, reverse=True)
    return fused[:top_k]


async def search_hybrid(
    session: AsyncSession,
    query_text: str,
    query_vector: list[float],
    top_k: int,
    fetch_k: int,
) -> list[RetrievedChunk]:
    """Fuse vector and keyword results with RRF."""
    vector_hits = await search_vector(session, query_vector, fetch_k)
    keyword_hits = await search_keyword(session, query_text, fetch_k)
    return reciprocal_rank_fusion([vector_hits, keyword_hits], top_k)
