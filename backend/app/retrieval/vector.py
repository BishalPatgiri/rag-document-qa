from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk, Document
from app.retrieval.base import RetrievedChunk


async def search_vector(
    session: AsyncSession, query_vector: list[float], top_k: int
) -> list[RetrievedChunk]:
    """Nearest-neighbour search by cosine distance over chunk embeddings."""
    distance = Chunk.embedding.cosine_distance(query_vector).label("distance")
    stmt = (
        select(Chunk, Document.filename, distance)
        .join(Document, Chunk.document_id == Document.id)
        .order_by(distance)
        .limit(top_k)
    )
    rows = (await session.execute(stmt)).all()
    return [
        RetrievedChunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            filename=filename,
            page=chunk.page,
            content=chunk.content,
            # cosine_distance in [0, 2]; convert to a [-1, 1] similarity.
            score=1.0 - float(distance_value),
        )
        for chunk, filename, distance_value in rows
    ]
