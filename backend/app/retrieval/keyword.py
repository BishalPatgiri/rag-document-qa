from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk, Document
from app.retrieval.base import RetrievedChunk


async def search_keyword(
    session: AsyncSession, query_text: str, top_k: int
) -> list[RetrievedChunk]:
    """Full-text search over the generated tsvector column, ranked by ts_rank."""
    tsquery = func.plainto_tsquery("english", query_text)
    rank = func.ts_rank(Chunk.tsv, tsquery).label("rank")
    stmt = (
        select(Chunk, Document.filename, rank)
        .join(Document, Chunk.document_id == Document.id)
        .where(Chunk.tsv.op("@@")(tsquery))
        .order_by(rank.desc())
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
            score=float(rank_value),
        )
        for chunk, filename, rank_value in rows
    ]
