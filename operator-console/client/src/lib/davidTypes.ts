export type RemoteState = "ready" | "unavailable" | "degraded";

export type RemoteResult<T> = {
  state: RemoteState;
  status: number | null;
  data: T | null;
  message: string;
};

export type DavidStatus = {
  health: RemoteResult<Record<string, unknown>>;
  voice: RemoteResult<{
    ttsConfigured: boolean;
    sttConfigured: boolean;
    provider: string | null;
    model: string | null;
  }>;
};

export type DavidResources = {
  runs: RemoteResult<unknown[]>;
  projects: RemoteResult<unknown[]>;
  memories: RemoteResult<unknown[]>;
  providers: RemoteResult<unknown>;
};
