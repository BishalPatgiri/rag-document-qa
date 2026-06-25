import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.generation.answer import stream_answer
from app.retrieval.base import RetrievedChunk
from app.retrieval.service import retrieve
from app.schemas import QueryRequest

router = APIRouter(tags=["query"])


def _sse(event: str, data: dict | list) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _serialize_sources(chunks: list[RetrievedChunk]) -> list[dict]:
    return [
        {
            "index": i,
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "filename": chunk.filename,
            "page": chunk.page,
            "content": chunk.content,
            "score": chunk.score,
        }
        for i, chunk in enumerate(chunks, start=1)
    ]


@router.post("/query")
async def query(
    request: QueryRequest, session: AsyncSession = Depends(get_session)
) -> StreamingResponse:
    """Retrieve context and stream a cited answer over Server-Sent Events.

    Event sequence: one ``sources`` event, many ``token`` events, then ``done``.
    """
    chunks = await retrieve(session, request.query, request.mode, request.top_k)

    async def event_stream() -> AsyncIterator[str]:
        yield _sse("sources", _serialize_sources(chunks))
        async for token in stream_answer(request.query, chunks):
            yield _sse("token", {"text": token})
        yield _sse("done", {})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
