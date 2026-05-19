"use client";

import { useEffect, useMemo, useState } from "react";
import { Activity, AlertTriangle, Clock3, Coins, ServerCrash, Sigma } from "lucide-react";
import { getDashboardMetrics, getRecentRequests, type DashboardMetrics, type LlmRequest } from "@/lib/api";
import { MetricCard } from "@/components/metric-card";
import { PromptConsole } from "@/components/prompt-console";
import { RequestTable } from "@/components/request-table";

const emptyMetrics: DashboardMetrics = {
  total_requests: 0,
  total_cost_usd: 0,
  average_latency_ms: 0,
  error_count: 0,
  suspicious_count: 0,
  total_tokens: 0,
};

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics>(emptyMetrics);
  const [requests, setRequests] = useState<LlmRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setError(null);
    const [metricData, requestData] = await Promise.all([getDashboardMetrics(), getRecentRequests()]);
    setMetrics(metricData);
    setRequests(requestData);
  }

  useEffect(() => {
    refresh()
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load dashboard"))
      .finally(() => setIsLoading(false));
  }, []);

  const metricCards = useMemo(
    () => [
      {
        label: "Total Requests",
        value: metrics.total_requests.toLocaleString(),
        detail: "Requests persisted in PostgreSQL",
        icon: Activity,
      },
      {
        label: "Total Cost",
        value: `$${metrics.total_cost_usd.toFixed(5)}`,
        detail: "Estimated from provider token usage",
        icon: Coins,
        tone: "success" as const,
      },
      {
        label: "Average Latency",
        value: `${Math.round(metrics.average_latency_ms)} ms`,
        detail: "End-to-end provider round trip",
        icon: Clock3,
      },
      {
        label: "Errors",
        value: metrics.error_count.toLocaleString(),
        detail: "Failed OpenAI or backend requests",
        icon: ServerCrash,
        tone: metrics.error_count > 0 ? ("danger" as const) : ("neutral" as const),
      },
      {
        label: "Suspicious Prompts",
        value: metrics.suspicious_count.toLocaleString(),
        detail: "Prompt injection and exfiltration signals",
        icon: AlertTriangle,
        tone: metrics.suspicious_count > 0 ? ("warning" as const) : ("neutral" as const),
      },
      {
        label: "Tokens",
        value: metrics.total_tokens.toLocaleString(),
        detail: "Prompt and completion tokens",
        icon: Sigma,
      },
    ],
    [metrics],
  );

  function onRequestCreated(request: LlmRequest) {
    setRequests((current) => [request, ...current].slice(0, 25));
    refresh().catch((err) => setError(err instanceof Error ? err.message : "Failed to refresh dashboard"));
  }

  return (
    <main className="min-h-screen">
      <header className="border-b border-[var(--border)] bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
            <div>
              <p className="text-sm font-semibold uppercase text-[var(--accent)]">AI Reliability Dashboard</p>
              <h1 className="mt-1 text-3xl font-semibold tracking-normal">LLM Observability Platform</h1>
            </div>
            <div className="rounded-md border border-[var(--border)] px-3 py-2 font-mono text-xs text-[var(--muted)]">
              FastAPI · PostgreSQL · Prometheus · OpenTelemetry
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[1fr_380px] lg:px-8">
        <div className="space-y-6">
          {error ? <p className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p> : null}
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {metricCards.map((card) => (
              <MetricCard key={card.label} {...card} value={isLoading ? "Loading" : card.value} />
            ))}
          </section>
          <RequestTable requests={requests} />
        </div>
        <aside>
          <PromptConsole onCreated={onRequestCreated} />
        </aside>
      </div>
    </main>
  );
}
