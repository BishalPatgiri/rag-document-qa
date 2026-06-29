"use client";

import type { Source } from "@/lib/types";

/**
 * Render answer text, turning inline [n] citation markers into chips that
 * highlight the matching source when clicked.
 */
export default function CitedAnswer({
  text,
  sources,
  onCite,
}: {
  text: string;
  sources: Source[];
  onCite?: (index: number) => void;
}) {
  const validIndexes = new Set(sources.map((s) => s.index));
  const parts = text.split(/(\[\d+\])/g);

  return (
    <p className="whitespace-pre-wrap leading-relaxed">
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+)\]$/);
        if (match) {
          const index = Number(match[1]);
          if (validIndexes.has(index)) {
            return (
              <button
                key={i}
                onClick={() => onCite?.(index)}
                className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded bg-foreground/10 px-1 align-baseline text-xs font-medium text-foreground/70 hover:bg-foreground/20"
                title={`Source ${index}`}
              >
                {index}
              </button>
            );
          }
        }
        return <span key={i}>{part}</span>;
      })}
    </p>
  );
}
