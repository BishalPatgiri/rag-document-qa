export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-1 flex-col justify-center gap-6 px-6 py-24">
      <div className="space-y-3">
        <span className="inline-block rounded-full border border-black/10 px-3 py-1 text-xs font-medium uppercase tracking-wide text-black/60 dark:border-white/15 dark:text-white/60">
          RAG · pgvector · OpenAI
        </span>
        <h1 className="text-4xl font-semibold tracking-tight">Document QA</h1>
        <p className="text-lg text-black/70 dark:text-white/70">
          Upload PDFs and get cited, streamed answers backed by hybrid
          (keyword + vector) retrieval — with a built-in evaluation harness and
          cost/latency tracking.
        </p>
      </div>
      <p className="text-sm text-black/50 dark:text-white/50">
        Frontend scaffold is live. Upload, chat, and metrics views land in a
        later phase.
      </p>
    </main>
  );
}
