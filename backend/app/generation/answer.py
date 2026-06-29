from collections.abc import AsyncIterator

from app.config import settings
from app.llm_client import get_client
from app.retrieval.base import RetrievedChunk

SYSTEM_PROMPT = (
    "You are a precise assistant that answers questions using only the provided "
    "sources. Cite every claim inline with bracketed source numbers like [1] or "
    "[2][3]. If the sources do not contain the answer, say you don't know based "
    "on the provided documents. Do not invent facts or sources."
)


def build_context(chunks: list[RetrievedChunk]) -> str:
    return "\n\n".join(
        f"[{i}] (source: {chunk.filename}, p.{chunk.page})\n{chunk.content}"
        for i, chunk in enumerate(chunks, start=1)
    )


def build_messages(query: str, chunks: list[RetrievedChunk]) -> list[dict]:
    if chunks:
        context = build_context(chunks)
        user_content = (
            f"Sources:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer using only the sources above, citing them with [n]."
        )
    else:
        user_content = (
            f"Question: {query}\n\n"
            "There are no sources available. Say you don't know based on the "
            "provided documents."
        )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


async def generate_answer(query: str, chunks: list[RetrievedChunk]):
    """Non-streaming answer. Returns (answer_text, usage) for eval/tracking."""
    response = await get_client().chat.completions.create(
        model=settings.chat_model,
        messages=build_messages(query, chunks),
        temperature=0.0,
    )
    return response.choices[0].message.content or "", response.usage


async def stream_answer(
    query: str,
    chunks: list[RetrievedChunk],
    usage_out: dict | None = None,
) -> AsyncIterator[str]:
    """Yield answer text deltas from the chat model as they arrive.

    If ``usage_out`` is provided, it is populated with prompt/completion token
    counts from the final usage event.
    """
    stream = await get_client().chat.completions.create(
        model=settings.chat_model,
        messages=build_messages(query, chunks),
        stream=True,
        temperature=0.0,
        stream_options={"include_usage": True},
    )
    async for event in stream:
        if event.usage is not None and usage_out is not None:
            usage_out["prompt_tokens"] = event.usage.prompt_tokens
            usage_out["completion_tokens"] = event.usage.completion_tokens
        if not event.choices:
            continue
        delta = event.choices[0].delta.content
        if delta:
            yield delta
