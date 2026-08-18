import type {
  Adapter,
  AgentRun,
  AssetItem,
  BackendHealth,
  Capability,
  ChatResponse,
  ConversationItem,
  Goal,
  GoalPlan,
  MemoryItem,
  ProjectItem,
  ReadinessResponse,
  RouteResult,
  GenerationItem,
  SupabaseStatus,
  Run,
  RunDetails,
  TaskItem,
  VoiceStatus,
  GitHubHealth,
  GitHubConnection,
  GitHubRepositoryItem,
  GitHubAuditItem,
  ProviderStatusResponse,
  CapabilityExecutionResponse,
  RenderHealth,
} from "./types";

// The public canonical service is deliberately the development fallback. A
// configured NEXT_PUBLIC_API_URL always wins, while an unset local frontend
// no longer points Agent Nexus controls at an unrelated, unconfigured port.
const CANONICAL_DAVID_API_URL = "https://david-ademola.onrender.com";
const primaryBase = (process.env.NEXT_PUBLIC_API_URL || CANONICAL_DAVID_API_URL).replace(/\/$/, "");
const fallbackBase = (process.env.NEXT_PUBLIC_API_FALLBACK_URL || "").replace(/\/$/, "");
const bases = [primaryBase, fallbackBase].filter((base, index, all) => Boolean(base) && all.indexOf(base) === index);

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let lastError: Error | null = null;

  for (const base of bases) {
    try {
      const headers = new Headers(init?.headers);
      if (!(init?.body instanceof FormData)) headers.set("Content-Type", "application/json");
      const response = await fetch(`${base}${path}`, {
        ...init,
        headers,
        cache: "no-store",
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `${response.status} ${response.statusText}`);
      }

      return (await response.json()) as T;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error("Request failed");
    }
  }

  throw lastError || new Error("No backend endpoint configured");
}

async function requestAnyPath<T>(paths: string[], init?: RequestInit): Promise<T> {
  let lastError: Error | null = null;

  for (const path of paths) {
    try {
      return await request<T>(path, init);
    } catch (error) {
      lastError = error instanceof Error ? error : new Error("Request failed");
    }
  }

  throw lastError || new Error("No backend endpoint configured");
}

const json = (body: unknown): RequestInit => ({
  method: "POST",
  body: JSON.stringify(body),
});

