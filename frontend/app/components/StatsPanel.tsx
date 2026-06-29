"use client";

import { useEffect, useState } from "react";

import { getStats } from "@/lib/client";
import type { Stats } from "@/lib/types";

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-foreground/10 px-3 py-2">
      <p className="text-xs text-foreground/50">{label}</p>
      <p className="text-lg font-semibold tabular-nums">{value}</p>
    </div>
  );
}

export default function StatsPanel({ refreshKey }: { refreshKey: number }) {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(() => setStats(null));
  }, [refreshKey]);

  if (!stats) return null;

  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-foreground/60">
        Usage
      </h2>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <Metric label="Queries" value={String(stats.total_queries)} />
        <Metric label="Avg latency" value={`${stats.avg_latency_ms} ms`} />
        <Metric
          label="Total cost"
          value={`$${stats.total_cost_usd.toFixed(4)}`}
        />
        <Metric
          label="Avg cost/query"
          value={`$${stats.avg_cost_usd.toFixed(4)}`}
        />
      </div>
    </section>
  );
}
