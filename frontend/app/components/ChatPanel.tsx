"use client";

import { useState } from "react";

import { streamQuery } from "@/lib/client";
import type { RetrievalMode, Source } from "@/lib/types";
import CitedAnswer from "./CitedAnswer";

const MODES: RetrievalMode[] = ["hybrid", "vector", "keyword"];

export default function ChatPanel({ onAnswered }: { onAnswered?: () => void }) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<RetrievalMode>("hybrid");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [activeSource, setActiveSource] = useState<number | null>(null);
  const [latency, setLatency] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setError(null);
    setAnswer("");
    setSources([]);
    setActiveSource(null);
    setLatency(null);

    try {
      await streamQuery(
        { query: query.trim(), mode },
        {
          onSources: setSources,
          onToken: (text) => setAnswer((prev) => prev + text),
          onDone: (info) => setLatency(info.latency_ms ?? null),
        },
      );
      onAnswered?.();
    } catch {
      setError("Something went wrong. Check the backend and your API key.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="flex flex-col gap-4">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your documents…"
          rows={3}
          className="w-full resize-none rounded-lg border border-foreground/15 bg-transparent px-3 py-2 text-sm outline-none focus:border-foreground/40"
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit(e);
          }}
        />
        <div className="flex items-center justify-between gap-3">
          <div className="flex gap-1 rounded-lg border border-foreground/15 p-1 text-xs">
            {MODES.map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setMode(m)}
                className={`rounded-md px-2.5 py-1 capitalize transition-colors ${
                  mode === m
                    ? "bg-foreground text-background"
                    : "text-foreground/60 hover:text-foreground"
                }`}
              >
                {m}
              </button>
            ))}
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background disabled:opacity-50"
          >
            {loading ? "Thinking…" : "Ask"}
          </button>
        </div>
        <p className="text-xs text-foreground/40">⌘/Ctrl + Enter to send</p>
      </form>

      {error && <p className="text-sm text-red-500">{error}</p>}

      {(answer || sources.length > 0) && (
        <div className="flex flex-col gap-4 rounded-lg border border-foreground/10 p-4">
          <div className="text-sm">
            <CitedAnswer
              text={answer}
              sources={sources}
              onCite={setActiveSource}
            />
            {loading && <span className="animate-pulse">▍</span>}
          </div>

          {latency !== null && (
            <p className="text-xs text-foreground/40">
              Answered in {latency} ms · {mode} retrieval
            </p>
          )}

          {sources.length > 0 && (
            <div className="flex flex-col gap-2 border-t border-foreground/10 pt-3">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-foreground/50">
                Sources
              </h3>
              {sources.map((s) => (
                <details
                  key={s.chunk_id}
                  open={activeSource === s.index}
                  className={`rounded-md border px-3 py-2 text-sm ${
                    activeSource === s.index
                      ? "border-foreground/40"
                      : "border-foreground/10"
                  }`}
                >
                  <summary className="cursor-pointer list-none font-medium">
                    <span className="mr-1.5 inline-flex h-5 min-w-5 items-center justify-center rounded bg-foreground/10 px-1 text-xs">
                      {s.index}
                    </span>
                    {s.filename}{" "}
                    <span className="text-foreground/40">· p.{s.page}</span>
                  </summary>
                  <p className="mt-2 whitespace-pre-wrap text-foreground/70">
                    {s.content}
                  </p>
                </details>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
