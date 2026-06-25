from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.retrieval.service import retrieve
from app.schemas import RetrievedChunkOut, SearchRequest

router = APIRouter(tags=["search"])


@router.post("/search", response_model=list[RetrievedChunkOut])
async def search(
    request: SearchRequest, session: AsyncSession = Depends(get_session)
):
    """Debug endpoint: inspect retrieval results for a query and mode."""
    return await retrieve(
        session, request.query, request.mode, request.top_k
    )
