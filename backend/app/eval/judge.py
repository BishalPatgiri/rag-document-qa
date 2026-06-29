import json

from app.config import settings
from app.llm_client import get_client
from app.retrieval.base import RetrievedChunk
from app.generation.answer import build_context

JUDGE_SYSTEM = (
    "You are a strict evaluator of question-answering systems. You are given a "
    "question, the source passages provided to the system, and the system's "
    "answer. Score the answer on two axes from 1 (poor) to 5 (excellent):\n"
    "- faithfulness: is every claim supported by the sources (no hallucination)?\n"
    "- relevance: does the answer actually address the question?\n"
    'Respond with strict JSON: {"faithfulness": int, "relevance": int, '
    '"rationale": string}.'
)


async def judge_answer(
    question: str, answer: str, chunks: list[RetrievedChunk]
) -> dict:
    """Score an answer for faithfulness and relevance via an LLM judge."""
    sources = build_context(chunks) if chunks else "(no sources retrieved)"
    user = (
        f"Question:\n{question}\n\n"
        f"Sources:\n{sources}\n\n"
        f"System answer:\n{answer}"
    )
    response = await get_client().chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)
    return {
        "faithfulness": int(data.get("faithfulness", 0)),
        "relevance": int(data.get("relevance", 0)),
        "rationale": data.get("rationale", ""),
    }
