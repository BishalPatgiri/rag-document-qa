export type RetrievalMode = "vector" | "keyword" | "hybrid";

export interface DocumentItem {
  id: number;
  filename: string;
  status: string;
  page_count: number;
  chunk_count: number;
  created_at: string;
}

export interface Source {
  index: number;
  chunk_id: number;
  document_id: number;
  filename: string;
  page: number;
  content: string;
  score: number;
}

export interface Stats {
  total_queries: number;
  avg_latency_ms: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_embedding_tokens: number;
  total_cost_usd: number;
  avg_cost_usd: number;
}
