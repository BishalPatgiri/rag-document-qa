"use client";

import { useState } from "react";

import ChatPanel from "./ChatPanel";
import StatsPanel from "./StatsPanel";
import UploadPanel from "./UploadPanel";

export default function Workspace() {
  const [refreshKey, setRefreshKey] = useState(0);
  const bump = () => setRefreshKey((k) => k + 1);

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 py-10">
      <header className="flex flex-col gap-1">
        <span className="text-xs font-medium uppercase tracking-wide text-foreground/50">
          RAG · pgvector · OpenAI
        </span>
        <h1 className="text-2xl font-semibold tracking-tight">Document QA</h1>
        <p className="text-sm text-foreground/60">
          Upload PDFs and ask questions — answers cite their sources and stream
          in live.
        </p>
      </header>

      <div className="grid gap-8 md:grid-cols-[18rem_1fr]">
        <aside>
          <UploadPanel onChange={bump} />
        </aside>
        <main>
          <ChatPanel onAnswered={bump} />
        </main>
      </div>

      <StatsPanel refreshKey={refreshKey} />
    </div>
  );
}
