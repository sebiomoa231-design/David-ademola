const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type CapabilityRoute = {
  objective: string;
  selected: null | {
    capability_id: string;
    name: string;
    available: boolean;
    state: string;
    reason?: string | null;
    agent?: string | null;
    skill?: string | null;
    tool?: string | null;
    provider?: string | null;
  };
  fallback_chain: string[];
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || "Request failed");
  }

  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; service: string }>("/api/health"),
  chat: (message: string) =>
    request<{ reply: string; provider: string; capability_routing?: CapabilityRoute }>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
  memories: () => request<any[]>("/api/memory"),
  addMemory: (payload: {
    type?: string;
    content: string;
    confidence?: number;
    importance?: number;
    source?: string;
    tags?: string[];
  }) =>
    request("/api/memory", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  searchMemories: (query: string) =>
    request<any[]>(`/api/memory/search?q=${encodeURIComponent(query)}`),
  projects: () => request<any[]>("/api/projects"),
  createProject: (payload: {
    name: string;
    description?: string;
    goals?: string[];
    decisions?: string[];
    milestones?: string[];
    blockers?: string[];
  }) =>
    request("/api/projects", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  tasks: () => request<any[]>("/api/projects/tasks"),
  conversations: () => request<any[]>("/api/conversations"),
  websiteGenerate: (prompt: string) =>
    request("/api/website/generate", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    }),
  planCreate: (goal: string) =>
    request("/api/plan", {
      method: "POST",
      body: JSON.stringify({ goal }),
    }),
  login: (email: string, password: string) =>
    request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (name: string, email: string, password: string) =>
    request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    }),
  capabilities: () => request<{ capabilities: unknown[] }>("/api/intelligence/capabilities"),
  capabilityDiscovery: () => request("/api/intelligence/capabilities/discovery"),
  routeCapability: (objective: string, requestedCapability?: string) =>
    request<CapabilityRoute>("/api/intelligence/route", {
      method: "POST",
      body: JSON.stringify({ objective, requested_capability: requestedCapability }),
    }),
  createGovernedRequest: (payload: {
    objective: string;
    title?: string;
    requested_capability?: string;
    context?: Record<string, unknown>;
    execute?: boolean;
    approved?: boolean;
    input?: Record<string, unknown>;
  }) =>
    request("/api/intelligence/requests", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
