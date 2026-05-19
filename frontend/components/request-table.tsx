import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import type { LlmRequest } from "@/lib/api";

type RequestTableProps = {
  requests: LlmRequest[];
};

function formatTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function RequestTable({ requests }: RequestTableProps) {
  return (
    <section className="overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--panel)] shadow-sm">
      <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3">
        <h2 className="text-base font-semibold">Recent LLM Requests</h2>
        <span className="text-sm text-[var(--muted)]">{requests.length} shown</span>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead className="bg-[var(--panel-muted)] text-xs uppercase text-[var(--muted)]">
            <tr>
              <th className="px-4 py-3 font-semibold">Status</th>
              <th className="px-4 py-3 font-semibold">Model</th>
              <th className="px-4 py-3 font-semibold">Prompt</th>
              <th className="px-4 py-3 font-semibold">Latency</th>
              <th className="px-4 py-3 font-semibold">Tokens</th>
              <th className="px-4 py-3 font-semibold">Cost</th>
              <th className="px-4 py-3 font-semibold">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border)]">
            {requests.map((request) => (
              <tr key={request.request_id} className="align-top">
                <td className="px-4 py-3">
                  {request.is_error ? (
                    <span className="inline-flex items-center gap-1 rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700">
                      <XCircle size={14} /> Error
                    </span>
                  ) : request.is_suspicious ? (
                    <span className="inline-flex items-center gap-1 rounded-md bg-amber-50 px-2 py-1 text-xs font-medium text-amber-700">
                      <AlertTriangle size={14} /> Flagged
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 rounded-md bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">
                      <CheckCircle2 size={14} /> OK
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 font-mono text-xs">{request.model}</td>
                <td className="max-w-md px-4 py-3 text-[var(--foreground)]">
                  <p className="line-clamp-2">{request.error_message ?? request.response ?? "No response captured"}</p>
                  {request.security_flags.length > 0 ? (
                    <p className="mt-1 font-mono text-xs text-[var(--warning)]">{request.security_flags.join(", ")}</p>
                  ) : null}
                </td>
                <td className="px-4 py-3 font-mono">{Math.round(request.latency_ms)} ms</td>
                <td className="px-4 py-3 font-mono">{request.total_tokens.toLocaleString()}</td>
                <td className="px-4 py-3 font-mono">${request.estimated_cost_usd.toFixed(6)}</td>
                <td className="px-4 py-3 font-mono text-xs text-[var(--muted)]">{formatTime(request.created_at)}</td>
              </tr>
            ))}
            {requests.length === 0 ? (
              <tr>
                <td className="px-4 py-8 text-center text-[var(--muted)]" colSpan={7}>
                  No LLM requests have been captured yet.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
