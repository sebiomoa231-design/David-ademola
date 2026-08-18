import { z } from "zod";
import { protectedProcedure, publicProcedure, router } from "./_core/trpc";

const DAVID_UPSTREAM = process.env.DAVID_API_BASE_URL?.trim().replace(/\/+$/, "");

export type RemoteState = "ready" | "unavailable" | "degraded";

export type RemoteResult<T> = {
  state: RemoteState;
  status: number | null;
  data: T | null;
  message: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function endpointLabel(path: string) {
  return path.replace(/^\/api\//, "");
}

export function unavailableResult<T>(path: string, status: number | null, message?: string): RemoteResult<T> {
  const detail = message || (status === 404
    ? `The connected David AI service does not currently expose ${path}.`
    : `The connected David AI service is unavailable for ${endpointLabel(path)}.`);

  return {
    state: status && status >= 500 ? "degraded" : "unavailable",
    status,
    data: null,
    message: detail,
  };
}

export async function requestDavid<T>(path: string, init?: RequestInit): Promise<RemoteResult<T>> {
  if (!DAVID_UPSTREAM) {
    return unavailableResult<T>(path, null, "David AI Operator backend is not configured. Set the server-side DAVID_API_BASE_URL environment variable.");
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 18_000);

  try {
    const response = await fetch(`${DAVID_UPSTREAM}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });

    const raw = await response.text();
    let data: unknown = null;
    try {
      data = raw ? JSON.parse(raw) : null;
    } catch {
      data = null;
    }

    if (!response.ok) {
      return unavailableResult<T>(path, response.status);
    }

    return {
      state: "ready",
      status: response.status,
      data: data as T,
      message: "Connected to the David AI service.",
    };
  } catch (error) {
    const message = error instanceof Error && error.name === "AbortError"
      ? `The connected David AI service timed out while checking ${endpointLabel(path)}.`
      : `The connected David AI service could not be reached for ${endpointLabel(path)}.`;
    return unavailableResult<T>(path, null, message);
  } finally {
    clearTimeout(timeout);
  }
}

function voiceSummary(result: RemoteResult<unknown>) {
  if (!result.data || !isRecord(result.data)) return result;
  return {
    ...result,
    data: {
      ttsConfigured: Boolean(result.data.tts_configured),
      sttConfigured: Boolean(result.data.stt_configured),
      provider: typeof result.data.tts_provider === "string" ? result.data.tts_provider : null,
      model: typeof result.data.model === "string" ? result.data.model : null,
    },
  };
}

export const davidApiRouter = router({
  status: publicProcedure.query(async () => {
    const [health, voice] = await Promise.all([
      requestDavid<Record<string, unknown>>("/api/health"),
      requestDavid<Record<string, unknown>>("/api/voice/status"),
    ]);

    return { health, voice: voiceSummary(voice) };
  }),

  resources: publicProcedure.query(async () => {
    const [runs, projects, memories, providers] = await Promise.all([
      requestDavid<unknown[]>("/api/intelligence/runs"),
      requestDavid<unknown[]>("/api/projects"),
      requestDavid<unknown[]>("/api/memory"),
      requestDavid<unknown>("/api/providers/status"),
    ]);

    return { runs, projects, memories, providers };
  }),

  chat: publicProcedure
    .input(z.object({ message: z.string().trim().min(1).max(4_000), conversationId: z.string().optional() }))
    .mutation(async ({ input }) => {
      const remote = await requestDavid<Record<string, unknown>>("/api/chat", {
        method: "POST",
        body: JSON.stringify({ message: input.message, conversation_id: input.conversationId }),
      });

      if (!remote.data || !isRecord(remote.data)) return { ...remote, reply: null, provider: null };
      const reply = [remote.data.reply, remote.data.response, remote.data.message, remote.data.content]
        .find((value) => typeof value === "string");
      const provider = typeof remote.data.provider === "string" ? remote.data.provider : null;
      return { ...remote, reply: typeof reply === "string" ? reply : null, provider };
    }),

  synthesize: publicProcedure
    .input(z.object({ text: z.string().trim().min(1).max(1_500) }))
    .mutation(async ({ input }) => requestDavid<Record<string, unknown>>("/api/voice/synthesize", {
      method: "POST",
      body: JSON.stringify({ text: input.text, language_mode: "AUTO" }),
    })),

  voice: router({
    status: publicProcedure.query(async () => requestDavid<Record<string, unknown>>("/api/voice/status")),

    transcribe: protectedProcedure
      .input(z.object({ audioBase64: z.string().min(32).max(24_000_000), language: z.string().trim().min(2).max(12).optional() }))
      .mutation(async ({ input }) => requestDavid<Record<string, unknown>>("/api/voice/transcribe", {
        method: "POST",
        body: JSON.stringify({ audio_base64: input.audioBase64, language: input.language }),
      })),

    synthesize: protectedProcedure
      .input(z.object({ text: z.string().trim().min(1).max(4_000), voiceId: z.string().trim().min(1).max(120).optional() }))
      .mutation(async ({ input }) => requestDavid<Record<string, unknown>>("/api/voice/synthesize", {
        method: "POST",
        body: JSON.stringify({ text: input.text, voice_id: input.voiceId }),
      })),
  }),
});
