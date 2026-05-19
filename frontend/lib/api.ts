export type DashboardMetrics = {
  total_requests: number;
  total_cost_usd: number;
  average_latency_ms: number;
  error_count: number;
  suspicious_count: number;
  total_tokens: number;
};

export type LlmRequest = {
  request_id: string;
  trace_id: string | null;
  model: string;
  response: string | null;
  latency_ms: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  is_error: boolean;
  error_message: string | null;
  is_suspicious: boolean;
  security_flags: string[];
  created_at: string;
};

export type ChatPayload = {
  prompt: string;
  model?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  return request<DashboardMetrics>("/dashboard/metrics");
}

export async function getRecentRequests(): Promise<LlmRequest[]> {
  return request<LlmRequest[]>("/requests?limit=25");
}

export async function sendChat(payload: ChatPayload): Promise<LlmRequest> {
  return request<LlmRequest>("/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
