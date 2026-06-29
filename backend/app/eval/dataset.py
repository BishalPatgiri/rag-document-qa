import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class EvalItem:
    id: str
    question: str
    relevant_documents: list[str] = field(default_factory=list)
    reference_answer: str | None = None


def load_testset(path: str | Path) -> list[EvalItem]:
    """Load a JSONL test set.

    Each line is an object with: id, question, relevant_documents (list of
    document filenames considered relevant), and optional reference_answer.
    """
    items: list[EvalItem] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            items.append(
                EvalItem(
                    id=str(row["id"]),
                    question=row["question"],
                    relevant_documents=row.get("relevant_documents", []),
                    reference_answer=row.get("reference_answer"),
                )
            )
    return items
