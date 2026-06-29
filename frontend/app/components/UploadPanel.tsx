"use client";

import { useEffect, useRef, useState } from "react";

import {
  deleteDocument,
  listDocuments,
  uploadDocument,
} from "@/lib/client";
import type { DocumentItem } from "@/lib/types";

export default function UploadPanel({
  onChange,
}: {
  onChange?: () => void;
}) {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function refresh() {
    try {
      setDocuments(await listDocuments());
    } catch {
      setError("Could not reach the API. Is the backend running?");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleFile(file: File) {
    setBusy(true);
    setError(null);
    try {
      await uploadDocument(file);
      await refresh();
      onChange?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  async function handleDelete(id: number) {
    await deleteDocument(id);
    await refresh();
    onChange?.();
  }

  return (
    <section className="flex flex-col gap-4">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-foreground/60">
        Documents
      </h2>

      <label
        className={`flex cursor-pointer flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-foreground/20 px-4 py-6 text-center text-sm transition-colors hover:border-foreground/40 ${
          busy ? "opacity-60" : ""
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          disabled={busy}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
        <span className="font-medium">
          {busy ? "Uploading…" : "Upload a PDF"}
        </span>
        <span className="text-foreground/50">Click to choose a file</span>
      </label>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <ul className="flex flex-col gap-2">
        {documents.length === 0 && !error && (
          <li className="text-sm text-foreground/50">No documents yet.</li>
        )}
        {documents.map((doc) => (
          <li
            key={doc.id}
            className="flex items-center justify-between gap-2 rounded-md border border-foreground/10 px-3 py-2 text-sm"
          >
            <div className="min-w-0">
              <p className="truncate font-medium">{doc.filename}</p>
              <p className="text-xs text-foreground/50">
                {doc.page_count} pages · {doc.chunk_count} chunks
              </p>
            </div>
            <button
              onClick={() => handleDelete(doc.id)}
              className="shrink-0 rounded px-2 py-1 text-xs text-foreground/50 hover:bg-foreground/5 hover:text-red-500"
              aria-label={`Delete ${doc.filename}`}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
