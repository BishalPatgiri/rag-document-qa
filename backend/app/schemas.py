from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.retrieval.base import RetrievalMode


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    status: str
    page_count: int
    chunk_count: int
    created_at: datetime


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    mode: RetrievalMode = RetrievalMode.hybrid
    top_k: int | None = Field(default=None, ge=1, le=50)


class RetrievedChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chunk_id: int
    document_id: int
    filename: str
    page: int
    content: str
    score: float


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    mode: RetrievalMode = RetrievalMode.hybrid
    top_k: int | None = Field(default=None, ge=1, le=50)


class StatsOut(BaseModel):
    total_queries: int
    avg_latency_ms: float
    total_prompt_tokens: int
    total_completion_tokens: int
    total_embedding_tokens: int
    total_cost_usd: float
    avg_cost_usd: float
