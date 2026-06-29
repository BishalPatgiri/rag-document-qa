import { apiUrl } from "./api";
import type { DocumentItem, RetrievalMode, Source, Stats } from "./types";

export async function listDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(apiUrl("/documents"), { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load documents");
  return res.json();
}

export async function uploadDocument(file: File): Promise<DocumentItem> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(apiUrl("/documents"), { method: "POST", body: form });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ?? "Upload failed");
  }
  return res.json();
}

export async function deleteDocument(id: number): Promise<void> {
  const res = await fetch(apiUrl(`/documents/${id}`), { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
}

export async function getStats(): Promise<Stats> {
  const res = await fetch(apiUrl("/stats"), { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load stats");
  return res.json();
}

interface QueryRequest {
  query: string;
  mode: RetrievalMode;
  top_k?: number;
}

interface QueryHandlers {
  onSources?: (sources: Source[]) => void;
  onToken?: (text: string) => void;
  onDone?: (info: { latency_ms?: number }) => void;
}

/**
 * POST /query and consume its Server-Sent Events stream. The endpoint is a POST
 * (so EventSource can't be used); we read the response body and parse SSE
 * frames manually.
 */
export async function streamQuery(
  request: QueryRequest,
  handlers: QueryHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(apiUrl("/query"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!res.ok || !res.body) throw new Error("Query failed");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const frame = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      dispatchFrame(frame, handlers);
      boundary = buffer.indexOf("\n\n");
    }
  }
}

function dispatchFrame(frame: string, handlers: QueryHandlers): void {
  let event = "message";
  let data = "";
  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data += line.slice(5).trim();
  }
  if (!data) return;

  const payload = JSON.parse(data);
  if (event === "sources") handlers.onSources?.(payload as Source[]);
  else if (event === "token") handlers.onToken?.((payload as { text: string }).text);
  else if (event === "done") handlers.onDone?.(payload as { latency_ms?: number });
}
