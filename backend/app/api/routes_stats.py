from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import QueryLog
from app.db.session import get_session
from app.schemas import StatsOut

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsOut)
async def stats(session: AsyncSession = Depends(get_session)) -> StatsOut:
    """Aggregate cost and latency across all logged queries."""
    row = (
        await session.execute(
            select(
                func.count(QueryLog.id),
                func.coalesce(func.avg(QueryLog.latency_ms), 0.0),
                func.coalesce(func.sum(QueryLog.prompt_tokens), 0),
                func.coalesce(func.sum(QueryLog.completion_tokens), 0),
                func.coalesce(func.sum(QueryLog.embedding_tokens), 0),
                func.coalesce(func.sum(QueryLog.est_cost_usd), 0.0),
            )
        )
    ).one()

    total, avg_latency, prompt_t, completion_t, embed_t, total_cost = row
    return StatsOut(
        total_queries=total,
        avg_latency_ms=round(float(avg_latency), 1),
        total_prompt_tokens=int(prompt_t),
        total_completion_tokens=int(completion_t),
        total_embedding_tokens=int(embed_t),
        total_cost_usd=round(float(total_cost), 6),
        avg_cost_usd=round(float(total_cost) / total, 6) if total else 0.0,
    )
