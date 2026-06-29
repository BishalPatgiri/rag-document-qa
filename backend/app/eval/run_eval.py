"""Evaluation harness: compare retrieval modes on a labelled test set.

Usage:
    python -m app.eval.run_eval --testset app/eval/testset.sample.jsonl --judge

Requires a populated database (documents ingested) and, for embeddings/judge,
an OPENAI_API_KEY.
"""
import argparse
import asyncio
import json
from statistics import mean

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.eval.dataset import EvalItem, load_testset
from app.eval.judge import judge_answer
from app.eval.metrics import precision_at_k, recall_at_k, reciprocal_rank
from app.generation.answer import generate_answer
from app.retrieval.base import RetrievalMode
from app.retrieval.service import retrieve


async def _eval_item(item: EvalItem, mode: RetrievalMode, top_k: int, judge: bool):
    async with AsyncSessionLocal() as session:
        chunks = await retrieve(session, item.question, mode, top_k)

    retrieved_docs = [c.filename for c in chunks]
    relevant = set(item.relevant_documents)
    result = {
        "id": item.id,
        "precision": precision_at_k(retrieved_docs, relevant, top_k),
        "recall": recall_at_k(retrieved_docs, relevant, top_k),
        "rr": reciprocal_rank(retrieved_docs, relevant),
    }

    if judge:
        answer, _ = await generate_answer(item.question, chunks)
        scores = await judge_answer(item.question, answer, chunks)
        result["faithfulness"] = scores["faithfulness"]
        result["relevance"] = scores["relevance"]

    return result


async def _eval_mode(items, mode: RetrievalMode, top_k: int, judge: bool) -> dict:
    per_item = [await _eval_item(it, mode, top_k, judge) for it in items]
    summary = {
        "precision@k": round(mean(r["precision"] for r in per_item), 4),
        "recall@k": round(mean(r["recall"] for r in per_item), 4),
        "mrr": round(mean(r["rr"] for r in per_item), 4),
        "n": len(per_item),
    }
    if judge:
        summary["faithfulness"] = round(mean(r["faithfulness"] for r in per_item), 2)
        summary["relevance"] = round(mean(r["relevance"] for r in per_item), 2)
    return {"summary": summary, "items": per_item}


def _print_table(report: dict, judge: bool) -> None:
    cols = ["precision@k", "recall@k", "mrr"] + (
        ["faithfulness", "relevance"] if judge else []
    )
    header = f"{'mode':<10}" + "".join(f"{c:>14}" for c in cols)
    print(header)
    print("-" * len(header))
    for mode, data in report["modes"].items():
        s = data["summary"]
        row = f"{mode:<10}" + "".join(f"{s[c]:>14}" for c in cols)
        print(row)


async def main() -> None:
    parser = argparse.ArgumentParser(description="RAG retrieval evaluation harness")
    parser.add_argument("--testset", default="app/eval/testset.sample.jsonl")
    parser.add_argument("--top-k", type=int, default=settings.top_k)
    parser.add_argument(
        "--modes",
        default="vector,keyword,hybrid",
        help="comma-separated retrieval modes",
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        help="also score answer faithfulness/relevance with an LLM judge",
    )
    parser.add_argument("--out", default="eval_report.json")
    args = parser.parse_args()

    items = load_testset(args.testset)
    modes = [RetrievalMode(m.strip()) for m in args.modes.split(",") if m.strip()]

    report = {"top_k": args.top_k, "testset": args.testset, "modes": {}}
    for mode in modes:
        report["modes"][mode.value] = await _eval_mode(
            items, mode, args.top_k, args.judge
        )

    _print_table(report, args.judge)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    asyncio.run(main())