export const api = {
  // `/api/health` is the repository's canonical contract. `/health` preserves
  // compatibility with the currently deployed Render service while it catches up.
  health: () => requestAnyPath<BackendHealth>(["/api/health", "/health"]),
  chat: (message: string, conversationId?: string) =>
    request<ChatResponse>("/api/chat", json({ message, conversation_id: conversationId })),
  agents: {
    list: () => request<Array<{ name: string; description: string; capabilities: string[] }>>("/api/agents"),
    dispatch: (agentName: string, goal: string, background = true) =>
      request<AgentRun>("/api/agents/dispatch", json({ agent_name: agentName, goal, background })),
    runs: (limit = 20) => request<AgentRun[]>(`/api/agents/runs?limit=${Math.max(1, Math.min(limit, 100))}`),
    run: (runId: string) => request<AgentRun>(`/api/agents/runs/${encodeURIComponent(runId)}`),
    cancel: (runId: string) => request<AgentRun>(`/api/agents/runs/${encodeURIComponent(runId)}/cancel`, { method: "POST" }),
  },
  voiceStatus: () => request<VoiceStatus>("/api/voice/status"),
  synthesize: (text: string) =>
    request<{
      audio_base64?: string | null;
      audio_format?: string;
      voice_id?: string;
      model_id?: string;
      audio_available?: boolean;
      provider?: string;
      text_fallback?: string;
      reason?: string | null;
    }>("/api/voice/synthesize", json({ text })),
  transcribe: (audioBase64: string, language?: string, audioFormat = "webm") =>
    request<{ text: string; language?: string; confidence?: number | null; provider?: string }>(
      "/api/voice/transcribe",
      json({ audio_base64: audioBase64, language: language || null, audio_format: audioFormat }),
    ),
  memories: () => request<MemoryItem[]>("/api/memory"),
  addMemory: (payload: Partial<MemoryItem> & { content: string }) => request<MemoryItem>("/api/memory", json(payload)),
  searchMemories: (query: string) => request<MemoryItem[]>(`/api/memory/search?q=${encodeURIComponent(query)}`),
  deleteMemory: (id: string) => request<void>(`/api/memory/${id}`, { method: "DELETE" }),
  projects: () => request<ProjectItem[]>("/api/projects"),
  createProject: (payload: Partial<ProjectItem> & { name: string }) => request<ProjectItem>("/api/projects", json(payload)),
  tasks: () => request<TaskItem[]>("/api/projects/tasks"),
  createTask: (payload: Partial<TaskItem> & { title?: string; description?: string }) => request<TaskItem>("/api/projects/tasks", json(payload)),
  conversations: () => request<ConversationItem[]>("/api/conversations"),
  websiteGenerate: (prompt: string, projectId?: string) => request<Record<string, unknown>>("/api/website/generate", json({ prompt, project_id: projectId || null })),
  planCreate: (goal: string) => request<Record<string, unknown>>("/api/plan", json({ goal })),
  login: (email: string, password: string) => request<Record<string, unknown>>("/api/auth/login", json({ email, password })),
  register: (name: string, email: string, password: string) => request<Record<string, unknown>>("/api/auth/register", json({ name, email, password })),
  uploadFile: (file: File, projectId?: string, kind = "other") => {
    const form = new FormData();
    form.append("file", file);
    if (projectId) form.append("project_id", projectId);
    form.append("kind", kind);
    return request<AssetItem & { status?: string; stored_as?: string; backend?: string }>("/api/files/upload", { method: "POST", body: form });
  },

  library: {
    status: () => request<SupabaseStatus>("/api/library/status"),
    assets: (projectId?: string, kind?: string) => request<AssetItem[]>(`/api/library/assets${projectId || kind ? `?${new URLSearchParams({ ...(projectId ? { project_id: projectId } : {}), ...(kind ? { kind } : {}) }).toString()}` : ""}`),
    favorite: (assetId: string, favorite: boolean) => request<AssetItem>(`/api/library/assets/${assetId}/favorite`, json({ favorite })),
    generations: (projectId?: string) => request<GenerationItem[]>(`/api/library/generations${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`),
    createGeneration: (payload: Partial<GenerationItem> & { kind?: string; prompt?: string }) => request<GenerationItem>("/api/library/generations", json(payload)),
  },

  providers: {
    list: () => request<ProviderStatusResponse>("/api/providers"),
    capabilities: () => request<Record<string, unknown>>("/api/providers/capabilities"),
    reasoning: (prompt: string, preferredProviders: string[] = []) => request<CapabilityExecutionResponse>("/api/providers/reasoning", json({ prompt, preferred_providers: preferredProviders })),
    image: (prompt: string, preferredProviders: string[] = []) => request<CapabilityExecutionResponse>("/api/providers/images", json({ prompt, preferred_providers: preferredProviders })),
    execute: (capability: string, payload: Record<string, unknown> = {}, preferredProviders: string[] = []) => request<CapabilityExecutionResponse>("/api/providers/execute", json({ capability, payload, preferred_providers: preferredProviders })),
  },

  deployments: {
    renderHealth: () => request<RenderHealth>("/api/deployments/render/health"),
    services: () => request<Record<string, unknown> | unknown[]>("/api/deployments/render/services"),
    deploy: (serviceId: string, clearCache = false) => request<Record<string, unknown>>(`/api/deployments/render/services/${encodeURIComponent(serviceId)}/deploy?clear_cache=${clearCache ? "true" : "false"}`, { method: "POST" }),
  },

  integrations: {
    sources: () =>
      request<{
        status: string;
        primary_repository: string;
        count: number;
        sources: Array<{
          id: string;
          name: string;
          repository: string;
          family: string;
          adapted_capabilities: string[];
          integration_boundary: string;
          source_files: string[];
        }>;
      }>("/api/integrations/sources"),
  },

  orchestrator: {
    process: (message: string, context: Record<string, unknown> = {}) =>
      request<{
        text: string;
        plan_id?: string | null;
        objective?: string | null;
        agents_used: string[];
        providers_used: string[];
        tasks_completed: number;
        tasks_failed: number;
        total_tasks: number;
        task_details: Array<Record<string, unknown>>;
      }>("/api/orchestrator/process", json({ message, context, use_multi_agent: true })),
    status: () => request<Record<string, unknown>>("/api/orchestrator/status"),
    agents: () => request<{ agents: Array<Record<string, unknown>> }>("/api/orchestrator/agents"),
    plans: () => request<{ plans: Array<Record<string, unknown>>; total: number }>("/api/orchestrator/plans"),
  },
  intelligence: {
    health: () => request<Record<string, unknown>>("/api/intelligence/health"),
    readiness: () => request<ReadinessResponse>("/api/intelligence/readiness"),
    capabilities: () => request<{ capabilities: Capability[] }>("/api/intelligence/capabilities"),
    adapters: () => request<{ adapters: Adapter[] }>("/api/intelligence/adapters"),
    agents: () => request<Record<string, unknown>>("/api/intelligence/agents"),
    tools: () => request<Record<string, unknown>>("/api/intelligence/tools"),
    providers: () => request<Record<string, unknown>>("/api/intelligence/providers"),
    workflows: () => request<Record<string, unknown>>("/api/intelligence/workflows"),
    policies: () => request<Record<string, unknown>>("/api/intelligence/policies"),
    route: (objective: string, requestedCapability?: string) =>
      request<RouteResult>("/api/intelligence/route", json({ objective, requested_capability: requestedCapability || null })),
    createGoal: (objective: string, context?: Record<string, unknown>) =>
      request<Goal>("/api/intelligence/goals", json({ objective, context: context || {} })),
    planGoal: (goalId: string) => request<GoalPlan>(`/api/intelligence/goals/${goalId}/plan`, { method: "POST" }),
    createRun: (goalId: string, objective?: string, requestedCapability?: string) =>
      request<Run>("/api/intelligence/runs", json({ goal_id: goalId, objective, requested_capability: requestedCapability || null })),
    authorizeRun: (runId: string, capability: string) =>
      request<Record<string, unknown>>(`/api/intelligence/runs/${runId}/authorize?capability=${encodeURIComponent(capability)}`, { method: "POST" }),
    executeRun: (runId: string, payload: { approved?: boolean; objective?: string; requested_capability?: string; input?: Record<string, unknown> } = {}) =>
      request<Record<string, unknown>>(`/api/intelligence/runs/${runId}/execute`, json(payload)),
    runDetails: (runId: string) => request<RunDetails>(`/api/intelligence/runs/${runId}`),
  },

  github: {
    health: () => request<GitHubHealth>("/api/github/health"),
    connection: () => request<GitHubConnection>("/api/github/connection"),
    connect: () => request<{ authorize_url: string; state: string }>("/api/github/connect", { method: "POST" }),
    connectCallback: (code: string, state: string) =>
      request<Record<string, unknown>>("/api/github/connect/callback", json({ code, state })),
    disconnect: () => request<Record<string, unknown>>("/api/github/disconnect", { method: "POST" }),
    repositories: (projectId?: string) =>
      request<GitHubRepositoryItem[]>(`/api/github/repositories${projectId ? `?project_id=${encodeURIComponent(projectId)}` : ""}`),
    createRepository: (topic: string, projectId?: string, options?: { private?: boolean }) =>
      request<GitHubRepositoryItem>(
        "/api/github/repositories",
        json({ topic, project_id: projectId || null, private: options?.private ?? true }),
      ),
    initializeRepository: (repositoryId: string, files: Record<string, string>) =>
      request<Record<string, unknown>>(`/api/github/repositories/${encodeURIComponent(repositoryId)}/initialize`, json({ files })),
    pushFiles: (repositoryId: string, files: Record<string, string>, commitMessage?: string) =>
      request<Record<string, unknown>>(
        `/api/github/repositories/${encodeURIComponent(repositoryId)}/push`,
        json({ files, commit_message: commitMessage || null }),
      ),
    updateRepository: (repositoryId: string, payload: Record<string, unknown>) =>
      request<GitHubRepositoryItem>(`/api/github/repositories/${encodeURIComponent(repositoryId)}/update`, json(payload)),
    audit: () => request<GitHubAuditItem[]>("/api/github/audit"),
  },
};

export function toAudioUrl(base64: string, format = "wav"): string {
  return `data:audio/${format};base64,${base64}`;
}
