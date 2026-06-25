from dataclasses import dataclass
from enum import Enum


class RetrievalMode(str, Enum):
    vector = "vector"
    keyword = "keyword"
    hybrid = "hybrid"


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    filename: str
    page: int
    content: str
    score: float
