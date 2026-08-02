const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:38000";

async function fetchJson(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  tasks: {
    list: (params?: { status?: string; agent_id?: string }) =>
      fetchJson(`/tasks?${new URLSearchParams(params || {})}`),
    get: (id: string) => fetchJson(`/tasks/${id}`),
    create: (data: any) => fetchJson("/tasks", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: any) =>
      fetchJson(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    start: (id: string) => fetchJson(`/tasks/${id}/start`, { method: "POST" }),
    score: (id: string) => fetchJson(`/tasks/${id}/score`, { method: "POST" }),
    graph: (id: string) => fetchJson(`/tasks/${id}/dependency-graph`),
  },
  agents: {
    list: (params?: { agent_type?: string; status?: string }) =>
      fetchJson(`/agents?${new URLSearchParams(params || {})}`),
    get: (id: string) => fetchJson(`/agents/${id}`),
    create: (data: any) => fetchJson("/agents", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: any) =>
      fetchJson(`/agents/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: string) => fetchJson(`/agents/${id}`, { method: "DELETE" }),
  },
  scores: {
    list: (params?: { task_id?: string; decision?: string }) =>
      fetchJson(`/scores?${new URLSearchParams(params || {})}`),
    get: (id: string) => fetchJson(`/scores/${id}`),
    override: (id: string, data: any) =>
      fetchJson(`/scores/${id}/override`, { method: "POST", body: JSON.stringify(data) }),
  },
  pii: {
    scrub: (data: any) => fetchJson("/pii/scrub", { method: "POST", body: JSON.stringify(data) }),
    scans: (taskId: string) => fetchJson(`/pii/scans/${taskId}`),
  },
  browser: {
    verify: (data: any) =>
      fetchJson("/browser/verify", { method: "POST", body: JSON.stringify(data) }),
    list: (taskId: string) => fetchJson(`/browser/verifications/${taskId}`),
  },
  webhooks: {
    list: (params?: { source?: string; processed?: boolean }) => {
      const query = new URLSearchParams();
      if (params?.source) query.set("source", params.source);
      if (params?.processed !== undefined) query.set("processed", String(params.processed));
      return fetchJson(`/webhooks?${query.toString()}`);
    },
    retry: (id: string) => fetchJson(`/webhooks/${id}/retry`, { method: "POST" }),
  },
  health: () => fetchJson("/health"),
};

export function connectSSE(
  orgId: string,
  onMessage: (data: any) => void,
  onOpen?: () => void,
  onError?: () => void
) {
  const es = new EventSource(`${API_BASE}/sse/org/${orgId}`);
  es.onopen = () => {
    if (onOpen) onOpen();
  };
  es.onmessage = (e) => {
    try {
      onMessage(JSON.parse(e.data));
    } catch {}
  };
  es.onerror = () => {
    if (onError) onError();
  };
  return es;
}
