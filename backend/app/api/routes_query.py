import json
from collections.abc import AsyncIterator
from time import perf_counter

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.generation.answer import stream_answer
from app.ingestion.chunker import count_tokens
from app.observability.tracking import log_query
from app.retrieval.base import RetrievalMode, RetrievedChunk
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
    started = perf_counter()
    chunks = await retrieve(session, request.query, request.mode, request.top_k)
    # Keyword-only retrieval performs no query embedding.
    embedding_tokens = (
        0 if request.mode is RetrievalMode.keyword else count_tokens(request.query)
    )

    async def event_stream() -> AsyncIterator[str]:
        yield _sse("sources", _serialize_sources(chunks))
        usage: dict = {}
        async for token in stream_answer(request.query, chunks, usage):
            yield _sse("token", {"text": token})

        latency_ms = (perf_counter() - started) * 1000
        await log_query(
            question=request.query,
            mode=request.mode.value,
            retrieved_chunk_ids=[c.chunk_id for c in chunks],
            latency_ms=latency_ms,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            embedding_tokens=embedding_tokens,
        )
        yield _sse("done", {"latency_ms": round(latency_ms, 1)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
